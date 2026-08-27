#!/usr/bin/env python3
"""Regression tests for the GitHub/UE P0 control plane."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "Scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ruleset = load_module("github_p0_ruleset", ROOT / "Scripts" / "github_p0_ruleset.py")
public = load_module("github_p0_public_verify", ROOT / "Scripts" / "github_p0_public_verify.py")
admin = load_module("github_p0_admin", ROOT / "Scripts" / "github_p0_admin.py")
status = load_module("github_p0_status", ROOT / "Scripts" / "github_p0_status.py")
readiness = load_module("runner_readiness", ROOT / "Scripts" / "runner_readiness.py")
preflight = load_module("p0_preflight", ROOT / "Scripts" / "p0_preflight.py")
lifecycle = load_module("branch_lifecycle_guard", ROOT / "Scripts" / "branch_lifecycle_guard.py")


class RulesetContractTests(unittest.TestCase):
    def make_ruleset(self) -> dict:
        return json.loads(json.dumps(ruleset.ruleset_payload()))

    def test_canonical_ruleset_passes(self):
        ok, failures = ruleset.evaluate_ruleset(self.make_ruleset())
        self.assertTrue(ok, failures)
        self.assertEqual(failures, [])

    def test_ruleset_is_active_and_targets_main(self):
        data = self.make_ruleset()
        self.assertEqual(data["enforcement"], "active")
        self.assertIn("refs/heads/main", data["conditions"]["ref_name"]["include"])

    def test_evaluate_mode_is_not_real_protection(self):
        data = self.make_ruleset()
        data["enforcement"] = "evaluate"
        ok, failures = ruleset.evaluate_ruleset(data)
        self.assertFalse(ok)
        self.assertTrue(any("active" in item for item in failures))

    def test_missing_required_check_is_blocked(self):
        data = self.make_ruleset()
        status_rule = next(rule for rule in data["rules"] if rule["type"] == "required_status_checks")
        status_rule["parameters"]["required_status_checks"] = [{"context": "static-and-contract"}]
        ok, failures = ruleset.evaluate_ruleset(data)
        self.assertFalse(ok)
        self.assertTrue(any("repository-quality" in item for item in failures))

    def test_non_strict_status_policy_is_blocked(self):
        data = self.make_ruleset()
        status_rule = next(rule for rule in data["rules"] if rule["type"] == "required_status_checks")
        status_rule["parameters"]["strict_required_status_checks_policy"] = False
        ok, failures = ruleset.evaluate_ruleset(data)
        self.assertFalse(ok)
        self.assertTrue(any("aktuell" in item for item in failures))

    def test_force_push_or_delete_gap_is_blocked(self):
        data = self.make_ruleset()
        data["rules"] = [rule for rule in data["rules"] if rule["type"] not in {"deletion", "non_fast_forward"}]
        ok, failures = ruleset.evaluate_ruleset(data)
        self.assertFalse(ok)
        self.assertTrue(any("Löschen" in item for item in failures))
        self.assertTrue(any("Force-Push" in item for item in failures))

    def test_bypass_actor_is_blocked(self):
        data = self.make_ruleset()
        data["bypass_actors"] = [{"actor_id": 1, "actor_type": "RepositoryRole", "bypass_mode": "always"}]
        ok, failures = ruleset.evaluate_ruleset(data)
        self.assertFalse(ok)
        self.assertTrue(any("Bypass" in item for item in failures))

    def test_ruleset_does_not_require_cp1_runtime_yet(self):
        data = self.make_ruleset()
        status_rule = next(rule for rule in data["rules"] if rule["type"] == "required_status_checks")
        contexts = {item["context"] for item in status_rule["parameters"]["required_status_checks"]}
        self.assertNotIn("cp1-runtime", contexts)

    def test_duplicate_name_is_not_treated_as_unique(self):
        item = {"id": 1, "name": ruleset.RULESET_NAME}
        self.assertIsNone(ruleset.find_named_ruleset([item, dict(item, id=2)]))


class PublicRulesetVerifierTests(unittest.TestCase):
    def setUp(self):
        self.original_get = public.github_get

    def tearDown(self):
        public.github_get = self.original_get

    def test_public_verifier_accepts_only_live_detail_that_matches_contract(self):
        detail = json.loads(json.dumps(ruleset.ruleset_payload()))
        detail["id"] = 42

        def fake_get(path: str):
            if path.endswith("/rulesets"):
                return True, [{"id": 42, "name": ruleset.RULESET_NAME}], ""
            if path.endswith("/rulesets/42"):
                return True, detail, ""
            return False, None, "unexpected endpoint"

        public.github_get = fake_get
        ok, message = public.verify_public_ruleset()
        self.assertTrue(ok, message)
        self.assertIn("42", message)

    def test_public_verifier_rejects_missing_ruleset(self):
        public.github_get = lambda path: (True, [], "")
        ok, message = public.verify_public_ruleset()
        self.assertFalse(ok)
        self.assertIn("nicht vorhanden", message)

    def test_public_verifier_rejects_evaluate_only_ruleset(self):
        detail = json.loads(json.dumps(ruleset.ruleset_payload()))
        detail["id"] = 42
        detail["enforcement"] = "evaluate"

        def fake_get(path: str):
            if path.endswith("/rulesets"):
                return True, [{"id": 42, "name": ruleset.RULESET_NAME}], ""
            return True, detail, ""

        public.github_get = fake_get
        ok, message = public.verify_public_ruleset()
        self.assertFalse(ok)
        self.assertIn("active", message)


class GitHubAdminDiagnosticTests(unittest.TestCase):
    def test_repo_admin_permission_is_accepted(self):
        ok, detail = admin.repo_admin_capability(
            {
                "full_name": admin.REPO,
                "archived": False,
                "permissions": {"admin": True, "maintain": True, "push": True},
            }
        )
        self.assertTrue(ok)
        self.assertIn("Adminrecht", detail)

    def test_maintain_without_admin_is_blocked(self):
        ok, detail = admin.repo_admin_capability(
            {
                "full_name": admin.REPO,
                "archived": False,
                "permissions": {"admin": False, "maintain": True, "push": True},
            }
        )
        self.assertFalse(ok)
        self.assertIn("Maintain", detail)

    def test_wrong_repository_is_blocked(self):
        ok, detail = admin.repo_admin_capability(
            {"full_name": "someone/else", "archived": False, "permissions": {"admin": True}}
        )
        self.assertFalse(ok)
        self.assertIn("falsches Repository", detail)

    def test_403_is_classified_as_authorization(self):
        code, _, next_step = admin.classify_gh_error("gh: Resource not accessible by integration (HTTP 403)")
        self.assertEqual(code, "AUTHORIZATION_403")
        self.assertIn("Admin", next_step)

    def test_404_is_classified_as_resource_problem(self):
        code, _, _ = admin.classify_gh_error("gh: Not Found (HTTP 404)")
        self.assertEqual(code, "RESOURCE_404")

    def test_422_is_classified_as_validation_problem(self):
        code, _, _ = admin.classify_gh_error("gh: Validation Failed (HTTP 422)")
        self.assertEqual(code, "VALIDATION_422")

    def test_unknown_error_is_not_misclassified(self):
        code, _, _ = admin.classify_gh_error("connection reset")
        self.assertEqual(code, "UNKNOWN_GITHUB_ERROR")


class GitHubStatusDiagnosticTests(unittest.TestCase):
    def test_server_protected_true_is_recognized(self):
        self.assertTrue(status.branch_protected_hint({"name": "main", "protected": True}))

    def test_server_protected_false_is_not_pass(self):
        self.assertFalse(status.branch_protected_hint({"name": "main", "protected": False}))

    def test_wrong_branch_cannot_prove_main(self):
        self.assertFalse(status.branch_protected_hint({"name": "develop", "protected": True}))

    def test_protection_evaluation_requires_both_checks_and_core_rules(self):
        good = {
            "required_status_checks": {
                "strict": True,
                "contexts": ["static-and-contract", "repository-quality"],
            },
            "enforce_admins": {"enabled": True},
            "required_pull_request_reviews": {"dismiss_stale_reviews": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
        }
        ok, checks = status.evaluate_protection(good)
        self.assertTrue(ok)
        self.assertEqual(checks, {"static-and-contract", "repository-quality"})

        bad = json.loads(json.dumps(good))
        bad["required_status_checks"]["contexts"] = ["static-and-contract"]
        ok, _ = status.evaluate_protection(bad)
        self.assertFalse(ok)


class EngineVersionTests(unittest.TestCase):
    def write_version(self, root: Path, major: int, minor: int) -> None:
        path = root / "Engine" / "Build" / "Build.version"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"MajorVersion": major, "MinorVersion": minor}), encoding="utf-8")

    def test_exact_58_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_version(root, 5, 8)
            ok, data, detail = readiness.read_engine_version(root)
        self.assertTrue(ok)
        self.assertEqual(data["MajorVersion"], 5)
        self.assertEqual(detail, "5.8")

    def test_57_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_version(root, 5, 7)
            ok, _, detail = readiness.read_engine_version(root)
        self.assertFalse(ok)
        self.assertEqual(detail, "5.7")

    def test_missing_version_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            ok, data, detail = readiness.read_engine_version(Path(td))
        self.assertFalse(ok)
        self.assertIsNone(data)
        self.assertIn("missing", detail)


class BranchLifecycleTests(unittest.TestCase):
    def test_main_is_never_feature_branch_reuse(self):
        self.assertFalse(lifecycle.branch_reused_after_merge("main", [{"number": 1}], 3))

    def test_merged_feature_branch_with_new_commits_is_blocked(self):
        self.assertTrue(lifecycle.branch_reused_after_merge("feature/x", [{"number": 1}], 2))

    def test_merged_feature_branch_without_new_commits_is_not_reuse(self):
        self.assertFalse(lifecycle.branch_reused_after_merge("feature/x", [{"number": 1}], 0))

    def test_open_or_never_merged_branch_is_allowed(self):
        self.assertFalse(lifecycle.branch_reused_after_merge("feature/x", [], 5))

    def test_invalid_pr_json_is_safe_empty(self):
        self.assertEqual(lifecycle.parse_merged_prs("not-json"), [])


class PreflightDecisionTests(unittest.TestCase):
    def result(self, key: str, code: int) -> object:
        steps = {step.key: step for step in (*preflight.BASE_STEPS, preflight.READINESS_STEP)}
        return preflight.StepResult(steps[key], code)

    def baseline(self) -> list[object]:
        return [
            self.result("branch", 0),
            self.result("static", 0),
            self.result("quality", 0),
            self.result("github", 0),
        ]

    def test_preflight_uses_token_free_ruleset_verifier(self):
        github_step = next(step for step in preflight.BASE_STEPS if step.key == "github")
        self.assertIn("github_p0_public_verify.py", github_step.command[-1])

    def test_branch_failure_has_highest_priority(self):
        results = self.baseline()
        results[0] = self.result("branch", 2)
        self.assertIn("Neuen Arbeitsbranch", preflight.next_action(results, False))

    def test_static_failure_is_next_action(self):
        results = self.baseline()
        results[1] = self.result("static", 1)
        self.assertIn("Statische Fehler", preflight.next_action(results, False))

    def test_quality_failure_is_next_action(self):
        results = self.baseline()
        results[2] = self.result("quality", 1)
        self.assertIn("Quality Guard", preflight.next_action(results, False))

    def test_github_failure_points_to_admin_doctor_and_ruleset(self):
        results = self.baseline()
        results[3] = self.result("github", 2)
        action = preflight.next_action(results, False)
        self.assertIn("github_p0_admin.py --doctor", action)
        self.assertIn("github_p0_admin.py --apply-ruleset", action)

    def test_hosted_pass_points_to_ue_machine(self):
        self.assertIn("--full", preflight.next_action(self.baseline(), False))

    def test_full_readiness_failure_blocks_activation(self):
        results = self.baseline() + [self.result("readiness", 1)]
        action = preflight.next_action(results, True)
        self.assertIn("Readiness", action)
        self.assertNotIn("enable-runner-variable", action)

    def test_full_pass_points_to_guarded_activation(self):
        results = self.baseline() + [self.result("readiness", 0)]
        action = preflight.next_action(results, True)
        self.assertIn("--apply-ruleset", action)
        self.assertIn("--enable-runner-variable", action)
        self.assertIn("CP1 UE 5.8 Runtime", action)


if __name__ == "__main__":
    unittest.main()

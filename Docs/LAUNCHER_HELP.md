# BUNKER BEATS — Hilfe zum intelligenten Qualitätssystem

## 1. Was macht der Startassistent?

Er prüft zuerst die Umgebung und bekannte Regressionen. Danach entscheidet er, ob Build/Runtime überhaupt sinnvoll gestartet werden darf.

## 2. Was bedeutet Rot?

Ein kritischer Zustand blockiert den abhängigen Start. Die Oberfläche zeigt Fehlercode, Ursache, betroffene Evidenz und mögliche Lösungen.

## 3. Was bedeutet Gelb?

Das Projekt ist nicht vollständig startbereit. Eine Voraussetzung oder belastbare Evidenz fehlt. Die Runtime wird nicht einfach „auf gut Glück“ gestartet.

## 4. Was wird aus Fehlern gelernt?

Jeder relevante Fehler erzeugt einen Laufnachweis. Wiederkehrende Fehler werden zu dauerhaften Preflight-Regeln.

## 5. Warum mehrere Lösungen?

Der Assistent bewertet Lösungen nach Risiko, Reversibilität, Aufwand und Evidenz. Die risikoärmste sinnvolle Option wird bevorzugt angezeigt.

## 6. Warum wird nicht alles automatisch installiert?

Systemweite Installationen und unbekannte Downloads können Daten oder die Entwicklungsumgebung beschädigen. Solche Schritte werden deshalb transparent vorbereitet und müssen bewusst bestätigt werden.

## 7. Kann das Tool Fehler selbst beheben?

Ja, bei eindeutig sicheren, lokalen und deterministischen Problemen. Danach wird immer erneut geprüft. Eine Reparatur zählt erst dann als erfolgreich, wenn die relevante Prüfung anschließend wirklich bestanden wurde.

## 8. Was ist eine Konfidenzangabe?

Sie beschreibt die Stärke einer Ursachenzuordnung:
- HIGH = reproduziert/erhärtet
- MEDIUM = starke Evidenz, aber noch nicht vollständig bestätigt
- LOW = schwache Korrelation
- NONE = keine belastbare Zuordnung.

Eine Konfidenz ist keine automatische Behauptung von Kausalität.

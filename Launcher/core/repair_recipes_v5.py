
RECIPES={
"SET_UE_ROOT_OR_INSTALL":{"mode":"ASSISTED","safe":False,
 "steps":["UE_ROOT auf das echte UE-5.8-Verzeichnis setzen.","RunUAT und UnrealEditor-Cmd erneut prüfen."]},
"INSTALL_VERIFIED_CLANG":{"mode":"ASSISTED","safe":False,
 "steps":["Unterstützte Linux-Umgebung prüfen.","Verifizierte Clang-/Toolchain-Version bereitstellen.","Preflight erneut ausführen."]},
"UPGRADE_SUPPORTED_OS":{"mode":"ASSISTED","safe":False,
 "steps":["Distribution und glibc prüfen.","Unterstützte OS-Version bereitstellen.","Preflight erneut ausführen."]},
"INSTALL_VS_CPP_TOOLCHAIN":{"mode":"ASSISTED","safe":False,
 "steps":["VS 2022 17.14+ bzw. empfohlene Umgebung bereitstellen.","C++ Build Tools aktivieren.","Preflight erneut ausführen."]},
"INSPECT_WINDOWS_SDK":{"mode":"READ_ONLY","safe":True,
 "steps":["Installierte SDK-Versionen lesen.","Mindestversion vergleichen."]}
}

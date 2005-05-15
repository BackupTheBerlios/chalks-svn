!define VER_MAJOR 0.0.1
!define DNAME Chalks

; The name of the installer
Name ${DNAME}

; The file to write
OutFile ${DNAME}-${VER_MAJOR}-win32.exe
SetCompressor bzip2

LicenseText "Chalks is licensed under the GPL"
LicenseData "COPYING"

; The default installation directory
InstallDir $PROGRAMFILES\${DNAME}
; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM SOFTWARE\${DNAME} "Install_Dir"

; The text to prompt the user to enter a directory
ComponentText "This will install ${DNAME} for Windows(tm) on your computer."
; The text to prompt the user to enter a directory
DirText "Choose a destination directory:"

; The stuff to install
Section "${DNAME} (required)"
  ;Annoying disclaimers
  ;MessageBox MB_OK "This is a BETA version. Please report all bugs at http://chalks.berlios.de/"
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  ; Put all files inside dist\ folder there
  File /r "dist\*.*"

  ; DLLs
  ;File msvcp71.dll
  ;File msvcr71.dll
    
  ; Documentation
  File README
  File AUTHORS
  ;File THANKS
  File COPYING
  ;File INSTALL
  File TODO
  ;File ChangeLog  
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\${DNAME} "Install_Dir" "$INSTDIR"
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${DNAME}" "DisplayName" "${DNAME} (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${DNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteUninstaller "uninstall.exe"
SectionEnd

; optional section
Section "Start Menu Shortcuts"
  CreateDirectory "$SMPROGRAMS\${DNAME}"
  CreateShortCut "$SMPROGRAMS\${DNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\${DNAME}\${DNAME}.lnk" "$INSTDIR\${DNAME}.exe" "" "$INSTDIR\${DNAME}.exe" 0
SectionEnd

; uninstall stuff

UninstallText "This will uninstall ${DNAME}. Hit next to continue."

; special uninstall section.
Section "Uninstall"
  ; remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${DNAME}"
  DeleteRegKey HKLM SOFTWARE\${DNAME}
  ; MUST REMOVE UNINSTALLER, too
  Delete $INSTDIR\uninstall.exe
  ; remove shortcuts, if any.
  Delete "$SMPROGRAMS\${DNAME}\*.*"
  ; remove directories used.
  RMDir "$SMPROGRAMS\${DNAME}"
  RMDir "$INSTDIR"
SectionEnd

; eof

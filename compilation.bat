@echo off
REM build_bigscreen.bat

REM Définir les noms des scripts Python et des exécutables
set SCRIPT_NAME_1=bs-frontend.py
set EXE_NAME_1="Big Screen"
set SCRIPT_NAME_2=bs-options.py
set EXE_NAME_2="options"
set SCRIPT_NAME_3=bs-mamewindow.py
set EXE_NAME_3="mamewindow"

REM Définir les chemins des icônes
set ICON_PATH_1=bs-frontend.ico
set ICON_PATH_2=bs-options.ico
set ICON_PATH_3=bs-mamewindow.ico

REM Nettoyer les anciens fichiers build et dist
rmdir /s /q build
rmdir /s /q dist

REM Créer l'exécutable pour bs-frontend.py avec PyInstaller
pyinstaller --onefile ^
            --windowed ^
            --add-data "variables.ini;." ^
            --icon=%ICON_PATH_1% ^
            --name=%EXE_NAME_1% ^
            --hidden-import=pygame ^
            %SCRIPT_NAME_1%

REM Créer l'exécutable pour bs-options.py avec PyInstaller
pyinstaller --onefile ^
            --windowed ^
            --icon=%ICON_PATH_2% ^
            --name=%EXE_NAME_2% ^
            %SCRIPT_NAME_2%

REM Créer l'exécutable pour bs-mamewindow.py avec PyInstaller
pyinstaller --onefile ^
            --windowed ^
            --icon=%ICON_PATH_3% ^
            --name=%EXE_NAME_3% ^
            %SCRIPT_NAME_3%

REM Vérifier si la création a réussi
if %ERRORLEVEL% == 0 (
    echo La création des exécutables a réussi.
    echo Les exécutables se trouvent dans le dossier 'dist'.
) else (
    echo Une erreur s'est produite lors de la création des exécutables.
)

REM Pause pour voir les résultats
pause
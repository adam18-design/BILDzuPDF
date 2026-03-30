@echo off
setlocal

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

pyinstaller --noconfirm --clean --onefile --windowed --name BILDzuPDF bild2pdf_gui.py
if errorlevel 1 exit /b 1

if exist dist\BILDzuPDF-Portable rmdir /s /q dist\BILDzuPDF-Portable
mkdir dist\BILDzuPDF-Portable
copy /y dist\BILDzuPDF.exe dist\BILDzuPDF-Portable\BILDzuPDF.exe >nul
echo Start: BILDzuPDF.exe> dist\BILDzuPDF-Portable\README-Windows.txt
echo Benutzerdaten: Es werden keine Systemdateien geaendert.>> dist\BILDzuPDF-Portable\README-Windows.txt

powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path 'dist/BILDzuPDF-Portable.zip') { Remove-Item 'dist/BILDzuPDF-Portable.zip' -Force }; Compress-Archive -Path 'dist/BILDzuPDF-Portable/*' -DestinationPath 'dist/BILDzuPDF-Portable.zip'"
if errorlevel 1 exit /b 1

where iscc >nul 2>nul
if not errorlevel 1 (
	iscc installer\BILDzuPDF.iss
)

echo.
echo EXE erstellt: dist\BILDzuPDF.exe
if exist dist\BILDzuPDF-Setup.exe echo Installer erstellt: dist\BILDzuPDF-Setup.exe
echo Portable ZIP erstellt: dist\BILDzuPDF-Portable.zip
endlocal

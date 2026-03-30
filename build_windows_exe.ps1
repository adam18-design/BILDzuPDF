$ErrorActionPreference = 'Stop'

python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean --onefile --windowed --name BILDzuPDF bild2pdf_gui.py

if (Test-Path "dist\BILDzuPDF-Portable") {
	Remove-Item -Recurse -Force "dist\BILDzuPDF-Portable"
}

New-Item -ItemType Directory -Path "dist\BILDzuPDF-Portable" | Out-Null
Copy-Item "dist\BILDzuPDF.exe" "dist\BILDzuPDF-Portable\BILDzuPDF.exe"
Set-Content -Path "dist\BILDzuPDF-Portable\README-Windows.txt" -Value "Start: BILDzuPDF.exe`nBenutzerdaten: Es werden keine Systemdateien geaendert."

if (Test-Path "dist\BILDzuPDF-Portable.zip") {
	Remove-Item -Force "dist\BILDzuPDF-Portable.zip"
}
Compress-Archive -Path "dist\BILDzuPDF-Portable\*" -DestinationPath "dist\BILDzuPDF-Portable.zip"

if (Get-Command iscc -ErrorAction SilentlyContinue) {
	iscc "installer\BILDzuPDF.iss"
}

Write-Host ""
Write-Host "EXE erstellt: dist/BILDzuPDF.exe"
if (Test-Path "dist\BILDzuPDF-Setup.exe") {
	Write-Host "Installer erstellt: dist/BILDzuPDF-Setup.exe"
}
Write-Host "Portable ZIP erstellt: dist/BILDzuPDF-Portable.zip"

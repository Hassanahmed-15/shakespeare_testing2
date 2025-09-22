# PowerShell script to download all Shakespeare JSON files from Clean_Plays2 repository
# Run this from your project directory: C:\Users\Dell\Shakespeare-Variorum-2

# Create destination directory if it doesn't exist
$destDir = ".\Public\Data"
if (-not (Test-Path $destDir)) {
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    Write-Host "Created directory: $destDir"
}

# Array of all JSON file URIs
$jsonFiles = @(
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/As_You_Like_It.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Coriolanus.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Cymbeline.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Henry_IV_Part1.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Henry_IV_Part2.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Julius_Caesar.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/King_John.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Loves_Labours_Lost.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Merchant_of_Venice.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Midsummer_Nights_Dream.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Much_Ado_About_Nothing.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Othello.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Richard_II.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Richard_III.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Romeo_and_Juliet.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/The_Tempest.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/The_Winters_Tale.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Troilus_and_Cressida.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Twelfth_Night.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/King_Lear.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Macbeth.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/Hamlet.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/kinglear_notes.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/macbeth_notes.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/macbeth_notes_complete_expanded.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/othello_notes.json",
    "https://raw.githubusercontent.com/Hassanahmed-15/Clean_Plays2/main/hamlet_notes (1).json"
)

Write-Host "Starting download of $($jsonFiles.Count) JSON files..." -ForegroundColor Green

# Download each file
foreach ($url in $jsonFiles) {
    try {
        $fileName = [System.IO.Path]::GetFileName($url)
        $outputPath = Join-Path $destDir $fileName
        
        Write-Host "Downloading: $fileName" -ForegroundColor Yellow
        Invoke-WebRequest -Uri $url -OutFile $outputPath -ErrorAction Stop
        
        # Verify the file was downloaded and has content
        if (Test-Path $outputPath) {
            $fileSize = (Get-Item $outputPath).Length
            Write-Host "✓ Downloaded: $fileName ($fileSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to download: $fileName" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "✗ Error downloading $fileName : $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDownload complete! Files saved to: $destDir" -ForegroundColor Green
Write-Host "Total files processed: $($jsonFiles.Count)" -ForegroundColor Cyan

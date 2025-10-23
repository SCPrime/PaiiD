# List Chrome Extensions
$path = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Extensions"
if (Test-Path $path) {
    Get-ChildItem $path -Directory | ForEach-Object {
        Write-Host "Extension ID: $($_.Name)"
    }
} else {
    Write-Host "Chrome extensions folder not found"
}

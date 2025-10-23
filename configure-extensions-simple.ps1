# Simple Configuration for Dual-AI Extensions

Write-Host "Configuring extensions for dual-AI workflow..." -ForegroundColor Cyan
Write-Host ""

$SettingsPath = "$env:APPDATA\Code\User\settings.json"
$CursorSettingsPath = "$env:APPDATA\Cursor\User\settings.json"

# Key settings to add
$KeySettings = @'
{
  "continue.enableTabAutocomplete": true,
  "errorLens.enabled": true,
  "errorLens.followCursor": "allLines",
  "sonarlint.rules": {
    "typescript:S1186": {"level": "on"},
    "typescript:S3776": {"level": "on"}
  },
  "jest.autoRun": "off",
  "jest.enableInlineErrorMessages": true,
  "gitlens.ai.model": "gitkraken",
  "gitlens.ai.gitkraken.model": "gemini:gemini-2.0-flash",
  "typescript.inlayHints.parameterNames.enabled": "all",
  "typescript.inlayHints.functionLikeReturnTypes.enabled": true,
  "editor.inlineSuggest.enabled": true,
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "todo-tree.general.tags": ["TODO", "FIXME", "CLAUDE", "CHATGPT", "ESCALATE", "REVIEW"]
}
'@

Write-Host "Settings to apply:" -ForegroundColor Yellow
Write-Host $KeySettings -ForegroundColor Gray
Write-Host ""

Write-Host "To complete configuration:" -ForegroundColor Cyan
Write-Host "1. Open VS Code settings (Ctrl+,)" -ForegroundColor White
Write-Host "2. Click {} icon (top right) for settings.json" -ForegroundColor White
Write-Host "3. Add the settings shown above" -ForegroundColor White
Write-Host "4. Save and restart" -ForegroundColor White
Write-Host ""

Write-Host "Configuration guide created!" -ForegroundColor Green
Write-Host "See DUAL_AI_EXTENSIONS_GUIDE.md for details" -ForegroundColor Cyan

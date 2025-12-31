# 示例：在 PowerShell 中为当前会话设置 Poe API Key
# 使用方法：
#   1) 复制本文件为 set_env.ps1（可选）
#   2) 将下面的值替换为你的 key
#   3) 执行：.\set_env.example.ps1

$env:POE_API_KEY = "在这里填入你的key"

Write-Host "已设置 POE_API_KEY（仅当前 PowerShell 会话生效）。"

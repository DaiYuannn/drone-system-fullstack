@echo off
REM 设置 TEST_SERVER 环境变量（当前命令行会话生效）
REM 用法：
REM   交互式：双击或在 cmd 中运行后按提示输入 IP 或完整地址
REM   参数方式：set_test_server_env.bat 1.2.3.4   或   set_test_server_env.bat http://1.2.3.4:5000

set SERVER_INPUT=%~1
if "%SERVER_INPUT%"=="" (
  set /p SERVER_INPUT=请输入服务器IP或完整地址(例如 1.2.3.4 或 http://1.2.3.4:5000): 
)

if "%SERVER_INPUT%"=="" (
  echo 未输入服务器地址。示例：1.2.3.4 或 http://1.2.3.4:5000
  goto :eof
)

set PREFIX=%SERVER_INPUT:~0,4%
if /I "%PREFIX%"=="http" (
  set TEST_SERVER=%SERVER_INPUT%
) else (
  set TEST_SERVER=http://%SERVER_INPUT%:5000
)

echo 已设置 TEST_SERVER=%TEST_SERVER%
echo 请在同一 cmd 会话中运行測試腳本以继承该环境变量，例如：
echo   python tests\windows\random_encrypt_upload.py --count 5 --interval 1
echo.
echo 若需持久化（重启终端后仍有效），可在本会话中执行：
echo   setx TEST_SERVER %TEST_SERVER%

:eof

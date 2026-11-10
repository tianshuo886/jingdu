@echo off
chcp 65001 >nul
title 静读 · 本地书架（关掉本窗口即停止）
cd /d "%~dp0"

set "PY="
if exist "%~dp0runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY if exist "C:\Python312\python.exe" set "PY=C:\Python312\python.exe"
if not defined PY if exist "C:\Python313\python.exe" set "PY=C:\Python313\python.exe"
if not defined PY (
  for /f "delims=" %%P in ('where python.exe 2^>nul') do if not defined PY set "PY=%%P"
)
if not defined PY (
  for /f "delims=" %%P in ('where py.exe 2^>nul') do if not defined PY set "PY=%%P"
)

if defined PY (
  "%PY%" "%~dp0启动器.py"
  goto :end
)

echo.
echo   这台电脑好像没有装 Python。
echo   阅读器本身不需要 Python，可以直接双击：
echo       静读阅读器.html
echo   不过双击打开时，浏览器可能不会自动读取同一文件夹里的书。
echo.
pause

:end

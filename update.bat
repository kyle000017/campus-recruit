@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ====================================
echo   校招信息更新脚本
echo ====================================
cd crawler
python crawler.py
if %errorlevel% neq 0 (
    echo [错误] 爬虫运行失败,请检查网络或依赖
    pause
    exit /b 1
)
echo.
echo [完成] 数据已更新,刷新浏览器即可看到最新信息
pause

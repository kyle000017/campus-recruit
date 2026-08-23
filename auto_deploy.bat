@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM 每日自动更新脚本(配合Windows任务计划程序使用,无人值守)

REM 更新数据
cd crawler
python crawler.py
if %errorlevel% neq 0 exit /b 1
cd ..

REM 提交推送
git add -A
git commit -m "每日自动更新 %date%" >nul 2>nul
git push origin main >nul 2>nul

REM 输出日志(可配合任务计划程序日志)
echo %date% %time% 更新完成 >> deploy.log

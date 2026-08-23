@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   校招信息站 - 一键更新并部署到 Gitee
echo ============================================

REM 第一步:运行爬虫更新数据
echo [1/4] 更新数据...
cd crawler
python crawler.py
if %errorlevel% neq 0 (
    echo [错误] 爬虫运行失败,请检查网络
    pause
    exit /b 1
)
cd ..

REM 第二步:git 提交
echo [2/4] 提交到 git...
git add -A
git commit -m "自动更新校招数据 %date%" 2>nul
if %errorlevel% neq 0 (
    echo 无新数据变化,跳过提交
)

REM 第三步:推送到 Gitee
echo [3/4] 推送到 Gitee...
git push origin main
if %errorlevel% neq 0 (
    echo [错误] 推送失败,请检查:
    echo   - 是否已执行首次配置(git remote add origin 你的仓库地址)
    echo   - 网络是否正常
    echo   - 首次推送可能需要输入 Gitee 账号密码
    pause
    exit /b 1
)

REM 第四步:刷新 Gitee Pages
echo [4/4] 请到 Gitee 仓库页面手动刷新 Pages 服务:
echo   Gitee 仓库 -> 服务 -> Gitee Pages -> 点击"更新"
echo   注: 若首次部署,需先开启 Gitee Pages 服务

echo.
echo [完成] 数据已更新并推送到 Gitee,刷新 Pages 后即可访问
echo 访问地址: https://你的用户名.gitee.io/仓库名/
pause

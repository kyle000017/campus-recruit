# 🚀 校招信息站 Gitee 部署指南

把网站部署到 **Gitee Pages**,实现外网访问,并用**本机每日自动任务**更新数据。

> 原理:网站文件推到 Gitee 仓库,Gitee Pages 生成静态网站;每天由你的电脑定时跑爬虫→推送→刷新 Pages。

---

## 一、注册/登录 Gitee(约2分钟)

1. 浏览器打开 **https://gitee.com**
2. 点右上角"**注册**",用手机号或邮箱注册(或直接登录)
3. 登录后记住你的**用户名**(形如 `yourname`),后面要用

---

## 二、创建 Gitee 仓库(约1分钟)

1. 登录后点右上角"**+**"→"**新建仓库**"
2. 仓库名称填:`campus-recruit`(或任意英文名)
3. **路径**自动生成(形如 `yourname/campus-recruit`)
4. 仓库类型选"**私有**"或"公开"(公开需审核,私有更方便)
5. 不要勾选"使用Readme初始化"、不要加.gitignore(避免冲突)
6. 点"创建"

---

## 三、本地首次配置(约3分钟)

在你电脑上打开命令行,执行:

```bash
cd "D:\Desktop\claude code\校招信息站"

# 1. 配置 git 用户名(改成你的)
git config user.name "你的名字"
git config user.email "你的邮箱"

# 2. 关联远程仓库(改成你的仓库地址)
git remote add origin https://gitee.com/你的用户名/campus-recruit.git

# 3. 提交并推送
git add -A
git commit -m "首次部署校招信息站"
git push -u origin main
```

> 首次推送会提示输入 Gitee 账号密码,或弹浏览器授权。

---

## 四、开启 Gitee Pages(约1分钟)

1. 进入 Gitee 仓库页面(`https://gitee.com/你的用户名/campus-recruit`)
2. 点顶部"**服务**"→"**Gitee Pages**"
3. 点"**启动服务**"
   - 部署分支选 `main`
   - 部署目录留空(网站文件在根目录)
4. 等待部署完成,会生成访问地址:
   **`https://你的用户名.gitee.io/campus-recruit/`**

> Gitee Pages 免费版需要实名认证后才能开启(提交一次身份证信息即可)。
> 个人免费版 Pages 有**访问量限制**,对校招站够用。

---

## 五、每天自动更新数据(Windows 任务计划)

1. 双击运行 `deploy.bat` **手动测试一次**,确认能正常更新+推送
2. 配置每日自动:
   - 按 `Win + R` 输入 `taskschd.msc` 回车
   - 点"创建基本任务"→ 名称"校招站每日更新"
   - 触发器"每天"→ 设定时间(建议 8:00)
   - 操作"启动程序"→ 程序:`C:\Windows\System32\cmd.exe`,参数:
     `/c "D:\Desktop\claude code\校招信息站\auto_deploy.bat"`
   - 完成

> 注意:每天到点需要**电脑开机**。auto_deploy.bat 会静默更新并推送,日志写入 deploy.log。

---

## 六、日常操作

| 操作 | 方法 |
|------|------|
| 手动更新数据 | 双击 `deploy.bat` |
| 只更新不推送 | 双击 `update.bat` |
| 查看是否更新成功 | 打开网站看"数据更新于"日期 |
| 修改数据源 | 编辑 `crawler/sources.json`,重跑 |

---

## 常见问题

**Q: Gitee Pages 启动按钮是灰的?**
A: 需要先完成 Gitee 实名认证(仓库页有提示),且仓库至少有1次推送。

**Q: 推送时提示权限错误?**
A: 检查 remote 地址是否正确,首次可改用 HTTPS 方式并输入账号密码。

**Q: 网站更新了但线上没变?**
A: Gitee Pages 需要手动点"**更新**"按钮(在 Gitee Pages 页面)。auto_deploy 只推送,Pages 刷新需手动或改用 Gitee 的自动化(见下)。

---

## 进阶:完全自动化(可选)

auto_deploy.bat 推送后,Gitee Pages 需要手动点"更新"。若想全自动,可用 **Gitee 的 Webhook** 或第三方服务(如阿里云函数/服务器)触发 Pages 更新,但这需要更多配置。**对校招站,建议每天早上花10秒点一下"更新"即可**。

# 🚀 校招信息站 GitHub Pages 部署指南

把网站部署到 **GitHub Pages**,实现外网访问 + **每天自动抓取更新**(无需电脑开机)。

> Gitee Pages 已下架,本方案改用 GitHub Pages(免费、稳定、可配 Actions 全自动)。
> 原理:GitHub Actions 每天在云端定时跑爬虫→更新数据→自动提交,GitHub Pages 自动发布。

---

## 一、注册/登录 GitHub(约2分钟)

1. 打开 **https://github.com/signup**
2. 填写邮箱、密码、用户名,完成注册
3. 到邮箱收验证邮件,点验证链接
4. 记住你的**用户名**(形如 `yourname`)

---

## 二、创建 GitHub 仓库(约1分钟)

1. 登录后点右上角"**+**"→"**New repository**"
2. Repository name 填:`campus-recruit`
3. 选 **Public**(公开)
4. 不要勾选 README/.gitignore(避免冲突)
5. 点"Create repository"

---

## 三、本地推送代码(约2分钟)

在你电脑上打开命令行:

```bash
cd "D:\Desktop\claude code\校招信息站"

# 关联 GitHub 远程(改成你的用户名)
git remote add github https://github.com/你的用户名/campus-recruit.git

# 推送到 GitHub
git push -u github main
```

> 首次推送会提示登录 GitHub(浏览器弹出授权或输账号密码)。

---

## 四、开启 GitHub Pages(约1分钟)

1. 打开仓库页 `https://github.com/你的用户名/campus-recruit`
2. 点顶部"**Settings**"→ 左侧"**Pages**"
3. 在"Build and deployment"处:
   - Source 选"**Deploy from a branch**"
   - Branch 选 `main` + 目录 `/ (root)`
4. 点"**Save**"
5. 等1-2分钟,访问:
   **`https://你的用户名.github.io/campus-recruit/`**

---

## 五、开启每日自动更新(约1分钟,推荐)

项目里已带 `auto-update.yml`(GitHub Actions 工作流),每天自动跑爬虫更新数据。只需在 GitHub 仓库里**启用 Actions**:

1. 打开仓库页 → 点顶部"**Actions**"
2. 如果提示启用,点"**I understand my workflows, go ahead and enable them**"
3. 左侧有"**每日自动更新校招数据**"工作流
4. 点该工作流 → 右上角"**Run workflow**"→ 选分支 main → 点按钮,**手动测试一次**
5. 等几分钟,看到绿色对勾 = 成功。之后**每天自动运行**(每天UTC 0点=北京时间早8点)

> 也可以不启用 Actions,用本机 `deploy.bat` 手动更新+推送,Pages 也会自动刷新。

---

## 六、日常操作

| 操作 | 方法 |
|------|------|
| 看是否更新成功 | 访问网站,看页脚"数据更新于"日期 |
| 手动触发云端爬虫 | 仓库 Actions → 工作流 → Run workflow |
| 本机手动更新 | 双击 `deploy.bat`(自动爬+push) |
| 只更新不推送 | 双击 `update.bat` |
| 修改数据源 | 编辑 `crawler/sources.json`,commit push |

---

## 常见问题

**Q: 访问地址打不开?**
A: 等1-2分钟部署完成;确认仓库是 Public;确认 Settings→Pages 分支选对了。

**Q: Actions 没自动跑?**
A: 确认仓库 Actions 已启用(仓库页 Actions 标签),且 `auto-update.yml` 在 main 分支上。

**Q: 爬虫在云端失败?**
A: GitHub Actions 的云服务器访问国内站点(如石油大学)偶尔会慢或超时。可在 Actions 运行日志里看;失败时保留上次数据不覆盖。若某源持续失败,可在 `sources.json` 里 `enabled:false` 临时停用。

**Q: 想用国内访问更快的方案?**
A: GitHub Pages 国内访问速度一般。可选 Cloudflare Pages(需绑定域名)或国内云托管(腾讯云/阿里云静态托管)。需要时可再配置。

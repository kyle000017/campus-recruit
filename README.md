# 🎓 校园招聘信息站

一个纯静态的校招信息聚合网站:每日更新的 **2027届校招** 企业信息 + **26届往届生** 求职专区 + 求职干货。

## 快速开始

1. **打开网站**:双击 `index.html` 即可在浏览器查看(无需任何服务器)
2. **数据来源**:`data/data.js`(由爬虫生成,网页直接加载)

## 更新数据

### 方式一:手动更新(推荐,最省心)
双击 `update.bat`,自动运行爬虫抓取最新校招信息并更新页面数据。完成后刷新浏览器即可。

### 方式二:每天自动更新(Windows 任务计划程序)
1. 按下 `Win + R`,输入 `taskschd.msc` 回车打开"任务计划程序"
2. 右侧点"**创建基本任务**"
3. 名称填"校招信息每日更新",点下一步
4. 触发器选"**每天**",设定时间(建议每天 8:00)
5. 操作选"**启动程序**",程序/脚本填:
   `C:\Windows\System32\cmd.exe`
   参数填:
   `/c "D:\Desktop\claude code\校招信息站\update.bat"`
6. 完成即可。之后每天到点自动抓取更新

> 注意:任务计划程序需保持电脑在设定时间处于开机状态。也可改用"空闲时运行"。

## 目录结构

```
校招信息站/
├── index.html          # 主页面
├── css/style.css       # 样式
├── js/app.js           # 前端逻辑(渲染/筛选/搜索)
├── data/
│   ├── data.js         # 页面实际加载的数据(爬虫生成)
│   ├── jobs2027.json   # 27届校招数据
│   ├── jobs2026.json   # 26届往届数据
│   └── tips.json       # 求职干货
├── crawler/
│   ├── crawler.py      # 爬虫脚本
│   ├── sources.json    # 数据源配置
│   └── requirements.txt
├── update.bat          # 一键更新脚本
└── README.md
```

## 数据源配置

编辑 `crawler/sources.json` 可增删数据源:

```json
{
  "sources": [
    {
      "name": "数据源名称",
      "type": "niuqizp 或 generic_list 或 wechat_recruit",
      "enabled": true,
      "..." : "其他参数"
    }
  ]
}
```

当前内置数据源:

| 数据源 | 类型 | 说明 |
|--------|------|------|
| 牛企直聘校招汇总 | `niuqizp` | 按行业/地区分类的27届校招页 |
| 中国石油大学2027届秋招汇总 | `wechat_recruit` | **含微信公众号推文链接**,质量高 |
| 中国农业大学就业网 | `generic_list` | 高校就业网 |
| 北理工就业信息网 | `generic_list` | 高校就业网 |
| 北师大就业资讯网 | `generic_list` | 高校就业网 |

- `niuqizp`:牛企直聘校招汇总页
- `wechat_recruit`:校招信息汇总页,标题+微信推文链接结构(如石油大学就业网)
- `generic_list`:通用列表页(高校就业网等),需配置 `list_url` 和 `item_selector`

爬虫内置容错:单源失败不影响其他源;数据缺失时保留上次成功数据。

### 添加新数据源步骤
1. 找到可访问的校招信息页(高校就业网/校招汇总页)
2. 在 `sources.json` 添加一条,`enabled` 设为 `true`
3. 运行 `python crawler.py`,观察解析数量;若为 0 需调整 `item_selector` 或改用其他 `type`

## 手动补充数据

如需手动添加某条校招信息,直接编辑 `data/jobs2027.json`(或 `jobs2026.json`),格式:

```json
{
  "id": "2027-011",
  "company": "企业名称",
  "title": "岗位/项目名",
  "industry": "行业",
  "city": "城市",
  "degree": "学历要求",
  "date": "2026-08-23",
  "link": "https://企业官网校招页",
  "is_new": false,
  "batch": "2027届"
}
```

保存后运行 `update.bat`(会重新生成 data.js),或手动更新 `data/data.js` 中对应字段。

## 部署到线上(Gitee)

见 **[Gitee部署指南.md](Gitee部署指南.md)**——完整步骤:注册 Gitee → 建仓库 → 开启 Pages → 配置每日自动更新,实现外网访问。

或部署到任意静态托管:
- **GitHub Pages**:仓库 Settings → Pages → 选择 main 分支
- **Vercel / Netlify**:拖拽文件夹即可部署

## 免责声明

所有校招信息来自公开渠道,以企业官方发布为准。本站仅做信息聚合,不保证信息完全及时准确。

# -*- coding: utf-8 -*-
"""
校招信息爬虫
- 多数据源抓取 2027 届校招信息
- 统一字段、去重、标记"今日新增"
- 单源失败自动降级,保留已有数据
- 输出 data/jobs2027.json 与 data/jobs2026.json

用法:
    python crawler.py            # 抓取并更新全部
    python crawler.py --source 牛企直聘-27届校招汇总   # 仅抓指定源
"""
import argparse
import json
import re
import sys
import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CRAWLER_DIR = Path(__file__).resolve().parent

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 15


# ---------------------------------------------------------------- 工具函数
def log(msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)


def safe_get(url, encoding=None):
    """带超时与编码处理的 GET,失败返回 None。"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        if encoding:
            r.encoding = encoding
        return r.text
    except Exception as e:
        log(f"  [抓取失败] {url} -> {e}")
        return None


def clean_text(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def guess_batch(company, title, text):
    """根据关键词判断数据属于 27届 还是 26届往届可投。
    27届校招但 26届往届生可投的岗位,归入 26届专区。
    """
    low = (company + " " + title + " " + text).lower()
    # 明确是 26届/往届/补录
    if any(k in low for k in ["2026届", "26届", "往届", "补招", "补录", "补录通道", "往届生可投", "应往届"]):
        return "2026届"
    # 27届校招但接受往届/毕业三年内/不限毕业年份的,归入26届(往届可投)
    if "2027届" in low or "2027" in low:
        if any(k in low for k in ["往届", "应往届", "毕业三年内", "毕业两年内", "不限毕业", "往届生", "可投", "含往届"]):
            return "2026届"
        return "2027届"
    return "2027届"


# ---------------------------------------------------------------- 数据源解析器
# 导航栏/框架链接黑名单(这些不是真实校招企业)
NAV_BLACKLIST = {
    "首页", "校招职位", "宣讲会", "社招职位", "更多", "院校库", "职场资讯",
    "招聘平台分享", "牛企直聘", "校招", "校招公告＆简章", "校园招聘",
    "校招公告＆简章网申秋招招聘最新信息", "半导体专场", "热门企业", "最新职位",
    "登录", "注册", "关于我们", "联系我们", "帮助中心",
    "招聘会", "招聘信息", "招聘场地简介", "医科招聘信息", "招聘简章",
    "招聘公告", "招聘职位", "公务员招录", "事业单位", "军队招聘", "基层就业",
    "校园大使", "生源信息", "毕业生生源信息",
}
# 黑名单关键词(标题含这些词大概率是导航/框架,不是企业招聘)
NAV_KEYWORDS = [
    "专场", "直聘", "招聘平台", "职位分类", "行业分类", "地区分类",
    "院校库", "职场资讯", "宣讲会预告", "全部", "更多>",
]


def is_navigation(title, link):
    """判断一条记录是否是导航/框架噪音。"""
    t = (title or "").strip()
    if not t or t in NAV_BLACKLIST:
        return True
    for kw in NAV_KEYWORDS:
        if kw in t:
            return True
    # 导航链接通常是站内频道页
    if link and "niuqizp.com" in link and "/offer/" not in link and "/schedulenew-" not in link:
        # 排除明显的企业招聘详情页;站内频道页算噪音
        if not ("/campus/" in link or "/schedulenew-" in link):
            pass
    return False


def _resolve_link(href, base_url):
    """把相对链接解析为绝对链接。"""
    if not href:
        return ""
    href = href.strip()
    if href.startswith("http"):
        return href
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return base_url + href
    return base_url + "/" + href.lstrip("/")


def parse_niuqizp(html, base_url):
    """
    牛企直聘 2027 校招汇总页解析。
    真实校招条目位于 h3/h4 标题内,多为"企业名 + 招聘标题"。
    做通用解析 + 招聘关键词过滤 + 导航过滤。
    """
    records = []
    soup = BeautifulSoup(html, "lxml")
    seen = set()
    candidates = []

    # 优先解析 h3/h4 标题(实测命中真实校招条目)
    for tag in soup.find_all(["h3", "h4"]):
        text = clean_text(tag.get_text())
        a = tag.find("a")
        link = _resolve_link(a.get("href") if a else "", base_url)
        if not text:
            continue
        candidates.append({"title": text, "link": link, "container": tag})

    # 兜底:列表容器
    for c in soup.select(
        "li, .item, .card, .job-item, .recruit-item, .list-item, [class*=schedulenew] li"
    ):
        text = clean_text(c.get_text())
        a = c.find("a")
        link = _resolve_link(a.get("href") if a else "", base_url)
        if text:
            candidates.append({"title": text, "link": link, "container": c})

    for cand in candidates:
        title = cand["title"]
        link = cand["link"]
        if not title or title in seen:
            continue
        # 过滤导航噪音
        if is_navigation(title, link):
            continue
        # 招聘标题一般含招聘关键词;不含的跳过(避免把页面标题/说明当企业)
        low = title.lower()
        if not any(k in low for k in ["招聘", "校招", "秋招", "春招", "届", "网申", "2026", "2027", "offer"]):
            continue
        seen.add(title)
        container_text = clean_text(cand["container"].get_text())
        # 从标题提取公司名(通常是第一个词,排除"招聘""公告"等词头)
        company = _extract_company(title)
        records.append({
            "title": title,
            "company": company,
            "link": link,
            "text": container_text,
        })
    return records


def parse_wechat_recruit(html):
    """
    高校就业网"校招信息汇总"页解析(如中国石油大学就业网)。
    结构: div.wp_articlecontent 内 <p><a>序号.企业2027届校招标题</a></p>,
    链接多为 mp.weixin.qq.com 公众号推文。
    """
    records = []
    soup = BeautifulSoup(html, "lxml")
    seen = set()
    container = soup.select_one(".wp_articlecontent")
    anchors = container.find_all("a") if container else soup.find_all("a")
    for a in anchors:
        title = clean_text(a.get_text())
        if not title or title in seen:
            continue
        # 去掉序号前缀 "1." / "2." 等
        clean_title = re.sub(r"^\s*\d+[\.、．]\s*", "", title)
        # 只要校招相关标题
        low = clean_title.lower()
        if not any(k in low for k in ["校招", "招聘", "秋招", "春招", "届", "网申", "2027", "2026", "offer"]):
            continue
        if is_navigation(clean_title, a.get("href") or ""):
            continue
        seen.add(title)
        link = _resolve_link(a.get("href") or "", "")
        company = _extract_company(clean_title)
        records.append({
            "title": clean_title,
            "company": company,
            "link": link,
            "text": clean_title,
        })
    return records


def _extract_company(title):
    """从招聘标题提取企业名:取第一个名词性片段。"""
    # 去掉常见前缀(含全角/半角括号包裹的"招聘")
    t = title
    t = re.sub(r"^[\s【\[]*(招聘|校招|秋招|春招|网申|2027届|2026届)[\s｜|】\]]*", "", t)
    t = t.lstrip("【[（(丨|：: ")
    # 去掉"招聘|"这类连写前缀
    t = re.sub(r"^(招聘|校招)[｜|]", "", t)
    # 去掉常见后缀
    t = re.split(r"(招聘|校招|秋招|春招|网申|公告|简章|2027|2026)", t)[0].strip()
    # 取第一个"单位/公司"形态:去空格、符号
    t = re.split(r"\s+|[|｜\-—_/]", t)[0]
    if len(t) > 12:
        t = t[:12]
    return t or title[:8]


def parse_generic_list(html, list_url, item_selector):
    """高校就业网等通用列表解析:抓取列表链接+标题,过滤导航噪音与无关条目。"""
    records = []
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(item_selector) if item_selector else soup.find_all("a")
    seen = set()
    for a in items:
        href = a.get("href") or ""
        if not href or href.startswith("#") or href.startswith("javascript"):
            continue
        if href.startswith("/"):
            from urllib.parse import urljoin
            href = urljoin(list_url, href)
        elif not href.startswith("http"):
            from urllib.parse import urljoin
            href = urljoin(list_url, href)
        title = clean_text(a.get_text())
        if not title or title in seen:
            continue
        # 过滤导航/框架噪音
        if is_navigation(title, href):
            continue
        # 只要招聘相关标题
        low = title.lower()
        if not any(k in low for k in ["校招", "招聘", "秋招", "春招", "届", "网申", "2027", "2026", "offer", "简章"]):
            continue
        seen.add(title)
        company = title.split(" ")[0].split("|")[0].split("-")[0] if title else ""
        records.append({
            "title": title,
            "company": company,
            "link": href,
            "text": title,
        })
    return records


# ---------------------------------------------------------------- 抓取主流程
def load_existing(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def normalize_and_merge(raw_records, existing, batch_tag, today):
    """合并新抓取与已有数据,去重,标注新增。"""
    merged = []
    known = set()
    for r in existing:
        if isinstance(r, dict) and r.get("company"):
            known.add((r.get("company", ""), r.get("title", "")))
            merged.append(r)

    added = 0
    for r in raw_records:
        key = (r.get("company", ""), r.get("title", ""))
        if not r.get("company") or not r.get("title") or key in known:
            continue
        known.add(key)
        merged.append({
            "id": "",
            "company": r["company"],
            "title": r["title"],
            "industry": r.get("industry", ""),
            "city": r.get("city", ""),
            "degree": r.get("degree", ""),
            "date": today,
            "link": r.get("link", ""),
            "is_new": True,
            "batch": batch_tag,
        })
        added += 1
    log(f"  新增 {added} 条")
    return merged


def finalize(records, batch_tag):
    """去重、排序、打 id。"""
    seen = set()
    out = []
    for r in records:
        key = (r.get("company", ""), r.get("title", ""))
        if not key[0] or not key[1] or key in seen:
            continue
        seen.add(key)
        # 过了一天,历史新增标记复位(保留当天新增)
        r["batch"] = batch_tag
        out.append(r)
    # 今日新增置顶,组内按日期降序(最新在前)
    out.sort(key=lambda x: (x.get("is_new"), x.get("date", "")), reverse=True)
    for i, r in enumerate(out, 1):
        r["id"] = f"{batch_tag[:4]}-{i:03d}"
    return out


# ---------------------------------------------------------------- 主入口
def main():
    parser = argparse.ArgumentParser(description="校招信息爬虫")
    parser.add_argument("--source", help="仅抓取指定源(名称)", default=None)
    parser.add_argument("--config", default=str(CRAWLER_DIR / "sources.json"))
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()

    # 读取配置
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    except Exception as e:
        log(f"读取配置失败: {e}")
        sys.exit(1)

    jobs2027_path = DATA_DIR / "jobs2027.json"
    jobs2026_path = DATA_DIR / "jobs2026.json"
    existing_27 = load_existing(jobs2027_path)
    existing_26 = load_existing(jobs2026_path)

    # 用于累积每次运行的新记录,供 is_new 标记得以保留
    all_new = [r for r in existing_27 + existing_26 if r.get("is_new")]

    fetched_27 = []
    fetched_26 = []

    for src in config.get("sources", []):
        if not src.get("enabled"):
            continue
        if args.source and src.get("name") != args.source:
            continue
        name = src.get("name", "未知源")
        log(f"抓取源: {name}")
        try:
            if src.get("type") == "niuqizp":
                # 牛企直聘 2027 汇总入口(行业/地区分类页)
                base = src.get("base_url")
                # 分类页的行业映射(从 URL 特征识别)
                url_industry_map = {
                    "computersoftwarehardwareservices": "互联网/科技",
                    "ConstructionMaterialsEngineering": "建筑/工程",
                }
                urls = [
                    f"{base}/schedulenew-computersoftwarehardwareservices-1/",
                    f"{base}/schedulenew-ConstructionMaterialsEngineering-jiangsuhuaian-1/",
                ]
                for u in urls:
                    html = safe_get(u)
                    if not html:
                        continue
                    # 从 URL 推断行业
                    inferred = "未分类"
                    for key, ind in url_industry_map.items():
                        if key in u:
                            inferred = ind
                            break
                    raw = parse_niuqizp(html, base)
                    for r in raw:
                        if not r.get("industry"):
                            r["industry"] = inferred
                        batch = guess_batch(r["company"], r["title"], r.get("text", ""))
                        if batch == "2026届":
                            fetched_26.append(r)
                        else:
                            fetched_27.append(r)
                    log(f"  解析到 {len(raw)} 条 (行业: {inferred})")
            elif src.get("type") == "generic_list":
                html = safe_get(src.get("list_url"))
                if html:
                    raw = parse_generic_list(html, src.get("list_url"), src.get("item_selector"))
                    for r in raw:
                        batch = guess_batch(r["company"], r["title"], r.get("text", ""))
                        if batch == "2026届":
                            fetched_26.append(r)
                        else:
                            fetched_27.append(r)
                    log(f"  解析到 {len(raw)} 条")
            elif src.get("type") == "wechat_recruit":
                html = safe_get(src.get("list_url"), encoding="utf-8")
                if html:
                    raw = parse_wechat_recruit(html)
                    for r in raw:
                        batch = guess_batch(r["company"], r["title"], r.get("text", ""))
                        if batch == "2026届":
                            fetched_26.append(r)
                        else:
                            fetched_27.append(r)
                    log(f"  解析到 {len(raw)} 条")
        except Exception as e:
            log(f"  [源异常] {name}: {e}")
            continue

    # 合并并写出(即使本次抓取为空,也保留已有数据,不覆盖丢失)
    merged_27 = normalize_and_merge(fetched_27, existing_27, "2027届", today)
    merged_26 = normalize_and_merge(fetched_26, existing_26, "2026届", today)

    # 将今日新增累积标记保留,然后复位过期的
    new_keys = set((r["company"], r["title"]) for r in all_new)
    for r in merged_27 + merged_26:
        if (r.get("company"), r.get("title")) in new_keys:
            r["is_new"] = True

    merged_27 = finalize(merged_27, "2027届")
    merged_26 = finalize(merged_26, "2026届")

    jobs2027_path.write_text(
        json.dumps(merged_27, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    jobs2026_path.write_text(
        json.dumps(merged_26, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 生成供前端 script 直接加载的 data.js(避免 file:// 下 fetch 被同源策略拦截)
    tips_path = DATA_DIR / "tips.json"
    tips = []
    if tips_path.exists():
        try:
            tips = json.loads(tips_path.read_text(encoding="utf-8"))
        except Exception:
            tips = []
    js_payload = {
        "updated_at": today,
        "jobs2027": merged_27,
        "jobs2026": merged_26,
        "tips": tips,
    }
    js_content = "window.SCHOOL_RECRUIT = " + json.dumps(js_payload, ensure_ascii=False, indent=2) + ";"
    (DATA_DIR / "data.js").write_text(js_content, encoding="utf-8")

    log(f"完成: 2027届 {len(merged_27)} 条, 2026届往届 {len(merged_26)} 条")
    log(f"输出: {jobs2027_path} / {jobs2026_path} / data/data.js")


if __name__ == "__main__":
    main()

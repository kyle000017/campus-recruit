/* 校招信息站前端逻辑 */
(function () {
  "use strict";

  // 数据来源: data/data.js 注入 window.SCHOOL_RECRUIT
  var DATA = window.SCHOOL_RECRUIT || { jobs2027: [], jobs2026: [], tips: [], updated_at: "" };

  var state = {
    activeTab: "campus2027",
    search: "",
    industry: "",
    city: "",
    degree: ""
  };

  // ---------- 工具 ----------
  function escapeHtml(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function unique(values) {
    return Array.from(new Set(values.filter(Boolean)));
  }

  // ---------- Tab 切换 ----------
  function initTabs() {
    var btns = document.querySelectorAll(".tab-btn");
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var tab = btn.getAttribute("data-tab");
        state.activeTab = tab;
        btns.forEach(function (b) { b.classList.toggle("active", b === btn); });
        document.querySelectorAll(".tab-panel").forEach(function (p) {
          p.classList.toggle("active", p.id === "tab-" + tab);
        });
        if (tab === "campus2027") render2027();
        if (tab === "alumni2026") render2026();
        if (tab === "tips") renderTips();
      });
    });
  }

  // ---------- 筛选控件 ----------
  function fillFilters() {
    var jobs = DATA.jobs2027 || [];
    var industrySel = document.getElementById("industryFilter");
    var citySel = document.getElementById("cityFilter");
    var degreeSel = document.getElementById("degreeFilter");
    if (!industrySel || !citySel || !degreeSel) return;

    var industries = unique(jobs.map(function (j) { return j.industry; }));
    var cities = unique(jobs.map(function (j) { return j.city; }));
    var degrees = unique(jobs.map(function (j) { return j.degree; }));

    fillSelect(industrySel, industries, "全部行业");
    fillSelect(citySel, cities, "全部城市");
    fillSelect(degreeSel, degrees, "全部学历");

    industrySel.addEventListener("change", function () { state.industry = this.value; render2027(); });
    citySel.addEventListener("change", function () { state.city = this.value; render2027(); });
    degreeSel.addEventListener("change", function () { state.degree = this.value; render2027(); });
    document.getElementById("searchInput").addEventListener("input", function () {
      state.search = this.value.trim().toLowerCase();
      render2027();
    });
    document.getElementById("resetFilter").addEventListener("click", function () {
      state.search = ""; state.industry = ""; state.city = ""; state.degree = "";
      document.getElementById("searchInput").value = "";
      industrySel.value = ""; citySel.value = ""; degreeSel.value = "";
      render2027();
    });
  }

  function fillSelect(sel, values, placeholder) {
    sel.innerHTML = '<option value="">' + placeholder + "</option>" +
      values.map(function (v) { return '<option value="' + escapeHtml(v) + '">' + escapeHtml(v) + "</option>"; }).join("");
  }

  // ---------- 渲染 ----------
  function render2027() {
    var jobs = (DATA.jobs2027 || []).filter(function (j) {
      var kw = state.search;
      if (kw) {
        var hay = (j.company + " " + j.title + " " + j.industry + " " + j.city).toLowerCase();
        if (hay.indexOf(kw) === -1) return false;
      }
      if (state.industry && j.industry !== state.industry) return false;
      if (state.city && j.city !== state.city) return false;
      if (state.degree && j.degree !== state.degree) return false;
      return true;
    });
    document.getElementById("resultInfo").textContent =
      "共 " + jobs.length + " 条校招信息" + (jobs.length ? " · " + (DATA.updated_at || "") + " 更新" : "");
    document.getElementById("jobList27").innerHTML = renderCards(jobs, "2027届");
  }

  function render2026() {
    var jobs = DATA.jobs2026 || [];
    document.getElementById("jobList26").innerHTML = renderCards(jobs, "2026届");
  }

  function renderCards(jobs, batch) {
    if (!jobs.length) {
      return '<div class="empty">暂无数据。运行爬虫或等待每日更新。</div>';
    }
    return jobs.map(function (j) {
      var tags = "";
      if (j.is_new) tags += '<span class="tag tag-new">今日新增</span>';
      tags += '<span class="tag tag-batch">' + escapeHtml(batch) + "</span>";
      if (batch === "2026届") tags += '<span class="tag tag-alumni">26届可投</span>';

      var linkBtn = "";
      if (j.link) {
        var isWechat = j.link.indexOf("mp.weixin.qq.com") > -1;
        var label = isWechat ? "查看校招推文 ↗" : "官网投递 ↗";
        linkBtn = '<a class="btn btn-primary" href="' + escapeHtml(j.link) + '" target="_blank" rel="noopener">' + label + "</a>";
      } else {
        linkBtn = '<span class="btn btn-outline disabled">链接待补充</span>';
      }

      return (
        '<div class="job-card">' +
          '<div class="company">' + escapeHtml(j.company) + "</div>" +
          '<div class="title">' + escapeHtml(j.title) + "</div>" +
          '<div class="meta">' +
            (j.industry ? '<span>🏷️ ' + escapeHtml(j.industry) + "</span>" : "") +
            (j.city ? '<span>📍 ' + escapeHtml(j.city) + "</span>" : "") +
            (j.degree ? '<span>🎓 ' + escapeHtml(j.degree) + "</span>" : "") +
            (j.date ? '<span>📅 ' + escapeHtml(j.date) + "</span>" : "") +
          "</div>" +
          '<div class="meta">' + tags + "</div>" +
          '<div class="actions">' + linkBtn + "</div>" +
        "</div>"
      );
    }).join("");
  }

  function renderTips() {
    var tips = DATA.tips || [];
    var el = document.getElementById("tipsContainer");
    if (!tips.length) {
      el.innerHTML = '<div class="empty">求职干货内容整理中...</div>';
      return;
    }
    el.innerHTML = tips.map(function (tip) {
      var lis = (tip.items || []).map(function (item) {
        return "<li>" + (item.strong ? "<strong>" + escapeHtml(item.strong) + "</strong>：" : "") + escapeHtml(item.text) + "</li>";
      }).join("");
      return (
        '<div class="tip-card">' +
          "<h3>" + escapeHtml(tip.title) + "</h3>" +
          (tip.sub ? '<p class="tip-sub">' + escapeHtml(tip.sub) + "</p>" : "") +
          "<ul>" + lis + "</ul>" +
        "</div>"
      );
    }).join("");
  }

  // ---------- 更新提示 ----------
  function initUpdatedAt() {
    var el = document.getElementById("updatedAt");
    if (el && DATA.updated_at) {
      el.textContent = "数据更新于 " + DATA.updated_at;
    }
  }

  // ---------- 启动 ----------
  document.addEventListener("DOMContentLoaded", function () {
    initTabs();
    fillFilters();
    render2027();
    render2026();
    renderTips();
    initUpdatedAt();
  });
})();

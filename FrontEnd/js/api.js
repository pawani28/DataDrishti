/* ==========================================================
   DataDrishti – shared client for the Flask API (Backend/app.py)
   Endpoints used:
     POST /api/upload                    (multipart, field "file")
     GET  /api/datasets/<id>             -> summary, insights
     GET  /api/datasets/<id>/dashboard   -> dashboard, insights
     GET  /api/datasets/latest           -> dataset, dashboard, summary, insights
     POST /api/datasets/<id>/chat        {question} -> answer
   ========================================================== */
(function (global) {
  "use strict";

  // Same-origin when served by Flask; fall back to localhost if a page is opened straight from disk.
  var API_BASE = global.DD_API_BASE !== undefined
    ? global.DD_API_BASE
    : (location.protocol === "file:" ? "http://127.0.0.1:5000" : "");

  var KEY_ID = "dd_dataset_id";
  var KEY_NAME = "dd_filename";

  function apiError(message, status) {
    var e = new Error(message);
    e.status = status || 0;
    return e;
  }

  async function request(path, options) {
    var res;
    try {
      res = await fetch(API_BASE + path, options);
    } catch (e) {
      throw apiError("Cannot reach the DataDrishti server. Please make sure the backend is running (python -m Backend.app).", 0);
    }
    var data = null;
    try { data = await res.json(); } catch (e) { /* non-JSON response */ }
    if (!res.ok || !data || data.success === false) {
      throw apiError((data && data.error) || ("Request failed (" + res.status + ")"), res.status);
    }
    return data;
  }

  /* ---------------- dataset calls ---------------- */

  async function uploadDataset(file) {
    var form = new FormData();
    form.append("file", file);
    var data = await request("/api/upload", { method: "POST", body: form });
    sessionStorage.setItem(KEY_ID, String(data.dataset_id));
    sessionStorage.setItem(KEY_NAME, data.filename || file.name);
    return data;
  }

  async function loadDataset() {
    var id = sessionStorage.getItem(KEY_ID);
    if (id) {
      try {
        var both = await Promise.all([
          request("/api/datasets/" + id),
          request("/api/datasets/" + id + "/dashboard")
        ]);
        return {
          id: Number(id),
          filename: sessionStorage.getItem(KEY_NAME) || ("Dataset #" + id),
          summary: both[0].summary,
          dashboard: both[1].dashboard,
          insights: both[1].insights
        };
      } catch (e) {
        if (e.status !== 404) throw e;      // stale id -> fall through to "latest"
        sessionStorage.removeItem(KEY_ID);
        sessionStorage.removeItem(KEY_NAME);
      }
    }
    var latest = await request("/api/datasets/latest");   // throws status 404 when nothing was uploaded yet
    sessionStorage.setItem(KEY_ID, String(latest.dataset.id));
    sessionStorage.setItem(KEY_NAME, latest.dataset.filename);
    return {
      id: latest.dataset.id,
      filename: latest.dataset.filename,
      summary: latest.summary,
      dashboard: latest.dashboard,
      insights: latest.insights
    };
  }

  async function askQuestion(question) {
    var id = sessionStorage.getItem(KEY_ID);
    if (!id) throw apiError("Upload a dataset first.", 404);
    var data = await request("/api/datasets/" + id + "/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
    });
    return data.answer;
  }

  /* ---------------- formatting helpers ---------------- */

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function inr(n) {
    if (n === null || n === undefined || isNaN(n)) return "—";
    var a = Math.abs(n), s = n < 0 ? "-" : "";
    if (a >= 1e7) return s + "₹" + (a / 1e7).toFixed(2) + " Cr";
    if (a >= 1e5) return s + "₹" + (a / 1e5).toFixed(2) + " L";
    return s + "₹" + a.toLocaleString("en-IN", { maximumFractionDigits: 0 });
  }

  function num(n) {
    if (n === null || n === undefined || isNaN(n)) return "—";
    return Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
  }

  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function prettyMonth(label) {                 // "2025-03" -> "Mar 2025"
    var m = /^(\d{4})-(\d{2})$/.exec(label);
    return m ? MONTHS[Number(m[2]) - 1] + " " + m[1] : String(label);
  }
  function nextMonths(lastLabel, count) {       // "2025-11", 3 -> ["2025-12","2026-01","2026-02"]
    var m = /^(\d{4})-(\d{2})$/.exec(lastLabel);
    if (!m) return [];
    var y = Number(m[1]), mo = Number(m[2]), out = [];
    for (var i = 0; i < count; i++) {
      mo++; if (mo > 12) { mo = 1; y++; }
      out.push(y + "-" + String(mo).padStart(2, "0"));
    }
    return out;
  }

  // % change between the last two points of a series (null if impossible)
  function lastChange(values) {
    if (!values || values.length < 2) return null;
    var prev = values[values.length - 2], cur = values[values.length - 1];
    if (!prev) return null;
    return ((cur - prev) / Math.abs(prev)) * 100;
  }

  // Ordinary least squares line through the series; returns next `count` points + slope
  function linearProjection(values, count) {
    var n = values.length;
    if (n < 4) return null;
    var sx = 0, sy = 0, sxy = 0, sxx = 0;
    for (var i = 0; i < n; i++) { sx += i; sy += values[i]; sxy += i * values[i]; sxx += i * i; }
    var den = n * sxx - sx * sx;
    if (!den) return null;
    var slope = (n * sxy - sx * sy) / den;
    var intercept = (sy - slope * sx) / n;
    var pts = [];
    for (var k = 0; k < count; k++) pts.push(Math.max(0, intercept + slope * (n + k)));
    return { points: pts, slope: slope, mean: sy / n };
  }

  // share of non-empty cells, 0..100
  function completeness(summary) {
    var total = (summary.rows || 0) * (summary.columns || 0);
    if (!total) return 100;
    var missing = 0;
    Object.keys(summary.missing_values || {}).forEach(function (k) { missing += summary.missing_values[k]; });
    return Math.max(0, 100 - (missing / total) * 100);
  }
  function missingCells(summary) {
    var missing = 0;
    Object.keys(summary.missing_values || {}).forEach(function (k) { missing += summary.missing_values[k]; });
    return missing;
  }

  function hasColumn(summary, needles) {
    return (summary.column_names || []).some(function (c) {
      return needles.some(function (n) { return c.toLowerCase().indexOf(n) !== -1; });
    });
  }

  /* ---------------- chart helper ---------------- */
  function themeChart() {
    if (!global.Chart) return;
    Chart.defaults.color = "#cbd5e1";
    Chart.defaults.font.family = "Poppins, sans-serif";
    Chart.defaults.borderColor = "rgba(255,255,255,0.08)";
  }

  /* ---------------- tiny user helpers (front-end only login) ---------------- */
  function currentUser() { return localStorage.getItem("userEmail") || ""; }
  function logout() { localStorage.removeItem("userEmail"); location.href = "login.html"; }

  global.DD = {
    uploadDataset: uploadDataset,
    loadDataset: loadDataset,
    askQuestion: askQuestion,
    getDatasetId: function () { return sessionStorage.getItem(KEY_ID); },
    esc: esc, inr: inr, num: num,
    prettyMonth: prettyMonth, nextMonths: nextMonths,
    lastChange: lastChange, linearProjection: linearProjection,
    completeness: completeness, missingCells: missingCells, hasColumn: hasColumn,
    themeChart: themeChart, currentUser: currentUser, logout: logout
  };
})(window);

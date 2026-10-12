/* DataDrishti – dashboard page. All numbers come from the Flask API via DD (api.js). */
(function () {
    "use strict";

    var $ = function (id) { return document.getElementById(id); };
    var esc = DD.esc;
    var chart = null;

    init();

    async function init() {
        var user = DD.currentUser();
        $("avatar").textContent = user ? user.charAt(0) : "U";
        $("logoutBtn").addEventListener("click", DD.logout);
        $("genReport").addEventListener("click", function () { location.href = "report.html"; });

        document.querySelectorAll("[data-go]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var go = btn.getAttribute("data-go");
                if (go.charAt(0) === "#") {
                    var el = document.querySelector(go);
                    if (el) el.scrollIntoView({ behavior: "smooth" });
                } else { location.href = go; }
            });
        });

        try {
            var data = await DD.loadDataset();
            $("content").style.display = "";
            render(data);
            $("content").classList.remove("is-loading");
            setupChat();
        } catch (err) {
            if (err.status === 404) {
                $("emptyState").classList.add("show");
            } else {
                var b = $("banner");
                b.textContent = err.message;
                b.classList.add("show");
            }
        }
    }

    /* ---------------- rendering ---------------- */

    function render(data) {
        var summary = data.summary, dash = data.dashboard, cards = dash.cards, ch = dash.chart;
        var hasRevenue = ch.label !== "Records";

        var badge = $("dsBadge");
        badge.style.display = "";
        badge.innerHTML = '<i class="fa-solid fa-database"></i> ' + esc(data.filename);

        $("welcomeText").innerHTML = "Showing results for <b>" + esc(data.filename) + "</b> — " +
            DD.num(summary.rows) + " rows × " + summary.columns + " columns.";

        // KPI cards
        var change = DD.lastChange(ch.values);
        $("cardRevenue").textContent = hasRevenue ? DD.inr(cards.total_revenue) : "—";
        var sub = $("cardRevenueSub");
        if (!hasRevenue) {
            sub.textContent = "No revenue / sales column detected";
        } else if (change !== null) {
            sub.className = change < 0 ? "down" : "";
            sub.textContent = (change >= 0 ? "▲ " : "▼ ") + Math.abs(change).toFixed(1) + "% vs previous month";
        } else {
            sub.textContent = "Sum of “" + ch.label.replace(/_/g, " ") + "”";
        }

        $("cardCustomers").textContent = cards.customers > 0 ? DD.num(cards.customers) : "—";
        $("cardCustomersSub").textContent = cards.customers > 0 ? "Unique customers" : "No customer column detected";

        $("cardOrders").textContent = DD.num(cards.orders);
        $("cardOrdersSub").textContent = DD.hasColumn(summary, ["order", "transaction", "invoice"]) ? "Unique orders" : "Total records";

        var hasProfit = cards.profit !== 0;
        $("cardProfit").textContent = hasProfit ? DD.inr(cards.profit) : "—";
        $("cardProfitSub").textContent = hasProfit
            ? (hasRevenue && cards.total_revenue ? ((cards.profit / cards.total_revenue) * 100).toFixed(1) + "% margin" : "Total profit")
            : "Add a “profit” column to see this";

        renderChart(ch);
        renderInsights(data.insights);
        renderOverview(summary.numeric_summary);
        renderTop(dash.top_products, ch.label, hasRevenue);
        renderQuality(summary);
    }

    function renderChart(ch) {
        var canvas = $("trendChart"), empty = $("trendEmpty");
        $("chartTitle").textContent = ch.values.length
            ? "Monthly " + ch.label.replace(/_/g, " ") + " (last " + ch.values.length + " months)"
            : "Sales Overview";

        if (!ch.values.length) {
            canvas.style.display = "none";
            empty.classList.add("show");
            empty.innerHTML = '<i class="fa-solid fa-chart-line"></i>Monthly trend needs a <b>date</b> column and a numeric ' +
                '<b>revenue / sales / amount / price / total</b> column.<br>Add them to your file and upload again.';
            return;
        }
        DD.themeChart();
        var ctx = canvas.getContext("2d");
        var grad = ctx.createLinearGradient(0, 0, 0, 300);
        grad.addColorStop(0, "rgba(110,231,255,.45)");
        grad.addColorStop(1, "rgba(110,231,255,0)");
        if (chart) chart.destroy();
        chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: ch.labels.map(DD.prettyMonth),
                datasets: [{
                    label: ch.label.replace(/_/g, " "),
                    data: ch.values,
                    borderColor: "#6ee7ff", backgroundColor: grad, fill: true,
                    tension: 0.35, pointRadius: 4, pointBackgroundColor: "#2563eb"
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: function (c) { return " " + DD.inr(c.parsed.y); } } }
                },
                scales: { y: { ticks: { callback: function (v) { return DD.inr(v); } } } }
            }
        });
    }

    function renderInsights(list) {
        var ul = $("insightsList");
        ul.innerHTML = "";
        (list || []).forEach(function (t) {
            var li = document.createElement("li");
            li.textContent = "✔ " + t;
            ul.appendChild(li);
        });
    }

    function renderOverview(ns) {
        var body = $("overviewBody"), keys = Object.keys(ns || {});
        if (!keys.length) {
            body.innerHTML = '<tr><td colspan="5" class="muted">No numeric columns found in this dataset.</td></tr>';
            return;
        }
        body.innerHTML = keys.map(function (k) {
            var s = ns[k];
            return "<tr><td>" + esc(k.replace(/_/g, " ")) + '</td><td class="num">' + DD.num(s.sum) +
                '</td><td class="num">' + DD.num(s.mean) + '</td><td class="num">' + DD.num(s.min) +
                '</td><td class="num">' + DD.num(s.max) + "</td></tr>";
        }).join("");
    }

    function renderTop(list, label, hasRevenue) {
        var box = $("topProducts");
        if (!list || !list.length) {
            box.innerHTML = '<p class="empty-line">' + (hasRevenue
                ? "No product / item / category column found, so products can’t be ranked."
                : "Needs a product column and a revenue / sales column.") + "</p>";
            return;
        }
        var max = Math.max.apply(null, list.map(function (p) { return p.value; })) || 1;
        box.innerHTML = list.map(function (p) {
            var w = Math.max(3, Math.round((p.value / max) * 100));
            return '<div class="product"><span title="' + esc(p.name) + '">' + esc(p.name) + "</span><span>" +
                DD.inr(p.value) + '</span></div><div class="progress"><div class="fill" style="width:' + w + '%"></div></div>';
        }).join("");
    }

    function renderQuality(summary) {
        var pct = DD.completeness(summary), missing = DD.missingCells(summary);
        $("qualityPct").textContent = pct.toFixed(1) + "%";
        $("qualityBar").style.width = pct.toFixed(1) + "%";

        var rows = [];
        rows.push(['Missing cells', missing ? '<span class="bad">' + DD.num(missing) + "</span>" : '<span class="ok">None ✔</span>']);
        Object.keys(summary.missing_values || {}).slice(0, 4).forEach(function (k) {
            rows.push(["&nbsp;&nbsp;" + esc(k.replace(/_/g, " ")), '<span class="bad">' + DD.num(summary.missing_values[k]) + "</span>"]);
        });
        rows.push(["Date column", summary.date_columns.length ? '<span class="ok">Found ✔</span>' : '<span class="bad">Not found</span>']);
        rows.push(["Numeric columns", DD.num(summary.numeric_columns.length)]);
        $("qualityList").innerHTML = rows.map(function (r) { return "<li><span>" + r[0] + "</span><span>" + r[1] + "</span></li>"; }).join("");
    }

    /* ---------------- AI chat ---------------- */

    function setupChat() {
        var form = $("chatForm"), input = $("chatInput"), box = $("chatMessages");

        function add(cls, text) {
            var d = document.createElement("div");
            d.className = cls;
            d.textContent = text;
            box.appendChild(d);
            box.scrollTop = box.scrollHeight;
            return d;
        }

        async function send(q) {
            q = q.trim();
            if (!q) return;
            add("user-msg", q);
            input.value = "";
            input.disabled = true;
            var pending = add("bot-msg pending", "Thinking…");
            try {
                var answer = await DD.askQuestion(q);
                pending.className = "bot-msg";
                pending.textContent = "📊 " + answer;
            } catch (err) {
                pending.className = "bot-msg";
                pending.textContent = "⚠️ " + err.message;
            }
            input.disabled = false;
            input.focus();
            box.scrollTop = box.scrollHeight;
        }

        form.addEventListener("submit", function (e) { e.preventDefault(); send(input.value); });
        document.querySelectorAll("#chatChips button").forEach(function (b) {
            b.addEventListener("click", function () { send(b.textContent); });
        });
    }
})();

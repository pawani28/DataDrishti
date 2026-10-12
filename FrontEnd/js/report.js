/* DataDrishti – report page. Built from the same API data as the dashboard. */
(function () {
    "use strict";

    var $ = function (id) { return document.getElementById(id); };
    var esc = DD.esc;
    var PALETTE = ["#38bdf8", "#2563eb", "#6ee7ff", "#818cf8", "#34d399"];

    $("downloadBtn").addEventListener("click", function () { window.print(); });
    init();

    async function init() {
        try {
            var data = await DD.loadDataset();
            $("content").style.display = "";
            render(data);
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

    function render(data) {
        var s = data.summary, d = data.dashboard, c = d.cards, ch = d.chart;
        var hasRevenue = ch.label !== "Records";
        var hasProfit = c.profit !== 0;
        var change = DD.lastChange(ch.values);

        /* ---- KPI cards ---- */
        $("kRevenue").textContent = hasRevenue ? DD.inr(c.total_revenue) : "—";
        $("kRevenueSub").textContent = hasRevenue ? "Sum of “" + ch.label.replace(/_/g, " ") + "”" : "No revenue column found";
        $("kProfit").textContent = hasProfit ? DD.inr(c.profit) : "—";
        $("kProfitSub").textContent = hasProfit && hasRevenue && c.total_revenue
            ? ((c.profit / c.total_revenue) * 100).toFixed(1) + "% margin" : "No profit column found";
        $("kCustomers").textContent = c.customers > 0 ? DD.num(c.customers) : "—";
        $("kCustomersSub").textContent = c.customers > 0 ? "Unique customers" : "No customer column found";
        $("kOrders").textContent = DD.num(c.orders);
        $("kOrdersSub").textContent = DD.hasColumn(s, ["order", "transaction", "invoice"]) ? "Unique orders" : "Total records";

        /* ---- Executive summary ---- */
        var parts = ["DataDrishti analysed <b>" + esc(data.filename) + "</b>, which contains <b>" + DD.num(s.rows) +
            "</b> records across <b>" + s.columns + "</b> columns."];
        if (hasRevenue) parts.push("Total " + esc(ch.label.replace(/_/g, " ")) + " is <b>" + DD.inr(c.total_revenue) + "</b>.");
        if (ch.values.length >= 2) {
            var best = ch.values.indexOf(Math.max.apply(null, ch.values));
            parts.push("The strongest month was <b>" + DD.prettyMonth(ch.labels[best]) + "</b> (" + DD.inr(ch.values[best]) + ")" +
                (change !== null ? ", and the latest month moved <b>" + (change >= 0 ? "up " : "down ") + Math.abs(change).toFixed(1) + "%</b> versus the one before." : "."));
        }
        if (d.top_products.length) parts.push("<b>" + esc(d.top_products[0].name) + "</b> is the top performer.");
        parts.push("Data completeness is <b>" + DD.completeness(s).toFixed(1) + "%</b>.");
        $("summaryText").innerHTML = parts.join(" ");

        renderTrend(ch);
        renderPie(d.top_products, hasRevenue);
        renderPerformance(ch);
        renderTop(d.top_products, hasRevenue);
        renderQuality(s, c, ch);
        renderFindings(data, hasRevenue, hasProfit, change);
        renderForecast(ch);
    }

    /* ---------------- charts ---------------- */

    var proj = null;   // cached projection so the table/cards and the chart agree

    function projection(ch) {
        if (proj === null) proj = DD.linearProjection(ch.values, 3) || false;
        return proj;
    }

    function renderTrend(ch) {
        var canvas = $("salesChart"), empty = $("salesEmpty");
        if (!ch.values.length) {
            canvas.style.display = "none";
            empty.classList.add("show");
            empty.innerHTML = '<i class="fa-solid fa-chart-line"></i>Needs a <b>date</b> column and a <b>revenue / sales</b> column to draw the monthly trend.';
            return;
        }
        DD.themeChart();
        var p = projection(ch);
        var labels = ch.labels.slice(), hist = ch.values.slice(), fore = null;
        if (p) {
            var extra = DD.nextMonths(ch.labels[ch.labels.length - 1], 3);
            labels = labels.concat(extra);
            hist = hist.concat([null, null, null]);
            fore = new Array(ch.values.length - 1).fill(null)
                .concat([ch.values[ch.values.length - 1]])
                .concat(p.points);
        }
        var datasets = [{
            label: ch.label.replace(/_/g, " "), data: hist,
            borderColor: "#38bdf8", backgroundColor: "rgba(56,189,248,.15)", fill: true, tension: .35, pointRadius: 4
        }];
        if (fore) datasets.push({
            label: "Trend projection", data: fore, borderColor: "#fbbf24", borderDash: [6, 6],
            tension: 0, pointRadius: 3, fill: false
        });
        new Chart(canvas.getContext("2d"), {
            type: "line",
            data: { labels: labels.map(DD.prettyMonth), datasets: datasets },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { tooltip: { callbacks: { label: function (c) { return " " + c.dataset.label + ": " + DD.inr(c.parsed.y); } } } },
                scales: { y: { ticks: { callback: function (v) { return DD.inr(v); } } } }
            }
        });
    }

    function renderPie(list, hasRevenue) {
        var canvas = $("pieChart"), empty = $("pieEmpty");
        if (!list.length) {
            canvas.style.display = "none";
            empty.classList.add("show");
            empty.innerHTML = '<i class="fa-solid fa-chart-pie"></i>' + (hasRevenue
                ? "No product / item / category column found." : "Needs a product column and a revenue column.");
            return;
        }
        DD.themeChart();
        new Chart(canvas.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: list.map(function (p) { return p.name; }),
                datasets: [{ data: list.map(function (p) { return p.value; }), backgroundColor: PALETTE, borderColor: "#0f172a", borderWidth: 2 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" },
                    tooltip: { callbacks: { label: function (c) { return " " + c.label + ": " + DD.inr(c.parsed); } } }
                }
            }
        });
    }

    /* ---------------- tables / lists ---------------- */

    function renderPerformance(ch) {
        var box = $("performanceBox");
        if (!ch.values.length) { box.style.display = "none"; return; }
        $("perfValueHead").textContent = ch.label.replace(/_/g, " ").replace(/^./, function (m) { return m.toUpperCase(); });
        $("perfBody").innerHTML = ch.labels.map(function (m, i) {
            var cell = "—", cls = "";
            if (i > 0 && ch.values[i - 1]) {
                var pct = ((ch.values[i] - ch.values[i - 1]) / Math.abs(ch.values[i - 1])) * 100;
                cell = (pct >= 0 ? "▲ " : "▼ ") + Math.abs(pct).toFixed(1) + "%";
                cls = pct >= 0 ? "up" : "dn";
            }
            return "<tr><td>" + esc(DD.prettyMonth(m)) + "</td><td>" + DD.inr(ch.values[i]) + '</td><td class="' + cls + '">' + cell + "</td></tr>";
        }).join("");
    }

    function renderTop(list, hasRevenue) {
        var box = $("topList");
        if (!list.length) {
            box.innerHTML = '<p class="empty-line">' + (hasRevenue ? "No product / item / category column found." : "Needs a product column and a revenue column.") + "</p>";
            return;
        }
        var max = Math.max.apply(null, list.map(function (p) { return p.value; })) || 1;
        box.innerHTML = list.map(function (p) {
            return '<div class="product-item"><span>' + esc(p.name) + "</span><span>" + DD.inr(p.value) +
                '</span></div><div class="progress"><div class="fill" style="width:' + Math.max(3, Math.round(p.value / max * 100)) + '%"></div></div>';
        }).join("");
    }

    function renderQuality(s, c, ch) {
        var pct = DD.completeness(s), missing = DD.missingCells(s);
        $("scoreValue").textContent = pct.toFixed(1) + "%";
        var status = pct >= 98 ? "Excellent" : pct >= 90 ? "Good" : pct >= 75 ? "Fair" : "Needs cleaning";
        function line(ok, text) { return '<p class="' + (ok ? "ok" : "bad") + '">' + (ok ? "✔ " : "✖ ") + text + "</p>"; }
        $("scoreDetails").innerHTML =
            "<p><strong>Overall Status:</strong> " + status + "</p>" +
            line(missing === 0, missing === 0 ? "No missing cells" : DD.num(missing) + " missing cells") +
            line(s.date_columns.length > 0, "Date column " + (s.date_columns.length ? "detected" : "not found")) +
            line(ch.label !== "Records", "Revenue / sales column " + (ch.label !== "Records" ? "detected" : "not found")) +
            line(c.customers > 0, "Customer column " + (c.customers > 0 ? "detected" : "not found")) +
            line(DD.hasColumn(s, ["profit"]), "Profit column " + (DD.hasColumn(s, ["profit"]) ? "detected" : "not found"));
    }

    function renderFindings(data, hasRevenue, hasProfit, change) {
        var s = data.summary, c = data.dashboard.cards, top = data.dashboard.top_products, out = [];
        if (top.length && hasRevenue && c.total_revenue > 0) {
            var share = top[0].value / c.total_revenue * 100;
            out.push("<b>" + esc(top[0].name) + "</b> brings in " + share.toFixed(1) + "% of total revenue" +
                (share >= 30 ? " — keep it well stocked and avoid depending on a single product." : " — a healthy spread across products."));
        }
        if (change !== null) {
            out.push(change >= 0
                ? "Revenue grew " + change.toFixed(1) + "% in the latest month — consider repeating whatever worked (offers, stock, timing)."
                : "Revenue fell " + Math.abs(change).toFixed(1) + "% in the latest month — review pricing, promotions and stock availability.");
        }
        if (hasProfit && hasRevenue && c.total_revenue) {
            var m = c.profit / c.total_revenue * 100;
            out.push("Overall profit margin is " + m.toFixed(1) + "%" + (m < 15 ? " — on the low side; check costs and discounts." : "."));
        }
        var miss = Object.keys(s.missing_values || {});
        if (miss.length) out.push("Clean missing values in: " + miss.slice(0, 4).map(function (k) { return "<b>" + esc(k.replace(/_/g, " ")) + "</b>"; }).join(", ") + ".");
        if (c.customers === 0) out.push("Add a customer ID column to unlock customer analysis.");
        if (!s.date_columns.length) out.push("Add a date column to unlock monthly trends and outlook.");
        if (!out.length) out.push("Your data looks complete. Upload more history to unlock richer trends.");
        $("findings").innerHTML = out.map(function (t) { return "<li>" + t + "</li>"; }).join("");
    }

    function renderForecast(ch) {
        var grid = $("forecastGrid"), note = $("forecastNote"), p = ch.values.length ? projection(ch) : false;
        if (!p) {
            grid.innerHTML = "";
            note.textContent = "An outlook needs at least 4 months of dated revenue data.";
            return;
        }
        var total3 = p.points.reduce(function (a, b) { return a + b; }, 0);
        var growth = p.mean ? (p.slope / p.mean) * 100 : 0;
        grid.innerHTML =
            card("fa-chart-line", "Next Month", DD.inr(p.points[0]), "Projected " + ch.label.replace(/_/g, " ")) +
            card("fa-arrow-trend-up", "Monthly Trend", (growth >= 0 ? "+" : "") + growth.toFixed(1) + "%", "Average change per month") +
            card("fa-calendar", "Next 3 Months", DD.inr(total3), "Projected total");
        note.textContent = "Simple straight-line trend fitted to your monthly figures (dashed line in the chart). It ignores seasonality, so treat it as a rough guide, not a guarantee.";
    }
    function card(icon, title, big, sub) {
        return '<div class="forecast-card"><i class="fa-solid ' + icon + '"></i><h3>' + title + "</h3><h1>" + big + "</h1><p>" + sub + "</p></div>";
    }
})();

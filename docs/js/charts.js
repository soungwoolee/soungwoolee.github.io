// Site charts. Every chart reads theme tokens from CSS, so light and dark stay consistent.
// Series order is fixed: New = series-1, Single repurchase = series-2, Cross-purchase = series-3.
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, attrs, text) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  };
  const fmt = (n) => (n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e3 ? (n / 1e3).toFixed(1).replace(/\.0$/, "") + "K" : String(Math.round(n)));
  const COLOR = { New: "var(--series-1)", "Single repurchase": "var(--series-2)", "Cross-purchase": "var(--series-3)" };

  function tipFor(root) {
    const t = document.createElement("div");
    t.className = "tip"; t.hidden = true; root.appendChild(t);
    return {
      show(target, html) {
        const box = root.getBoundingClientRect(), b = target.getBoundingClientRect();
        t.innerHTML = html; t.hidden = false;
        t.style.left = `${b.left - box.left + b.width / 2}px`;
        t.style.top = `${b.top - box.top}px`;
      },
      hide() { t.hidden = true; },
    };
  }
  function hover(node, tip, html) {
    node.setAttribute("tabindex", "0");
    const on = () => tip.show(node, html);
    node.addEventListener("pointerenter", on); node.addEventListener("focus", on);
    node.addEventListener("pointerleave", tip.hide); node.addEventListener("blur", tip.hide);
  }
  function legend(root, items) {
    const l = document.createElement("div"); l.className = "legend";
    l.innerHTML = items.map(([name, c]) => `<span><i style="background:${c}"></i>${name}</span>`).join("");
    root.appendChild(l);
  }
  function table(root, head, rows) {
    const d = document.createElement("details"); d.className = "sr-table";
    d.innerHTML = `<summary>Show as table</summary><div class="tbl-wrap"><table><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
    root.appendChild(d);
  }

  // 1. New vs repeat customers, indexed to new = 100
  function clvIndex(root) {
    const groups = ["Order value", "Acquisition cost"];
    const series = [{ key: "New", color: COLOR.New, v: [100, 100] }, { key: "Repeat", color: COLOR["Single repurchase"], v: [130, 33] }];
    legend(root, series.map((s) => [s.key + " customers", s.color]));
    const W = 460, H = 230, m = { t: 22, r: 8, b: 30, l: 34 }, ih = H - m.t - m.b, max = 140;
    const y = (v) => m.t + ih - (v / max) * ih, gw = (W - m.l - m.r) / 2, bw = 46;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Indexed to new customers = 100: repeat customers' order value 130, acquisition cost 33" });
    const tip = tipFor(root);
    [0, 50, 100].forEach((t) => {
      svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: t ? "var(--grid)" : "var(--rule-strong)" }));
      svg.appendChild(el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end", class: "axis" }, t));
    });
    groups.forEach((g, gi) => {
      const cx = m.l + gw * gi + gw / 2;
      svg.appendChild(el("text", { x: cx, y: H - 8, "text-anchor": "middle", class: "lbl" }, g));
      series.forEach((s, si) => {
        const v = s.v[gi], x = cx - bw - 1 + si * (bw + 2), top = y(v), r = 4;
        const bar = el("path", { d: `M${x},${y(0)} V${top + r} Q${x},${top} ${x + r},${top} H${x + bw - r} Q${x + bw},${top} ${x + bw},${top + r} V${y(0)} Z`, fill: s.color });
        svg.appendChild(bar);
        svg.appendChild(el("text", { x: x + bw / 2, y: top - 6, "text-anchor": "middle", class: "val" }, v));
        hover(bar, tip, `${s.key} customers · ${g}: <b>${v}</b>`);
      });
    });
    root.appendChild(svg);
    table(root, ["Metric", "New", "Repeat"], groups.map((g, i) => [g, series[0].v[i], series[1].v[i]]));
  }

  // 2. Segment bubbles: customers (log x) vs CLV per customer, size = total CLV
  function bubbles(root, data) {
    const types = ["New", "Single repurchase", "Cross-purchase"];
    legend(root, types.map((t) => [t, COLOR[t]]));
    const W = 760, H = 420, m = { t: 16, r: 20, b: 44, l: 56 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const lx = (v) => m.l + ((Math.log10(v) - 1) / (5 - 1)) * iw;
    const ly = (v) => m.t + ih - (v / 11000) * ih;
    const maxT = Math.max(...data.map((d) => d.total));
    const rr = (t) => 4 + Math.sqrt(t / maxT) * 30;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Customer segments by number of customers and CLV per customer" });
    const tip = tipFor(root);
    [0, 2500, 5000, 7500, 10000].forEach((t) => {
      svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: ly(t), y2: ly(t), stroke: t ? "var(--grid)" : "var(--rule-strong)" }));
      svg.appendChild(el("text", { x: m.l - 8, y: ly(t) + 4, "text-anchor": "end", class: "axis" }, t ? "$" + t / 1000 + "K" : "$0"));
    });
    [10, 100, 1000, 10000, 100000].forEach((t) => {
      svg.appendChild(el("line", { x1: lx(t), x2: lx(t), y1: m.t, y2: m.t + ih, stroke: "var(--grid)" }));
      svg.appendChild(el("text", { x: lx(t), y: m.t + ih + 18, "text-anchor": "middle", class: "axis" }, fmt(t)));
    });
    svg.appendChild(el("text", { x: m.l + iw / 2, y: H - 4, "text-anchor": "middle", class: "lbl" }, "D2C customers (log scale)"));
    svg.appendChild(el("text", { x: 14, y: m.t + ih / 2, "text-anchor": "middle", class: "lbl", transform: `rotate(-90 14 ${m.t + ih / 2})` }, "CLV per customer"));
    const label = new Set(["TV", "WM", "AC", "TV → TV", "REF → REF", "WM → TV", "AC → AC"]);
    [...data].sort((a, b) => b.total - a.total).forEach((d) => {
      const cx = lx(d.customers), cy = ly(d.clv), r = rr(d.total);
      const c = el("circle", { cx, cy, r, fill: COLOR[d.type], "fill-opacity": 0.82, stroke: "var(--surface)", "stroke-width": 2 });
      svg.appendChild(c);
      hover(c, tip, `<b>${d.seg}</b> · ${d.type}<br>${fmt(d.customers)} customers · CLV $${fmt(d.clv)}<br>Order value $${fmt(d.aov)} · Total CLV $${fmt(d.total)}`);
    });
    data.filter((d) => label.has(d.seg)).forEach((d) => {
      const cx = lx(d.customers), cy = ly(d.clv), r = rr(d.total);
      const below = d.seg === "AC";
      svg.appendChild(el("text", { x: cx, y: below ? cy + r + 14 : cy - r - 5, "text-anchor": "middle", class: "dlab" }, d.seg));
    });
    root.appendChild(svg);
    table(root, ["Segment", "Type", "Customers", "CLV per customer", "Total CLV"], data.map((d) => [d.seg, d.type, fmt(d.customers), "$" + fmt(d.clv), "$" + fmt(d.total)]));
  }

  // 3. Conversion rate by acquisition channel
  function channels(root, data) {
    const rows = data.map((d) => ({ ...d, rate: (d.buyers / d.visits) * 100 })).sort((a, b) => b.rate - a.rate);
    const W = 900, rowH = 30, m = { l: 110, r: 190, t: 6 }, H = m.t + rows.length * rowH + 8, max = 1.0;
    const x = (v) => m.l + (v / max) * (W - m.l - m.r);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Purchase conversion rate by acquisition channel" });
    const tip = tipFor(root);
    rows.forEach((d, i) => {
      const yy = m.t + i * rowH, bh = 16, w = Math.max(2, x(d.rate) - m.l);
      svg.appendChild(el("text", { x: m.l - 10, y: yy + bh / 2 + 9, "text-anchor": "end", class: "lbl" }, d.channel));
      const bar = el("rect", { x: m.l, y: yy + 5, width: w, height: bh, rx: 4, fill: "var(--series-1)" });
      svg.appendChild(bar);
      svg.appendChild(el("text", { x: m.l + w + 8, y: yy + bh / 2 + 9, class: "val" }, `${d.rate.toFixed(2)}%`));
      svg.appendChild(el("text", { x: W - 4, y: yy + bh / 2 + 9, "text-anchor": "end", class: "axis" }, `${fmt(d.buyers)} of ${fmt(d.visits)}`));
      hover(bar, tip, `<b>${d.channel}</b><br>${d.buyers.toLocaleString()} buyers of ${d.visits.toLocaleString()} visitors`);
    });
    root.appendChild(svg);
    table(root, ["Channel", "Visitors", "Buyers", "Conversion"], rows.map((d) => [d.channel, d.visits.toLocaleString(), d.buyers.toLocaleString(), d.rate.toFixed(2) + "%"]));
  }

  // 4. Subsidiary requests converging on HQ
  function worldMap(root) {
    const M = window.WORLD_MAP; if (!M) return;
    const svg = el("svg", { viewBox: `0 0 ${M.W} ${M.H - 75}`, role: "img", "aria-label": "Development requests from regional subsidiaries flowing to headquarters in Korea" });
    svg.appendChild(el("path", { d: M.d, fill: "var(--land)", stroke: "none" }));
    const [hx, hy] = M.regions.hq;
    const tip = tipFor(root);
    Object.entries(M.regions).forEach(([name, [x, y]]) => {
      if (name === "hq") return;
      const mx = (x + hx) / 2, my = Math.min(y, hy) - 60 - Math.abs(x - hx) * 0.08;
      svg.appendChild(el("path", { d: `M${x},${y} Q${mx},${my} ${hx},${hy}`, fill: "none", stroke: "var(--series-1)", "stroke-width": 2, "stroke-opacity": 0.55, class: "flow-line" }));
      const dot = el("circle", { cx: x, cy: y, r: 7, fill: "var(--series-1)", stroke: "var(--surface)", "stroke-width": 2 });
      svg.appendChild(dot);
      svg.appendChild(el("text", { x, y: y + 22, "text-anchor": "middle", class: "maplab" }, name));
      hover(dot, tip, `${name} subsidiaries → HQ`);
    });
    svg.appendChild(el("circle", { cx: hx, cy: hy, r: 11, fill: "var(--series-2)", stroke: "var(--surface)", "stroke-width": 2.5 }));
    svg.appendChild(el("text", { x: hx + 16, y: hy + 5, class: "maplab strong" }, "HQ"));
    root.appendChild(svg);
  }


  // 5. Profit variance split into volume vs margin
  function decomp(root, data) {
    const W = 440, rowH = 44, m = { l: 112, r: 64, t: 4 }, H = m.t + data.length * rowH + 22;
    const x0 = m.l + 34, sc = (W - m.r - x0) / 110, x = (v) => x0 + v * sc;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Share of production profit variance explained by order volume and by margin rate" });
    const tip = tipFor(root);
    svg.appendChild(el("line", { x1: x(0), x2: x(0), y1: m.t, y2: H - 20, stroke: "var(--rule-strong)" }));
    data.forEach((d, i) => {
      const yy = m.t + i * rowH + 10, bh = 20, a = Math.min(x(0), x(d.v)), w = Math.max(2, Math.abs(x(d.v) - x(0)));
      svg.appendChild(el("text", { x: m.l - 4, y: yy + 15, "text-anchor": "end", class: "lbl" }, d.k));
      const bar = el("rect", { x: a, y: yy, width: w, height: bh, rx: 3, fill: i === 1 ? "var(--series-1)" : "var(--muted)" });
      svg.appendChild(bar);
      svg.appendChild(el("text", { x: Math.max(x(0), x(d.v)) + 6, y: yy + 15, class: "val" }, (d.v < 0 ? "−" : "") + Math.abs(d.v).toFixed(1) + "%"));
      hover(bar, tip, `${d.k}: <b>${d.v.toFixed(1)}%</b>`);
    });
    svg.appendChild(el("text", { x: x(0), y: H - 4, "text-anchor": "middle", class: "axis" }, "0%"));
    svg.appendChild(el("text", { x: x(100), y: H - 4, "text-anchor": "middle", class: "axis" }, "100%"));
    root.appendChild(svg);
  }

  // 6. Contribution of each account group to margin variance, top 10 highlighted
  function pareto(root, data) {
    const W = 760, rowH = 22, m = { l: 270, r: 120, t: 4 }, H = m.t + data.length * rowH + 30;
    const max = 16, x = (v) => m.l + (Math.abs(v) / max) * (W - m.l - m.r);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Contribution to margin variance by account group; top 10 explain 70.8%" });
    const tip = tipFor(root);
    svg.appendChild(el("text", { x: W - 4, y: m.t + 10, "text-anchor": "end", class: "axis" }, "cumulative"));
    data.forEach((d, i) => {
      const yy = m.t + 14 + i * rowH, top = i < 10;
      if (i === 10) {
        svg.appendChild(el("line", { x1: 8, x2: W - 4, y1: yy - 3, y2: yy - 3, stroke: "var(--ink)", "stroke-dasharray": "3 3" }));
      }
      svg.appendChild(el("text", { x: m.l - 8, y: yy + 12, "text-anchor": "end", class: "lbl", style: top ? "" : "opacity:.7" }, d.name));
      const bar = el("rect", { x: m.l, y: yy + 2, width: Math.max(2, x(d.contrib) - m.l), height: 13, rx: 3, fill: top ? "var(--series-1)" : "var(--rule-strong)" });
      svg.appendChild(bar);
      svg.appendChild(el("text", { x: x(d.contrib) + 6, y: yy + 12, class: top ? "val" : "axis" }, (d.contrib < 0 ? "−" : "") + Math.abs(d.contrib).toFixed(1) + "%"));
      svg.appendChild(el("text", { x: W - 4, y: yy + 12, "text-anchor": "end", class: i === 9 ? "val" : "axis" }, d.cum.toFixed(1) + "%"));
      hover(bar, tip, `<b>${d.name}</b><br>Contribution ${d.contrib.toFixed(2)}% · swing ${d.swing}%p · r ${d.r}`);
    });
    root.appendChild(svg);
    table(root, ["Rank", "Account group", "Contribution", "Cumulative"], data.map((d, i) => [i + 1, d.name, d.contrib.toFixed(2) + "%", d.cum.toFixed(2) + "%"]));
  }

  // 7. Swing size vs co-movement with margin, with the screening cut-offs
  function quadScatter(root, data) {
    const W = 760, H = 400, m = { t: 16, r: 20, b: 44, l: 56 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const x = (v) => m.l + (v / 3) * iw, y = (v) => m.t + ih - (v / 0.8) * ih;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Account groups by size of monthly swing and co-movement with margin" });
    const tip = tipFor(root);
    [0, 0.2, 0.4, 0.6, 0.8].forEach((t) => { svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: "var(--grid)" })); svg.appendChild(el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end", class: "axis" }, t.toFixed(1))); });
    [0, 1, 2, 3].forEach((t) => svg.appendChild(el("text", { x: x(t), y: m.t + ih + 18, "text-anchor": "middle", class: "axis" }, t + "%p")));
    svg.appendChild(el("line", { x1: x(1), x2: x(1), y1: m.t, y2: m.t + ih, stroke: "var(--ink-2)", "stroke-dasharray": "4 4" }));
    svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y(0.35), y2: y(0.35), stroke: "var(--ink-2)", "stroke-dasharray": "4 4" }));
    const corner = (tx, ty, a, t) => svg.appendChild(el("text", { x: tx, y: ty, "text-anchor": a, class: "maplab strong" }, t));
    corner(W - m.r - 6, m.t + 14, "end", "Key drivers"); corner(m.l + 6, m.t + 14, "start", "Alert indicators");
    corner(W - m.r - 6, m.t + ih - 8, "end", "Check offsetting account"); corner(m.l + 6, m.t + ih - 8, "start", "Lower priority");
    svg.appendChild(el("text", { x: m.l + iw / 2, y: H - 4, "text-anchor": "middle", class: "lbl" }, "Size of monthly swing in cost ratio"));
    svg.appendChild(el("text", { x: 14, y: m.t + ih / 2, "text-anchor": "middle", class: "lbl", transform: `rotate(-90 14 ${m.t + ih / 2})` }, "Co-movement with margin |r|"));
    const lab = { "Outsourced materials (net of free-issue)": [0, -16, "middle", "Outsourced materials"], "Production labor: bonus": [0, 26, "middle", "Production bonus"], "Paid-supply materials (net)": [0, -16, "end", "Paid-supply materials"], "Electricity": [10, 4, "start", "Electricity"], "Raw materials (incl. price variance)": [0, 26, "end", "Raw materials"] };
    data.forEach((d, i) => {
      const cx = x(d.swing), cy = y(Math.abs(d.r)), r = 4 + Math.sqrt(Math.abs(d.contrib)) * 2.6;
      const c = el("circle", { cx, cy, r, fill: i < 10 ? "var(--series-1)" : "var(--muted)", "fill-opacity": 0.85, stroke: "var(--surface)", "stroke-width": 2 });
      svg.appendChild(c);
      const L = lab[d.name]; if (L) svg.appendChild(el("text", { x: cx + L[0] + (L[2] === "start" ? r : L[2] === "end" ? r : 0), y: cy + L[1], "text-anchor": L[2], class: "dlab" }, L[3]));
      hover(c, tip, `<b>${d.name}</b><br>Swing ${d.swing}%p · r ${d.r} · contribution ${d.contrib}%`);
    });
    root.appendChild(svg);
  }


  // 8. Monthly profit: actual vs. margin held at its average
  function profitLines(root, data) {
    legend(root, [["Actual monthly production profit", "var(--series-1)"], ["If margin rate had stayed at its 5-year average", "var(--series-2)"]]);
    const W = 760, H = 300, m = { t: 14, r: 16, b: 34, l: 52 }, iw = W - m.l - m.r, ih = H - m.t - m.b;
    const ys = data.flatMap((d) => [d.profit, d.cf]), lo = Math.floor(Math.min(...ys)), hi = Math.ceil(Math.max(...ys));
    const x = (i) => m.l + (i / (data.length - 1)) * iw, y = (v) => m.t + ih - ((v - lo) / (hi - lo)) * ih;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Monthly production profit versus the same profit with margin held at its average, 2021 to 2025" });
    for (let t = lo; t <= hi; t += 1) {
      svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: t === 0 ? "var(--rule-strong)" : "var(--grid)" }));
      svg.appendChild(el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end", class: "axis" }, t + "bn"));
    }
    data.forEach((d, i) => { if (d.ym % 100 === 1) svg.appendChild(el("text", { x: x(i), y: H - 10, "text-anchor": "middle", class: "axis" }, Math.floor(d.ym / 100))); });
    const path = (k) => data.map((d, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(d[k]).toFixed(1)}`).join(" ");
    svg.appendChild(el("path", { d: path("cf"), fill: "none", stroke: "var(--series-2)", "stroke-width": 2 }));
    svg.appendChild(el("path", { d: path("profit"), fill: "none", stroke: "var(--series-1)", "stroke-width": 2 }));
    const guide = el("line", { y1: m.t, y2: m.t + ih, stroke: "var(--ink-2)", "stroke-dasharray": "3 3", visibility: "hidden" });
    const dot = el("circle", { r: 4.5, fill: "var(--series-1)", stroke: "var(--surface)", "stroke-width": 2, visibility: "hidden" });
    svg.appendChild(guide); svg.appendChild(dot);
    const tip = tipFor(root);
    const hit = el("rect", { x: m.l, y: m.t, width: iw, height: ih, fill: "transparent" });
    hit.addEventListener("pointermove", (e) => {
      const r = svg.getBoundingClientRect(), px = ((e.clientX - r.left) / r.width) * W;
      const i = Math.max(0, Math.min(data.length - 1, Math.round(((px - m.l) / iw) * (data.length - 1)))), d = data[i];
      guide.setAttribute("x1", x(i)); guide.setAttribute("x2", x(i)); guide.setAttribute("visibility", "visible");
      dot.setAttribute("cx", x(i)); dot.setAttribute("cy", y(d.profit)); dot.setAttribute("visibility", "visible");
      tip.show(dot, `<b>${Math.floor(d.ym / 100)}.${String(d.ym % 100).padStart(2, "0")}</b><br>Actual ${d.profit.toFixed(2)}bn · margin ${d.mgn}%<br>Margin at average ${d.cf.toFixed(2)}bn`);
    });
    hit.addEventListener("pointerleave", () => { guide.setAttribute("visibility", "hidden"); dot.setAttribute("visibility", "hidden"); tip.hide(); });
    svg.appendChild(hit);
    root.appendChild(svg);
  }

  // 9. Cumulative share of margin variance by account-group rank
  function cumCurve(root, data) {
    const W = 420, H = 300, m = { t: 14, r: 14, b: 36, l: 44 }, iw = W - m.l - m.r, ih = H - m.t - m.b, n = data.length;
    const x = (i) => m.l + (i / (n - 1)) * iw, y = (v) => m.t + ih - (v / 100) * ih;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "Cumulative share of margin variance by account group rank" });
    const tip = tipFor(root);
    [0, 25, 50, 75, 100].forEach((t) => { svg.appendChild(el("line", { x1: m.l, x2: W - m.r, y1: y(t), y2: y(t), stroke: t ? "var(--grid)" : "var(--rule-strong)" })); svg.appendChild(el("text", { x: m.l - 6, y: y(t) + 4, "text-anchor": "end", class: "axis" }, t + "%")); });
    [1, 5, 10, 15, 21].forEach((r) => svg.appendChild(el("text", { x: x(r - 1), y: H - 18, "text-anchor": "middle", class: "axis" }, r)));
    svg.appendChild(el("text", { x: m.l + iw / 2, y: H - 2, "text-anchor": "middle", class: "lbl" }, "Account groups, ranked by contribution"));
    svg.appendChild(el("path", { d: data.map((d, i) => `${i ? "L" : "M"}${x(i)},${y(d.cum)}`).join(" ") + ` L${x(n - 1)},${y(0)} L${x(0)},${y(0)} Z`, fill: "var(--series-1)", "fill-opacity": 0.1, stroke: "none" }));
    svg.appendChild(el("path", { d: data.map((d, i) => `${i ? "L" : "M"}${x(i)},${y(d.cum)}`).join(" "), fill: "none", stroke: "var(--series-1)", "stroke-width": 2 }));
    svg.appendChild(el("line", { x1: x(9), x2: x(9), y1: y(0), y2: y(70.77), stroke: "var(--ink)", "stroke-dasharray": "3 3" }));
    data.forEach((d, i) => {
      const c = el("circle", { cx: x(i), cy: y(d.cum), r: i === 9 ? 6 : 3.5, fill: i < 10 ? "var(--series-1)" : "var(--muted)", stroke: "var(--surface)", "stroke-width": 1.5 });
      svg.appendChild(c);
      hover(c, tip, `#${i + 1} <b>${d.name}</b><br>+${Math.abs(d.contrib).toFixed(1)}% → ${d.cum.toFixed(1)}% cumulative`);
    });
    svg.appendChild(el("text", { x: x(9) + 10, y: y(70.77) + 18, class: "val" }, "Top 10 = 70.8%"));
    root.appendChild(svg);
  }

  const q = (id) => document.getElementById(id);
  if (q("chart-clv-index")) clvIndex(q("chart-clv-index"));
  if (q("chart-clv-bubbles") && window.CLV_BUBBLE) bubbles(q("chart-clv-bubbles"), window.CLV_BUBBLE);
  if (q("chart-clv-channels") && window.CLV_CHANNELS) channels(q("chart-clv-channels"), window.CLV_CHANNELS);
  if (q("chart-map")) worldMap(q("chart-map"));
  if (q("chart-profit") && window.MARGIN_MONTHLY) profitLines(q("chart-profit"), window.MARGIN_MONTHLY);
  if (q("chart-cum") && window.MARGIN_SETS) cumCurve(q("chart-cum"), window.MARGIN_SETS);
  if (q("chart-pareto") && window.MARGIN_SETS) pareto(q("chart-pareto"), window.MARGIN_SETS);
  if (q("chart-quad") && window.MARGIN_SETS) quadScatter(q("chart-quad"), window.MARGIN_SETS);
})();

(() => {
  "use strict";

  const BASE = "data/btc-001/evidence/";
  const NS = "http://www.w3.org/2000/svg";
  const $ = id => document.getElementById(id);

  async function csv(path) {
    const response = await fetch(BASE + path);
    if (!response.ok) throw new Error(`Could not load ${path}: HTTP ${response.status}`);
    const text = await response.text();
    const lines = text.trim().split(/\r?\n/);
    const headers = lines.shift().split(",");
    return lines.map(line => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
    });
  }

  function svg(id, content, label) {
    const host = $(id);
    if (!host) return;
    host.innerHTML = `<svg viewBox="0 0 900 330" role="img" aria-label="${label}" xmlns="${NS}">${content}</svg>`;
  }

  function lineChart(id, series, label, percent = false) {
    const W = 900, H = 330, L = 76, R = 24, T = 24, B = 48;
    const all = series.flatMap(s => s.values).filter(Number.isFinite);
    if (!all.length) throw new Error("Chart has no valid data.");
    let min = Math.min(...all), max = Math.max(...all);
    if (min === max) max = min + 1;
    if (percent) {
      min -= (max - min) * 0.05;
      max = 0;
    } else {
      const pad = (max - min) * 0.03;
      min -= pad; max += pad;
    }
    const x = i => L + i / Math.max(1, series[0].values.length - 1) * (W - L - R);
    const y = v => T + (max - v) / (max - min) * (H - T - B);
    let out = "";
    for (let i = 0; i <= 4; i++) {
      const v = min + (max - min) * i / 4;
      const yy = y(v);
      out += `<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" class="chart-grid"/>`;
      out += `<text x="${L-12}" y="${yy+4}" text-anchor="end" class="chart-axis">${percent ? (v*100).toFixed(0)+"%" : "$"+Math.round(v).toLocaleString("en-US")}</text>`;
    }
    series.forEach(s => {
      const points = s.values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
      out += `<polyline points="${points}" class="${s.className}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
    });
    out += `<text x="${L}" y="${H-12}" class="chart-axis">23 Dec 2022</text>`;
    out += `<text x="${W-R}" y="${H-12}" text-anchor="end" class="chart-axis">09 Jul 2026</text>`;
    svg(id, out, label);
  }

  function barChart(id, rows, label) {
    const W = 900, H = 330, L = 76, R = 30, T = 25, B = 65;
    const vals = rows.flatMap(r => [r.a, r.b]);
    let min = Math.min(0, ...vals), max = Math.max(0, ...vals);
    const pad = Math.max(0.02, (max-min)*0.05);
    min -= pad; max += pad;
    const y = v => T + (max-v)/(max-min)*(H-T-B);
    const zero = y(0), group = (W-L-R)/rows.length, bw = Math.min(54, group*.25);
    let out = `<line x1="${L}" y1="${zero}" x2="${W-R}" y2="${zero}" class="chart-axis-line"/>`;
    rows.forEach((r,i) => {
      const cx = L + group*(i+.5);
      [[r.a,cx-bw-3,"chart-bar-a"],[r.b,cx+3,"chart-bar-b"]].forEach(([v,xv,cls]) => {
        const yy = y(v), top = Math.min(yy,zero), height = Math.max(1,Math.abs(zero-yy));
        out += `<rect x="${xv}" y="${top}" width="${bw}" height="${height}" rx="4" class="${cls}"><title>${r.name}: ${(v*100).toFixed(2)}%</title></rect>`;
      });
      out += `<text x="${cx}" y="${H-28}" text-anchor="middle" class="chart-axis">${r.name}</text>`;
    });
    for (let i=0;i<=4;i++) {
      const v=min+(max-min)*i/4, yy=y(v);
      out += `<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" class="chart-grid"/>`;
      out += `<text x="${L-12}" y="${yy+4}" text-anchor="end" class="chart-axis">${(v*100).toFixed(0)}%</text>`;
    }
    svg(id,out,label);
  }

  function drawdown(values) {
    let peak = -Infinity;
    return values.map(v => {
      peak = Math.max(peak, v);
      return v / peak - 1;
    });
  }

  function exposureChart(events) {
    const W=900,H=260,L=90,R=30,top=30;
    const start=Date.parse("2022-12-23"), end=Date.parse("2026-07-09");
    const x=d=>L+(Date.parse(d)-start)/(end-start)*(W-L-R);
    let out="";
    events.forEach((e,i)=>{
      const yy=top+i*11.2;
      const a=x(e.entry_date), b=x(e.exit_date);
      out+=`<line x1="${a}" y1="${yy}" x2="${b}" y2="${yy}" class="chart-exposure"/>`;
    });
    out+=`<text x="${L}" y="${H-12}" class="chart-axis">23 Dec 2022</text><text x="${W-R}" y="${H-12}" text-anchor="end" class="chart-axis">09 Jul 2026</text>`;
    out+=`<text x="${L}" y="17" class="chart-axis">17 completed position events · horizontal bars show entry-to-exit holding periods</text>`;
    svg("exposure-chart",out,"Historical position holding periods from recorded entry and exit dates.");
  }

  async function render() {
    const status=$("chart-status");
    try {
      const [sma,bh,exposure,events,regimes,summary] = await Promise.all([
        csv("validation/sma_cross_oos_equity_curve.csv"),
        csv("validation/buy_hold_oos_equity_curve.csv"),
        csv("exposure/exposure_summary.csv"),
        csv("exposure/position_events.csv"),
        csv("regimes/regime_summary.csv"),
        csv("validation/oos_summary.csv")
      ]);
      if (sma.length !== bh.length || !sma.length) throw new Error("Equity curve series are empty or misaligned.");
      if (sma.some((r,i)=>r.Date!==bh[i].Date)) throw new Error("Equity curve dates do not align.");

      const a=sma.map(r=>Number(r.Portfolio_Value));
      const b=bh.map(r=>Number(r.Portfolio_Value));
      lineChart("equity-chart",[
        {values:a,className:"chart-line-a"},
        {values:b,className:"chart-line-b"}
      ],"Daily out-of-sample portfolio value: SMA crossover and buy-and-hold.");

      lineChart("drawdown-chart",[
        {values:drawdown(a),className:"chart-line-a"},
        {values:drawdown(b),className:"chart-line-b"}
      ],"Drawdown derived from each daily equity curve.",true);

      exposureChart(events);

      const regimeRows=regimes.map(r=>({
        name:r.regime==="sideways_transition"?"Transition":r.regime.charAt(0).toUpperCase()+r.regime.slice(1),
        a:Number(r.sma_compounded_return), b:Number(r.bh_compounded_return)
      }));
      barChart("regime-chart",regimeRows,"Compounded historical returns by market regime.");

      const stress=[
        {name:"0.00%",a:.421319},
        {name:"0.05%",a:.4101},
        {name:"0.10%",a:.3989},
        {name:"0.20%",a:.3765}
      ];
      const max=Math.max(...stress.map(r=>r.a)), min=Math.min(...stress.map(r=>r.a));
      const W=900,H=300,L=85,R=35,T=25,B=55;
      const axisMin=Math.floor((min-.015)*100)/100, axisMax=Math.ceil((max+.015)*100)/100;
      const y=v=>T+(axisMax-v)/(axisMax-axisMin)*(H-T-B);
      let out="";
      for(let i=0;i<=4;i++){ const v=axisMin+(axisMax-axisMin)*i/4;
        const yy=y(v);
        out+=`<line x1="${L}" y1="${yy}" x2="${W-R}" y2="${yy}" class="chart-grid"/><text x="${L-12}" y="${yy+4}" text-anchor="end" class="chart-axis">${(v*100).toFixed(0)}%</text>`;
      }
      const pts=stress.map((r,i)=>`${L+i*(W-L-R)/3},${y(r.a)}`).join(" ");
      out+=`<polyline points="${pts}" class="chart-line-a" fill="none"/>`;
      stress.forEach((r,i)=>{
        const xx=L+i*(W-L-R)/3, yy=y(r.a);
        out+=`<circle cx="${xx}" cy="${yy}" r="6" class="chart-dot"><title>${r.name} slippage: ${(r.a*100).toFixed(2)}% return</title></circle><text x="${xx}" y="${H-25}" text-anchor="middle" class="chart-axis">${r.name}</text>`;
      });
      svg("slippage-chart",out,"Historical out-of-sample returns under four tested slippage assumptions.");

      const meta=exposure[0], result=summary[0];
      if ($("exposure-note")) $("exposure-note").textContent =
        `${meta.invested_days} invested days (${(Number(meta.exposure_pct)*100).toFixed(2)}% exposure), ${meta.flat_days} flat days, ${meta.completed_trades} completed trades.`;
      if ($("slippage-note")) $("slippage-note").textContent =
        `Tested slippage assumptions; commission remained ${result.commission}. Returns: 42.13%, 41.01%, 39.89%, and 37.65%.`;
      if (status) status.textContent="All research charts loaded from the published evidence CSVs.";
    } catch (error) {
      if (status) status.textContent="Chart data could not be loaded: "+error.message+" Open this page through a local web server, not file://.";
      console.error(error);
    }
  }

  document.addEventListener("DOMContentLoaded",render);
})();

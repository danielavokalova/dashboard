const $ = (id) => document.getElementById(id);
const fmt = new Intl.NumberFormat("cs-CZ");
const state = { data: null, changeLimit: 10 };
const monthFmt = new Intl.DateTimeFormat("cs-CZ", { month: "short", year: "numeric" });

function toast(message) {
  const el = $("toast"); el.textContent = message; el.classList.add("show");
  clearTimeout(toast.timer); toast.timer = setTimeout(() => el.classList.remove("show"), 2200);
}

function percent(value) { return `${Number(value || 0).toLocaleString("cs-CZ", { maximumFractionDigits: 1 })} %`; }
function monthLabel(period) { const d = new Date(`${period}-01T00:00:00`); return Number.isNaN(d.valueOf()) ? period : monthFmt.format(d); }
function escapeHtml(value) { const d = document.createElement("div"); d.textContent = String(value); return d.innerHTML; }

function selectedAgencies() {
  const agency = $("agencyFilter").value, country = $("countryFilter").value;
  return state.data.agencies.filter((item) => (agency === "all" || item.name === agency) && (country === "all" || item.country === country));
}

function periodBounds() {
  const from = $("monthFrom").value, to = $("monthTo").value;
  return { from: from <= to ? from : to, to: from <= to ? to : from };
}

function agencySeries(agency, bounds) { return agency.months.filter((item) => item.period >= bounds.from && item.period <= bounds.to); }

function aggregate() {
  const agencies = selectedAgencies(), bounds = periodBounds();
  const periods = state.data.months.map((m) => m.period).filter((p) => p >= bounds.from && p <= bounds.to);
  const months = periods.map((period) => {
    const row = { period, bookings: 0, issued: 0, active: 0 };
    agencies.forEach((agency) => {
      const item = agency.months.find((m) => m.period === period);
      if (item) { row.bookings += item.bookings || 0; row.issued += item.issued || 0; }
    });
    row.active = Math.max(0, row.bookings - row.issued); return row;
  });
  const totals = months.reduce((acc, m) => ({ bookings: acc.bookings + m.bookings, issued: acc.issued + m.issued, active: acc.active + m.active }), { bookings: 0, issued: 0, active: 0 });
  totals.offline = agencies.reduce((sum, agency) => sum + Number(agency.overall.offline || 0), 0);
  totals.conversion = totals.bookings ? totals.issued / totals.bookings * 100 : 0;
  return { agencies, months, totals, bounds };
}

function renderKpis(view) {
  $("kpiBookings").textContent = fmt.format(view.totals.bookings);
  $("kpiIssued").textContent = fmt.format(view.totals.issued);
  $("kpiOther").textContent = fmt.format(view.totals.active);
  $("kpiOffline").textContent = fmt.format(view.totals.offline);
  $("kpiConversion").textContent = percent(view.totals.conversion);
  $("kpiIssuedSub").textContent = `${percent(view.totals.conversion)} z rezervací`;
  $("kpiOtherSub").textContent = `${percent(view.totals.bookings ? view.totals.active / view.totals.bookings * 100 : 0)} z rezervací`;
  const status = $("statusFilter").value;
  if (status === "issued") { $("kpiBookings").textContent = fmt.format(view.totals.issued); $("kpiBookingsSub").textContent = "vystavené ve vybraném období"; }
  else if (status === "other") { $("kpiBookings").textContent = fmt.format(view.totals.active); $("kpiBookingsSub").textContent = "nevystavené / ostatní"; }
  else $("kpiBookingsSub").textContent = "ve vybraném období";
}

function renderTrend(view) {
  const max = Math.max(1, ...view.months.map((m) => Math.max(m.bookings, m.issued, m.active)));
  const status = $("statusFilter").value;
  $("trendChart").innerHTML = view.months.map((m) => {
    const heights = [m.bookings, m.issued, m.active].map((v) => Math.max(v ? 3 : 0, v / max * 100));
    return `<div class="month-group" data-tip="${escapeHtml(monthLabel(m.period))}: ${fmt.format(m.bookings)} / ${fmt.format(m.issued)} / ${fmt.format(m.active)}">
      <i style="height:${heights[0]}%;${status !== "all" ? "opacity:.2" : ""}"></i>
      <i style="height:${heights[1]}%;${status === "other" ? "opacity:.2" : ""}"></i>
      <i style="height:${heights[2]}%;${status === "issued" ? "opacity:.2" : ""}"></i><label>${escapeHtml(monthLabel(m.period))}</label></div>`;
  }).join("") || "<p>Pro vybraný filtr nejsou data.</p>";
}

function agencyMetrics(view) {
  return view.agencies.map((agency) => {
    const series = agencySeries(agency, view.bounds);
    const bookings = series.reduce((s, m) => s + Number(m.bookings || 0), 0);
    const issued = series.reduce((s, m) => s + Number(m.issued || 0), 0);
    return { agency, series, bookings, issued, other: Math.max(0, bookings - issued), conversion: bookings ? issued / bookings * 100 : 0 };
  });
}

function renderChanges(view) {
  const rows = agencyMetrics(view).map((item) => {
    const prev = item.series.at(-2)?.bookings || 0, current = item.series.at(-1)?.bookings || 0;
    const delta = current - prev, rate = prev ? delta / prev * 100 : current ? 100 : 0;
    return { name: item.agency.name, prev, current, delta, rate };
  });
  const createRows = (items, type) => items.map((r) => `<div class="change-row"><b>${escapeHtml(r.name)}</b><span>${fmt.format(r.prev)} → ${fmt.format(r.current)}</span><em class="${type}">${r.delta >= 0 ? "+" : ""}${fmt.format(r.delta)} · ${r.rate >= 0 ? "+" : ""}${r.rate.toLocaleString("cs-CZ", { maximumFractionDigits: 1 })}%</em></div>`).join("") || "<div class=change-row>Bez dat</div>";
  const growth = rows.filter((r) => r.delta > 0).sort((a,b) => b.delta - a.delta).slice(0, state.changeLimit);
  const decline = rows.filter((r) => r.delta < 0).sort((a,b) => a.delta - b.delta).slice(0, state.changeLimit);
  $("growthList").innerHTML = createRows(growth, "up"); $("declineList").innerHTML = createRows(decline, "down");
}

function renderHorizontal(id, rows, valueKey, formatValue) {
  const max = Math.max(1, ...rows.map((r) => r[valueKey]));
  $(id).innerHTML = rows.map((r) => `<div class="hbar-row"><span title="${escapeHtml(r.agency.name)}">${escapeHtml(r.agency.name)}</span><div class="hbar-track"><i style="width:${Math.max(1, r[valueKey] / max * 100)}%"></i></div><b>${formatValue(r[valueKey])}</b></div>`).join("") || "<p>Pro vybraný filtr nejsou data.</p>";
}

function renderRankings(view) {
  const rows = agencyMetrics(view);
  renderHorizontal("agencyRanking", rows.filter((r) => r.bookings > 0).sort((a,b) => b.bookings - a.bookings).slice(0,10), "bookings", (v) => fmt.format(v));
  renderHorizontal("conversionRanking", rows.filter((r) => r.bookings >= 10).sort((a,b) => b.conversion - a.conversion).slice(0,10), "conversion", percent);
}

function renderConnectors() {
  const rows = state.data.rankings.connectors || [], max = Math.max(1, ...rows.map((r) => r.value));
  $("connectorChart").innerHTML = rows.slice(0,8).map((r) => `<div class="connector"><span>${escapeHtml(r.name)}</span><strong>${fmt.format(r.value)}</strong><i><b style="width:${r.value / max * 100}%"></b></i></div>`).join("");
}

function render() {
  const view = aggregate(); renderKpis(view); renderTrend(view); renderChanges(view); renderRankings(view); renderConnectors();
  const agency = $("agencyFilter").selectedOptions[0]?.textContent || "Všechny agentury";
  const country = $("countryFilter").value === "all" ? "všechny země" : $("countryFilter").value;
  $("selectionInfo").textContent = `${agency} · ${country} · ${monthLabel(view.bounds.from)} až ${monthLabel(view.bounds.to)}`;
}

function populateFilters() {
  const months = state.data.months.map((m) => m.period), agencies = [...state.data.agencies].sort((a,b) => a.name.localeCompare(b.name,"cs"));
  const monthOptions = months.map((m) => `<option value="${m}">${monthLabel(m)}</option>`).join("");
  $("monthFrom").innerHTML = monthOptions; $("monthTo").innerHTML = monthOptions; $("monthTo").value = months.at(-1); $("monthFrom").value = months[0];
  $("agencyFilter").insertAdjacentHTML("beforeend", agencies.map((a) => `<option value="${escapeHtml(a.name)}">${escapeHtml(a.name)}</option>`).join(""));
  const countries = [...new Set(agencies.map((a) => a.country).filter(Boolean))].sort();
  $("countryFilter").insertAdjacentHTML("beforeend", countries.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join(""));
}

function syncAgencyOptions() {
  const country = $("countryFilter").value;
  [...$("agencyFilter").options].forEach((o) => { if (o.value !== "all") { const agency = state.data.agencies.find((a) => a.name === o.value); o.hidden = country !== "all" && agency?.country !== country; } });
  const selected = state.data.agencies.find((a) => a.name === $("agencyFilter").value);
  if (selected && country !== "all" && selected.country !== country) $("agencyFilter").value = "all";
}

async function loadData(fresh = false) {
  $("loading").classList.remove("hidden");
  try {
    const response = await fetch(`data/air-insights.json${fresh ? `?v=${Date.now()}` : ""}`, { cache: fresh ? "no-store" : "default" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    if (!$("monthFrom").options.length) populateFilters();
    const updated = new Date(state.data.meta.generatedAt).toLocaleString("cs-CZ", { dateStyle:"medium", timeStyle:"short", timeZone:"Europe/Prague" });
    $("dataInfo").textContent = `Statistiky rezervací · aktualizováno ${updated}`; render();
    if (fresh) toast("Data byla obnovena");
  } catch (error) { console.error(error); toast("Data se nepodařilo načíst"); }
  finally { $("loading").classList.add("hidden"); }
}

["agencyFilter","statusFilter","monthFrom","monthTo"].forEach((id) => $(id).addEventListener("change", render));
$("countryFilter").addEventListener("change", () => { syncAgencyOptions(); render(); });
$("refreshButton").addEventListener("click", () => loadData(true));
$("clearFilters").addEventListener("click", () => { $("agencyFilter").value="all"; $("statusFilter").value="all"; $("countryFilter").value="all"; const months=state.data.months; $("monthFrom").value=months[0].period; $("monthTo").value=months.at(-1).period; syncAgencyOptions(); render(); });
document.querySelectorAll("[data-limit]").forEach((button) => button.addEventListener("click", () => { document.querySelectorAll("[data-limit]").forEach((b) => b.classList.remove("active")); button.classList.add("active"); state.changeLimit=Number(button.dataset.limit); render(); }));
loadData();

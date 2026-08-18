const $ = (id) => document.getElementById(id);
const state = { data: null, current: null, period: "weeks" };
const fmt = new Intl.NumberFormat("cs-CZ");
const pct = (value) => `${Number(value || 0).toLocaleString("cs-CZ", { maximumFractionDigits: 1 })} %`;

function showToast(message) {
  const toast = $("toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 2400);
}

function periodDelta(series, key, span = 4) {
  if (!series || series.length < span * 2) return null;
  const recent = series.slice(-span).reduce((sum, item) => sum + Number(item[key] || 0), 0);
  const prior = series.slice(-span * 2, -span).reduce((sum, item) => sum + Number(item[key] || 0), 0);
  if (!prior) return recent ? 100 : 0;
  return ((recent - prior) / prior) * 100;
}

function setDelta(id, value) {
  const node = $(id);
  if (value === null || !Number.isFinite(value)) {
    node.textContent = "bez srovnání";
    node.className = "delta";
    return;
  }
  node.textContent = `${value >= 0 ? "↑" : "↓"} ${Math.abs(value).toLocaleString("cs-CZ", { maximumFractionDigits: 1 })} %`;
  node.className = `delta ${value >= 0 ? "positive" : "negative"}${node.id === "issuedDelta" ? " light" : ""}`;
}

function fillSpark(series) {
  const values = (series || []).slice(-18).map((item) => item.bookings || 0);
  const max = Math.max(...values, 1);
  $("bookingSpark").innerHTML = values.map((value) => `<i style="height:${Math.max(6, (value / max) * 100)}%"></i>`).join("");
}

function fillPeople(value) {
  const ratio = Math.max(1, Math.min(10, Math.round((value || 1) * 5)));
  $("peopleViz").innerHTML = Array.from({ length: 10 }, (_, index) => `<i class="${index < ratio ? "on" : ""}"></i>`).join("");
}

function escapeXml(value) {
  return String(value).replace(/[<>&'\"]/g, (char) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '\"': "&quot;" }[char]));
}

function renderTrend(series) {
  const node = $("trendChart");
  if (!series?.length) {
    node.innerHTML = "<p>Pro tento výběr zatím není dost dat.</p>";
    return;
  }
  const width = 900, height = 280, padX = 34, padY = 24;
  const values = series.flatMap((item) => [item.bookings || 0, item.issued || 0]);
  const max = Math.max(...values, 1) * 1.08;
  const x = (index) => padX + (index / Math.max(series.length - 1, 1)) * (width - padX * 2);
  const y = (value) => height - padY - (value / max) * (height - padY * 2);
  const points = (key) => series.map((item, index) => `${x(index).toFixed(1)},${y(item[key] || 0).toFixed(1)}`).join(" ");
  const area = `${padX},${height - padY} ${points("bookings")} ${width - padX},${height - padY}`;
  const labelEvery = Math.max(1, Math.ceil(series.length / 7));
  const labels = series.map((item, index) => index % labelEvery === 0 || index === series.length - 1
    ? `<text class="chart-label" x="${x(index)}" y="${height - 4}" text-anchor="middle">${escapeXml(item.period.replace("-W", " / "))}</text>` : "").join("");
  const grids = [0, .25, .5, .75, 1].map((part) => {
    const gy = padY + part * (height - padY * 2);
    return `<line class="chart-grid" x1="${padX}" y1="${gy}" x2="${width - padX}" y2="${gy}"/>`;
  }).join("");
  node.innerHTML = `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" aria-hidden="true">
    <defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#171b25" stop-opacity=".13"/><stop offset="1" stop-color="#171b25" stop-opacity="0"/></linearGradient></defs>
    ${grids}<polygon class="chart-area" points="${area}"/><polyline class="chart-bookings" points="${points("bookings")}"/><polyline class="chart-issued" points="${points("issued")}"/>${labels}</svg>`;
}

function renderRankList(id, items, limit = 7) {
  const values = (items || []).slice(0, limit);
  $(id).innerHTML = values.length ? values.map((item, index) => `<div class="ranking-row"><span>${String(index + 1).padStart(2, "0")}</span><strong title="${escapeXml(item.name)}">${escapeXml(item.name)}</strong><b>${fmt.format(item.value)}</b></div>`).join("") : "<p>Bez dat</p>";
}

function renderAncillaries(metrics) {
  const items = [
    ["Offline", metrics.offline], ["UNIQA", metrics.uniqa], ["Parking", metrics.parking],
    ["Lounge", metrics.lounge], ["Assistance", metrics.assistance]
  ];
  const max = Math.max(...items.map((item) => item[1]), 1);
  $("ancillaryBars").innerHTML = items.map(([name, value]) => `<div class="rank-bar"><div><span>${name}</span><b>${fmt.format(value)}</b></div><i><b style="width:${(value / max) * 100}%"></b></i></div>`).join("");
}

function topName(items) { return items?.[0]?.name || "—"; }

function renderBrief(record, series) {
  const metrics = record.overall;
  const delta = periodDelta(series, "bookings", 4);
  const bestRoute = topName(record.topConnectors?.length ? record.topConnectors : state.data.rankings.connectors);
  const addonTotal = metrics.uniqa + metrics.parking + metrics.lounge + metrics.assistance;
  const addonRate = metrics.bookings ? (addonTotal / metrics.bookings) * 100 : 0;
  $("briefVolume").textContent = fmt.format(metrics.bookings);
  $("briefVolumeText").textContent = `${fmt.format(metrics.travelers)} cestujících, průměr ${metrics.travelersPerBooking.toLocaleString("cs-CZ")} na rezervaci.`;
  $("briefConversion").textContent = pct(metrics.successRate);
  $("briefConversionText").textContent = metrics.successRate >= 70 ? "Silná konverze rozhodnutých rezervací — prostor držet výkon." : "Konverze nabízí téma k diskusi: expirace, ceny nebo proces vystavení.";
  $("briefTrend").textContent = delta === null ? "Bez srovnání" : `${delta >= 0 ? "+" : ""}${delta.toLocaleString("cs-CZ", { maximumFractionDigits: 1 })} %`;
  $("briefTrendText").textContent = `${delta >= 0 ? "Objem v posledním období roste." : "Objem v posledním období klesá."} Hlavní technologický zdroj: ${bestRoute}.`;
  $("briefOpportunity").textContent = pct(addonRate);
  $("briefOpportunityText").textContent = addonRate < 10 ? "Nízké využití doplňků — dobré téma pro cross-sell UNIQA, parkingu či lounge." : "Doplňkové služby se používají; zaměřte se na mix a další růst.";
}

function currentRecord() {
  const value = $("agencySelect").value;
  if (value === "__all__") {
    return {
      name: "Všechny agentury", country: "Globální portfolio", overall: state.data.overall,
      months: state.data.months, weeks: state.data.weeks,
      topAirlines: state.data.rankings.statuses, topRoutes: state.data.rankings.agencies,
      topDestinations: state.data.rankings.destinations, topConnectors: state.data.rankings.connectors
    };
  }
  return state.data.agencies.find((item) => item.name === value) || state.data.agencies[0];
}

function render() {
  const record = currentRecord();
  state.current = record;
  const metrics = record.overall;
  const shortSeries = record.weeks?.length >= 4 ? record.weeks.slice(-26) : record.months.slice(-6);
  const series = state.period === "weeks" ? shortSeries : record.months.slice(-24);
  $("selectedAgency").textContent = record.name;
  $("selectedCountry").textContent = record.country || "—";
  $("heroPeriod").textContent = state.period === "weeks" ? "KRÁTKODOBÝ POHLED" : "DLOUHODOBÝ POHLED";
  $("bookingsValue").textContent = fmt.format(metrics.bookings);
  $("issuedValue").textContent = fmt.format(metrics.issued);
  $("issueRateValue").textContent = pct(metrics.issueRate);
  $("successRateValue").textContent = pct(metrics.successRate);
  $("successProgress").style.width = `${Math.min(100, metrics.successRate)}%`;
  const monthlyAverage = record.months?.length ? metrics.bookings / record.months.length : metrics.bookings;
  $("travelersValue").textContent = monthlyAverage.toLocaleString("cs-CZ", { maximumFractionDigits: 1 });
  setDelta("bookingDelta", periodDelta(shortSeries, "bookings", 2));
  setDelta("issuedDelta", periodDelta(shortSeries, "issued", 2));
  setDelta("successDelta", periodDelta(shortSeries, "successRate", 2));
  setDelta("travelerDelta", periodDelta(shortSeries, "bookings", 2));
  fillSpark(shortSeries);
  fillPeople(Math.min(2, monthlyAverage / Math.max(1, metrics.bookings) * 12));
  renderTrend(series);
  $("trendHeadline").textContent = state.period === "weeks" ? "Krátkodobý trend" : "Dlouhodobý trend";

  const recent = shortSeries.slice(-4).reduce((acc, item) => {
    ["bookings", "issued", "canceled"].forEach((key) => acc[key] += Number(item[key] || 0)); return acc;
  }, { bookings: 0, issued: 0, canceled: 0 });
  const bookingTrend = periodDelta(shortSeries, "bookings", 2) || 0;
  const conversionTrend = periodDelta(shortSeries, "successRate", 2) || 0;
  const pulse = Math.round(Math.max(0, Math.min(100, 58 + bookingTrend * .55 + conversionTrend * .35)));
  $("pulseScore").textContent = pulse;
  $("pulseText").textContent = pulse >= 70 ? "Portfolio má pozitivní dynamiku. Na schůzce stavte na růstu." : pulse >= 45 ? "Výkon je stabilní. Hledejte konkrétní příležitosti v konverzi a doplňcích." : "Poslední týdny zpomalují. Prověřte pokles objemu a důvody rušení.";
  $("recentBookings").textContent = fmt.format(recent.bookings);
  $("recentIssued").textContent = fmt.format(recent.issued);
  $("recentCanceled").textContent = fmt.format(recent.canceled);

  $("funnelBookings").textContent = fmt.format(metrics.bookings);
  $("funnelActive").textContent = fmt.format(metrics.active);
  $("funnelIssued").textContent = fmt.format(metrics.issued);
  $("funnelCanceled").textContent = fmt.format(metrics.canceled);
  const width = (value) => `${metrics.bookings ? Math.max(2, (value / metrics.bookings) * 100) : 0}%`;
  $("activeBar").style.width = width(metrics.active);
  $("issuedBar").style.width = width(metrics.issued);
  $("canceledBar").style.width = width(metrics.canceled);
  const tripTotal = metrics.bookings;
  const returnShare = tripTotal ? (metrics.offline / tripTotal) * 100 : 0;
  $("tripDonut").style.setProperty("--value", `${returnShare}%`);
  $("returnShare").textContent = pct(returnShare);
  $("returnCount").textContent = fmt.format(metrics.offline);
  $("onewayCount").textContent = fmt.format(Math.max(0, metrics.bookings - metrics.offline));
  renderAncillaries(metrics);
  renderRankList("routesList", state.data.rankings.agencies);
  renderRankList("airlinesList", [{ name: "Vystavené", value: metrics.issued }, { name: "Nevystavené / ostatní", value: metrics.active }]);
  renderRankList("connectorsList", record.topConnectors?.length ? record.topConnectors : state.data.rankings.connectors);
  renderBrief(record, shortSeries);
}

function populateAgencies() {
  const select = $("agencySelect");
  const fragment = document.createDocumentFragment();
  state.data.agencies.forEach((agency) => {
    const option = document.createElement("option");
    option.value = agency.name;
    option.textContent = `${agency.name} · ${fmt.format(agency.overall.bookings)}`;
    fragment.appendChild(option);
  });
  select.appendChild(fragment);
}

async function loadData(cacheBust = false) {
  $("loading").classList.remove("hidden");
  try {
    const response = await fetch(`data/air-insights.json${cacheBust ? `?v=${Date.now()}` : ""}`, { cache: cacheBust ? "no-store" : "default" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    if (!state.data?.overall || !Array.isArray(state.data.agencies)) throw new Error("Neplatná data");
    if ($("agencySelect").options.length === 1) populateAgencies();
    const meta = state.data.meta;
    const from = new Date(meta.dateFrom).toLocaleDateString("cs-CZ", { month: "short", year: "numeric" });
    const to = new Date(meta.dateTo).toLocaleDateString("cs-CZ", { month: "short", year: "numeric" });
    $("dataRange").textContent = `${from} — ${to}`;
    $("lastUpdated").textContent = `Aktualizováno ${new Date(meta.generatedAt).toLocaleString("cs-CZ", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Prague" })}`;
    render();
    if (cacheBust) showToast("Data byla znovu načtena");
  } catch (error) {
    console.error(error);
    showToast("Data se nepodařilo načíst. Zkuste obnovit stránku.");
    $("lastUpdated").textContent = "Data nejsou momentálně dostupná";
  } finally {
    $("loading").classList.add("hidden");
  }
}

$("agencySelect").addEventListener("change", render);
$("refreshButton").addEventListener("click", () => loadData(true));
document.querySelectorAll("[data-period]").forEach((button) => button.addEventListener("click", () => {
  document.querySelectorAll("[data-period]").forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
  state.period = button.dataset.period;
  render();
}));
$("mobileMenu").addEventListener("click", () => document.querySelector(".sidebar").classList.toggle("open"));
document.querySelectorAll(".nav-link").forEach((link) => link.addEventListener("click", () => {
  document.querySelectorAll(".nav-link").forEach((item) => item.classList.remove("active"));
  link.classList.add("active");
  document.querySelector(".sidebar").classList.remove("open");
}));
$("copyBrief").addEventListener("click", async () => {
  const record = state.current;
  if (!record) return;
  const text = `${record.name}\nRezervace: ${fmt.format(record.overall.bookings)}\nVystaveno: ${fmt.format(record.overall.issued)} (${pct(record.overall.issueRate)})\nÚspěšnost: ${pct(record.overall.successRate)}\nCestující: ${fmt.format(record.overall.travelers)}\nTop trasa: ${topName(record.topRoutes)}\nTop dopravce: ${topName(record.topAirlines)}`;
  try { await navigator.clipboard.writeText(text); showToast("Shrnutí je zkopírované"); }
  catch { showToast("Kopírování není v tomto prohlížeči dostupné"); }
});

loadData();

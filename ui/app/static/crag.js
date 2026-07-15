const areaId = document.body.dataset.areaId;
const nameEl = document.getElementById("area-name");

fetch(`/api/areas/${areaId}`)
  .then(r => (r.ok ? r.json() : null))
  .then(a => { nameEl.textContent = a?.node?.area_name ?? "Forecast"; })
  .catch(() => { nameEl.textContent = "Forecast"; });

(async () => {
    const el = document.getElementById("charts");
    try {
        const res = await fetch(`/api/forecast?area_id=${areaId}`);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();

        const metrics = Object.entries(data.series);
        if (metrics.every(([, list]) => list.every(s => s.points.length === 0))) {
            el.innerHTML = "<p>No forecast available.</p>";     // empty case
            return;
        }
        for (const [metric, seriesList] of metrics) {
            renderChart(el, metric, seriesList);                // one chart per metric
        }
    } catch (e) {
        document.getElementById("error").hidden = false;
        document.getElementById("error").textContent = "Failed to load forecast.";
    }
})();

function renderChart(container, metric, seriesList) {
    const box = document.createElement("div");
    box.className = "chart-box";
    const canvas = document.createElement("canvas");
    box.appendChild(canvas);
    container.appendChild(box);
    container.appendChild(canvas);

    const datasets = seriesList.map(s => ({
        label: s.label ?? s.source,                    // identity
        data: s.points.map(p => ({ x: p.t, y: p.v })), // time-series
        borderWidth: 2, pointRadius: 0, lineTension: 0.3,

    }));

    new Chart(canvas, {
        type: metric === "precip_probability" ? "bar" : "line",
        data: { datasets },
        options: {
            interaction: { mode: "nearest", axis: "x", intersect: false },
            scales: {
                x: {
                    type: "time",
                    time: {
                        unit: "hour",
                        stepSize: 3,                          // every hour (see density note)
                        displayFormats: { hour: "HH:mm" },
                    },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: false,                      // keep midnight ticks so date shows
                        callback(value, index, ticks) {
                            const d = new Date(ticks[index].value);
                            const hour = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false }); // "00:00"
                            const prev = index > 0 ? new Date(ticks[index - 1].value) : null;
                            const newDay = !prev || d.toDateString() !== prev.toDateString();

                            if (newDay) {
                                const date = d.toLocaleDateString([], { weekday: "short", month: "numeric", day: "numeric" });
                                return [hour, date];   // two rows on the first tick of a new day
                            }
                            return hour;
                        },
                    },
                    grid: { color: "rgba(0,0,0,0.06)" },
                },
                y: { grid: { color: "rgba(0,0,0,0.06)" } },
            },             // shared time axis
            plugins: {
                title: { display: true, text: metric },
                legend: { display: seriesList.length > 1 },
                tooltip: {
                    callbacks: {
                        title: (items) => new Date(items[0].parsed.x).toLocaleString([], {
                            weekday: "short", month: "numeric", day: "numeric",
                            hour: "numeric",
                        }),   // -> "Mon, 7/13, 3 PM"
                    },
                },
            }
        },
    });
}
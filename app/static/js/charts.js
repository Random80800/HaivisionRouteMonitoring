const charts = window.CHART_DATA || [];
const selectedWindow = window.SELECTED_WINDOW || 60;
const destinationCharts = {};

function buildLineChart(canvas, chartData) {
  return new Chart(canvas, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: chartData.datasets.map((ds) => ({
        label: ds.label,
        data: ds.values,
        borderColor: ds.borderColor,
        backgroundColor: ds.borderColor,
        tension: 0.18,
        pointRadius: ds.values.length > 40 ? 0 : 2,
        pointHoverRadius: 4,
        borderWidth: 2,
        fill: false,
        spanGaps: true,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: { display: true },
        tooltip: { enabled: true },
      },
      scales: {
        x: {
          ticks: {
            maxTicksLimit: 8,
            autoSkip: true,
            maxRotation: 0,
            minRotation: 0,
          },
          grid: { display: false },
        },
        y: {
          beginAtZero: true,
          ticks: {
            maxTicksLimit: 6,
          },
        },
      },
    },
  });
}

charts.forEach((item, idx) => {
  const canvas = document.getElementById(`chart-${idx + 1}`);
  if (!canvas) return;
  buildLineChart(canvas, item);
});

async function loadDestinationChart(button) {
  const routeId = button.dataset.routeId;
  const destinationId = button.dataset.destinationId;
  const canvasId = button.dataset.canvasId;
  const wrapId = canvasId.replace("dst-chart-", "dst-chart-wrap-");

  const wrap = document.getElementById(wrapId);
  const canvas = document.getElementById(canvasId);
  if (!wrap || !canvas) return;

  const alreadyOpen = wrap.style.display !== "none";

  if (alreadyOpen) {
    wrap.style.display = "none";
    button.textContent = "Show Trend";
    return;
  }

  wrap.style.display = "block";
  button.textContent = "Hide Trend";

  const chartKey = `${routeId}__${destinationId}`;
  if (destinationCharts[chartKey]) {
    return;
  }

  try {
    const response = await fetch(`/api/destination-history/${encodeURIComponent(routeId)}/${encodeURIComponent(destinationId)}?window=${selectedWindow}`);
    const data = await response.json();
    destinationCharts[chartKey] = buildLineChart(canvas, data);
  } catch (error) {
    console.error("Failed to load destination history:", error);
  }
}

document.querySelectorAll(".trend-toggle-btn").forEach((button) => {
  button.addEventListener("click", () => loadDestinationChart(button));
});
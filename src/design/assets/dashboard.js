const apiStatus = document.querySelector("[data-api-status]");

const formatMetric = (payload, key) => payload?.metrics?.[key]?.formatted ?? "";
const metricValue = (payload, key) => payload?.metrics?.[key]?.value;

const setText = (selector, value) => {
  const element = document.querySelector(selector);
  if (element) {
    element.textContent = value ?? "";
  }
};

const setWidth = (selector, value) => {
  const element = document.querySelector(selector);
  const numberValue = Number(value);

  if (element && Number.isFinite(numberValue)) {
    element.style.width = `${Math.max(0, Math.min(100, numberValue))}%`;
  }
};

const clearDashboard = () => {
  document.querySelectorAll("[data-metric], [data-copy], [data-progress-label]").forEach((element) => {
    element.textContent = "";
  });

  document.querySelectorAll("[data-progress]").forEach((element) => {
    element.style.width = "0%";
  });

  const tableBody = document.querySelector("[data-quality-table]");
  if (tableBody) {
    tableBody.innerHTML = "";
  }

  const flowList = document.querySelector("[data-flow-list]");
  if (flowList) {
    flowList.innerHTML = "";
  }

  if (apiStatus) {
    apiStatus.textContent = "";
  }
};

const setChart = (name, src) => {
  const image = document.querySelector(`[data-chart="${name}"]`);
  if (image && src) {
    image.src = src;
  }
};

const renderQuality = (quality) => {
  const tableBody = document.querySelector("[data-quality-table]");
  if (!tableBody || !Array.isArray(quality)) {
    return;
  }

  tableBody.innerHTML = quality
    .map(
      (item) => `
        <tr>
          <td>${item.label}</td>
          <td>${item.value}</td>
        </tr>
      `,
    )
    .join("");
};

const renderFlow = (flow) => {
  const flowList = document.querySelector("[data-flow-list]");
  if (!flowList || !Array.isArray(flow)) {
    return;
  }

  flowList.innerHTML = flow
    .map(
      (item) => `
        <div class="flow-step">
          <small>${item.step}</small>
          <strong>${item.artifact}</strong>
          <span>${item.description}</span>
        </div>
      `,
    )
    .join("");
};

const renderDashboard = (payload) => {
  setText("[data-metric='orders_total']", formatMetric(payload, "orders_total"));
  setText("[data-metric='delivered_total']", formatMetric(payload, "delivered_total"));
  setText("[data-metric='late_rate']", formatMetric(payload, "late_rate"));
  setText("[data-metric='delivery_days_mean']", formatMetric(payload, "delivery_days_mean"));

  setText("[data-copy='delivered_rate']", `${formatMetric(payload, "delivered_rate")} da base com entrega registrada.`);
  setText("[data-copy='delivery_median']", `Mediana de ${formatMetric(payload, "delivery_days_median")} e cauda longa operacional.`);
  setText(
    "[data-copy='delivery_insight']",
    `O prazo medio fica em ${formatMetric(payload, "delivery_days_mean")}, com dispersao suficiente para merecer monitoramento por rota.`,
  );
  setText(
    "[data-copy='freight_insight']",
    `O frete medio e ${formatMetric(payload, "freight_mean")}, enquanto o maximo chega a ${formatMetric(payload, "freight_max")}.`,
  );
  setText(
    "[data-copy='distance_insight']",
    `A distancia media estimada e ${formatMetric(payload, "distance_mean")}, com 75% dos pedidos abaixo de ${formatMetric(payload, "distance_p75")}.`,
  );
  setText(
    "[data-copy='quality_insight']",
    `${formatMetric(payload, "duplicate_orders")} pedidos duplicados e ${formatMetric(payload, "invalid_delivery")} entregas com prazo negativo.`,
  );

  setText("[data-progress-label='delivered_rate']", formatMetric(payload, "delivered_rate"));
  setText("[data-progress-label='late_rate']", formatMetric(payload, "late_rate"));
  setText("[data-progress-label='distance_completeness']", formatMetric(payload, "distance_completeness"));

  setWidth("[data-progress='delivered_rate']", metricValue(payload, "delivered_rate"));
  setWidth("[data-progress='late_rate']", metricValue(payload, "late_rate"));
  setWidth("[data-progress='distance_completeness']", metricValue(payload, "distance_completeness"));

  setChart("monthly_orders", payload.charts?.monthly_orders);
  setChart("delivery_histogram", payload.charts?.delivery_histogram);
  setChart("freight_by_region", payload.charts?.freight_by_region);
  setChart("distance_delivery", payload.charts?.distance_delivery);
  setChart("correlation", payload.charts?.correlation);

  renderQuality(payload.quality);
  renderFlow(payload.flow);

  if (apiStatus) {
    apiStatus.textContent = payload.source?.mode === "live" ? "API conectada" : "Fallback ativo";
  }
};

const loadDashboard = async () => {
  clearDashboard();

  try {
    const response = await fetch("/api/dashboard");
    if (!response.ok) {
      throw new Error(`API respondeu com status ${response.status}`);
    }

    renderDashboard(await response.json());
  } catch (error) {
    clearDashboard();
    console.info("Dashboard aguardando API:", error);
  }
};

loadDashboard();

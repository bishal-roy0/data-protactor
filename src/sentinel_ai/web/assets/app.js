const form = document.querySelector("#analysis-form");
const submitButton = document.querySelector("#submit-button");
const error = document.querySelector("#form-error");
const result = document.querySelector("#result");
const emptyResult = document.querySelector("#empty-result");
const title = document.querySelector("#result-title");

const riskColors = { safe: "#4ce8c4", low: "#35a8ff", medium: "#ffc857", high: "#ff4fa3", critical: "#ff4d5c" };

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  error.textContent = "";
  const text = document.querySelector("#message").value.trim();
  const urls = document.querySelector("#urls").value.split("\n").map((url) => url.trim()).filter(Boolean);
  if (!text && !urls.length) { error.textContent = "Add a message, a URL, or both before analyzing."; return; }
  submitButton.disabled = true;
  submitButton.innerHTML = "Checking signals…";
  try {
    const response = await fetch("/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: text || null, urls }) });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail?.[0]?.msg || payload.detail || "Analysis could not be completed.");
    renderResult(payload);
  } catch (requestError) { error.textContent = requestError.message; }
  finally { submitButton.disabled = false; submitButton.innerHTML = "Analyze safety <span>→</span>"; }
});

function renderResult(payload) {
  const level = payload.risk_level;
  const color = riskColors[level] || "#35a8ff";
  title.textContent = "Assessment complete";
  emptyResult.hidden = true;
  result.hidden = false;
  const badge = document.querySelector("#risk-badge");
  badge.textContent = level.toUpperCase(); badge.style.color = color;
  document.querySelector("#risk-score").innerHTML = `${payload.risk_score}<span>/100</span>`;
  document.querySelector("#confidence").textContent = `${Math.round(payload.confidence * 100)}%`;
  const meter = document.querySelector("#meter-fill"); meter.style.width = `${payload.risk_score}%`; meter.style.background = color;
  document.querySelector("#category").textContent = payload.threat_category.replaceAll("_", " ");
  document.querySelector("#action").textContent = payload.recommended_action.replaceAll("_", " ");
  document.querySelector("#summary").textContent = payload.summary;
  const evidence = document.querySelector("#evidence"); evidence.replaceChildren();
  if (!payload.evidence.length) evidence.innerHTML = "<li><strong>No suspicious signals detected.</strong> Continue to verify unexpected requests independently.</li>";
  payload.evidence.forEach((item) => { const row = document.createElement("li"); row.innerHTML = `<strong>${item.signal} (+${item.weight})</strong><br>${item.explanation}`; evidence.appendChild(row); });
}

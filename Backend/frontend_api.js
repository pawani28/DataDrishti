// Replace the current upload.html inline analysis logic with this API integration.
// The backend serves the frontend, so API_BASE can stay empty.
const API_BASE = "";

async function uploadAndAnalyze(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.error || "Upload failed");
    }

    sessionStorage.setItem("datasetId", data.dataset_id);
    return data;
}

async function loadDashboard() {
    const datasetId = sessionStorage.getItem("datasetId");
    const url = datasetId
        ? `${API_BASE}/api/datasets/${datasetId}/dashboard`
        : `${API_BASE}/api/datasets/latest`;

    const response = await fetch(url);
    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.error || "Could not load dashboard");
    }
    return data;
}

async function askDataDrishti(question) {
    const datasetId = sessionStorage.getItem("datasetId");
    if (!datasetId) throw new Error("Upload a dataset first.");

    const response = await fetch(`${API_BASE}/api/datasets/${datasetId}/chat`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.error || "Chat request failed");
    }
    return data.answer;
}

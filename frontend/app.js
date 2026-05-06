/* ECHO — form submit handler and checklist loader */

const API_BASE = "";   // same origin; update if backend runs on a different port

/* ── index.html ── */
const form = document.getElementById("echo-form");
if (form) {
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        clearError();
        setLoading(true);

        const complications = Array.from(
            document.querySelectorAll('input[name="complications_flagged"]:checked')
        ).map((cb) => cb.value);

        const payload = {
            age: parseInt(document.getElementById("age").value, 10),
            race_ethnicity: document.getElementById("race_ethnicity").value,
            payer: document.getElementById("payer").value,
            state: document.getElementById("state").value,
            hospital_name: document.getElementById("hospital_name").value.trim(),
            weeks_postpartum: parseInt(document.getElementById("weeks_postpartum").value, 10),
            complications_flagged: complications,
            primary_language: document.getElementById("primary_language").value.trim(),
        };

        // client-side required-field check
        const missing = Object.entries(payload)
            .filter(([k, v]) => k !== "complications_flagged" && (v === "" || isNaN(v)))
            .map(([k]) => k);
        if (missing.length) {
            setLoading(false);
            showError("Please fill in all required fields: " + missing.join(", "));
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/generate-checklist`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: res.statusText }));
                throw new Error(err.detail || "Server error");
            }

            const data = await res.json();
            sessionStorage.setItem("echoChecklist", JSON.stringify(data));
            sessionStorage.setItem("echoPatient", JSON.stringify(payload));
            window.location.href = "checklist.html";
        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    });
}

function setLoading(on) {
    const btn = document.getElementById("submit-btn");
    const spinner = document.getElementById("spinner");
    if (!btn) return;
    btn.disabled = on;
    btn.textContent = on ? "Generating checklist…" : "Generate Checklist";
    if (spinner) spinner.classList.toggle("hidden", !on);
}

function showError(msg) {
    const el = document.getElementById("error-msg");
    if (el) { el.textContent = msg; el.classList.remove("hidden"); }
}

function clearError() {
    const el = document.getElementById("error-msg");
    if (el) { el.textContent = ""; el.classList.add("hidden"); }
}


/* ── checklist.html ── */
function loadChecklist() {
    const raw = sessionStorage.getItem("echoChecklist");
    const patientRaw = sessionStorage.getItem("echoPatient");
    if (!raw) { window.location.href = "index.html"; return; }

    const data = JSON.parse(raw);
    const patient = patientRaw ? JSON.parse(patientRaw) : {};

    renderPatientHeader(patient, data);
    renderFramingBlock(data.framing_block);
    renderItems(data.items);
    renderHospitalStatus(data.hospital_status);
    renderConflicts(data.conflict_flags);
    renderConfidenceSummary(data.confidence_summary);
    renderDisclaimer(data.clinical_disclaimer);
}

function renderPatientHeader(patient, data) {
    const el = document.getElementById("patient-header");
    if (!el) return;
    const urgencyColors = { HIGH: "red", MED: "yellow", LOW: "green" };
    const tier = data.urgency_tier || "";
    const color = urgencyColors[tier] || "gray";
    el.innerHTML = `
        <div class="flex flex-wrap gap-4 items-start">
            <div class="flex-1 min-w-0">
                <h2 class="text-lg font-semibold text-gray-800">Postpartum Screening Checklist</h2>
                <p class="text-sm text-gray-500 mt-1">
                    ${patient.state || ""} &middot;
                    ${patient.race_ethnicity || ""} &middot;
                    ${patient.payer || ""} &middot;
                    ${patient.weeks_postpartum != null ? patient.weeks_postpartum + " weeks postpartum" : ""} &middot;
                    ${patient.primary_language || ""}
                    ${patient.complications_flagged && patient.complications_flagged.length
                        ? " &middot; Complications: " + patient.complications_flagged.join(", ")
                        : ""}
                </p>
            </div>
            ${tier ? `<span class="px-3 py-1 rounded-full text-sm font-semibold bg-${color}-100 text-${color}-800 border border-${color}-300">
                Urgency: ${tier}
            </span>` : ""}
        </div>`;
}

function renderFramingBlock(framing) {
    const el = document.getElementById("framing-block");
    if (!el || !framing) return;
    const sources = (framing.framing_sources || [])
        .map((s) => s.url ? `<a href="${s.url}" class="underline" target="_blank">${s.name}</a>` : s.name)
        .join(", ");
    const seeAlso = (framing.see_also || [])
        .map((url) => `<a href="${url}" class="underline" target="_blank">${url}</a>`)
        .join(", ");
    el.innerHTML = `
        <p class="text-gray-700">${framing.framing_copy}</p>
        ${sources ? `<p class="text-xs text-gray-500 mt-2">Sources: ${sources}</p>` : ""}
        ${seeAlso ? `<p class="text-xs text-gray-500 mt-1">See also: ${seeAlso}</p>` : ""}`;
}

function isSDOH(item) {
    const src = (item.source || "").toLowerCase();
    return src.includes("cms") || src.includes("hrsn") || src.includes("ahc") || src.includes("sdoh");
}

function renderItem(item) {
    return `
        <div class="checklist-item${item.confidence === "FLAGGED" ? " flagged" : ""}">
            <div class="flex items-start gap-3">
                <span class="priority-badge">${item.priority_rank}</span>
                <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2 mb-1">
                        <h3 class="font-semibold text-sm" style="color: var(--text-primary);">${item.label}</h3>
                        <span class="confidence-${item.confidence}">${item.confidence}</span>
                    </div>
                    <p class="text-sm mb-1" style="color: var(--text-secondary);">${item.detail}</p>
                    <p class="text-sm font-medium mb-1" style="color: var(--accent-text);">${item.action}</p>
                    <p class="text-xs" style="color: var(--text-muted);">Source: ${item.source}</p>
                </div>
            </div>
        </div>`;
}

function renderItems(items) {
    const warningEl    = document.getElementById("warning-signs");
    const sdohEl       = document.getElementById("sdoh-flags");
    const warningEmpty = document.getElementById("warning-signs-empty");
    const sdohEmpty    = document.getElementById("sdoh-flags-empty");

    if (!warningEl && !sdohEl) return;

    if (!items || !items.length) {
        if (warningEmpty) warningEmpty.classList.remove("hidden");
        if (sdohEmpty)    sdohEmpty.classList.remove("hidden");
        return;
    }

    const warningItems = items.filter((item) => !isSDOH(item));
    const sdohItems    = items.filter(isSDOH);

    if (warningEl) {
        if (warningItems.length) {
            warningEl.innerHTML = warningItems.map(renderItem).join("");
            if (warningEmpty) warningEmpty.classList.add("hidden");
        } else {
            if (warningEmpty) warningEmpty.classList.remove("hidden");
        }
    }

    if (sdohEl) {
        if (sdohItems.length) {
            sdohEl.innerHTML = sdohItems.map(renderItem).join("");
            if (sdohEmpty) sdohEmpty.classList.add("hidden");
        } else {
            if (sdohEmpty) sdohEmpty.classList.remove("hidden");
        }
    }
}

function renderHospitalStatus(hs) {
    const el = document.getElementById("hospital-status");
    if (!el || !hs) return;
    const bfColors = {
        "Meets criteria": "green",
        "Does not meet criteria": "red",
        "Not found in CMS dataset": "gray",
    };
    const color = bfColors[hs.birthing_friendly] || "gray";
    el.innerHTML = `
        <h3 class="font-semibold text-gray-800 mb-2">Hospital Commitment Status</h3>
        <p class="text-sm font-medium">${hs.hospital_name}</p>
        <span class="inline-block mt-1 text-xs px-2 py-0.5 rounded bg-${color}-100 text-${color}-800 border border-${color}-300">
            CMS Birthing-Friendly: ${hs.birthing_friendly}
        </span>
        ${hs.hcahps_discharge_score != null
            ? `<p class="text-xs text-gray-600 mt-1">HCAHPS Discharge Score: ${hs.hcahps_discharge_score}</p>`
            : ""}
        ${hs.state_postpartum_visit_rate != null
            ? `<p class="text-xs text-gray-600 mt-1">State Postpartum Visit Rate (PPC-AD): ${(hs.state_postpartum_visit_rate * 100).toFixed(1)}%</p>`
            : ""}`;
}

function renderConflicts(flags) {
    const el = document.getElementById("conflict-flags");
    if (!el) return;
    if (!flags || !flags.length) { el.classList.add("hidden"); return; }
    el.classList.remove("hidden");
    el.innerHTML = `
        <h3 class="font-semibold text-purple-800 mb-2">Conflict Flags — CNM Review Required</h3>
        ${flags.map((f) => `
            <div class="mb-3 p-3 bg-purple-50 border border-purple-200 rounded">
                <p class="text-sm font-medium text-purple-900">${f.label}</p>
                <p class="text-sm text-purple-700 mt-1">${f.detail}</p>
                ${f.agents_involved && f.agents_involved.length
                    ? `<p class="text-xs text-purple-500 mt-1">Agents involved: ${f.agents_involved.join(", ")}</p>`
                    : ""}
            </div>`).join("")}`;
}

function renderConfidenceSummary(summary) {
    const el = document.getElementById("confidence-summary");
    if (!el || !summary) return;
    el.textContent = summary;
}

function renderDisclaimer(text) {
    const el = document.getElementById("clinical-disclaimer");
    if (!el) return;
    el.textContent = text;
}

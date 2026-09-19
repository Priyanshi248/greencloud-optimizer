/* =========================================================
   GREENCLOUD OPTIMIZER
   Frontend Controller
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL = "https://greencloud-optimizer.onrender.com";


/* =========================================================
   APPLICATION STATE
========================================================= */

let currentWorkloadId = null;

let currentCandidates = [];

let currentOptimizationResult = null;


/* =========================================================
   DOM REFERENCES
========================================================= */

// Navigation

const navLinks =
    document.querySelectorAll(".nav-link");


// Workload fields

const workloadName =
    document.getElementById("workload-name");

const workloadType =
    document.getElementById("workload-type");

const cpuCores =
    document.getElementById("cpu-cores");

const memoryGb =
    document.getElementById("memory-gb");

const storageGb =
    document.getElementById("storage-gb");

const runtimeMinutes =
    document.getElementById("runtime-minutes");

const deadlineMinutes =
    document.getElementById("deadline-minutes");

const dataTransferGb =
    document.getElementById("data-transfer-gb");


// Optimization

const optimizeButton =
    document.getElementById("optimize-button");

const optimizationStatus =
    document.getElementById("optimization-status");


// KPI values

const carbonValue =
    document.getElementById("carbon-value");

const energyValue =
    document.getElementById("energy-value");

const costValue =
    document.getElementById("cost-value");

const executionValue =
    document.getElementById("execution-value");


// Selected provider

const providerName =
    document.getElementById("provider-name");

const providerRegion =
    document.getElementById("provider-region");

const carbonScore =
    document.getElementById("carbon-score");

const resultCarbon =
    document.getElementById("result-carbon");

const resultEnergy =
    document.getElementById("result-energy");

const resultExecution =
    document.getElementById("result-execution");


// Providers

const providerTable =
    document.getElementById("provider-table");

const providerCount =
    document.getElementById("provider-count");


// Analytics

const carbonChart =
    document.getElementById("carbon-chart");

const analyticsProvider =
    document.getElementById("analytics-provider");

const analyticsEnergy =
    document.getElementById("analytics-energy");

const analyticsCarbon =
    document.getElementById("analytics-carbon");

const analyticsExecution =
    document.getElementById("analytics-execution");

const analyticsCost =
    document.getElementById("analytics-cost");


// Chat

const chatMessages =
    document.getElementById("chat-messages");

const chatInput =
    document.getElementById("chat-input");

const chatButton =
    document.getElementById("chat-button");


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeNavigation();

        initializeWorkloadListeners();

        initializeOptimization();

        initializeChat();

        checkApiHealth();

    }
);


/* =========================================================
   API HEALTH
========================================================= */

async function checkApiHealth() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/health`
            );

        if (!response.ok) {
            throw new Error(
                "API health check failed."
            );
        }

        setOptimizationStatus(
            "API connected. Ready to optimize your workload.",
            "success"
        );

    } catch (error) {

        console.error(
            "API health error:",
            error
        );

        setOptimizationStatus(
            "FastAPI is not reachable. Start the backend on port 8000.",
            "error"
        );

    }

}


/* =========================================================
   NAVIGATION
========================================================= */

function initializeNavigation() {

    navLinks.forEach(
        (link) => {

            link.addEventListener(
                "click",
                () => {

                    navLinks.forEach(
                        (item) => {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );

                    link.classList.add(
                        "active"
                    );

                }
            );

        }
    );


    const sections =
        document.querySelectorAll(
            ".page-section"
        );


    const observer =
        new IntersectionObserver(
            (entries) => {

                const visibleSections =
                    entries
                        .filter(
                            (entry) =>
                                entry.isIntersecting
                        )
                        .sort(
                            (a, b) =>
                                b.intersectionRatio -
                                a.intersectionRatio
                        );


                if (
                    visibleSections.length === 0
                ) {
                    return;
                }


                const currentSection =
                    visibleSections[0]
                        .target
                        .id;


                navLinks.forEach(
                    (link) => {

                        link.classList.toggle(
                            "active",
                            link.dataset.section ===
                                currentSection
                        );

                    }
                );

            },
            {
                rootMargin:
                    "-30% 0px -55% 0px",
                threshold: [0.05, 0.2, 0.5]
            }
        );


    sections.forEach(
        (section) => {

            observer.observe(
                section
            );

        }
    );

}


/* =========================================================
   WORKLOAD INPUT LISTENERS
========================================================= */

function initializeWorkloadListeners() {

    const inputs = [

        workloadName,
        workloadType,
        cpuCores,
        memoryGb,
        storageGb,
        runtimeMinutes,
        deadlineMinutes,
        dataTransferGb

    ];


    inputs.forEach(
        (input) => {

            if (!input) {
                return;
            }


            input.addEventListener(
                "input",
                handleWorkloadChange
            );


            input.addEventListener(
                "change",
                handleWorkloadChange
            );

        }
    );

}


/* =========================================================
   HANDLE WORKLOAD CHANGE
========================================================= */

function handleWorkloadChange() {

    /*
     * The previous optimization result is no longer
     * guaranteed to represent the current workload.
     */

    currentOptimizationResult = null;

    currentCandidates = [];

    currentWorkloadId = null;


    resetOptimizationDisplay();

    renderProviderPlaceholder();

    renderChartPlaceholder();


    setOptimizationStatus(
        "Workload changed. Run CEGP to calculate a fresh result.",
        ""
    );

}


/* =========================================================
   OPTIMIZATION INITIALIZATION
========================================================= */

function initializeOptimization() {

    if (!optimizeButton) {
        return;
    }


    optimizeButton.addEventListener(
        "click",
        runOptimization
    );

}


/* =========================================================
   READ WORKLOAD FORM
========================================================= */

function getWorkloadPayload() {

    return {

        name:
            workloadName.value.trim(),

        workload_type:
            workloadType.value,

        cpu_cores:
            Number(
                cpuCores.value
            ),

        memory_gb:
            Number(
                memoryGb.value
            ),

        storage_gb:
            Number(
                storageGb.value
            ),

        runtime_minutes:
            Number(
                runtimeMinutes.value
            ),

        deadline_minutes:
            Number(
                deadlineMinutes.value
            ),

        data_transfer_gb:
            Number(
                dataTransferGb.value
            )

    };

}


/* =========================================================
   VALIDATE WORKLOAD
========================================================= */

function validateWorkload(
    workload
) {

    if (!workload.name) {

        return "Please enter a workload name.";

    }


    if (
        !Number.isFinite(
            workload.cpu_cores
        ) ||
        workload.cpu_cores <= 0
    ) {

        return "CPU cores must be greater than 0.";

    }


    if (
        !Number.isFinite(
            workload.memory_gb
        ) ||
        workload.memory_gb <= 0
    ) {

        return "Memory must be greater than 0.";

    }


    if (
        !Number.isFinite(
            workload.storage_gb
        ) ||
        workload.storage_gb <= 0
    ) {

        return "Storage must be greater than 0.";

    }


    if (
        !Number.isFinite(
            workload.runtime_minutes
        ) ||
        workload.runtime_minutes <= 0
    ) {

        return "Runtime must be greater than 0.";

    }


    if (
        !Number.isFinite(
            workload.deadline_minutes
        ) ||
        workload.deadline_minutes <= 0
    ) {

        return "Deadline must be greater than 0.";

    }


    if (
        workload.deadline_minutes <
        workload.runtime_minutes
    ) {

        return (
            "Deadline should be greater than or equal to the workload runtime."
        );

    }


    if (
        !Number.isFinite(
            workload.data_transfer_gb
        ) ||
        workload.data_transfer_gb < 0
    ) {

        return (
            "Data transfer cannot be negative."
        );

    }


    return null;

}


/* =========================================================
   CREATE WORKLOAD
========================================================= */

async function createWorkload() {

    const workload =
        getWorkloadPayload();


    const validationError =
        validateWorkload(
            workload
        );


    if (validationError) {

        throw new Error(
            validationError
        );

    }


    const response =
        await fetch(
            `${API_BASE_URL}/workloads`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        workload
                    )
            }
        );


    if (!response.ok) {

        const errorText =
            await response.text();


        throw new Error(
            `Unable to create workload: ${errorText}`
        );

    }


    return response.json();

}


/* =========================================================
   RUN OPTIMIZATION
========================================================= */

async function runOptimization() {

    optimizeButton.disabled = true;


    setOptimizationStatus(
        "Preparing workload...",
        "loading"
    );


    try {

        /*
         * Always create a fresh workload from the
         * current form values.
         *
         * This means the frontend never depends
         * on a hardcoded UUID.
         */

        const workload =
            await createWorkload();


        currentWorkloadId =
            workload.id;


        setOptimizationStatus(
            "Evaluating active cloud providers...",
            "loading"
        );


        /*
         * First retrieve every provider's metrics.
         *
         * This is separate from selection so that
         * the UI can transparently display all
         * candidate environments.
         */

        await loadCandidates(
            currentWorkloadId
        );


        setOptimizationStatus(
            "Running CEGP optimization...",
            "loading"
        );


        /*
         * Ask the backend to run the deterministic
         * CEGP algorithm.
         */

        const response =
            await fetch(
                `${API_BASE_URL}/optimization/run`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                workload_id:
                                    currentWorkloadId,

                                algorithm:
                                    "cegp"
                            }
                        )
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(
                `Optimization failed: ${errorText}`
            );

        }


        const result =
            await response.json();


        currentOptimizationResult =
            result;


        updateOptimizationDashboard(
            result
        );


        highlightSelectedProvider(
            result.provider_id
        );


        updateAnalytics(
            result
        );


        renderCarbonChart(
            currentCandidates
        );


        setOptimizationStatus(
            "Optimization completed successfully.",
            "success"
        );


        /*
         * Scroll to the result after a successful
         * optimization so the user immediately sees it.
         */

        const resultSection =
            document.getElementById(
                "optimization-result"
            );


        if (resultSection) {

            setTimeout(
                () => {

                    resultSection.scrollIntoView(
                        {
                            behavior: "smooth",
                            block: "start"
                        }
                    );

                },
                250
            );

        }

    } catch (error) {

        console.error(
            "Optimization error:",
            error
        );


        setOptimizationStatus(
            error.message ||
            "Unable to run optimization.",
            "error"
        );

    } finally {

        optimizeButton.disabled = false;

    }

}


/* =========================================================
   LOAD CANDIDATES
========================================================= */

async function loadCandidates(
    workloadId
) {

    const response =
        await fetch(
            `${API_BASE_URL}/optimization/candidates/${workloadId}`
        );


    if (!response.ok) {

        const errorText =
            await response.text();


        throw new Error(
            `Unable to load provider candidates: ${errorText}`
        );

    }


    const candidates =
        await response.json();


    currentCandidates =
        Array.isArray(candidates)
            ? candidates
            : [];


    renderProviders(
        currentCandidates
    );


    renderCarbonChart(
        currentCandidates
    );


    return currentCandidates;

}


/* =========================================================
   RENDER PROVIDERS
========================================================= */

function renderProviders(
    candidates
) {

    if (!providerTable) {
        return;
    }


    if (
        !Array.isArray(candidates) ||
        candidates.length === 0
    ) {

        renderProviderPlaceholder();

        return;

    }


    providerTable.innerHTML = "";


    if (providerCount) {

        providerCount.textContent =
            `${candidates.length} environments`;

    }


    candidates.forEach(
        (candidate) => {

            const card =
                createProviderCard(
                    candidate
                );


            providerTable.appendChild(
                card
            );

        }
    );

}


/* =========================================================
   CREATE PROVIDER CARD
========================================================= */

function createProviderCard(
    candidate
) {

    const card =
        document.createElement(
            "div"
        );


    card.className =
        "provider-card";


    card.dataset.providerId =
        candidate.provider_id;


    const providerNameValue =
        candidate.provider_name ||
        "Unknown Provider";


    const providerType =
        formatProviderType(
            candidate.provider_type
        );


    const region =
        candidate.region ||
        "Unknown region";


    const energy =
        formatNumber(
            candidate.energy_kwh,
            2
        );


    const carbon =
        formatNumber(
            candidate.carbon_kg,
            3
        );


    const cost =
        formatNumber(
            candidate.cost,
            2
        );


    card.innerHTML = `

        <div class="provider-card-header">

            <div class="provider-title">

                <div class="provider-mini-icon">
                    ${getProviderInitials(
                        providerNameValue
                    )}
                </div>

                <div>

                    <h3>
                        ${escapeHtml(
                            providerNameValue
                        )}
                    </h3>

                    <span>
                        ${escapeHtml(
                            providerType
                        )}
                    </span>

                </div>

            </div>

            <span class="provider-region">
                ${escapeHtml(
                    region
                )}
            </span>

        </div>


        <div class="provider-metrics">

            <div class="provider-metric">

                <span>
                    Carbon
                </span>

                <strong>
                    ${carbon}
                </strong>

            </div>


            <div class="provider-metric">

                <span>
                    Energy
                </span>

                <strong>
                    ${energy}
                </strong>

            </div>


            <div class="provider-metric">

                <span>
                    Cost
                </span>

                <strong>
                    $${cost}
                </strong>

            </div>

        </div>

    `;


    return card;

}


/* =========================================================
   HIGHLIGHT SELECTED PROVIDER
========================================================= */

function highlightSelectedProvider(
    providerId
) {

    const cards =
        document.querySelectorAll(
            ".provider-card"
        );


    cards.forEach(
        (card) => {

            const isSelected =
                card.dataset.providerId ===
                String(providerId);


            card.classList.toggle(
                "selected",
                isSelected
            );


            const existingBadge =
                card.querySelector(
                    ".provider-selected-badge"
                );


            if (existingBadge) {

                existingBadge.remove();

            }


            if (isSelected) {

                const badge =
                    document.createElement(
                        "span"
                    );


                badge.className =
                    "provider-selected-badge";


                badge.textContent =
                    "SELECTED";


                card.appendChild(
                    badge
                );

            }

        }
    );

}


/* =========================================================
   UPDATE OPTIMIZATION DASHBOARD
========================================================= */

function updateOptimizationDashboard(
    result
) {

    const carbon =
        Number(
            result.carbon_emissions_kg
        );


    const energy =
        Number(
            result.energy_consumption_kwh
        );


    const cost =
        Number(
            result.estimated_cost
        );


    const execution =
        Number(
            result.execution_time_minutes
        );


    const score =
        Number(
            result.carbon_score
        );


    if (carbonValue) {

        carbonValue.textContent =
            formatNumber(
                carbon,
                3
            );

    }


    if (energyValue) {

        energyValue.textContent =
            formatNumber(
                energy,
                2
            );

    }


    if (costValue) {

        costValue.textContent =
            formatNumber(
                cost,
                2
            );

    }


    if (executionValue) {

        executionValue.textContent =
            formatNumber(
                execution,
                1
            );

    }


    if (providerName) {

        providerName.textContent =
            result.provider_name ||
            "Unknown provider";

    }


    if (providerRegion) {

        providerRegion.textContent =
            result.region ||
            "Unknown region";

    }


    if (carbonScore) {

        carbonScore.textContent =
            formatNumber(
                score,
                3
            );

    }


    if (resultCarbon) {

        resultCarbon.textContent =
            formatNumber(
                carbon,
                3
            );

    }


    if (resultEnergy) {

        resultEnergy.textContent =
            formatNumber(
                energy,
                2
            );

    }


    if (resultExecution) {

        resultExecution.textContent =
            formatNumber(
                execution,
                1
            );

    }

}


/* =========================================================
   ANALYTICS
========================================================= */

function updateAnalytics(
    result
) {

    if (analyticsProvider) {

        analyticsProvider.textContent =
            result.provider_name ||
            "—";

    }


    if (analyticsEnergy) {

        analyticsEnergy.textContent =
            `${formatNumber(
                result.energy_consumption_kwh,
                2
            )} kWh`;

    }


    if (analyticsCarbon) {

        analyticsCarbon.textContent =
            `${formatNumber(
                result.carbon_emissions_kg,
                3
            )} kg`;

    }


    if (analyticsExecution) {

        analyticsExecution.textContent =
            `${formatNumber(
                result.execution_time_minutes,
                1
            )} min`;

    }


    if (analyticsCost) {

        analyticsCost.textContent =
            `$${formatNumber(
                result.estimated_cost,
                2
            )}`;

    }

}


/* =========================================================
   CARBON CHART
========================================================= */

function renderCarbonChart(
    candidates
) {

    if (!carbonChart) {
        return;
    }


    if (
        !Array.isArray(candidates) ||
        candidates.length === 0
    ) {

        renderChartPlaceholder();

        return;

    }


    const carbonValues =
        candidates.map(
            (candidate) =>
                Number(
                    candidate.carbon_kg
                )
        );


    const maximum =
        Math.max(
            ...carbonValues,
            0.001
        );


    carbonChart.innerHTML = "";


    candidates.forEach(
        (candidate) => {

            const carbon =
                Number(
                    candidate.carbon_kg
                );


            const percentage =
                Math.max(
                    7,
                    (carbon / maximum) * 100
                );


            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "bar-wrapper";


            const value =
                document.createElement(
                    "span"
                );


            value.className =
                "bar-value";


            value.textContent =
                formatNumber(
                    carbon,
                    3
                );


            const bar =
                document.createElement(
                    "div"
                );


            bar.className =
                "bar";


            bar.style.height =
                `${percentage}%`;


            const label =
                document.createElement(
                    "span"
                );


            label.className =
                "bar-label";


            label.textContent =
                candidate.provider_name ||
                "Provider";


            label.title =
                `${candidate.provider_name || "Provider"} — ${candidate.region || ""}`;


            wrapper.appendChild(
                value
            );


            wrapper.appendChild(
                bar
            );


            wrapper.appendChild(
                label
            );


            carbonChart.appendChild(
                wrapper
            );

        }
    );

}


/* =========================================================
   CHAT INITIALIZATION
========================================================= */

function initializeChat() {

    if (!chatButton || !chatInput) {
        return;
    }


    chatButton.addEventListener(
        "click",
        sendChatMessage
    );


    chatInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendChatMessage();

            }

        }
    );

}


/* =========================================================
   SEND CHAT MESSAGE
========================================================= */

async function sendChatMessage() {

    const message =
        chatInput.value.trim();


    if (!message) {
        return;
    }


    addChatMessage(
        message,
        "user"
    );


    chatInput.value = "";

    chatButton.disabled = true;


    const loadingMessage =
        addChatMessage(
            "Thinking...",
            "assistant"
        );


    try {

        const payload = {

            message:
                message

        };


        /*
         * If a workload has been created during
         * this session, give the agent its ID.
         *
         * Otherwise the AI can still answer
         * general RAG questions.
         */

        if (currentWorkloadId) {

            payload.workload_id =
                currentWorkloadId;

        }


        const response =
            await fetch(
                `${API_BASE_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(
                `Chat request failed: ${errorText}`
            );

        }


        const result =
            await response.json();


        const answer =
            result.response ||
            result.message ||
            result.answer ||
            "No response received.";


        updateChatMessage(
            loadingMessage,
            answer
        );

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );


        updateChatMessage(
            loadingMessage,
            "Unable to connect to GreenCloud AI. Make sure the FastAPI server is running."
        );

    } finally {

        chatButton.disabled = false;

        chatInput.focus();

    }

}


/* =========================================================
   ADD CHAT MESSAGE
========================================================= */

function addChatMessage(
    message,
    sender
) {

    const messageElement =
        document.createElement(
            "div"
        );


    messageElement.className =
        `chat-message ${sender}`;


    const label =
        document.createElement(
            "span"
        );


    label.className =
        "message-label";


    label.textContent =
        sender === "user"
            ? "You"
            : "GreenCloud AI";


    const paragraph =
        document.createElement(
            "p"
        );


    paragraph.textContent =
        message;


    messageElement.appendChild(
        label
    );


    messageElement.appendChild(
        paragraph
    );


    chatMessages.appendChild(
        messageElement
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return messageElement;

}


/* =========================================================
   UPDATE CHAT MESSAGE
========================================================= */

function updateChatMessage(
    messageElement,
    message
) {

    if (!messageElement) {
        return;
    }


    const paragraph =
        messageElement.querySelector(
            "p"
        );


    if (paragraph) {

        paragraph.textContent =
            message;

    }


    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


/* =========================================================
   RESET OPTIMIZATION DISPLAY
========================================================= */

function resetOptimizationDisplay() {

    const fields = [

        carbonValue,
        energyValue,
        costValue,
        executionValue,
        providerName,
        providerRegion,
        carbonScore,
        resultCarbon,
        resultEnergy,
        resultExecution,
        analyticsProvider,
        analyticsEnergy,
        analyticsCarbon,
        analyticsExecution,
        analyticsCost

    ];


    fields.forEach(
        (element) => {

            if (element) {

                element.textContent =
                    "—";

            }

        }
    );

}


/* =========================================================
   PROVIDER PLACEHOLDER
========================================================= */

function renderProviderPlaceholder() {

    if (!providerTable) {
        return;
    }


    if (providerCount) {

        providerCount.textContent =
            "Waiting";

    }


    providerTable.innerHTML = `

        <div class="empty-state">

            <div class="empty-state-icon">
                ☁
            </div>

            <strong>
                Provider comparison
            </strong>

            <p>
                Run CEGP optimization to load
                all active cloud environments.
            </p>

        </div>

    `;

}


/* =========================================================
   CHART PLACEHOLDER
========================================================= */

function renderChartPlaceholder() {

    if (!carbonChart) {
        return;
    }


    carbonChart.innerHTML = `

        <div class="chart-placeholder">

            Run optimization to see the
            provider comparison.

        </div>

    `;

}


/* =========================================================
   STATUS
========================================================= */

function setOptimizationStatus(
    message,
    type
) {

    if (!optimizationStatus) {
        return;
    }


    optimizationStatus.textContent =
        message;


    optimizationStatus.className =
        "optimization-status";


    if (type) {

        optimizationStatus.classList.add(
            type
        );

    }

}


/* =========================================================
   FORMATTING
========================================================= */

function formatNumber(
    value,
    decimals = 2
) {

    const number =
        Number(value);


    if (!Number.isFinite(number)) {

        return "—";

    }


    return number.toFixed(
        decimals
    );

}


/* =========================================================
   PROVIDER TYPE FORMATTING
========================================================= */

function formatProviderType(
    providerType
) {

    if (!providerType) {

        return "Cloud environment";

    }


    return String(
        providerType
    )
        .replace(
            /_/g,
            " "
        )
        .replace(
            /\b\w/g,
            (letter) =>
                letter.toUpperCase()
        );

}


/* =========================================================
   PROVIDER INITIALS
========================================================= */

function getProviderInitials(
    name
) {

    if (!name) {
        return "GC";
    }


    const words =
        String(name)
            .trim()
            .split(/\s+/)
            .filter(Boolean);


    if (words.length === 1) {

        return words[0]
            .substring(0, 2)
            .toUpperCase();

    }


    return (
        words[0][0] +
        words[1][0]
    ).toUpperCase();

}


/* =========================================================
   HTML ESCAPING
========================================================= */

function escapeHtml(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}
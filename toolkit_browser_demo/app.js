const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const categories = {
  documents: [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"],
  spreadsheets: [".csv", ".xls", ".xlsx", ".ods"],
  presentations: [".ppt", ".pptx", ".key"],
  images: [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"],
  videos: [".mp4", ".mov", ".avi", ".mkv", ".webm"],
  audio: [".mp3", ".wav", ".aac", ".flac", ".m4a"],
  archives: [".zip", ".rar", ".7z", ".tar", ".gz"],
  code: [".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".xml"]
};

const emailTemplates = {
  welcome: {
    subject: "Welcome to {company}",
    body: "Hi {name},\n\nWelcome to {company}. We are glad to have you with us.\n\nBest,\n{sender}"
  },
  follow_up: {
    subject: "Following up on {topic}",
    body: "Hi {name},\n\nI wanted to follow up on {topic}. Please let me know if you need anything from my side.\n\nBest,\n{sender}"
  },
  meeting_request: {
    subject: "Meeting request: {topic}",
    body: "Hi {name},\n\nCan we schedule a meeting to discuss {topic}? I am available this week.\n\nBest,\n{sender}"
  },
  invoice_reminder: {
    subject: "Invoice reminder",
    body: "Hi {name},\n\nThis is a reminder that the invoice is pending. Please let me know if you need any details.\n\nBest,\n{sender}"
  }
};

const automationTools = [
  {
    id: "excel_reverse_engineering",
    name: "Excel Reverse Engineering",
    tier: "Advanced",
    input: "Workbook",
    output: "Formula map",
    description: "Explain formulas, dependencies, errors, logic, and workbook structure.",
    sampleInput: "Workbook has Sales, Costs, Forecast sheets. Revenue uses VLOOKUP, Margin shows #DIV/0!, and Dashboard depends on hidden lookup tables.",
    deliverables: ["Workbook structure map", "Formula explanation", "Dependency graph", "Error report", "Refactor recommendations"]
  },
  {
    id: "vendor_comparison",
    name: "Vendor Comparison",
    tier: "Advanced",
    input: "Proposals",
    output: "Recommendation",
    description: "Compare proposals, pricing, features, risks, and recommend vendors.",
    sampleInput: "Vendor A quoted INR 4,80,000 for implementation, 30 days delivery, includes support. Vendor B quoted INR 4,10,000, 45 days delivery, limited support.",
    deliverables: ["Comparison table", "Risk scoring", "Feature coverage", "Negotiation points", "Recommended vendor"]
  },
  {
    id: "government_forms",
    name: "Government Forms",
    tier: "Paid",
    input: "Business details",
    output: "Filing packet",
    description: "Generate tax, permit, compliance, and filing documents.",
    sampleInput: "Generate a permit filing packet for a small consulting business with two directors, GST registration, and annual compliance needs.",
    deliverables: ["Required forms checklist", "Draft filing data", "Supporting documents list", "Submission timeline", "Compliance reminders"]
  },
  {
    id: "data_cleanup",
    name: "Data Cleanup",
    tier: "Free plus",
    input: "Messy data",
    output: "Clean dataset",
    description: "Deduplicate, validate, normalize, and enrich business data.",
    sampleInput: "Customer file has duplicate emails, mixed phone formats, missing company names, and inconsistent state names.",
    deliverables: ["Deduplication rules", "Validation report", "Normalized fields", "Enrichment plan", "Clean export schema"]
  },
  {
    id: "excel_to_system",
    name: "Excel-to-System",
    tier: "Custom",
    input: "Spreadsheet",
    output: "App blueprint",
    description: "Convert spreadsheets into databases, workflows, dashboards, and web apps.",
    sampleInput: "Operations tracker uses Excel tabs for orders, vendors, invoices, approvals, and monthly dashboard reporting.",
    deliverables: ["Database schema", "Workflow states", "Dashboard metrics", "User roles", "Web app build plan"]
  },
  {
    id: "audit_engine",
    name: "Audit Engine",
    tier: "Advanced",
    input: "Evidence",
    output: "Audit package",
    description: "Collect evidence and generate audit-ready compliance packages.",
    sampleInput: "Need ISO audit evidence for access reviews, vendor approvals, incident logs, and policy acknowledgements.",
    deliverables: ["Evidence checklist", "Control mapping", "Gap report", "Audit index", "Reviewer-ready package"]
  },
  {
    id: "rfp_generator",
    name: "RFP Generator",
    tier: "Advanced",
    input: "Company docs",
    output: "Proposal response",
    description: "Create proposal responses from company knowledge and documents.",
    sampleInput: "Respond to an RFP for workflow automation, integrations, support SLA, implementation timeline, and security practices.",
    deliverables: ["Response outline", "Answer drafts", "Compliance matrix", "Pricing assumptions", "Submission checklist"]
  },
  {
    id: "invoice_matcher",
    name: "Invoice Matcher",
    tier: "Paid",
    input: "Invoice + PO + receipt",
    output: "Mismatch report",
    description: "Match invoices, purchase orders, and delivery receipts; flag discrepancies.",
    sampleInput: "Invoice INV-91 bills 120 units at INR 950. PO approved 100 units at INR 900. Delivery receipt shows 96 units received.",
    deliverables: ["Three-way match", "Discrepancy list", "Approval status", "Exception workflow", "Payment recommendation"]
  },
  {
    id: "process_recorder",
    name: "Process Recorder",
    tier: "Advanced",
    input: "User actions",
    output: "SOP",
    description: "Convert user actions into SOPs, workflows, training guides, and checklists.",
    sampleInput: "User logs into CRM, exports leads, cleans duplicates, assigns owners, emails summary, and updates manager tracker.",
    deliverables: ["Step-by-step SOP", "Workflow diagram", "Training guide", "Quality checklist", "Automation candidates"]
  },
  {
    id: "email_to_workflow",
    name: "Email-to-Workflow",
    tier: "Advanced",
    input: "Email thread",
    output: "Tasks",
    description: "Transform emails into tasks, approvals, tickets, and automations.",
    sampleInput: "Client asks for contract revision, finance approval, delivery date confirmation, and a support ticket for onboarding.",
    deliverables: ["Extracted tasks", "Approval routing", "Ticket fields", "Due dates", "Automation triggers"]
  },
  {
    id: "folder_to_kb",
    name: "Folder-to-Knowledge Base",
    tier: "Advanced",
    input: "Document folder",
    output: "Searchable KB",
    description: "Convert document collections into searchable knowledge systems.",
    sampleInput: "Folder contains HR policies, product FAQs, support playbooks, onboarding docs, and pricing sheets.",
    deliverables: ["Document taxonomy", "Search index plan", "Answer categories", "Permission model", "Knowledge base launch plan"]
  },
  {
    id: "contract_analyzer",
    name: "Contract Analyzer",
    tier: "Paid",
    input: "Contracts",
    output: "Obligation tracker",
    description: "Extract obligations, deadlines, risks, renewals, and compliance requirements.",
    sampleInput: "Vendor contract renews automatically in 60 days, includes 99.5% SLA, data processing clause, and termination notice period.",
    deliverables: ["Obligations", "Deadlines", "Risk clauses", "Renewal alerts", "Owner assignments"]
  },
  {
    id: "invoice_to_accounting",
    name: "Invoice-to-Accounting",
    tier: "Paid",
    input: "Invoices",
    output: "ERP entries",
    description: "Convert invoices into accounting entries and ERP-ready transactions.",
    sampleInput: "Invoice for software subscription, INR 72,000 plus GST, payable in 15 days, cost center IT-OPS.",
    deliverables: ["Ledger entries", "Tax treatment", "Cost center coding", "ERP import row", "Approval checks"]
  },
  {
    id: "sop_to_automation",
    name: "SOP-to-Automation",
    tier: "Custom",
    input: "Procedure",
    output: "Executable workflow",
    description: "Convert procedures into executable workflows and automations.",
    sampleInput: "When a new vendor is approved, collect documents, verify GST, create ERP vendor, notify finance, and schedule review.",
    deliverables: ["Workflow steps", "Automation triggers", "Required integrations", "Exception paths", "Build backlog"]
  },
  {
    id: "policy_impact_analyzer",
    name: "Policy Impact Analyzer",
    tier: "Advanced",
    input: "Policy change",
    output: "Impact map",
    description: "Identify affected teams, systems, documents, and controls.",
    sampleInput: "New data retention policy changes customer record retention from 7 years to 5 years across sales, support, and finance systems.",
    deliverables: ["Affected teams", "System impact", "Document updates", "Control changes", "Rollout checklist"]
  },
  {
    id: "activity_to_training",
    name: "Activity-to-Training",
    tier: "Advanced",
    input: "Employee activity",
    output: "Training material",
    description: "Generate onboarding and training materials from employee actions.",
    sampleInput: "Senior operations employee processes refunds, verifies approvals, updates CRM notes, and sends customer closure emails.",
    deliverables: ["Onboarding module", "Training guide", "Practice checklist", "Assessment questions", "Manager review steps"]
  }
];

let knowledgeDocs = [];

function showTool(tool) {
  $$(".tool-panel").forEach((panel) => panel.classList.remove("active"));
  $$(".tool-nav button").forEach((button) => button.classList.remove("active"));
  $(`#tool-${tool}`).classList.add("active");
  $(`[data-tool="${tool}"]`).classList.add("active");
  $("#pageTitle").textContent = $(`#tool-${tool}`).dataset.title;
}

function parseCsv(text) {
  return text.trim().split(/\r?\n/).map((line) => {
    const cells = [];
    let current = "";
    let inQuotes = false;
    for (const char of line) {
      if (char === '"') inQuotes = !inQuotes;
      else if (char === "," && !inQuotes) {
        cells.push(current.trim());
        current = "";
      } else {
        current += char;
      }
    }
    cells.push(current.trim());
    return cells;
  });
}

function normalizeHeader(value) {
  return value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "column";
}

function toCsv(rows) {
  return rows.map((row) => row.map((cell) => {
    const value = String(cell ?? "");
    return /[",\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value;
  }).join(",")).join("\n");
}

function cleanCsv() {
  const rows = parseCsv($("#csvInput").value);
  if (!rows.length) return;
  const headers = rows[0].map(normalizeHeader);
  const dedupe = $("#csvDedupe").checked;
  const seen = new Set();
  const cleanRows = [headers];
  rows.slice(1).forEach((row) => {
    const clean = headers.map((_, index) => (row[index] || "").trim());
    const key = JSON.stringify(clean);
    if (dedupe && seen.has(key)) return;
    seen.add(key);
    cleanRows.push(clean);
  });
  $("#csvOutput").value = toCsv(cleanRows);
}

function downloadText(filename, text, type = "text/plain") {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function fileCategory(name) {
  const lower = name.toLowerCase();
  const dot = lower.lastIndexOf(".");
  const ext = dot >= 0 ? lower.slice(dot) : "";
  return Object.entries(categories).find(([, values]) => values.includes(ext))?.[0] || "others";
}

function renderFileOrganizer(files) {
  const rows = Array.from(files).map((file) => `<tr><td>${escapeHtml(file.name)}</td><td>${fileCategory(file.name)}</td></tr>`);
  $("#fileOrganizerRows").innerHTML = rows.join("") || "<tr><td colspan=\"2\">No files selected.</td></tr>";
}

function extractData() {
  const text = $("#extractInput").value;
  const patterns = {
    invoice_number: /invoice\s*(?:number|no|#)\s*[:\-]?\s*([A-Z0-9\-\/]+)/i,
    date: /\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})\b/i,
    total: /(?:total|amount due|grand total)\s*[:\-]?\s*(?:rs\.?|inr|\$)?\s*([0-9,]+(?:\.\d{2})?)/i,
    email: /[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}/i,
    phone: /(?:\+?\d[\d\s\-()]{7,}\d)/i
  };
  const result = {};
  Object.entries(patterns).forEach(([key, pattern]) => {
    const match = text.match(pattern);
    if (match) result[key] = match[1] || match[0];
  });
  $("#extractOutput").textContent = JSON.stringify(result, null, 2);
}

function hrSkills() {
  return $("#hrSkills").value.split(",").map((skill) => skill.trim()).filter(Boolean);
}

function generateHrOutput(type) {
  const role = $("#hrRole").value.trim() || "Team Member";
  const level = $("#hrLevel").value.trim() || "Mid-level";
  const skills = hrSkills();
  if (type === "jd") {
    $("#hrOutput").textContent = `# ${level} ${role}

Responsibilities:
- Own day-to-day ${role} workstreams
- Collaborate with stakeholders
- Track progress and communicate risks
- Improve process quality

Required skills:
- ${skills.join("\n- ")}
- Clear communication
- Strong ownership`;
  }
  if (type === "questions") {
    const questions = [
      `Tell us about your experience as a ${role}.`,
      "Describe a difficult project and how you handled it.",
      "How do you prioritize urgent work?",
      ...skills.map((skill) => `How have you used ${skill} in a real work situation?`)
    ];
    $("#hrOutput").textContent = questions.map((item, index) => `${index + 1}. ${item}`).join("\n");
  }
  if (type === "evaluation") {
    $("#hrOutput").textContent = `Employee Evaluation: ${role}

Job Knowledge: /5
Quality of Work: /5
Productivity: /5
Communication: /5
Teamwork: /5
Ownership: /5

Achievements:
-

Improvement Areas:
-

Goals:
-`;
  }
}

function parseResume() {
  const text = $("#resumeText").value;
  const email = text.match(/[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}/)?.[0] || "";
  const phone = text.match(/(?:\+?\d[\d\s\-()]{7,}\d)/)?.[0] || "";
  const skills = ["python", "excel", "sql", "power bi", "tableau", "react", "sales", "communication"].filter((skill) => text.toLowerCase().includes(skill));
  const years = text.match(/(\d+)\+?\s*(?:years|yrs)/i)?.[1] || "0";
  $("#hrOutput").textContent = JSON.stringify({ email, phone, skills, estimated_years_experience: Number(years) }, null, 2);
}

function buildInvoice() {
  const items = $("#invoiceItems").value.split(/\r?\n/).filter(Boolean).map((line) => {
    const [description, quantity, unitPrice] = line.split("|").map((part) => part.trim());
    return { description, quantity: Number(quantity || 1), unitPrice: Number(unitPrice || 0) };
  });
  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
  const tax = subtotal * Number($("#taxRate").value || 0);
  const total = subtotal + tax;
  $("#invoicePreview").innerHTML = `<header><div><h4>Invoice</h4><p>${escapeHtml($("#invoiceNo").value)}</p></div><strong>${escapeHtml($("#bizName").value)}</strong></header>
    <p><strong>Bill To:</strong> ${escapeHtml($("#clientName").value)}</p>
    <table><thead><tr><th>Description</th><th>Qty</th><th>Unit</th><th>Total</th></tr></thead><tbody>
    ${items.map((item) => `<tr><td>${escapeHtml(item.description)}</td><td>${item.quantity}</td><td>${money(item.unitPrice)}</td><td>${money(item.quantity * item.unitPrice)}</td></tr>`).join("")}
    </tbody></table>
    <p><strong>Subtotal:</strong> ${money(subtotal)}<br><strong>Tax:</strong> ${money(tax)}<br><strong>Total:</strong> ${money(total)}</p>`;
}

function generateEmail() {
  const name = $("#emailName").value;
  const company = $("#emailCompany").value;
  const topic = $("#emailTopic").value;
  const sender = $("#emailSender").value;
  const template = emailTemplates[$("#emailTemplate").value];
  const replaceVars = (text) => text.replaceAll("{name}", name).replaceAll("{company}", company).replaceAll("{topic}", topic).replaceAll("{sender}", sender);
  $("#emailOutput").textContent = `Subject: ${replaceVars(template.subject)}\n\n${replaceVars(template.body)}`;
}

async function loadKnowledgeFiles(files) {
  knowledgeDocs = [];
  for (const file of files) {
    knowledgeDocs.push({ name: file.name, text: await file.text() });
  }
  $("#knowledgeOutput").textContent = `${knowledgeDocs.length} document(s) loaded. Ask a question.`;
}

function askKnowledge() {
  const query = tokenize($("#knowledgeQuestion").value);
  const chunks = knowledgeDocs.flatMap((doc) => chunk(doc.text).map((text) => ({ source: doc.name, text })));
  const ranked = chunks.map((item) => ({ ...item, score: score(query, tokenize(item.text)) })).sort((a, b) => b.score - a.score).slice(0, 3);
  const relevant = ranked.filter((item) => item.score > 0);
  $("#knowledgeOutput").textContent = relevant.length
    ? relevant.map((item, index) => `${index + 1}. Source: ${item.source}\n${item.text.slice(0, 700)}`).join("\n\n")
    : "No relevant answer found in uploaded documents.";
}

function estimateCustom() {
  const brief = $("#customBrief").value;
  const wordCount = brief.split(/\s+/).filter(Boolean).length;
  const complexity = wordCount > 35 ? "Advanced" : wordCount > 18 ? "Medium" : "Simple";
  const base = complexity === "Advanced" ? 499 : complexity === "Medium" ? 249 : 99;
  $("#customOutput").textContent = JSON.stringify({
    tool_name: $("#customName").value,
    visibility: $("#customVisibility").value,
    estimated_complexity: complexity,
    suggested_setup_price_usd: base,
    platform_fee_model: $("#customVisibility").value === "Public marketplace" ? "Small platform fee on each paid usage" : "Private monthly hosting fee"
  }, null, 2);
}

function renderAutomationTools() {
  const select = $("#automationTool");
  const cards = $("#automationCards");
  select.innerHTML = automationTools.map((tool) => `<option value="${tool.id}">${tool.name}</option>`).join("");
  cards.innerHTML = automationTools.map((tool) => `<button class="automation-card" type="button" data-automation-id="${tool.id}">
    <strong>${escapeHtml(tool.name)}</strong>
    <p>${escapeHtml(tool.description)}</p>
    <div class="meta-row">
      <span class="meta-chip">${escapeHtml(tool.tier)}</span>
      <span class="meta-chip">${escapeHtml(tool.input)}</span>
      <span class="meta-chip">${escapeHtml(tool.output)}</span>
    </div>
  </button>`).join("");
  cards.querySelectorAll("[data-automation-id]").forEach((card) => {
    card.addEventListener("click", () => {
      select.value = card.dataset.automationId;
      syncAutomationTool(true);
    });
  });
  syncAutomationTool(true);
}

function syncAutomationTool(useSample = false) {
  const selected = automationTools.find((tool) => tool.id === $("#automationTool").value) || automationTools[0];
  $$(".automation-card").forEach((card) => card.classList.toggle("active", card.dataset.automationId === selected.id));
  if (useSample) {
    $("#automationInput").value = selected.sampleInput;
  }
}

function generateAutomationOutput() {
  const selected = automationTools.find((tool) => tool.id === $("#automationTool").value) || automationTools[0];
  const input = $("#automationInput").value.trim();
  const keywords = Array.from(new Set(tokenize(input))).slice(0, 12);
  const complexity = input.length > 450 ? "High" : input.length > 180 ? "Medium" : "Simple";
  const result = {
    tool: selected.name,
    tier: selected.tier,
    purpose: selected.description,
    detected_input_type: selected.input,
    target_output: selected.output,
    complexity,
    extracted_keywords: keywords,
    generated_deliverables: selected.deliverables,
    recommended_workflow: [
      "Collect source input and supporting documents",
      "Extract entities, dates, amounts, owners, risks, and decisions",
      "Validate missing or conflicting information",
      "Generate structured output for review",
      "Route approvals or exceptions",
      "Export to dashboard, document, workflow, or system integration"
    ],
    automation_opportunities: [
      "Reusable intake form",
      "Template-based output generation",
      "Approval routing",
      "Exception alerts",
      "Export to CSV, JSON, PDF, or API"
    ],
    pricing_hint: selected.tier === "Custom"
      ? "Quote based on integrations, workflow complexity, and private/public marketplace choice"
      : selected.tier === "Free plus"
        ? "Free basic cleanup with paid batch processing and enrichment"
        : "Paid advanced tool with usage limits, workspace history, and exports"
  };
  $("#automationOutput").textContent = JSON.stringify(result, null, 2);
}

function tokenize(text) {
  return text.toLowerCase().match(/[a-z0-9]{3,}/g) || [];
}

function chunk(text) {
  const parts = text.split(/\n\s*\n/).map((item) => item.trim()).filter(Boolean);
  return parts.length ? parts : [text.slice(0, 1200)];
}

function score(queryTokens, textTokens) {
  const textSet = new Set(textTokens);
  return queryTokens.reduce((total, token) => total + (textSet.has(token) ? 1 : 0), 0);
}

function money(value) {
  return Number(value || 0).toFixed(2);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

$$(".tool-nav button").forEach((button) => button.addEventListener("click", () => showTool(button.dataset.tool)));
$("#cleanCsvBtn").addEventListener("click", cleanCsv);
$("#downloadCsvBtn").addEventListener("click", () => downloadText("clean.csv", $("#csvOutput").value, "text/csv"));
$("#fileOrganizerInput").addEventListener("change", (event) => renderFileOrganizer(event.target.files));
$("#extractBtn").addEventListener("click", extractData);
$("#downloadExtractBtn").addEventListener("click", () => downloadText("extracted_data.json", $("#extractOutput").textContent, "application/json"));
$$("[data-hr-action]").forEach((button) => button.addEventListener("click", () => generateHrOutput(button.dataset.hrAction)));
$("#parseResumeBtn").addEventListener("click", parseResume);
$("#buildInvoiceBtn").addEventListener("click", buildInvoice);
$("#generateEmailBtn").addEventListener("click", generateEmail);
$("#copyEmailBtn").addEventListener("click", () => navigator.clipboard.writeText($("#emailOutput").textContent));
$("#knowledgeFiles").addEventListener("change", (event) => loadKnowledgeFiles(event.target.files));
$("#askKnowledgeBtn").addEventListener("click", askKnowledge);
$("#estimateCustomBtn").addEventListener("click", estimateCustom);
$("#automationTool").addEventListener("change", () => syncAutomationTool(true));
$("#runAutomationBtn").addEventListener("click", generateAutomationOutput);
$("#downloadAutomationBtn").addEventListener("click", () => downloadText("automation_output.json", $("#automationOutput").textContent, "application/json"));

renderAutomationTools();
cleanCsv();
extractData();
generateHrOutput("jd");
buildInvoice();
generateEmail();
estimateCustom();
generateAutomationOutput();

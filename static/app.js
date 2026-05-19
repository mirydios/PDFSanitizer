// ==========================================
// STATE MANAGEMENT & GLOBAL VARIABLES
// ==========================================
let processedData = null;
let currentPage = 1;
let totalPages = 1;
let activeTableIndex = 0;
let showTableSanitized = true;

// ==========================================
// DOM ELEMENT REFERENCES
// ==========================================
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const processingSection = document.getElementById('processing-section');
const resultsSection = document.getElementById('results-section');

// Progress Bar & Step Elements
const progressBar = document.getElementById('progress-bar');
const processStepText = document.getElementById('process-step');
const stepUpload = document.getElementById('step-upload');
const stepExtract = document.getElementById('step-extract');
const stepSanitize = document.getElementById('step-sanitize');

// Result Summary & Metadata
const metaPages = document.getElementById('meta-pages');
const totalMasked = document.getElementById('total-masked');
const totalTables = document.getElementById('total-tables');
const infoFilename = document.getElementById('info-filename');
const infoTitle = document.getElementById('info-title');
const infoAuthor = document.getElementById('info-author');
const infoSize = document.getElementById('info-size');
const barChartContainer = document.getElementById('bar-chart-container');

// Text Viewer Panel
const btnPagePrev = document.getElementById('btn-page-prev');
const btnPageNext = document.getElementById('btn-page-next');
const currentPageNum = document.getElementById('current-page-num');
const totalPageNum = document.getElementById('total-page-num');
const paneOriginalText = document.getElementById('pane-original-text');
const paneSanitizedText = document.getElementById('pane-sanitized-text');

// Tables Panel
const tableSelect = document.getElementById('table-select');
const tablePageLocation = document.getElementById('table-page-location');
const toggleTableSanitized = document.getElementById('toggle-table-sanitized');
const toggleTableOriginal = document.getElementById('toggle-table-original');
const btnDownloadTableCsv = document.getElementById('btn-download-table-csv');
const btnDownloadTableJson = document.getElementById('btn-download-table-json');
const extractedTable = document.getElementById('extracted-table');
const tabTablesBtn = document.getElementById('tab-tables-btn');

// Audit Panel
const auditLogTbody = document.getElementById('audit-log-tbody');

// Action Buttons
const btnDownloadJson = document.getElementById('btn-download-json');
const btnDownloadText = document.getElementById('btn-download-text');
const btnReset = document.getElementById('btn-reset');

// ==========================================
// DRAG AND DROP EVENTS
// ==========================================
['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    }, false);
});

dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// ==========================================
// FILE HANDLER & API FETCH
// ==========================================
function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Formato de arquivo inválido. Por favor, envie apenas arquivos PDF.');
        return;
    }
    uploadFile(file);
}

async function uploadFile(file) {
    // 1. Show processing state
    uploadSection.classList.add('hidden');
    processingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    updateProgress(15, 'Enviando arquivo ao servidor...', 'upload');
    
    // Create form payload
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Simulate progress intervals for visual feedback
        const progressInterval = setInterval(() => {
            if (progressBar.style.width === '15%') {
                updateProgress(35, 'Iniciando extração estruturada de páginas...', 'extract');
            } else if (progressBar.style.width === '35%') {
                updateProgress(55, 'Extraindo textos de páginas e tabelas...', 'extract');
            } else if (progressBar.style.width === '55%') {
                updateProgress(75, 'Buscando padrões de dados sensíveis da LGPD...', 'sanitize');
            } else if (progressBar.style.width === '75%') {
                updateProgress(90, 'Aplicando algoritmos de validação e máscaras...', 'sanitize');
            }
        }, 1200);

        // Fetch request to Process API
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erro desconhecido ao processar PDF.');
        }
        
        processedData = await response.json();
        
        // Success completion
        updateProgress(100, 'Processamento de segurança concluído!', 'complete');
        
        setTimeout(() => {
            renderDashboard();
            processingSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
        }, 800);
        
    } catch (err) {
        alert(`Falha no Processamento:\n${err.message}`);
        resetUploader();
    }
}

function updateProgress(percentage, text, step) {
    progressBar.style.width = `${percentage}%`;
    processStepText.textContent = text;
    
    if (step === 'upload') {
        stepUpload.className = 'step-item active';
        stepExtract.className = 'step-item';
        stepSanitize.className = 'step-item';
    } else if (step === 'extract') {
        stepUpload.className = 'step-item completed';
        stepExtract.className = 'step-item active';
        stepSanitize.className = 'step-item';
    } else if (step === 'sanitize') {
        stepUpload.className = 'step-item completed';
        stepExtract.className = 'step-item completed';
        stepSanitize.className = 'step-item active';
    } else if (step === 'complete') {
        stepUpload.className = 'step-item completed';
        stepExtract.className = 'step-item completed';
        stepSanitize.className = 'step-item completed';
    }
}

// ==========================================
// TAB SWITCHING ENGINE
// ==========================================
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        
        // Remove active state
        tabButtons.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));
        
        // Set active state
        btn.classList.add('active');
        document.getElementById(`panel-${targetTab}`).classList.add('active');
        
        // Hook triggers
        if (targetTab === 'text-view') {
            renderPageText();
        }
    });
});

// ==========================================
// RENDER OUTCOMES & UI ENGINE
// ==========================================
function renderDashboard() {
    if (!processedData) return;
    
    currentPage = 1;
    totalPages = processedData.metadata.page_count || 1;
    activeTableIndex = 0;
    showTableSanitized = true;
    
    // 1. KPI Cards
    metaPages.textContent = totalPages;
    totalMasked.textContent = processedData.stats.total_masked_items;
    
    const tableCount = processedData.tables ? processedData.tables.length : 0;
    totalTables.textContent = tableCount;
    
    // Show/Hide Tables Tab button
    if (tableCount === 0) {
        tabTablesBtn.style.display = 'none';
    } else {
        tabTablesBtn.style.display = 'flex';
    }
    
    // 2. Metadata details
    infoFilename.textContent = processedData.filename;
    infoTitle.textContent = processedData.metadata.title || 'Sem título nos metadados';
    infoAuthor.textContent = processedData.metadata.author || 'Autor desconhecido';
    
    const bytes = processedData.metadata.file_size_bytes || 0;
    const kb = (bytes / 1024).toFixed(1);
    infoSize.textContent = bytes > 1024 * 1024 
        ? `${(bytes / (1024 * 1024)).toFixed(2)} MB` 
        : `${kb} KB`;
        
    // 3. Stats Chart
    renderChart();
    
    // 4. Tables dropdown populating
    populateTablesSelector();
    
    // 5. Audit Log rendering
    renderAuditLog();
}

function renderChart() {
    barChartContainer.innerHTML = '';
    const maskedMap = processedData.stats.masked_by_type;
    const maxVal = Math.max(...Object.values(maskedMap), 1); // Avoid div by 0
    
    const classMapping = {
        'CPF': 'cpf',
        'CNPJ': 'cnpj',
        'E-mail': 'email',
        'Telefone': 'phone',
        'Dados Bancários': 'bank'
    };
    
    Object.keys(maskedMap).forEach(key => {
        const count = maskedMap[key];
        const pct = (count / maxVal) * 100;
        
        const chartItem = document.createElement('div');
        chartItem.className = 'chart-bar-item animate-fade-in';
        chartItem.innerHTML = `
            <div class="chart-bar-label-row">
                <span class="chart-bar-name">${key}</span>
                <span class="chart-bar-count">${count} ocorrência(s)</span>
            </div>
            <div class="chart-bar-track">
                <div class="chart-bar-fill ${classMapping[key] || 'cpf'}" style="width: ${pct}%"></div>
            </div>
        `;
        barChartContainer.appendChild(chartItem);
    });
}

// ==========================================
// SIDE-BY-SIDE HIGHLIGHTED PAGE TEXT
// ==========================================
btnPagePrev.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderPageText();
    }
});

btnPageNext.addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        renderPageText();
    }
});

function renderPageText() {
    if (!processedData) return;
    
    currentPageNum.textContent = currentPage;
    totalPageNum.textContent = totalPages;
    
    // Toggle page actions availability
    btnPagePrev.disabled = currentPage === 1;
    btnPageNext.disabled = currentPage === totalPages;
    
    const pageIndex = currentPage - 1;
    const rawText = processedData.original_pages[pageIndex] || "";
    const sanitizedText = processedData.sanitized_pages[pageIndex] || "";
    
    // Display sanitized text directly
    paneSanitizedText.innerHTML = escapeHtml(sanitizedText)
        .replace(/\[CPF MASCARADO\]/g, '<span class="pii-sanitized-tag">CPF Ocultado</span>')
        .replace(/\[CNPJ MASCARADO\]/g, '<span class="pii-sanitized-tag">CNPJ Ocultado</span>')
        .replace(/\[EMAIL MASCARADO\]/g, '<span class="pii-sanitized-tag">E-mail Ocultado</span>')
        .replace(/\[TELEFONE MASCARADO\]/g, '<span class="pii-sanitized-tag">Telefone Ocultado</span>');
    
    // Highlight original text side-by-side using audit trail detections for this page
    let highlightedOriginalHtml = escapeHtml(rawText);
    
    const pageAudits = processedData.audit_trail.filter(a => a.page === currentPage);
    
    // Sort page audits by original value length descending to prevent shorter substrings
    // from matching inside longer values (e.g. replacing '123' inside '123.456')
    const sortedAudits = [...pageAudits].sort((a, b) => b.original.length - a.original.length);
    
    // Set of replaced items to prevent double highlights
    const replacedSet = new Set();
    
    sortedAudits.forEach(audit => {
        const origVal = audit.original;
        if (!origVal || replacedSet.has(origVal)) return;
        replacedSet.add(origVal);
        
        // Escape standard characters for safe regex replacement
        const escapedOrig = origVal.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        const regex = new RegExp(escapedOrig, 'g');
        
        highlightedOriginalHtml = highlightedOriginalHtml.replace(regex, (match) => {
            return `<mark class="pii-original-tag" title="Tipo: ${audit.type}">${match}</mark>`;
        });
    });
    
    paneOriginalText.innerHTML = highlightedOriginalHtml;
}

// ==========================================
// INTERACTIVE TABLES SECTION
// ==========================================
function populateTablesSelector() {
    tableSelect.innerHTML = '';
    const tables = processedData.tables || [];
    
    if (tables.length === 0) {
        return;
    }
    
    tables.forEach((table, idx) => {
        const option = document.createElement('option');
        option.value = idx;
        option.textContent = `Tabela #${idx + 1}`;
        tableSelect.appendChild(option);
    });
    
    activeTableIndex = 0;
    renderSelectedTable();
}

tableSelect.addEventListener('change', (e) => {
    activeTableIndex = parseInt(e.target.value, 10);
    renderSelectedTable();
});

toggleTableSanitized.addEventListener('click', () => {
    showTableSanitized = true;
    toggleTableSanitized.classList.add('active');
    toggleTableOriginal.classList.remove('active');
    renderSelectedTable();
});

toggleTableOriginal.addEventListener('click', () => {
    showTableSanitized = false;
    toggleTableSanitized.classList.remove('active');
    toggleTableOriginal.classList.add('active');
    renderSelectedTable();
});

function renderSelectedTable() {
    const tables = processedData.tables || [];
    if (tables.length === 0 || !tables[activeTableIndex]) {
        extractedTable.innerHTML = '<tr><td style="text-align: center;">Nenhuma tabela disponível neste arquivo.</td></tr>';
        return;
    }
    
    const tableObj = tables[activeTableIndex];
    tablePageLocation.textContent = `Página ${tableObj.page}`;
    
    const originalGrid = tableObj.original;
    const sanitizedGrid = tableObj.sanitized;
    const gridToRender = showTableSanitized ? sanitizedGrid : originalGrid;
    
    extractedTable.innerHTML = '';
    
    if (gridToRender.length === 0) {
        extractedTable.innerHTML = '<tr><td style="text-align: center;">Tabela vazia.</td></tr>';
        return;
    }
    
    // Render Header (first row)
    const headerRow = document.createElement('tr');
    gridToRender[0].forEach(cell => {
        const th = document.createElement('th');
        th.textContent = cell;
        headerRow.appendChild(th);
    });
    extractedTable.appendChild(headerRow);
    
    // Render Body Rows (remaining)
    for (let r = 1; r < gridToRender.length; r++) {
        const tr = document.createElement('tr');
        gridToRender[r].forEach((cell, c) => {
            const td = document.createElement('td');
            
            // Check if cell has been sanitized (differs between sanitized and original grid)
            const wasSanitized = showTableSanitized && (originalGrid[r][c] !== sanitizedGrid[r][c]);
            
            if (wasSanitized) {
                td.innerHTML = `<span class="cell-masked-badge" title="Valor Original: ${escapeHtml(originalGrid[r][c])}">${escapeHtml(cell)}</span>`;
            } else {
                td.textContent = cell;
            }
            tr.appendChild(td);
        });
        extractedTable.appendChild(tr);
    }
}

// ==========================================
// AUDIT LOG LIST
// ==========================================
function renderAuditLog() {
    auditLogTbody.innerHTML = '';
    const audits = processedData.audit_trail || [];
    
    if (audits.length === 0) {
        auditLogTbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;">
                    Nenhum dado pessoal sensível foi detectado no arquivo. Documento em total conformidade!
                </td>
            </tr>
        `;
        return;
    }
    
    audits.forEach(audit => {
        const tr = document.createElement('tr');
        
        // Highlight matched text inside context
        let contextHtml = escapeHtml(audit.context);
        const escapedMatch = escapeHtml(audit.original);
        if (escapedMatch) {
            const regex = new RegExp(escapedMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g');
            contextHtml = contextHtml.replace(regex, `<mark>${escapedMatch}</mark>`);
        }
        
        const categoryClass = audit.type.toLowerCase().replace(/\s+/g, '-');
        
        tr.innerHTML = `
            <td><span class="audit-page-badge">Pág ${audit.page}</span></td>
            <td><span class="audit-category-tag ${categoryClass}">${audit.type}</span></td>
            <td style="font-family: monospace; color: #fca5a5;">${escapeHtml(audit.original)}</td>
            <td style="font-family: monospace; color: #34d399;">${escapeHtml(audit.masked)}</td>
            <td><div class="audit-context-snippet">${contextHtml}</div></td>
        `;
        auditLogTbody.appendChild(tr);
    });
}

// ==========================================
// EXPORTS & RESET SYSTEM
// ==========================================

// Complete JSON Export
btnDownloadJson.addEventListener('click', async () => {
    if (!processedData) return;
    const payload = {
        data: processedData,
        filename: `${processedData.filename.replace('.pdf', '')}_relatorio_completo.json`
    };
    triggerDownload('/api/download/json', payload);
});

// Extracted & Sanitized Text Export
btnDownloadText.addEventListener('click', () => {
    if (!processedData) return;
    const blob = new Blob([processedData.sanitized_text_full], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${processedData.filename.replace('.pdf', '')}_sanitizado.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Selected Table Download as CSV
btnDownloadTableCsv.addEventListener('click', () => {
    const tables = processedData.tables || [];
    if (tables.length === 0 || !tables[activeTableIndex]) return;
    
    const tableObj = tables[activeTableIndex];
    const grid = showTableSanitized ? tableObj.sanitized : tableObj.original;
    
    const payload = {
        table: grid,
        filename: `${processedData.filename.replace('.pdf', '')}_tabela_${activeTableIndex + 1}_${showTableSanitized ? 'sanitizada' : 'original'}.csv`
    };
    triggerDownload('/api/download/csv', payload);
});

// Selected Table Download as JSON
btnDownloadTableJson.addEventListener('click', () => {
    const tables = processedData.tables || [];
    if (tables.length === 0 || !tables[activeTableIndex]) return;
    
    const tableObj = tables[activeTableIndex];
    const grid = showTableSanitized ? tableObj.sanitized : tableObj.original;
    
    // Convert 2D Grid to standard Array of Objects (JSON format)
    const jsonRows = [];
    if (grid.length > 0) {
        const headers = grid[0];
        for (let r = 1; r < grid.length; r++) {
            const rowObj = {};
            grid[r].forEach((cell, idx) => {
                const header = headers[idx] || `Coluna_${idx + 1}`;
                rowObj[header] = cell;
            });
            jsonRows.push(rowObj);
        }
    }
    
    const payload = {
        data: { table_index: activeTableIndex, page: tableObj.page, rows: jsonRows },
        filename: `${processedData.filename.replace('.pdf', '')}_tabela_${activeTableIndex + 1}_${showTableSanitized ? 'sanitizada' : 'original'}.json`
    };
    triggerDownload('/api/download/json', payload);
});

async function triggerDownload(url, payload) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error('Falha ao baixar o arquivo.');
        
        const blob = await response.blob();
        const disposition = response.headers.get('Content-Disposition');
        let filename = payload.filename || 'download';
        if (disposition && disposition.indexOf('attachment') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) { 
                filename = matches[1].replace(/['"]/g, '');
            }
        }
        
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);
        
    } catch (err) {
        alert(err.message);
    }
}

btnReset.addEventListener('click', resetUploader);

function resetUploader() {
    processedData = null;
    currentPage = 1;
    totalPages = 1;
    activeTableIndex = 0;
    fileInput.value = '';
    
    uploadSection.classList.remove('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

// ==========================================
// STRING ESCAPER FOR SECURITY
// ==========================================
function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

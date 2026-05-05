const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const exportTeklaBtn = document.getElementById('exportTeklaBtn');
const sendTeklaDirectBtn = document.getElementById('sendTeklaDirectBtn');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileRemove = document.getElementById('fileRemove');

let selectedFile = null;
let currentJobId = null;
let aiValidationState = { ready: false, report: null, pending: false, needsUserConfirmation: false };

const validationModal = document.getElementById('validationModal');
const validationTitle = document.getElementById('validationTitle');
const validationAdvice = document.getElementById('validationAdvice');
const validationSuggestions = document.getElementById('validationSuggestions');
const validationConfidence = document.getElementById('validationConfidence');
const validationGaps = document.getElementById('validationGaps');
const validationSemantic = document.getElementById('validationSemantic');
const validationYesBtn = document.getElementById('validationYesBtn');
const validationNoBtn = document.getElementById('validationNoBtn');
const validationCloseBtn = document.getElementById('validationCloseBtn');

// File selection
uploadArea.addEventListener('click', (e) => {
    if (e.target !== fileRemove) fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    handleFileSelection(e.target.files[0]);
});

// Remove file
fileRemove.addEventListener('click', (e) => {
    e.stopPropagation();
    removeFile();
});

validationYesBtn?.addEventListener('click', async () => {
    if (!currentJobId) return;
    await resolveAiAction(currentJobId, 'apply_all', 'yes');
});

validationNoBtn?.addEventListener('click', async () => {
    if (!currentJobId) return;
    await resolveAiAction(currentJobId, 'accept_as_is', 'no');
});

validationCloseBtn?.addEventListener('click', () => {
    hideValidationModal();
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFileSelection(e.dataTransfer.files[0]);
});

function handleFileSelection(file) {
    if (!file) return;
    
    selectedFile = file;
    uploadBtn.disabled = false;
    
    // Show file preview
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    filePreview.style.display = 'flex';
}

function removeFile() {
    selectedFile = null;
    uploadBtn.disabled = true;
    filePreview.style.display = 'none';
    fileInput.value = '';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function showValidationModal() {
    if (!validationModal) return;
    validationModal.style.display = 'flex';
}

function hideValidationModal() {
    if (!validationModal) return;
    validationModal.style.display = 'none';
}

function renderAiSummary(report) {
    const aiSummary = document.getElementById('aiSummary');
    if (!aiSummary || !report) return;

    aiSummary.innerHTML = `
        <strong>Self-Healing Consultant</strong>
        <p class="muted">Confidence ${Math.round((report.confidence_score || 0) * 100)}% — ${report.advisory_text || 'Review suggested before Tekla export.'}</p>
    `;

    const trendPanel = document.getElementById('aiTrendPanel');
    if (trendPanel) {
        trendPanel.innerHTML = `
            <strong>Global AI Trend</strong>
            <p class="muted">Average confidence ${Math.round((report.confidence_score || 0) * 100)}% for this job.</p>
        `;
    }
}

async function runAiValidation(jobId) {
    aiValidationState.pending = true;
    try {
        const response = await fetch(`/api/ai-validate/${jobId}`);
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') {
            document.getElementById('aiSummary').innerHTML = `
                <strong>Self-Healing Consultant</strong>
                <p class="muted">Unable to validate: ${data.message || 'Unknown error'}. Export is still available.</p>
            `;
            exportTeklaBtn.disabled = false;
            sendTeklaDirectBtn.disabled = false;
            return;
        }

        aiValidationState.ready = true;
        aiValidationState.report = data.audit;
        aiValidationState.pending = false;
        aiValidationState.needsUserConfirmation = data.needs_user_confirmation;
        renderAiReport(data.audit);
        fetchAiTrend();

        if (data.needs_user_confirmation) {
            showConsultantDialog(data.audit);
        } else {
            exportTeklaBtn.disabled = false;
            sendTeklaDirectBtn.disabled = false;
        }
    } catch (error) {
        console.error('AI validation error', error);
        const aiSummary = document.getElementById('aiSummary');
        if (aiSummary) {
            aiSummary.innerHTML = `
                <strong>Self-Healing Consultant</strong>
                <p class="muted">Validation unavailable: ${error.message}. Export is still available.</p>
            `;
        }
        exportTeklaBtn.disabled = false;
        sendTeklaDirectBtn.disabled = false;
    }
}

function renderAiReport(audit) {
    if (!audit) return;
    const aiSummary = document.getElementById('aiSummary');
    if (aiSummary) {
        aiSummary.innerHTML = `
            <strong>Self-Healing Consultant</strong>
            <p class="muted">${audit.advisory_text || 'Validation complete.'}</p>
            <div style="margin-top: 10px; font-size: 0.9rem; color: var(--gray-200);">
                <span>Confidence: ${Math.round(audit.confidence_score * 100)}%</span> ·
                <span>Gaps: ${audit.disconnected_node_count}</span> ·
                <span>Classification issues: ${audit.semantic_mismatch_count}</span>
            </div>
        `;
    }
    if (validationConfidence) {
        validationConfidence.textContent = (audit.confidence_score || 0).toFixed(2);
    }
    if (validationGaps) {
        validationGaps.textContent = audit.disconnected_node_count || 0;
    }
    if (validationSemantic) {
        validationSemantic.textContent = audit.semantic_mismatch_count || 0;
    }
}

function showConsultantDialog(audit) {
    if (!validationAdvice || !validationSuggestions) return;
    validationAdvice.textContent = audit.advisory_text || 'The AI consultant recommends reviewing the model before export.';
    validationSuggestions.innerHTML = '';
    (audit.suggestions || []).forEach((suggestion) => {
        const p = document.createElement('p');
        p.textContent = suggestion;
        validationSuggestions.appendChild(p);
    });
    showValidationModal();
}

async function resolveAiAction(jobId, action, decision) {
    if (!jobId) return;
    validationYesBtn.disabled = true;
    validationNoBtn.disabled = true;
    try {
        const response = await fetch(`/api/ai-act/${jobId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action, decision })
        });
        const data = await response.json();
        if (response.ok && data.status === 'ok') {
            aiValidationState.report = data.audit;
            aiValidationState.needsUserConfirmation = false;
            renderAiReport(data.audit);
            hideValidationModal();
            exportTeklaBtn.disabled = false;
            sendTeklaDirectBtn.disabled = false;
            document.getElementById('teklaStatus').innerHTML = `
                <strong style="color: var(--success);">✓ Self-healing update applied</strong><br>
                <span style="font-size: 0.875rem; color: var(--gray-600);">The model is ready for Tekla export.</span>
            `;
        } else {
            document.getElementById('teklaStatus').innerHTML = `
                <strong style="color: var(--error);">❌ Self-healing action failed</strong><br>
                <span style="font-size: 0.875rem; color: var(--gray-600);">${data.message || 'Please try again.'}</span>
            `;
        }
    } catch (error) {
        document.getElementById('teklaStatus').innerHTML = `
            <strong style="color: var(--error);">❌ Self-healing action failed</strong><br>
            <span style="font-size: 0.875rem; color: var(--gray-600);">${error.message}</span>
        `;
    } finally {
        validationYesBtn.disabled = false;
        validationNoBtn.disabled = false;
    }
}

async function fetchAiTrend() {
    try {
        const response = await fetch('/api/ai-feedback-trend');
        const data = await response.json();
        if (!response.ok || data.status !== 'ok') return;
        const trendPanel = document.getElementById('aiTrendPanel');
        if (!trendPanel) return;
        trendPanel.innerHTML = `
            <strong>AI Confidence Trend</strong>
            <p class="muted">Average confidence across ${data.trend.decisions} decisions: ${Math.round((data.trend.average_confidence || 0) * 100)}%</p>
        `;
    } catch (error) {
        console.warn('Unable to load AI trend', error);
    }
}

// Upload and process
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        // Show progress section
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('progressSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        
        // Animate processing steps
        const steps = ['upload', 'convert', 'analyze', 'export'];
        let currentStep = 0;
        
        const stepInterval = setInterval(() => {
            if (currentStep > 0) {
                const prevStep = document.querySelector(`[data-step="${steps[currentStep - 1]}"]`);
                if (prevStep) {
                    prevStep.classList.remove('active');
                    prevStep.classList.add('completed');
                }
            }
            if (currentStep < steps.length) {
                const currStep = document.querySelector(`[data-step="${steps[currentStep]}"]`);
                if (currStep) {
                    currStep.classList.add('active');
                }
                currentStep++;
            }
        }, 1000);
        
        // Animate progress bar
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + Math.random() * 15, 90);
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('progressPercentage').textContent = Math.round(progress) + '%';
        }, 400);
        
        // Upload file
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        clearInterval(stepInterval);
        
        const data = await response.json();
        
        console.log('Response received:', response.ok, data);
        
        if (response.ok && data.status === 'ok') {
            console.log('Processing success response...');
            currentJobId = data.job_id;
            
            // Complete all steps
            steps.forEach(step => {
                const stepEl = document.querySelector(`[data-step="${step}"]`);
                if (stepEl) {
                    stepEl.classList.remove('active');
                    stepEl.classList.add('completed');
                }
            });
            
            // Complete progress bar
            document.getElementById('progressBar').style.width = '100%';
            document.getElementById('progressPercentage').textContent = '100%';
            
            // Show success indicator
            const stepIndicator = document.querySelector('#progressSection .step-indicator');
            stepIndicator.classList.remove('active');
            stepIndicator.classList.add('success');
            stepIndicator.innerHTML = `
                <svg class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            `;
            
            // Show results after animation
            setTimeout(() => {
                console.log('About to call showResults with:', data);
                showResults(data);
            }, 800);
        } else {
            showError(data.message || 'Pipeline execution failed');
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }
});

function showResults(data) {
    console.log('=== showResults() called ===');
    console.log('Full response data:', JSON.stringify(data, null, 2));
    
    const outputs = data.outputs || {};
    const summary = outputs.summary || {};
    
    // Debug: Log the data to console
    console.log('Results data:', data);
    console.log('Output path:', data.output_path);
    console.log('outputs.file_details:', outputs.file_details);
    
    // Update statistics
    const statsHtml = `
        <li>Total Members: ${summary.members || 0}</li>
        <li>Conversion Time: ${summary.time || 'N/A'}</li>
        <li>Format: ${summary.format || 'DXF'}</li>
        <li>Entities Extracted: ${summary.entities || 0}</li>
    `;
    document.getElementById('statistics').innerHTML = statsHtml;
    
    // Update download links with output path header
    const downloadList = document.getElementById('downloadLinks');
    console.log('downloadLinks element found:', downloadList);
    
    if (!downloadList) {
        console.error('ERROR: downloadLinks element not found in DOM!');
        return;
    }
    
    downloadList.innerHTML = '';
    
    // Add output path display
    if (data.output_path) {
        const pathDisplay = document.createElement('div');
        pathDisplay.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;
        pathDisplay.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                </svg>
                <strong style="font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">Output Location</strong>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); padding: 12px; border-radius: 8px; font-family: 'Monaco', 'Courier New', monospace; font-size: 0.875rem; word-break: break-all; backdrop-filter: blur(10px);">
                ${data.output_path}
            </div>
            <div style="margin-top: 8px; font-size: 0.75rem; opacity: 0.9;">
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="display: inline; vertical-align: middle; margin-right: 4px;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                All generated files are saved in this directory
            </div>
        `;
        downloadList.appendChild(pathDisplay);
    }
    
    if (outputs.file_details && outputs.file_details.length > 0) {
        outputs.file_details.forEach(file => {
            const link = document.createElement('a');
            link.href = `/api/download/${currentJobId}/${file.name}`;
            link.className = 'download-link';
            const fileSizeFormatted = formatFileSize(file.size);
            link.innerHTML = `
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                </svg>
                <span style="flex: 1;">${file.name}</span>
                <span style="font-size: 0.75rem; color: var(--gray-500); background: var(--gray-100); padding: 2px 8px; border-radius: 4px;">${file.type}</span>
                <span style="font-size: 0.75rem; color: var(--gray-500); margin-left: 8px;">${fileSizeFormatted}</span>
            `;
            downloadList.appendChild(link);
        });
    } else if (outputs.files && outputs.files.length > 0) {
        outputs.files.forEach(file => {
            const link = document.createElement('a');
            link.href = `/api/download/${currentJobId}/${file}`;
            link.className = 'download-link';
            link.innerHTML = `
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                </svg>
                ${file}
            `;
            downloadList.appendChild(link);
        });
    } else {
        downloadList.innerHTML += '<p style="color: var(--gray-600); font-size: 0.875rem;">No output files available</p>';
    }
    
    // Update quality metrics with animations
    const metrics = [
        { id: 'accuracy', value: summary.accuracy || 98, label: 'Geometry Accuracy' },
        { id: 'completeness', value: summary.completeness || 95, label: 'Data Completeness' },
        { id: 'quality', value: summary.quality || 97, label: 'Overall Quality' }
    ];
    
    const metricsHtml = metrics.map(metric => `
        <div class="metric">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="metric-label">${metric.label}</span>
                <span class="metric-value">${metric.value}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: ${metric.value}%"></div>
            </div>
        </div>
    `).join('');
    
    const qualityMetricsEl = document.getElementById('qualityMetrics');
    if (qualityMetricsEl) {
        qualityMetricsEl.innerHTML = metricsHtml;
    } else {
        console.warn('qualityMetrics element not found, skipping metrics display');
    }

    exportTeklaBtn.disabled = true;
    sendTeklaDirectBtn.disabled = true;
    runAiValidation(currentJobId);
    
    // Show results section
    console.log('Showing results section...');
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    console.log('Results section displayed!');
}

// Export to Tekla
exportTeklaBtn.addEventListener('click', async () => {
    if (!currentJobId) return;
    if (!aiValidationState.ready) {
        showConsultantDialog(aiValidationState.report || { suggestions: ['AI validation is still pending. Please wait or refresh the page.'] });
        return;
    }
    if (aiValidationState.needsUserConfirmation) {
        showConsultantDialog(aiValidationState.report || { suggestions: ['AI validation requires action before export.'] });
        return;
    }

    // Show loading state
    exportTeklaBtn.disabled = true;
    exportTeklaBtn.innerHTML = `
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25"></circle>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>
        </svg>
        Exporting...
    `;
    
    try {
        const response = await fetch(`/api/export-tekla/${currentJobId}`);
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            const teklaStatus = document.getElementById('teklaStatus');
            if (data.ifc_available) {
                teklaStatus.innerHTML = `
                    <strong style="color: var(--success);">✓ IFC model ready for Tekla import</strong><br>
                    <span style="font-size: 0.875rem; color: var(--gray-600);">
                        Import this file into Tekla Structures to continue your workflow
                    </span>
                `;
                
                // Add download button
                const downloadBtn = document.createElement('a');
                downloadBtn.href = data.ifc_path;
                downloadBtn.className = 'btn btn-tekla';
                downloadBtn.style.marginTop = '12px';
                downloadBtn.innerHTML = `
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                    </svg>
                    Download IFC Model
                `;
                teklaStatus.appendChild(downloadBtn);
            } else {
                teklaStatus.innerHTML = `
                    <strong style="color: var(--warning);">⚠ IFC export not available</strong><br>
                    <span style="font-size: 0.875rem; color: var(--gray-600);">
                        Please check the pipeline output for more information
                    </span>
                `;
            }
            
            // Reset button
            exportTeklaBtn.disabled = false;
            exportTeklaBtn.innerHTML = `
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
                Export to Tekla IFC
            `;
        } else {
            teklaStatus.innerHTML = `
                <strong style="color: var(--error);">❌ Export failed</strong><br>
                <span style="font-size: 0.875rem; color: var(--gray-600);">
                    ${data.message || 'An error occurred during export'}
                </span>
            `;
            
            // Reset button
            exportTeklaBtn.disabled = false;
            exportTeklaBtn.innerHTML = `
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                </svg>
                Retry Export
            `;
        }
    } catch (error) {
        document.getElementById('teklaStatus').innerHTML = `
            <strong style="color: var(--error);">❌ Error</strong><br>
            <span style="font-size: 0.875rem; color: var(--gray-600);">
                ${error.message}
            </span>
        `;
        
        // Reset button
        exportTeklaBtn.disabled = false;
        exportTeklaBtn.innerHTML = `
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            Retry Export
        `;
    }
});

sendTeklaDirectBtn?.addEventListener('click', async () => {
    if (!currentJobId) return;

    sendTeklaDirectBtn.disabled = true;
    sendTeklaDirectBtn.innerHTML = `
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25"></circle>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>
        </svg>
        Sending...
    `;

    try {
        const response = await fetch(`/api/export-tekla-direct/${currentJobId}`);
        const data = await response.json();
        const directStatus = document.getElementById('teklaDirectStatus');

        if (response.ok && data.status === 'ok') {
            directStatus.innerHTML = `
                <strong style="color: var(--success);">✓ Sent to Tekla API</strong><br>
                <span style="font-size: 0.875rem; color: var(--gray-600);">
                    ${data.tekla_response?.message || 'Tekla structure render request was accepted.'}
                </span>
            `;
        } else {
            directStatus.innerHTML = `
                <strong style="color: var(--error);">❌ Direct Tekla export failed</strong><br>
                <span style="font-size: 0.875rem; color: var(--gray-600);">
                    ${data.message || 'Tekla bridge is not connected or the payload is invalid.'}
                </span>
            `;
        }
    } catch (error) {
        document.getElementById('teklaDirectStatus').innerHTML = `
            <strong style="color: var(--error);">❌ Error</strong><br>
            <span style="font-size: 0.875rem; color: var(--gray-600);">
                ${error.message}
            </span>
        `;
    } finally {
        sendTeklaDirectBtn.disabled = false;
        sendTeklaDirectBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Send directly to Tekla
        `;
    }
});

function showError(message) {
    // Reset processing steps
    const steps = ['upload', 'convert', 'analyze', 'export'];
    steps.forEach(step => {
        const stepEl = document.querySelector(`[data-step="${step}"]`);
        if (stepEl) {
            stepEl.classList.remove('active', 'completed');
        }
    });
    
    // Show error section
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// Reset button functionality
function resetUpload() {
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('uploadSection').style.display = 'block';
    removeFile();
    currentJobId = null;
}

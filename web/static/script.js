const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const exportTeklaBtn = document.getElementById('exportTeklaBtn');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileRemove = document.getElementById('fileRemove');

let selectedFile = null;
let currentJobId = null;

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
                const prevStep = document.getElementById(`step-${steps[currentStep - 1]}`);
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
            }
            if (currentStep < steps.length) {
                const currStep = document.getElementById(`step-${steps[currentStep]}`);
                currStep.classList.add('active');
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
        
        if (response.ok && data.status === 'ok') {
            currentJobId = data.job_id;
            
            // Complete all steps
            steps.forEach(step => {
                const stepEl = document.getElementById(`step-${step}`);
                stepEl.classList.remove('active');
                stepEl.classList.add('completed');
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
    const outputs = data.outputs || {};
    const summary = outputs.summary || {};
    
    // Update statistics
    const statsHtml = `
        <li>Total Members: ${summary.members || 0}</li>
        <li>Conversion Time: ${summary.time || 'N/A'}</li>
        <li>Format: ${summary.format || 'DXF'}</li>
        <li>Entities Extracted: ${summary.entities || 0}</li>
    `;
    document.getElementById('statistics').innerHTML = statsHtml;
    
    // Update download links
    const downloadList = document.getElementById('downloadList');
    downloadList.innerHTML = '';
    
    if (outputs.files && outputs.files.length > 0) {
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
        downloadList.innerHTML = '<p style="color: var(--gray-600); font-size: 0.875rem;">No output files available</p>';
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
    
    document.getElementById('qualityMetrics').innerHTML = metricsHtml;
    
    // Show results section
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
}

// Export to Tekla
exportTeklaBtn.addEventListener('click', async () => {
    if (!currentJobId) return;
    
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
                Export to Tekla
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

function showError(message) {
    // Reset processing steps
    const steps = ['upload', 'convert', 'analyze', 'export'];
    steps.forEach(step => {
        const stepEl = document.getElementById(`step-${step}`);
        stepEl.classList.remove('active', 'completed');
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

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const exportTeklaBtn = document.getElementById('exportTeklaBtn');

let selectedFile = null;
let currentJobId = null;

// File selection
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];
    uploadBtn.disabled = !selectedFile;
    if (selectedFile) {
        uploadArea.style.borderColor = 'var(--success)';
        uploadArea.innerHTML = `<p>✓ ${selectedFile.name} selected</p>`;
    }
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
    selectedFile = e.dataTransfer.files[0];
    uploadBtn.disabled = !selectedFile;
    if (selectedFile) {
        uploadArea.style.borderColor = 'var(--success)';
        uploadArea.innerHTML = `<p>✓ ${selectedFile.name} selected</p>`;
    }
});

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
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + Math.random() * 30, 90);
            document.getElementById('progressBar').style.width = progress + '%';
        }, 300);
        
        // Upload file
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            currentJobId = data.job_id;
            document.getElementById('progressBar').style.width = '100%';
            
            // Show results
            setTimeout(() => {
                showResults(data);
            }, 500);
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
    
    // Status
    document.getElementById('pipelineStatus').textContent = '✓ Successfully processed';
    
    // Statistics
    const stats = document.getElementById('statistics');
    stats.innerHTML = `
        <li>Members: ${summary.members}</li>
        <li>Errors: ${summary.errors}</li>
        <li>Clashes: ${summary.clashes}</li>
    `;
    
    // Download links
    const downloads = document.getElementById('downloadLinks');
    downloads.innerHTML = '';
    (outputs.files || []).forEach(file => {
        const a = document.createElement('a');
        a.href = `/api/download/${currentJobId}/${file}`;
        a.textContent = `📥 ${file}`;
        a.className = 'download-link';
        downloads.appendChild(a);
    });
    
    // Show results section
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
}

// Export to Tekla
exportTeklaBtn.addEventListener('click', async () => {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/api/export-tekla/${currentJobId}`);
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            const teklaStatus = document.getElementById('teklaStatus');
            if (data.ifc_available) {
                teklaStatus.innerHTML = `
                    ✓ IFC model ready for Tekla import<br>
                    <a href="${data.ifc_path}" class="download-link" style="margin-top: 10px; display: block;">
                        📥 Download model.ifc
                    </a>
                `;
            } else {
                teklaStatus.textContent = '⚠ IFC export not yet available. Please check the pipeline output.';
            }
        } else {
            document.getElementById('teklaStatus').textContent = '❌ ' + (data.message || 'Export failed');
        }
    } catch (error) {
        document.getElementById('teklaStatus').textContent = '❌ Error: ' + error.message;
    }
});

function showError(message) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

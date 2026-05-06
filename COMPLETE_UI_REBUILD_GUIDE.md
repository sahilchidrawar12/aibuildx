# AIBuildX - Complete UI Rebuild Guide

## 🎨 **UI Architecture Overview**

The AIBuildX interface is built with modern web technologies focusing on:
- **Progressive Enhancement**: Works without JavaScript
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Optimized animations and interactions

## 📁 **File Structure**

```
web/
├── static/
│   ├── style.css          # Main stylesheet
│   ├── script.js          # Main JavaScript
│   └── assets/            # Images, icons, fonts
├── templates/
│   ├── index.html         # Main application page
│   ├── viewer.html        # 3D IFC viewer
│   └── components/        # Reusable HTML components
└── README.md             # UI documentation
```

## 🎯 **Core CSS Architecture**

### **Design System Variables**

```css
:root {
  /* Colors */
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #818cf8;
  --secondary: #64748b;
  --success: #10b981;
  --error: #ef4444;
  --warning: #f59e0b;

  /* Neutrals */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-glass: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));

  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;

  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}
```

### **Glass Card Component**

```css
.glass-card {
  background: var(--gradient-glass);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
}
```

### **Button System**

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-weight: 500;
  font-size: var(--font-size-sm);
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left var(--transition-normal);
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.btn-secondary {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}

.btn-tekla {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
}

.btn-tekla-secondary {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
}
```

## 🖥️ **Complete HTML Structure**

### **Main Index Template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIBuildX - DWG to Tekla Converter</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Background Animation -->
    <div class="bg-animation">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
    </div>

    <div class="container">
        <!-- Navigation -->
        <nav class="navbar">
            <div class="logo">
                <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                <span class="logo-text">AIBuildX</span>
            </div>
            <div class="nav-links">
                <a href="#" class="nav-link active">Converter</a>
                <a href="#" class="nav-link">Docs</a>
                <a href="#" class="nav-link">API</a>
            </div>
        </nav>

        <!-- Hero Section -->
        <header class="hero">
            <div class="hero-badge">
                <span class="badge-dot"></span>
                <span>Production Ready</span>
            </div>
            <h1 class="hero-title">Transform CAD to BIM<br/>in Seconds</h1>
            <p class="hero-subtitle">Industry-leading DWG/DXF to Tekla Structures conversion with AI-powered accuracy</p>
            <div class="hero-stats">
                <div class="stat">
                    <div class="stat-value">50%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                <div class="stat">
                    <div class="stat-value">&lt;30s</div>
                    <div class="stat-label">Avg. Time</div>
                </div>
                <div class="stat">
                    <div class="stat-value">15+</div>
                    <div class="stat-label">Formats</div>
                </div>
            </div>
        </header>

        <main>
            <!-- Upload Section -->
            <section id="uploadSection" class="glass-card">
                <div class="section-header">
                    <div class="step-indicator">
                        <span class="step-number">1</span>
                    </div>
                    <div>
                        <h2>Upload Your File</h2>
                        <p class="section-desc">Support for DWG, DXF formats</p>
                    </div>
                </div>

                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon-wrapper">
                        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                        <div class="upload-pulse"></div>
                    </div>
                    <h3 class="upload-title">Drop files here or click to browse</h3>
                    <p class="upload-desc">Supports .DWG, .DXF • Max 50MB</p>
                    <input type="file" id="fileInput" accept=".dwg,.dxf" hidden>
                    <div class="file-preview" id="filePreview" style="display: none;">
                        <div class="file-icon">📄</div>
                        <div class="file-info">
                            <div class="file-name" id="fileName"></div>
                            <div class="file-size" id="fileSize"></div>
                        </div>
                        <button class="file-remove" id="fileRemove">×</button>
                    </div>
                </div>

                <button class="btn btn-primary" id="uploadBtn" disabled>
                    <span class="btn-text">Start Conversion</span>
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </button>
            </section>

            <!-- Processing Section -->
            <section id="progressSection" class="glass-card" style="display: none;">
                <div class="section-header">
                    <div class="step-indicator active">
                        <span class="step-number">2</span>
                        <div class="step-spinner"></div>
                    </div>
                    <div>
                        <h2>Processing</h2>
                        <p class="section-desc" id="progressText">Initializing pipeline...</p>
                    </div>
                </div>

                <div class="progress-container">
                    <div class="progress">
                        <div class="progress-bar" id="progressBar"></div>
                        <div class="progress-glow"></div>
                    </div>
                    <div class="progress-percentage" id="progressPercentage">0%</div>
                </div>

                <div class="processing-steps">
                    <div class="processing-step" data-step="upload">
                        <div class="step-icon">📤</div>
                        <div class="step-text">Uploading</div>
                    </div>
                    <div class="processing-step" data-step="convert">
                        <div class="step-icon">🔄</div>
                        <div class="step-text">Converting</div>
                    </div>
                    <div class="processing-step" data-step="analyze">
                        <div class="step-icon">🔍</div>
                        <div class="step-text">Analyzing</div>
                    </div>
                    <div class="processing-step" data-step="export">
                        <div class="step-icon">📦</div>
                        <div class="step-text">Exporting</div>
                    </div>
                </div>
            </section>

            <!-- Results Section -->
            <section id="resultsSection" class="glass-card" style="display: none;">
                <div class="section-header">
                    <div class="step-indicator success">
                        <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </div>
                    <div>
                        <h2>Conversion Complete!</h2>
                        <p class="section-desc">Your files are ready for download</p>
                    </div>
                </div>

                <div class="results-grid">
                    <div class="result-card">
                        <div class="result-icon">📊</div>
                        <h3>Statistics</h3>
                        <ul class="result-list" id="statistics"></ul>
                    </div>

                    <div class="result-card">
                        <div class="result-icon">📁</div>
                        <h3>Output Files</h3>
                        <div class="download-list" id="downloadLinks"></div>
                    </div>

                    <div class="result-card">
                        <div class="result-icon">👁️</div>
                        <h3>3D Viewer</h3>
                        <p class="result-desc">Open interactive IFC viewer</p>
                        <a class="btn btn-primary" id="viewerLink" href="#" target="_blank" style="display:none">
                            <span>Open 3D Viewer</span>
                        </a>
                        <p class="muted" id="viewerHint">Viewer appears when IFC is generated.</p>
                    </div>

                    <div class="result-card">
                        <div class="result-icon">🏗️</div>
                        <h3>Tekla Export</h3>
                        <p class="result-desc">Export to Tekla Structures format</p>
                        <button class="btn btn-tekla" id="exportTeklaBtn">
                            <span>Export to Tekla IFC</span>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                        </button>
                        <button class="btn btn-tekla-secondary" id="sendTeklaDirectBtn">
                            <span>Send directly to Tekla</span>
                        </button>
                        <p class="tekla-status" id="teklaStatus"></p>
                        <p class="tekla-status" id="teklaDirectStatus"></p>
                        <div id="aiSummary" class="ai-summary">
                            <strong>Self-Healing Consultant</strong>
                            <p class="muted">Validating before Tekla export...</p>
                        </div>
                    </div>

                    <div class="result-card">
                        <div class="result-icon">✨</div>
                        <h3>Quality Report</h3>
                        <div id="aiTrendPanel" class="ai-trend">
                            <p class="muted">AI confidence trend loading...</p>
                        </div>
                        <div class="quality-metrics">
                            <div class="metric">
                                <div class="metric-label">Accuracy</div>
                                <div class="metric-bar">
                                    <div class="metric-fill" style="width: 98%"></div>
                                </div>
                                <div class="metric-value">98%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <button class="btn btn-secondary" onclick="location.reload()">
                        <span>Convert Another File</span>
                    </button>
                </div>
            </section>

            <!-- AI Validation Modal -->
            <div id="validationModal" class="modal" style="display:none;">
                <div class="modal-backdrop"></div>
                <div class="modal-card">
                    <div class="modal-header">
                        <h2 id="validationTitle">AI Validation Consultant</h2>
                        <button class="close-modal" id="validationCloseBtn">×</button>
                    </div>
                    <div class="modal-content">
                        <p id="validationAdvice" class="section-desc"></p>
                        <div id="validationSuggestions" class="validation-suggestions"></div>
                        <div class="validation-metrics">
                            <div><strong>Confidence</strong>: <span id="validationConfidence">0.0</span></div>
                            <div><strong>Disconnected nodes</strong>: <span id="validationGaps">0</span></div>
                            <div><strong>Semantic mismatches</strong>: <span id="validationSemantic">0</span></div>
                        </div>
                        <div class="modal-actions">
                            <button class="btn btn-tekla" id="validationYesBtn">Yes, repair now</button>
                            <button class="btn btn-secondary" id="validationNoBtn">No, export as-is</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Error Section -->
            <section id="errorSection" class="glass-card error-card" style="display: none;">
                <div class="error-icon-wrapper">
                    <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                </div>
                <h2>Conversion Failed</h2>
                <p class="error-message" id="errorMessage"></p>
                <button class="btn btn-secondary" onclick="location.reload()">
                    <span>Try Again</span>
                </button>
            </section>
        </main>

        <footer class="footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h4>AIBuildX</h4>
                    <p>Next-generation CAD to BIM conversion</p>
                </div>
                <div class="footer-section">
                    <h4>Resources</h4>
                    <a href="#">Documentation</a>
                    <a href="#">API Reference</a>
                    <a href="#">Support</a>
                </div>
                <div class="footer-section">
                    <h4>Company</h4>
                    <a href="#">About</a>
                    <a href="#">Contact</a>
                    <a href="#">Privacy</a>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2025 AIBuildX. All rights reserved.</p>
            </div>
        </footer>
    </div>

    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
```

## 🎮 **Complete JavaScript Implementation**

### **State Management**

```javascript
class AppState {
    constructor() {
        this.currentJobId = null;
        this.selectedFile = null;
        this.aiValidationState = {
            ready: false,
            report: null,
            pending: false,
            needsUserConfirmation: false
        };
        this.processingState = {
            active: false,
            progress: 0,
            currentStep: null
        };
    }

    reset() {
        this.currentJobId = null;
        this.selectedFile = null;
        this.aiValidationState = {
            ready: false,
            report: null,
            pending: false,
            needsUserConfirmation: false
        };
        this.processingState = {
            active: false,
            progress: 0,
            currentStep: null
        };
    }
}

const appState = new AppState();
```

### **File Upload Handler**

```javascript
class FileUploadHandler {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.filePreview = document.getElementById('filePreview');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.fileRemove = document.getElementById('fileRemove');

        this.init();
    }

    init() {
        // Click to upload
        this.uploadArea.addEventListener('click', (e) => {
            if (e.target !== this.fileRemove) this.fileInput.click();
        });

        // File selection
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files[0]);
        });

        // Remove file
        this.fileRemove.addEventListener('click', (e) => {
            e.stopPropagation();
            this.removeFile();
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFileSelection(e.dataTransfer.files[0]);
        });
    }

    handleFileSelection(file) {
        if (!file) return;

        appState.selectedFile = file;
        this.uploadBtn.disabled = false;

        // Show file preview
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.filePreview.style.display = 'flex';

        // Add visual feedback
        this.uploadArea.classList.add('file-selected');
    }

    removeFile() {
        appState.selectedFile = null;
        this.uploadBtn.disabled = true;
        this.filePreview.style.display = 'none';
        this.fileInput.value = '';
        this.uploadArea.classList.remove('file-selected');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
}
```

### **Processing Animation System**

```javascript
class ProcessingAnimator {
    constructor() {
        this.progressBar = document.getElementById('progressBar');
        this.progressPercentage = document.getElementById('progressPercentage');
        this.progressText = document.getElementById('progressText');
        this.stepIndicator = document.querySelector('#progressSection .step-indicator');
        this.processingSteps = document.querySelectorAll('.processing-step');

        this.steps = ['upload', 'convert', 'analyze', 'export'];
        this.currentStepIndex = 0;
        this.animationInterval = null;
    }

    start() {
        appState.processingState.active = true;
        this.resetSteps();
        this.animateSteps();
        this.animateProgress();
    }

    stop() {
        appState.processingState.active = false;
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
            this.animationInterval = null;
        }
    }

    complete() {
        this.stop();
        this.progressBar.style.width = '100%';
        this.progressPercentage.textContent = '100%';
        this.stepIndicator.classList.remove('active');
        this.stepIndicator.classList.add('success');
        this.stepIndicator.innerHTML = `
            <svg class="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        `;

        // Complete all steps
        this.processingSteps.forEach(step => {
            step.classList.remove('active');
            step.classList.add('completed');
        });
    }

    animateSteps() {
        this.animationInterval = setInterval(() => {
            if (this.currentStepIndex > 0) {
                const prevStep = document.querySelector(`[data-step="${this.steps[this.currentStepIndex - 1]}"]`);
                if (prevStep) {
                    prevStep.classList.remove('active');
                    prevStep.classList.add('completed');
                }
            }

            if (this.currentStepIndex < this.steps.length) {
                const currStep = document.querySelector(`[data-step="${this.steps[this.currentStepIndex]}"]`);
                if (currStep) {
                    currStep.classList.add('active');
                }
                this.currentStepIndex++;
            }
        }, 1000);
    }

    animateProgress() {
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (!appState.processingState.active) {
                clearInterval(progressInterval);
                return;
            }

            progress = Math.min(progress + Math.random() * 15, 90);
            this.progressBar.style.width = progress + '%';
            this.progressPercentage.textContent = Math.round(progress) + '%';
        }, 400);
    }

    resetSteps() {
        this.currentStepIndex = 0;
        this.processingSteps.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        this.stepIndicator.classList.add('active');
        this.stepIndicator.innerHTML = '<div class="step-spinner"></div>';
    }
}
```

### **AI Validation Modal**

```javascript
class AIValidationModal {
    constructor() {
        this.modal = document.getElementById('validationModal');
        this.title = document.getElementById('validationTitle');
        this.advice = document.getElementById('validationAdvice');
        this.suggestions = document.getElementById('validationSuggestions');
        this.confidence = document.getElementById('validationConfidence');
        this.gaps = document.getElementById('validationGaps');
        this.semantic = document.getElementById('validationSemantic');
        this.yesBtn = document.getElementById('validationYesBtn');
        this.noBtn = document.getElementById('validationNoBtn');
        this.closeBtn = document.getElementById('validationCloseBtn');

        this.init();
    }

    init() {
        this.yesBtn?.addEventListener('click', async () => {
            if (!appState.currentJobId) return;
            await this.resolveAction(appState.currentJobId, 'apply_all', 'yes');
        });

        this.noBtn?.addEventListener('click', async () => {
            if (!appState.currentJobId) return;
            await this.resolveAction(appState.currentJobId, 'accept_as_is', 'no');
        });

        this.closeBtn?.addEventListener('click', () => {
            this.hide();
        });
    }

    show(auditReport) {
        if (!this.modal) return;

        this.renderReport(auditReport);
        this.modal.style.display = 'flex';
    }

    hide() {
        if (!this.modal) return;
        this.modal.style.display = 'none';
    }

    renderReport(audit) {
        if (!audit) return;

        this.advice.textContent = audit.advisory_text || 'The AI consultant recommends reviewing the model before export.';
        this.suggestions.innerHTML = '';

        (audit.suggestions || []).forEach((suggestion) => {
            const p = document.createElement('p');
            p.textContent = suggestion;
            this.suggestions.appendChild(p);
        });

        if (this.confidence) {
            this.confidence.textContent = (audit.confidence_score || 0).toFixed(2);
        }
        if (this.gaps) {
            this.gaps.textContent = audit.disconnected_node_count || 0;
        }
        if (this.semantic) {
            this.semantic.textContent = audit.semantic_mismatch_count || 0;
        }
    }

    async resolveAction(jobId, action, decision) {
        if (!jobId) return;

        this.yesBtn.disabled = true;
        this.noBtn.disabled = true;

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
                appState.aiValidationState.report = data.audit;
                appState.aiValidationState.needsUserConfirmation = false;
                this.updateAISummary(data.audit);
                this.hide();

                // Enable export buttons
                document.getElementById('exportTeklaBtn').disabled = false;
                document.getElementById('sendTeklaDirectBtn').disabled = false;

                this.showSuccessMessage('Self-healing update applied successfully!');
            } else {
                this.showErrorMessage(data.message || 'Action failed');
            }
        } catch (error) {
            this.showErrorMessage(error.message);
        } finally {
            this.yesBtn.disabled = false;
            this.noBtn.disabled = false;
        }
    }

    updateAISummary(audit) {
        const aiSummary = document.getElementById('aiSummary');
        if (aiSummary) {
            aiSummary.innerHTML = `
                <strong>Self-Healing Consultant</strong>
                <p class="muted">${audit.advisory_text || 'Validation complete.'}</p>
                <div style="margin-top: 10px; font-size: 0.9rem; color: var(--gray-200);">
                    <span>Confidence: ${Math.round(audit.confidence_score * 100)}%</span> •
                    <span>Gaps: ${audit.disconnected_node_count}</span> •
                    <span>Issues: ${audit.semantic_mismatch_count}</span>
                </div>
            `;
        }
    }

    showSuccessMessage(message) {
        const statusEl = document.getElementById('teklaStatus');
        if (statusEl) {
            statusEl.innerHTML = `<strong style="color: var(--success);">✓ ${message}</strong>`;
        }
    }

    showErrorMessage(message) {
        const statusEl = document.getElementById('teklaStatus');
        if (statusEl) {
            statusEl.innerHTML = `<strong style="color: var(--error);">❌ ${message}</strong>`;
        }
    }
}
```

### **Main Application Controller**

```javascript
class AIBuildXApp {
    constructor() {
        this.fileHandler = new FileUploadHandler();
        this.processingAnimator = new ProcessingAnimator();
        this.aiModal = new AIValidationModal();

        this.uploadBtn = document.getElementById('uploadBtn');
        this.exportTeklaBtn = document.getElementById('exportTeklaBtn');
        this.sendTeklaDirectBtn = document.getElementById('sendTeklaDirectBtn');

        this.init();
    }

    init() {
        // Upload button
        this.uploadBtn.addEventListener('click', () => {
            this.startConversion();
        });

        // Export buttons
        this.exportTeklaBtn.addEventListener('click', () => {
            this.exportToTekla();
        });

        this.sendTeklaDirectBtn.addEventListener('click', () => {
            this.sendToTeklaDirect();
        });
    }

    async startConversion() {
        if (!appState.selectedFile) return;

        const formData = new FormData();
        formData.append('file', appState.selectedFile);

        try {
            // Show processing
            this.showSection('progressSection');
            this.processingAnimator.start();

            // Upload and process
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.status === 'ok') {
                appState.currentJobId = data.job_id;
                this.processingAnimator.complete();
                setTimeout(() => {
                    this.showResults(data);
                }, 800);
            } else {
                this.showError(data.message || 'Conversion failed');
            }
        } catch (error) {
            this.showError('Upload failed: ' + error.message);
        }
    }

    showResults(data) {
        this.renderStatistics(data.outputs.summary);
        this.renderDownloadLinks(data.outputs.file_details, appState.currentJobId);
        this.setupViewerLink(data.viewer_url);

        // Start AI validation
        this.runAiValidation(appState.currentJobId);

        this.showSection('resultsSection');
    }

    async runAiValidation(jobId) {
        appState.aiValidationState.pending = true;

        try {
            const response = await fetch(`/api/ai-validate/${jobId}`);
            const data = await response.json();

            if (!response.ok || data.status !== 'ok') {
                this.updateAISummary('Unable to validate: ' + (data.message || 'Unknown error'));
                this.exportTeklaBtn.disabled = false;
                this.sendTeklaDirectBtn.disabled = false;
                return;
            }

            appState.aiValidationState.ready = true;
            appState.aiValidationState.report = data.audit;
            appState.aiValidationState.pending = false;
            appState.aiValidationState.needsUserConfirmation = data.needs_user_confirmation;

            this.updateAISummary(data.audit);
            this.updateQualityMetrics(data.audit);

            if (data.needs_user_confirmation) {
                this.aiModal.show(data.audit);
            } else {
                this.exportTeklaBtn.disabled = false;
                this.sendTeklaDirectBtn.disabled = false;
            }
        } catch (error) {
            console.error('AI validation error', error);
            this.updateAISummary('Validation unavailable: ' + error.message);
            this.exportTeklaBtn.disabled = false;
            this.sendTeklaDirectBtn.disabled = false;
        }
    }

    async exportToTekla() {
        if (!appState.currentJobId) return;

        if (!appState.aiValidationState.ready) {
            this.aiModal.show(appState.aiValidationState.report || {
                suggestions: ['AI validation is still pending. Please wait or refresh the page.']
            });
            return;
        }

        if (appState.aiValidationState.needsUserConfirmation) {
            this.aiModal.show(appState.aiValidationState.report || {
                suggestions: ['AI validation requires action before export.']
            });
            return;
        }

        // Show loading state
        this.exportTeklaBtn.disabled = true;
        this.exportTeklaBtn.innerHTML = `
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25"></circle>
                <path d="M4 12a8 8 0 018-8" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>
            </svg>
            Exporting...
        `;

        try {
            const response = await fetch(`/api/export-tekla/${appState.currentJobId}`);
            const data = await response.json();

            if (response.ok && data.status === 'ok') {
                this.showExportSuccess(data);
            } else {
                this.showExportError(data.message || 'Export failed');
            }
        } catch (error) {
            this.showExportError(error.message);
        } finally {
            this.resetExportButton();
        }
    }

    // Additional methods for rendering, error handling, etc.
    showSection(sectionId) {
        ['uploadSection', 'progressSection', 'resultsSection', 'errorSection'].forEach(id => {
            document.getElementById(id).style.display = id === sectionId ? 'block' : 'none';
        });
    }

    renderStatistics(summary) {
        const statsHtml = `
            <li>Total Members: ${summary.members || 0}</li>
            <li>Conversion Time: ${summary.time || 'N/A'}</li>
            <li>Format: ${summary.format || 'DXF'}</li>
            <li>Entities Extracted: ${summary.entities || 0}</li>
        `;
        document.getElementById('statistics').innerHTML = statsHtml;
    }

    renderDownloadLinks(files, jobId) {
        const downloadList = document.getElementById('downloadLinks');
        downloadList.innerHTML = '';

        if (files && files.length > 0) {
            files.forEach(file => {
                const link = document.createElement('a');
                link.href = `/api/download/${jobId}/${file.name}`;
                link.className = 'download-link';
                link.innerHTML = `
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                    </svg>
                    <span>${file.name}</span>
                    <span class="file-type">${file.type}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                `;
                downloadList.appendChild(link);
            });
        }
    }

    updateAISummary(audit) {
        const aiSummary = document.getElementById('aiSummary');
        if (aiSummary) {
            aiSummary.innerHTML = `
                <strong>Self-Healing Consultant</strong>
                <p class="muted">${audit.advisory_text || 'Validation complete.'}</p>
            `;
        }
    }

    showError(message) {
        this.processingAnimator.stop();
        document.getElementById('errorMessage').textContent = message;
        this.showSection('errorSection');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AIBuildXApp();
});
```

## 🎨 **CSS Component Library**

### **Modal System**

```css
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
}

.modal-card {
    position: relative;
    background: var(--gradient-glass);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-6);
}

.modal-header h2 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: 600;
}

.close-modal {
    background: none;
    border: none;
    font-size: var(--font-size-2xl);
    cursor: pointer;
    color: var(--gray-400);
    padding: var(--space-1);
    border-radius: var(--radius);
    transition: all var(--transition-fast);
}

.close-modal:hover {
    background: var(--gray-100);
    color: var(--gray-700);
}

.modal-actions {
    display: flex;
    gap: var(--space-3);
    margin-top: var(--space-6);
    justify-content: flex-end;
}
```

### **Progress Indicators**

```css
.progress-container {
    margin: var(--space-6) 0;
}

.progress {
    position: relative;
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: var(--space-3);
}

.progress-bar {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: var(--radius);
    transition: width var(--transition-normal);
    position: relative;
}

.progress-glow {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: progress-glow 2s infinite;
}

@keyframes progress-glow {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-percentage {
    text-align: center;
    font-weight: 600;
    color: var(--primary);
    font-size: var(--font-size-lg);
}

.processing-steps {
    display: flex;
    justify-content: space-between;
    margin-top: var(--space-6);
}

.processing-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    opacity: 0.4;
    transition: all var(--transition-normal);
}

.processing-step.active {
    opacity: 1;
}

.processing-step.active .step-icon {
    animation: pulse 1.5s infinite;
}

.processing-step.completed {
    opacity: 0.7;
}

.processing-step.completed .step-icon {
    color: var(--success);
}

.step-icon {
    font-size: var(--font-size-2xl);
    transition: all var(--transition-normal);
}

.step-text {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--gray-600);
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}
```

### **Results Grid**

```css
.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-6);
    margin: var(--space-8) 0;
}

.result-card {
    background: var(--gradient-glass);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    transition: all var(--transition-normal);
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.result-icon {
    font-size: var(--font-size-3xl);
    margin-bottom: var(--space-4);
}

.result-card h3 {
    margin: var(--space-4) 0 var(--space-3) 0;
    font-size: var(--font-size-lg);
    font-weight: 600;
}

.result-desc {
    color: var(--gray-600);
    margin-bottom: var(--space-4);
}

.download-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.download-link {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius);
    text-decoration: none;
    color: var(--gray-200);
    transition: all var(--transition-fast);
}

.download-link:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateX(4px);
}

.quality-metrics {
    margin-top: var(--space-4);
}

.metric {
    margin-bottom: var(--space-4);
}

.metric-label {
    display: block;
    font-size: var(--font-size-sm);
    color: var(--gray-600);
    margin-bottom: var(--space-2);
}

.metric-bar {
    height: 8px;
    background: var(--gray-200);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: var(--space--2);
}

.metric-fill {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: var(--radius);
    transition: width var(--transition-slow);
}

.metric-value {
    font-weight: 600;
    color: var(--primary);
    font-size: var(--font-size-sm);
}
```

## 🚀 **Deployment & Build Process**

### **Build Script**

```bash
#!/bin/bash
# Build and deploy AIBuildX UI

echo "Building AIBuildX UI..."

# Install dependencies
npm install

# Build assets
npm run build

# Minify CSS and JS
npm run minify

# Run tests
npm test

# Deploy to production
npm run deploy

echo "UI build complete!"
```

### **Package.json**

```json
{
  "name": "aibuildx-ui",
  "version": "1.0.0",
  "description": "AIBuildX Web Interface",
  "main": "static/script.js",
  "scripts": {
    "build": "postcss static/style.css -o static/style.min.css",
    "minify": "terser static/script.js -o static/script.min.js",
    "test": "jest",
    "deploy": "rsync -avz web/ user@server:/var/www/aibuildx/"
  },
  "devDependencies": {
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "cssnano": "^6.0.0",
    "terser": "^5.16.0",
    "jest": "^29.0.0"
  }
}
```

This complete UI rebuild guide provides everything needed to recreate the AIBuildX interface with modern web technologies, comprehensive state management, and seamless user experience.
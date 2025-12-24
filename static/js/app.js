/**
 * AI Track Masterer - Frontend Application
 */

class AITrackMasterer {
    constructor() {
        this.selectedFiles = [];
        this.selectedPreset = 'streaming';
        this.selectedFormat = 'wav';
        this.noiseReduction = false;
        this.noiseStrength = 0.3;
        this.outputFolder = '';

        this.init();
    }

    init() {
        this.bindElements();
        this.bindEvents();
        this.loadOutputFiles();

        // Select default preset and format
        this.selectPreset('streaming');
        this.selectFormat('wav');
    }

    bindElements() {
        // Upload elements
        this.uploadZone = document.getElementById('uploadZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.filesContainer = document.getElementById('filesContainer');
        this.clearFilesBtn = document.getElementById('clearFiles');

        // Settings elements
        this.presetGrid = document.getElementById('presetGrid');
        this.formatOptions = document.getElementById('formatOptions');
        this.advancedToggle = document.getElementById('advancedToggle');
        this.advancedOptions = document.getElementById('advancedOptions');
        this.noiseReductionCheckbox = document.getElementById('noiseReduction');
        this.noiseStrengthRow = document.getElementById('noiseStrengthRow');
        this.noiseStrengthInput = document.getElementById('noiseStrength');
        this.noiseStrengthValue = document.getElementById('noiseStrengthValue');
        this.outputFolderInput = document.getElementById('outputFolder');

        // Action elements
        this.masterBtn = document.getElementById('masterBtn');

        // Progress elements
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.processingLog = document.getElementById('processingLog');

        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContainer = document.getElementById('resultsContainer');

        // Analysis elements
        this.analysisSection = document.getElementById('analysisSection');
        this.analysisGrid = document.getElementById('analysisGrid');

        // Output panel elements
        this.outputFiles = document.getElementById('outputFiles');
        this.refreshFilesBtn = document.getElementById('refreshFiles');
    }

    bindEvents() {
        // Upload events
        this.uploadZone.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFiles(e.target.files));
        this.clearFilesBtn.addEventListener('click', () => this.clearFiles());

        // Drag and drop
        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadZone.classList.add('dragover');
        });

        this.uploadZone.addEventListener('dragleave', () => {
            this.uploadZone.classList.remove('dragover');
        });

        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // Preset selection
        this.presetGrid.querySelectorAll('.preset-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectPreset(card.dataset.preset);
            });
        });

        // Format selection
        this.formatOptions.querySelectorAll('.format-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectFormat(btn.dataset.format);
            });
        });

        // Advanced options toggle
        this.advancedToggle.addEventListener('click', () => {
            this.advancedToggle.classList.toggle('open');
            this.advancedOptions.style.display =
                this.advancedOptions.style.display === 'none' ? 'block' : 'none';
        });

        // Noise reduction toggle
        this.noiseReductionCheckbox.addEventListener('change', () => {
            this.noiseReduction = this.noiseReductionCheckbox.checked;
            this.noiseStrengthRow.style.display = this.noiseReduction ? 'block' : 'none';
        });

        // Noise strength slider
        this.noiseStrengthInput.addEventListener('input', () => {
            this.noiseStrength = parseFloat(this.noiseStrengthInput.value);
            this.noiseStrengthValue.textContent = this.noiseStrength.toFixed(1);
        });

        // Output folder
        this.outputFolderInput.addEventListener('input', () => {
            this.outputFolder = this.outputFolderInput.value;
        });

        // Master button
        this.masterBtn.addEventListener('click', () => this.startMastering());

        // Refresh files button
        this.refreshFilesBtn.addEventListener('click', () => this.loadOutputFiles());
    }

    handleFiles(fileList) {
        const validFiles = Array.from(fileList).filter(file => {
            const ext = file.name.split('.').pop().toLowerCase();
            return ['mp3', 'wav', 'flac', 'ogg', 'aiff', 'm4a', 'wma'].includes(ext);
        });

        if (validFiles.length === 0) {
            this.showNotification('No valid audio files selected', 'error');
            return;
        }

        this.selectedFiles = [...this.selectedFiles, ...validFiles];
        this.updateFileList();
        this.updateMasterButton();
    }

    updateFileList() {
        if (this.selectedFiles.length === 0) {
            this.fileList.style.display = 'none';
            return;
        }

        this.fileList.style.display = 'block';
        this.filesContainer.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 18V5l12-2v13"/>
                            <circle cx="6" cy="18" r="3"/>
                            <circle cx="18" cy="16" r="3"/>
                        </svg>
                    </div>
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="remove-btn" onclick="app.removeFile(${index})">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.updateMasterButton();
    }

    clearFiles() {
        this.selectedFiles = [];
        this.updateFileList();
        this.updateMasterButton();
        this.fileInput.value = '';
    }

    selectPreset(preset) {
        this.selectedPreset = preset;
        this.presetGrid.querySelectorAll('.preset-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.preset === preset);
        });
    }

    selectFormat(format) {
        this.selectedFormat = format;
        this.formatOptions.querySelectorAll('.format-btn').forEach(btn => {
            btn.classList.toggle('selected', btn.dataset.format === format);
        });
    }

    updateMasterButton() {
        this.masterBtn.disabled = this.selectedFiles.length === 0;
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    showNotification(message, type = 'info') {
        // Simple console notification for now
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    async startMastering() {
        if (this.selectedFiles.length === 0) return;

        // Show progress section
        this.progressSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.analysisSection.style.display = 'none';

        // Update button state
        this.masterBtn.querySelector('.btn-text').style.display = 'none';
        this.masterBtn.querySelector('.btn-loading').style.display = 'flex';
        this.masterBtn.disabled = true;

        this.processingLog.innerHTML = '';
        this.resultsContainer.innerHTML = '';

        const results = [];
        const totalFiles = this.selectedFiles.length;

        for (let i = 0; i < totalFiles; i++) {
            const file = this.selectedFiles[i];
            const progress = ((i / totalFiles) * 100).toFixed(0);

            this.progressFill.style.width = progress + '%';
            this.progressText.textContent = `Processing ${file.name} (${i + 1}/${totalFiles})`;
            this.addLogEntry(`Processing: ${file.name}`, 'info');

            try {
                const result = await this.masterFile(file);
                results.push(result);
                this.addLogEntry(`Completed: ${file.name}`, 'success');
            } catch (error) {
                this.addLogEntry(`Error: ${file.name} - ${error.message}`, 'error');
                results.push({ filename: file.name, success: false, error: error.message });
            }
        }

        // Complete
        this.progressFill.style.width = '100%';
        this.progressText.textContent = 'Mastering complete!';

        // Show results
        this.showResults(results);

        // Reset button
        this.masterBtn.querySelector('.btn-text').style.display = 'inline';
        this.masterBtn.querySelector('.btn-loading').style.display = 'none';
        this.masterBtn.disabled = false;

        // Refresh output files list
        this.loadOutputFiles();
    }

    async masterFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('preset', this.selectedPreset);
        formData.append('format', this.selectedFormat);
        formData.append('noise_reduction', this.noiseReduction);
        formData.append('noise_strength', this.noiseStrength);
        formData.append('output_folder', this.outputFolder);

        const response = await fetch('/api/master', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Mastering failed');
        }

        return await response.json();
    }

    addLogEntry(message, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        this.processingLog.appendChild(entry);
        this.processingLog.scrollTop = this.processingLog.scrollHeight;
    }

    showResults(results) {
        this.resultsSection.style.display = 'block';

        const successfulResults = results.filter(r => r.success);

        if (successfulResults.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="empty-message">
                    <p>No files were successfully mastered.</p>
                </div>
            `;
            return;
        }

        this.resultsContainer.innerHTML = successfulResults.map(result => `
            <div class="result-card">
                <div class="result-info">
                    <h4>${result.output_filename}</h4>
                    <p>Size: ${result.output_size_mb} MB | Preset: ${result.preset_used} | Format: ${result.format}</p>
                </div>
                <div class="result-actions">
                    <a href="${result.download_url}" class="download-btn" download>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="7 10 12 15 17 10"/>
                            <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                        Download
                    </a>
                </div>
            </div>
        `).join('');

        // Show analysis for first successful result
        if (successfulResults.length > 0 && successfulResults[0].report) {
            this.showAnalysis(successfulResults[0].report);
        }
    }

    showAnalysis(report) {
        this.analysisSection.style.display = 'block';

        const original = report.original_analysis;
        const final = report.final_analysis;

        this.analysisGrid.innerHTML = `
            <div class="analysis-item">
                <div class="label">Original Loudness</div>
                <div class="value">${original.loudness_lufs.toFixed(1)}</div>
                <div class="unit">LUFS</div>
            </div>
            <div class="analysis-item">
                <div class="label">Final Loudness</div>
                <div class="value">${final.loudness_lufs.toFixed(1)}</div>
                <div class="unit">LUFS</div>
            </div>
            <div class="analysis-item">
                <div class="label">Original Peak</div>
                <div class="value">${original.peak_db.toFixed(1)}</div>
                <div class="unit">dB</div>
            </div>
            <div class="analysis-item">
                <div class="label">Final Peak</div>
                <div class="value">${final.peak_db.toFixed(1)}</div>
                <div class="unit">dB</div>
            </div>
            <div class="analysis-item">
                <div class="label">Dynamic Range</div>
                <div class="value">${original.dynamic_range_db.toFixed(1)}</div>
                <div class="unit">dB</div>
            </div>
            <div class="analysis-item">
                <div class="label">Duration</div>
                <div class="value">${this.formatDuration(original.duration_seconds)}</div>
                <div class="unit"></div>
            </div>
            <div class="analysis-item">
                <div class="label">Sample Rate</div>
                <div class="value">${(original.sample_rate / 1000).toFixed(1)}</div>
                <div class="unit">kHz</div>
            </div>
            <div class="analysis-item">
                <div class="label">Channels</div>
                <div class="value">${original.channels}</div>
                <div class="unit">${original.channels === 1 ? 'Mono' : 'Stereo'}</div>
            </div>
        `;
    }

    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    async loadOutputFiles() {
        try {
            const response = await fetch('/api/list-output');
            const files = await response.json();

            if (files.length === 0) {
                this.outputFiles.innerHTML = '<p class="empty-message">No mastered files yet</p>';
                return;
            }

            this.outputFiles.innerHTML = files.slice(0, 20).map(file => `
                <div class="output-file-item">
                    <span class="file-name" title="${file.filename}">${file.filename}</span>
                    <div class="file-actions">
                        <a href="${file.download_url}" class="action-btn" title="Download" download>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                        </a>
                        <button class="action-btn delete" onclick="app.deleteFile('${file.filename}')" title="Delete">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load output files:', error);
        }
    }

    async deleteFile(filename) {
        if (!confirm(`Delete ${filename}?`)) return;

        try {
            const response = await fetch(`/api/delete/${filename}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadOutputFiles();
            }
        } catch (error) {
            console.error('Failed to delete file:', error);
        }
    }
}

// Initialize app
const app = new AITrackMasterer();

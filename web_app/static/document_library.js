/**
 * Document Library JavaScript
 * Handles stored document browsing and management
 */

class DocumentLibrary {
    constructor() {
        this.documents = [];
        this.currentPage = 1;
        this.documentsPerPage = 10;
        this.init();
    }

    init() {
        this.loadDocuments();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refreshDocuments')?.addEventListener('click', () => {
            this.loadDocuments();
        });

        // Search functionality
        document.getElementById('documentSearch')?.addEventListener('input', (e) => {
            this.filterDocuments(e.target.value);
        });

        // Sort functionality
        document.getElementById('sortDocuments')?.addEventListener('change', (e) => {
            this.sortDocuments(e.target.value);
        });
    }

    async loadDocuments() {
        try {
            const response = await fetch('/documents');
            const data = await response.json();
            
            this.documents = data.documents || [];
            this.statistics = data.statistics || {};
            this.azureEnabled = data.azure_enabled || false;
            
            this.renderDocuments();
            this.renderStatistics();
            
        } catch (error) {
            console.error('Error loading documents:', error);
            this.showError('Failed to load documents');
        }
    }

    renderDocuments() {
        const container = document.getElementById('documentsContainer');
        if (!container) return;

        if (this.documents.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No documents stored yet</h5>
                    <p class="text-muted">Upload documents to see them here</p>
                </div>
            `;
            return;
        }

        const documentsHtml = this.documents.map(doc => this.renderDocumentCard(doc)).join('');
        
        container.innerHTML = `
            <div class="row">
                ${documentsHtml}
            </div>
            ${this.renderPagination()}
        `;
    }

    renderDocumentCard(doc) {
        const uploadDate = new Date(doc.upload_date).toLocaleDateString();
        const fileSize = this.formatFileSize(doc.file_size);
        
        return `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100 document-card">
                    <div class="card-header bg-light">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 text-truncate" title="${doc.filename}">
                                <i class="fas fa-file-alt text-primary me-2"></i>
                                ${doc.filename}
                            </h6>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" 
                                        data-bs-toggle="dropdown">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#" onclick="documentLibrary.viewDocument('${doc.document_id}')">
                                        <i class="fas fa-eye me-2"></i>View Details
                                    </a></li>
                                    <li><a class="dropdown-item" href="#" onclick="documentLibrary.reprocessDocument('${doc.document_id}', 'document_analysis')">
                                        <i class="fas fa-redo me-2"></i>Reprocess
                                    </a></li>
                                    <li><a class="dropdown-item" href="#" onclick="documentLibrary.downloadDocument('${doc.document_id}')">
                                        <i class="fas fa-download me-2"></i>Download
                                    </a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3">
                            <div class="col-4">
                                <div class="stat-item">
                                    <div class="stat-value text-primary">${fileSize}</div>
                                    <div class="stat-label">Size</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <div class="stat-value text-success">${uploadDate}</div>
                                    <div class="stat-label">Uploaded</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <div class="stat-value text-info">
                                        <i class="fas fa-cloud" title="Stored in Azure"></i>
                                    </div>
                                    <div class="stat-label">Cloud</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-sm" 
                                    onclick="documentLibrary.analyzeDocument('${doc.document_id}')">
                                <i class="fas fa-chart-line me-2"></i>Analyze
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" 
                                    onclick="documentLibrary.viewDocument('${doc.document_id}')">
                                <i class="fas fa-info-circle me-2"></i>View Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderStatistics() {
        const container = document.getElementById('statisticsContainer');
        if (!container || !this.statistics) return;

        const stats = this.statistics;
        
        container.innerHTML = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <h3 class="mb-0">${stats.total_documents || 0}</h3>
                            <small>Total Documents</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <h3 class="mb-0">${this.formatNumber(stats.total_tokens_processed || 0)}</h3>
                            <small>Tokens Processed</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <h3 class="mb-0">${stats.total_chunks_created || 0}</h3>
                            <small>Chunks Created</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <h3 class="mb-0">${this.azureEnabled ? 'Yes' : 'No'}</h3>
                            <small>Azure Storage</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPagination() {
        const totalPages = Math.ceil(this.documents.length / this.documentsPerPage);
        if (totalPages <= 1) return '';

        let paginationHtml = '<nav aria-label="Document pagination"><ul class="pagination justify-content-center">';
        
        for (let i = 1; i <= totalPages; i++) {
            const active = i === this.currentPage ? 'active' : '';
            paginationHtml += `
                <li class="page-item ${active}">
                    <a class="page-link" href="#" onclick="documentLibrary.changePage(${i})">${i}</a>
                </li>
            `;
        }
        
        paginationHtml += '</ul></nav>';
        return paginationHtml;
    }

    changePage(page) {
        this.currentPage = page;
        this.renderDocuments();
    }

    filterDocuments(searchTerm) {
        if (!searchTerm) {
            this.loadDocuments();
            return;
        }

        this.documents = this.documents.filter(doc => 
            doc.filename.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderDocuments();
    }

    sortDocuments(sortBy) {
        switch (sortBy) {
            case 'name':
                this.documents.sort((a, b) => a.filename.localeCompare(b.filename));
                break;
            case 'date':
                this.documents.sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));
                break;
            case 'size':
                this.documents.sort((a, b) => b.file_size - a.file_size);
                break;
        }
        this.renderDocuments();
    }

    async viewDocument(documentId) {
        try {
            const response = await fetch(`/document/${documentId}`);
            const doc = await response.json();
            
            if (doc.error) {
                this.showError(doc.error);
                return;
            }
            
            this.showDocumentDetails(doc);
            
        } catch (error) {
            console.error('Error viewing document:', error);
            this.showError('Failed to load document details');
        }
    }

    showDocumentDetails(doc) {
        const modal = document.getElementById('documentDetailsModal');
        if (!modal) return;

        const modalBody = modal.querySelector('.modal-body');
        const chunkInfo = doc.chunk_info || [];
        
        modalBody.innerHTML = `
            <div class="document-details">
                <h5 class="mb-3">${doc.filename}</h5>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Document ID:</strong><br>
                        <code class="small">${doc.document_id}</code>
                    </div>
                    <div class="col-md-6">
                        <strong>Upload Date:</strong><br>
                        ${new Date(doc.upload_timestamp).toLocaleString()}
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-4">
                        <strong>File Size:</strong><br>
                        ${this.formatFileSize(doc.file_size)}
                    </div>
                    <div class="col-md-4">
                        <strong>Total Tokens:</strong><br>
                        ${this.formatNumber(doc.total_tokens)}
                    </div>
                    <div class="col-md-4">
                        <strong>Total Chunks:</strong><br>
                        ${doc.total_chunks}
                    </div>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Document Type:</strong><br>
                        <span class="badge bg-secondary">${doc.document_type}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Processing Status:</strong><br>
                        <span class="badge bg-success">${doc.processing_status}</span>
                    </div>
                </div>
                
                ${doc.azure_url ? `
                    <div class="mb-3">
                        <strong>Azure Storage:</strong><br>
                        <i class="fas fa-cloud text-success me-2"></i>
                        <small class="text-muted">Stored in Azure Blob Storage</small>
                    </div>
                ` : ''}
                
                ${chunkInfo.length > 0 ? `
                    <div class="mb-3">
                        <strong>Chunk Information:</strong>
                        <div class="table-responsive mt-2">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Chunk</th>
                                        <th>Type</th>
                                        <th>Tokens</th>
                                        <th>Preview</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${chunkInfo.map(chunk => `
                                        <tr>
                                            <td>${chunk.chunk_index + 1}</td>
                                            <td><span class="badge bg-light text-dark">${chunk.chunk_type}</span></td>
                                            <td>${chunk.token_count}</td>
                                            <td class="text-muted small">${chunk.content_preview}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                ` : ''}
                
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <button class="btn btn-primary" onclick="documentLibrary.analyzeDocument('${doc.document_id}')">
                        <i class="fas fa-chart-line me-2"></i>Analyze Document
                    </button>
                    <button class="btn btn-outline-secondary" onclick="documentLibrary.reprocessDocument('${doc.document_id}', 'document_analysis')">
                        <i class="fas fa-redo me-2"></i>Reprocess
                    </button>
                </div>
            </div>
        `;
        
        new bootstrap.Modal(modal).show();
    }

    async analyzeDocument(documentId) {
        await this.reprocessDocument(documentId, 'document_analysis');
    }

    async reprocessDocument(documentId, action = 'document_analysis') {
        try {
            const response = await fetch(`/document/${documentId}/reprocess`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `action=${action}`
            });
            
            const result = await response.json();
            
            if (result.task_id) {
                this.showSuccess(`Document reprocessing started! Task ID: ${result.task_id}`);
                
                // Monitor the task
                this.monitorTask(result.task_id);
            } else {
                this.showError('Failed to start document reprocessing');
            }
            
        } catch (error) {
            console.error('Error reprocessing document:', error);
            this.showError('Failed to reprocess document');
        }
    }

    async monitorTask(taskId) {
        const checkTask = async () => {
            try {
                const response = await fetch(`/task/${taskId}`);
                const task = await response.json();
                
                if (task.status === 'completed') {
                    this.showSuccess('Document processing completed!');
                    // Optionally show results
                    if (task.result) {
                        this.showTaskResult(task);
                    }
                } else if (task.status === 'error') {
                    this.showError(`Processing failed: ${task.error_message}`);
                } else {
                    // Still processing, check again
                    setTimeout(checkTask, 2000);
                }
                
            } catch (error) {
                console.error('Error checking task status:', error);
            }
        };
        
        checkTask();
    }

    showTaskResult(task) {
        // This could open a modal with the analysis results
        console.log('Task completed:', task);
        // You could integrate this with the main app's result display
    }

    downloadDocument(documentId) {
        // This would need to be implemented to download from Azure
        this.showInfo('Download functionality coming soon!');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    formatNumber(num) {
        return num.toLocaleString();
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'danger');
    }

    showInfo(message) {
        this.showToast(message, 'info');
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Add to toast container
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.insertAdjacentHTML('beforeend', toastHtml);
        
        // Show toast
        const toastElement = container.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove after hiding
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Initialize when page loads
let documentLibrary;
document.addEventListener('DOMContentLoaded', () => {
    documentLibrary = new DocumentLibrary();
});
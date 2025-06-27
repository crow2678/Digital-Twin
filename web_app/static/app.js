// Digital Twin Enterprise Dashboard JavaScript

// Global variables
let processingTasks = {};
let refreshInterval;
let currentResults = null;

// Action descriptions
const actionDescriptions = {
    'document_analysis': 'Analyzes documents to extract key points, action items, risks, opportunities, and smart questions for clarification.',
    'meeting_processing': 'Processes meeting transcripts to extract your action items, questions to ask others, follow-up emails, and next steps.',
    'smart_questions': 'Generates intelligent questions based on the content to help clarify unclear points, explore opportunities, and identify risks.',
    'email_drafting': 'Drafts professional email responses based on the original email and your intended response. Use format: [Original Email] | [Your Intent]',
    'custom': 'Analyze any text content with AI-powered insights and recommendations.'
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initial status check
    checkTwinStatus();
    refreshTasks();
    startAutoRefresh();
    setupFileUpload();
    
    // Set up periodic status checking (every 10 seconds)
    setInterval(checkTwinStatus, 10000);
});

// Check digital twin status
async function checkTwinStatus() {
    try {
        const response = await fetch('/twin/status');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const status = await response.json();
        
        const statusElement = document.getElementById('twin-status');
        if (status.status === 'available') {
            statusElement.innerHTML = 'Connected';
            statusElement.className = 'text-success';
            // Update parent element icon
            const parentSpan = statusElement.parentElement;
            const icon = parentSpan.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-circle text-success me-1';
            }
        } else if (status.status === 'unavailable') {
            statusElement.innerHTML = 'Twin Unavailable';
            statusElement.className = 'text-warning';
            // Update parent element icon
            const parentSpan = statusElement.parentElement;
            const icon = parentSpan.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-circle text-warning me-1';
            }
            console.warn('Digital Twin not initialized:', status.message);
        } else {
            statusElement.innerHTML = 'Disconnected';
            statusElement.className = 'text-danger';
            // Update parent element icon
            const parentSpan = statusElement.parentElement;
            const icon = parentSpan.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-circle text-danger me-1';
            }
        }
    } catch (error) {
        console.error('Failed to check twin status:', error);
        const statusElement = document.getElementById('twin-status');
        statusElement.innerHTML = 'Error';
        statusElement.className = 'text-warning';
        // Update parent element icon
        const parentSpan = statusElement.parentElement;
        const icon = parentSpan.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-circle text-warning me-1';
        }
    }
}

// Show upload modal
function showUploadModal(action) {
    document.getElementById('upload-action').value = action;
    document.getElementById('uploadModalTitle').textContent = getActionTitle(action);
    document.getElementById('action-description').textContent = actionDescriptions[action];
    
    const modal = new bootstrap.Modal(document.getElementById('uploadModal'));
    modal.show();
}

// Show text modal
function showTextModal(action) {
    document.getElementById('text-action').value = action;
    document.getElementById('textModalTitle').textContent = getActionTitle(action);
    
    const modal = new bootstrap.Modal(document.getElementById('textModal'));
    modal.show();
}

// Get action title
function getActionTitle(action) {
    const titles = {
        'document_analysis': 'Document Analysis',
        'meeting_processing': 'Meeting Processing',
        'smart_questions': 'Smart Questions',
        'email_drafting': 'Email Drafting',
        'custom': 'Custom Analysis'
    };
    return titles[action] || 'Analysis';
}

// Upload file
async function uploadFile() {
    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);
    
    try {
        showUploadProgress();
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            hideUploadProgress();
            bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
            
            // Add task to processing queue
            addTaskToQueue(result.task_id, {
                status: 'pending',
                action: formData.get('action'),
                filename: formData.get('file').name,
                progress: 0
            });
            
            showAlert('success', 'File uploaded successfully! Processing started.');
            form.reset();
        } else {
            hideUploadProgress();
            showAlert('danger', result.detail || 'Upload failed');
        }
    } catch (error) {
        hideUploadProgress();
        showAlert('danger', 'Network error: ' + error.message);
    }
}

// Process text
async function processText() {
    const form = document.getElementById('textForm');
    const formData = new FormData(form);
    
    const requestData = {
        action: formData.get('action'),
        content: formData.get('content'),
        filename: formData.get('filename') || 'text_input.txt',
        user_id: formData.get('user_id')
    };
    
    try {
        showTextProgress();
        
        const response = await fetch('/process-text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            hideTextProgress();
            bootstrap.Modal.getInstance(document.getElementById('textModal')).hide();
            
            // Add task to processing queue
            addTaskToQueue(result.task_id, {
                status: 'pending',
                action: requestData.action,
                filename: requestData.filename,
                progress: 0
            });
            
            showAlert('success', 'Text processing started!');
            form.reset();
        } else {
            hideTextProgress();
            showAlert('danger', result.detail || 'Processing failed');
        }
    } catch (error) {
        hideTextProgress();
        showAlert('danger', 'Network error: ' + error.message);
    }
}

// Show upload progress
function showUploadProgress() {
    const button = document.querySelector('#uploadModal .btn-primary');
    button.disabled = true;
    button.innerHTML = '<div class="loading-spinner me-2"></div>Uploading...';
}

// Hide upload progress
function hideUploadProgress() {
    const button = document.querySelector('#uploadModal .btn-primary');
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-upload me-2"></i>Process Document';
}

// Show text progress
function showTextProgress() {
    const button = document.querySelector('#textModal .btn-primary');
    button.disabled = true;
    button.innerHTML = '<div class="loading-spinner me-2"></div>Processing...';
}

// Hide text progress
function hideTextProgress() {
    const button = document.querySelector('#textModal .btn-primary');
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-cogs me-2"></i>Analyze Text';
}

// Add task to processing queue
function addTaskToQueue(taskId, taskData) {
    processingTasks[taskId] = taskData;
    updateProcessingQueue();
}

// Update processing queue display
function updateProcessingQueue() {
    const queueElement = document.getElementById('processing-queue');
    const tasks = Object.entries(processingTasks);
    
    if (tasks.length === 0) {
        queueElement.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-inbox fa-3x mb-3"></i>
                <p>No active tasks. Upload a document or paste text to get started.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    for (const [taskId, task] of tasks) {
        html += createTaskElement(taskId, task);
    }
    
    queueElement.innerHTML = html;
    updateStats();
}

// Create task element HTML
function createTaskElement(taskId, task) {
    const statusClass = getStatusClass(task.status);
    const statusIcon = getStatusIcon(task.status);
    const actionIcon = getActionIcon(task.action);
    
    return `
        <div class="processing-item ${statusClass} fade-in">
            <div class="row align-items-center">
                <div class="col">
                    <div class="d-flex align-items-center mb-2">
                        <i class="${actionIcon} me-2 text-primary"></i>
                        <h6 class="mb-0">${getActionTitle(task.action)}</h6>
                        <span class="status-badge status-${task.status} ms-auto">
                            ${statusIcon} ${task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                        </span>
                    </div>
                    <div class="small text-muted mb-2">
                        <i class="fas fa-file me-1"></i>${task.filename}
                    </div>
                    ${task.status === 'processing' || task.status === 'pending' ? `
                        <div class="progress mb-2">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 style="width: ${task.progress}%"></div>
                        </div>
                    ` : ''}
                    ${task.error_message ? `
                        <div class="alert alert-danger py-2 mb-2">
                            <small><i class="fas fa-exclamation-triangle me-1"></i>${task.error_message}</small>
                        </div>
                    ` : ''}
                </div>
                <div class="col-auto">
                    <div class="btn-group">
                        ${task.status === 'completed' ? `
                            <button class="btn btn-sm btn-outline-primary" onclick="viewResults('${taskId}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-outline-secondary" onclick="deleteTask('${taskId}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Get status class
function getStatusClass(status) {
    const classes = {
        'pending': 'pending',
        'processing': 'processing',
        'completed': 'completed',
        'error': 'error'
    };
    return classes[status] || '';
}

// Get status icon
function getStatusIcon(status) {
    const icons = {
        'pending': '<i class="fas fa-clock"></i>',
        'processing': '<i class="fas fa-spinner fa-spin"></i>',
        'completed': '<i class="fas fa-check"></i>',
        'error': '<i class="fas fa-exclamation-triangle"></i>'
    };
    return icons[status] || '';
}

// Get action icon
function getActionIcon(action) {
    const icons = {
        'document_analysis': 'fas fa-file-alt',
        'meeting_processing': 'fas fa-users',
        'smart_questions': 'fas fa-question-circle',
        'email_drafting': 'fas fa-envelope',
        'custom': 'fas fa-cogs'
    };
    return icons[action] || 'fas fa-file';
}

// Refresh tasks
async function refreshTasks() {
    try {
        const response = await fetch('/tasks');
        const data = await response.json();
        
        // Update processing tasks
        for (const task of data.tasks) {
            if (processingTasks[task.task_id]) {
                processingTasks[task.task_id] = {
                    ...processingTasks[task.task_id],
                    status: task.status,
                    progress: task.progress
                };
            }
        }
        
        // Get detailed status for each task
        for (const taskId of Object.keys(processingTasks)) {
            try {
                const taskResponse = await fetch(`/task/${taskId}`);
                if (taskResponse.ok) {
                    const taskData = await taskResponse.json();
                    processingTasks[taskId] = {
                        ...processingTasks[taskId],
                        status: taskData.status,
                        progress: taskData.progress,
                        error_message: taskData.error_message,
                        result: taskData.result
                    };
                }
            } catch (error) {
                console.error(`Failed to refresh task ${taskId}:`, error);
            }
        }
        
        updateProcessingQueue();
    } catch (error) {
        console.error('Failed to refresh tasks:', error);
    }
}

// Start auto refresh
function startAutoRefresh() {
    refreshInterval = setInterval(refreshTasks, 2000); // Refresh every 2 seconds
}

// Stop auto refresh
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// View results
async function viewResults(taskId) {
    try {
        const response = await fetch(`/task/${taskId}`);
        const data = await response.json();
        
        if (data.result) {
            currentResults = data.result;
            displayResults(data.result);
            
            const modal = new bootstrap.Modal(document.getElementById('resultsModal'));
            modal.show();
        } else {
            showAlert('warning', 'No results available yet.');
        }
    } catch (error) {
        showAlert('danger', 'Failed to load results: ' + error.message);
    }
}

// Display results
function displayResults(result) {
    const container = document.getElementById('results-content');
    let html = '';
    
    // Header
    html += `
        <div class="mb-4">
            <h4><i class="${getActionIcon(result.action)} me-2"></i>${getActionTitle(result.action)} Results</h4>
            <div class="text-muted">
                <i class="fas fa-file me-1"></i>${result.filename} • 
                <i class="fas fa-clock me-1"></i>${new Date(result.processed_at).toLocaleString()}
            </div>
        </div>
    `;
    
    // Results based on type
    if (result.type === 'document_analysis') {
        html += generateDocumentAnalysisResults(result);
    } else if (result.type === 'meeting_processing') {
        html += generateMeetingProcessingResults(result);
    } else if (result.type === 'smart_questions') {
        html += generateSmartQuestionsResults(result);
    } else if (result.type === 'email_drafting') {
        html += generateEmailDraftingResults(result);
    }
    
    container.innerHTML = html;
}

// Generate document analysis results
function generateDocumentAnalysisResults(result) {
    let html = '';
    
    if (result.summary) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-file-text me-2"></i>Summary</h5>
                <p>${result.summary}</p>
            </div>
        `;
    }
    
    if (result.key_points && result.key_points.length > 0) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-list me-2"></i>Key Points</h5>
                <ul>
                    ${result.key_points.map(point => `<li>${point}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.action_items && result.action_items.length > 0) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-tasks me-2"></i>Action Items</h5>
                ${result.action_items.map(item => `
                    <div class="action-item ${item.priority}-priority">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${item.task}</strong>
                                <div class="small text-muted">
                                    ${item.assignee ? `Assigned to: ${item.assignee}` : ''}
                                    ${item.due_date ? ` • Due: ${item.due_date}` : ''}
                                    ${item.estimated_time ? ` • Est. ${item.estimated_time} min` : ''}
                                </div>
                                ${item.context ? `<div class="small">${item.context}</div>` : ''}
                            </div>
                            <span class="badge bg-${getPriorityColor(item.priority)}">${item.priority}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (result.questions && result.questions.length > 0) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-question-circle me-2"></i>Smart Questions</h5>
                ${result.questions.map(q => `
                    <div class="question-item">
                        <div class="fw-bold">${q.question}</div>
                        <div class="small text-muted">
                            Category: ${q.category} • Urgency: ${q.urgency}
                            ${q.target_person ? ` • Ask: ${q.target_person}` : ''}
                        </div>
                        ${q.reasoning ? `<div class="small mt-1">${q.reasoning}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (result.risks && result.risks.length > 0) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-exclamation-triangle me-2 text-warning"></i>Risks</h5>
                <ul>
                    ${result.risks.map(risk => `<li class="text-warning">${risk}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.opportunities && result.opportunities.length > 0) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-lightbulb me-2 text-success"></i>Opportunities</h5>
                <ul>
                    ${result.opportunities.map(opp => `<li class="text-success">${opp}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    return html;
}

// Generate meeting processing results
function generateMeetingProcessingResults(result) {
    let html = '';
    
    if (result.my_action_items && result.my_action_items.length > 0) {
        html += `
            <div class="result-section border-start-primary">
                <h5><i class="fas fa-user me-2"></i>My Action Items</h5>
                ${result.my_action_items.map(item => `
                    <div class="action-item ${item.priority}-priority">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <strong>${item.task}</strong>
                                <div class="small text-muted">
                                    ${item.due_date ? `Due: ${item.due_date}` : ''}
                                    ${item.estimated_time ? ` • Est. ${item.estimated_time} min` : ''}
                                </div>
                            </div>
                            <span class="badge bg-${getPriorityColor(item.priority)}">${item.priority}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (result.others_action_items && result.others_action_items.length > 0) {
        html += `
            <div class="result-section border-start-secondary">
                <h5><i class="fas fa-users me-2"></i>Others' Action Items</h5>
                ${result.others_action_items.map(item => `
                    <div class="action-item">
                        <strong>${item.assignee}:</strong> ${item.task}
                        ${item.due_date ? `<div class="small text-muted">Due: ${item.due_date}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (result.questions_to_ask && result.questions_to_ask.length > 0) {
        html += `
            <div class="result-section border-start-info">
                <h5><i class="fas fa-question-circle me-2"></i>Questions to Ask</h5>
                ${result.questions_to_ask.map(q => `
                    <div class="question-item">
                        <div class="fw-bold">${q.question}</div>
                        ${q.target_person ? `<div class="small text-muted">Ask: ${q.target_person}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (result.next_steps && result.next_steps.length > 0) {
        html += `
            <div class="result-section border-start-success">
                <h5><i class="fas fa-arrow-right me-2"></i>Next Steps</h5>
                <ul>
                    ${result.next_steps.map(step => `<li>${step}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.decisions_made && result.decisions_made.length > 0) {
        html += `
            <div class="result-section border-start-warning">
                <h5><i class="fas fa-gavel me-2"></i>Decisions Made</h5>
                <ul>
                    ${result.decisions_made.map(decision => `<li>${decision}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (result.meeting_effectiveness) {
        html += `
            <div class="result-section">
                <h5><i class="fas fa-chart-line me-2"></i>Meeting Effectiveness</h5>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-3" style="height: 25px;">
                        <div class="progress-bar" style="width: ${result.meeting_effectiveness * 10}%">
                            ${result.meeting_effectiveness}/10
                        </div>
                    </div>
                    <span class="fw-bold">${result.meeting_effectiveness}/10</span>
                </div>
            </div>
        `;
    }
    
    return html;
}

// Generate smart questions results
function generateSmartQuestionsResults(result) {
    let html = `
        <div class="result-section">
            <h5><i class="fas fa-lightbulb me-2"></i>Generated Questions</h5>
            <div class="mb-3">
                <strong>Context:</strong> ${result.context}
            </div>
            ${result.questions.map(q => `
                <div class="question-item">
                    <div class="fw-bold">${q.question}</div>
                    <div class="small text-muted">
                        Category: ${q.category} • Urgency: ${q.urgency}
                        ${q.target_person ? ` • Ask: ${q.target_person}` : ''}
                    </div>
                    ${q.reasoning ? `<div class="small mt-1 text-info">${q.reasoning}</div>` : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    return html;
}

// Generate email drafting results
function generateEmailDraftingResults(result) {
    let html = `
        <div class="result-section">
            <h5><i class="fas fa-envelope me-2"></i>Email Draft</h5>
            
            <div class="mb-3">
                <strong>Original Email:</strong>
                <div class="bg-light p-3 rounded mt-2">
                    ${result.original_email.replace(/\n/g, '<br>')}
                </div>
            </div>
            
            <div class="mb-3">
                <strong>Your Intent:</strong>
                <div class="text-muted">${result.intent}</div>
            </div>
            
            <div class="email-draft">
                <div class="mb-2"><strong>To:</strong> ${result.draft.to}</div>
                <div class="mb-2"><strong>Subject:</strong> ${result.draft.subject}</div>
                <div class="mb-3"><strong>Tone:</strong> <span class="badge bg-info">${result.draft.tone}</span></div>
                
                <div class="border p-3 bg-white">
                    ${result.draft.body.replace(/\n/g, '<br>')}
                </div>
                
                <div class="mt-2 d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary" onclick="copyToClipboard('${escapeHtml(result.draft.body)}')">
                        <i class="fas fa-copy me-1"></i>Copy Body
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('${escapeHtml(result.draft.subject)}')">
                        <i class="fas fa-copy me-1"></i>Copy Subject
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return html;
}

// Get priority color
function getPriorityColor(priority) {
    const colors = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
    };
    return colors[priority] || 'secondary';
}

// Delete task
async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            const response = await fetch(`/task/${taskId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                delete processingTasks[taskId];
                updateProcessingQueue();
                showAlert('success', 'Task deleted successfully.');
            } else {
                showAlert('danger', 'Failed to delete task.');
            }
        } catch (error) {
            showAlert('danger', 'Network error: ' + error.message);
        }
    }
}

// Update stats
function updateStats() {
    const totalTasks = Object.keys(processingTasks).length;
    const activeTasks = Object.values(processingTasks).filter(task => 
        task.status === 'processing' || task.status === 'pending'
    ).length;
    const completedTasks = Object.values(processingTasks).filter(task => 
        task.status === 'completed'
    ).length;
    const successRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 100;
    
    document.getElementById('tasks-count').textContent = totalTasks;
    document.getElementById('active-tasks').textContent = activeTasks;
    document.getElementById('success-rate').textContent = `${successRate}%`;
}

// Export results
function exportResults() {
    if (currentResults) {
        const dataStr = JSON.stringify(currentResults, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `digital_twin_results_${new Date().getTime()}.json`;
        link.click();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('success', 'Copied to clipboard!');
    }).catch(() => {
        showAlert('warning', 'Failed to copy to clipboard.');
    });
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, "\\'");
}

// Show alert
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container-fluid');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = alertHtml;
    container.insertBefore(tempDiv.firstElementChild, container.firstElementChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }
    }, 5000);
}

// Setup file upload drag and drop
function setupFileUpload() {
    const fileInput = document.getElementById('file-input');
    const uploadModal = document.getElementById('uploadModal');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadModal.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadModal.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadModal.addEventListener(eventName, unhighlight, false);
    });
    
    uploadModal.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        uploadModal.classList.add('dragover');
    }
    
    function unhighlight(e) {
        uploadModal.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
        }
    }
}
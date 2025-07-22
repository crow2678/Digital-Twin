// Digital Cockpit JavaScript - AI-Powered Command Center
class DigitalCockpit {
    constructor() {
        this.tasks = {
            assignedToMe: [],
            assignedToOthers: [],
            completed: []
        };
        this.documents = {
            processing: [],
            completed: []
        };
        this.userProfile = {};
        this.init();
    }

    init() {
        this.loadUserProfile();
        this.loadTasks();
        this.loadDocuments();
        this.setupEventListeners();
        this.startPeriodicUpdates();
        this.loadAISuggestions();
    }

    async loadUserProfile() {
        try {
            const response = await fetch('/api/user-profile');
            this.userProfile = await response.json();
            console.log('User profile loaded:', this.userProfile);
        } catch (error) {
            console.error('Error loading user profile:', error);
            // Default profile
            this.userProfile = {
                name: 'Paresh',
                email: 'paresh@tavant.com',
                role: 'Product Manager',
                department: 'Technology',
                skills: ['AI/ML', 'Product Strategy', 'Team Leadership'],
                preferences: {
                    taskAssignment: 'smart',
                    emailStyle: 'professional',
                    workingHours: '9-6 PST'
                }
            };
        }
    }

    async loadTasks() {
        try {
            const response = await fetch('/api/smart-tasks/Paresh');
            const data = await response.json();
            
            // Handle the API response structure
            const tasks = data.success ? data.tasks : [];
            
            // Categorize tasks using LLM-based assignment
            await this.categorizeTasks(tasks);
            this.renderTasks();
            this.updateTaskCounts();
        } catch (error) {
            console.error('Error loading tasks:', error);
            this.loadMockTasks();
        }
    }

    async categorizeTasks(tasks) {
        // Reset categories
        this.tasks = {
            assignedToMe: [],
            assignedToOthers: [],
            completed: []
        };

        for (const task of tasks) {
            if (task.status === 'completed') {
                this.tasks.completed.push(task);
            } else {
                // Use LLM to determine assignment based on user profile
                const assignment = await this.getTaskAssignment(task);
                if (assignment === 'me') {
                    this.tasks.assignedToMe.push(task);
                } else {
                    this.tasks.assignedToOthers.push(task);
                }
            }
        }
    }

    async getTaskAssignment(task) {
        try {
            const response = await fetch('/api/llm/task-assignment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task: task,
                    userProfile: this.userProfile
                })
            });
            const result = await response.json();
            return result.assignment; // 'me' or 'others'
        } catch (error) {
            console.error('Error getting task assignment:', error);
            // Fallback logic
            return this.fallbackTaskAssignment(task);
        }
    }

    fallbackTaskAssignment(task) {
        const title = task.title.toLowerCase();
        const description = task.description.toLowerCase();
        
        // Simple keyword-based assignment
        const myKeywords = ['review', 'approve', 'strategy', 'decision', 'plan', 'meeting'];
        const delegateKeywords = ['implement', 'code', 'test', 'deploy', 'design'];
        
        const content = `${title} ${description}`;
        
        const myScore = myKeywords.reduce((score, word) => 
            score + (content.includes(word) ? 1 : 0), 0);
        const delegateScore = delegateKeywords.reduce((score, word) => 
            score + (content.includes(word) ? 1 : 0), 0);
        
        return myScore >= delegateScore ? 'me' : 'others';
    }

    renderTasks() {
        this.renderTaskSection('my-tasks', this.tasks.assignedToMe, 'assigned-to-me');
        this.renderTaskSection('delegated-tasks', this.tasks.assignedToOthers, 'assigned-to-others');
        this.renderTaskSection('completed-tasks', this.tasks.completed, 'completed');
    }

    renderTaskSection(containerId, tasks, taskType) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        if (tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>No tasks in this category</p>
                </div>
            `;
            return;
        }

        tasks.forEach(task => {
            const taskElement = this.createTaskElement(task, taskType);
            container.appendChild(taskElement);
        });
    }

    createTaskElement(task, taskType) {
        const taskDiv = document.createElement('div');
        taskDiv.className = `task-card ${taskType} priority-${task.priority || 'medium'}`;
        
        const priorityIcon = this.getPriorityIcon(task.priority);
        const statusBadge = this.getStatusBadge(task.status);
        
        taskDiv.innerHTML = `
            <div class="task-header">
                <div class="task-title">${task.title}</div>
                <div class="d-flex align-items-center gap-2">
                    ${priorityIcon}
                    ${statusBadge}
                </div>
            </div>
            <div class="task-description text-secondary mb-2">${task.description}</div>
            <div class="task-meta">
                <span><i class="fas fa-user"></i> ${task.assigned_to || 'Unassigned'}</span>
                <span><i class="fas fa-calendar"></i> ${this.formatDate(task.due_date)}</span>
                <span><i class="fas fa-folder"></i> ${task.source_document || 'Manual'}</span>
            </div>
            <div class="task-actions">
                ${this.getTaskActions(task, taskType)}
            </div>
        `;

        return taskDiv;
    }

    getTaskActions(task, taskType) {
        if (taskType === 'completed') {
            return `
                <button class="btn btn-outline btn-sm" onclick="cockpit.viewTaskDetails('${task.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
            `;
        }

        if (taskType === 'assigned-to-me') {
            return `
                <button class="btn btn-smart btn-sm" onclick="cockpit.askAVAForHelp('${task.id}')">
                    <i class="fas fa-robot"></i> Ask AVA
                </button>
                <button class="btn btn-outline btn-sm" onclick="cockpit.draftEmailForTask('${task.id}')">
                    <i class="fas fa-envelope"></i> Draft Email
                </button>
                <button class="btn btn-outline btn-sm" onclick="cockpit.completeTask('${task.id}')">
                    <i class="fas fa-check"></i> Complete
                </button>
            `;
        }

        if (taskType === 'assigned-to-others') {
            return `
                <button class="btn btn-smart btn-sm" onclick="cockpit.requestUpdate('${task.id}')">
                    <i class="fas fa-question-circle"></i> Request Update
                </button>
                <button class="btn btn-outline btn-sm" onclick="cockpit.draftFollowUpEmail('${task.id}')">
                    <i class="fas fa-paper-plane"></i> Follow Up
                </button>
            `;
        }

        return '';
    }

    getPriorityIcon(priority) {
        const icons = {
            high: '<i class="fas fa-exclamation-triangle text-danger"></i>',
            medium: '<i class="fas fa-minus-circle text-warning"></i>',
            low: '<i class="fas fa-arrow-down text-success"></i>'
        };
        return icons[priority] || icons.medium;
    }

    getStatusBadge(status) {
        const badges = {
            pending: '<span class="badge bg-warning">Pending</span>',
            in_progress: '<span class="badge bg-info">In Progress</span>',
            completed: '<span class="badge bg-success">Completed</span>',
            blocked: '<span class="badge bg-danger">Blocked</span>'
        };
        return badges[status] || badges.pending;
    }

    updateTaskCounts() {
        document.getElementById('assigned-to-me-count').textContent = this.tasks.assignedToMe.length;
        document.getElementById('assigned-to-others-count').textContent = this.tasks.assignedToOthers.length;
        document.getElementById('completed-count').textContent = this.tasks.completed.length;
        
        document.getElementById('my-tasks-badge').textContent = this.tasks.assignedToMe.length;
        document.getElementById('delegated-tasks-badge').textContent = this.tasks.assignedToOthers.length;
        document.getElementById('completed-tasks-badge').textContent = this.tasks.completed.length;
    }

    async loadAISuggestions() {
        try {
            const response = await fetch('/api/llm/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userProfile: this.userProfile,
                    tasks: this.tasks,
                    documents: this.documents
                })
            });
            const suggestions = await response.json();
            this.renderSuggestions(suggestions);
        } catch (error) {
            console.error('Error loading AI suggestions:', error);
            this.renderDefaultSuggestions();
        }
    }

    renderSuggestions(suggestions) {
        const container = document.getElementById('ai-suggestions');
        container.innerHTML = '';

        suggestions.forEach(suggestion => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'suggestion-item';
            suggestionElement.innerHTML = `
                <div class="d-flex align-items-start gap-3">
                    <i class="fas ${suggestion.icon} mt-1"></i>
                    <div>
                        <strong>${suggestion.title}:</strong> ${suggestion.description}
                        <div class="mt-2">
                            ${suggestion.actions.map(action => 
                                `<button class="btn btn-light btn-sm me-2" onclick="cockpit.${action.handler}('${action.params}')">
                                    <i class="fas ${action.icon}"></i> ${action.label}
                                </button>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(suggestionElement);
        });
    }

    renderDefaultSuggestions() {
        // Keep the existing default suggestions from HTML
        console.log('Using default AI suggestions');
    }

    async askAVAForHelp(taskId) {
        const task = this.findTaskById(taskId);
        if (!task) return;

        const message = `Help me with this task: "${task.title}". ${task.description}`;
        this.sendAVAMessage(message);
        this.toggleChat();
    }

    async draftEmailForTask(taskId) {
        const task = this.findTaskById(taskId);
        if (!task) return;

        try {
            const response = await fetch('/api/llm/draft-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task: task,
                    userProfile: this.userProfile,
                    type: 'task_action'
                })
            });
            const emailDraft = await response.json();
            this.showEmailModal(emailDraft);
        } catch (error) {
            console.error('Error drafting email:', error);
            this.showEmailModal({
                to: task.assigned_to || '',
                subject: `Regarding: ${task.title}`,
                body: `Hi,\n\nI wanted to follow up on the task "${task.title}".\n\n${task.description}\n\nPlease let me know if you need any clarification.\n\nBest regards,\n${this.userProfile.name}`
            });
        }
    }

    async completeTask(taskId) {
        try {
            const response = await fetch(`/api/smart-tasks/${taskId}/complete?user_id=Paresh`, {
                method: 'POST'
            });
            if (response.ok) {
                this.loadTasks(); // Refresh tasks
                this.showNotification('Task completed successfully!', 'success');
            }
        } catch (error) {
            console.error('Error completing task:', error);
            this.showNotification('Error completing task', 'error');
        }
    }

    findTaskById(taskId) {
        const allTasks = [
            ...this.tasks.assignedToMe,
            ...this.tasks.assignedToOthers,
            ...this.tasks.completed
        ];
        return allTasks.find(task => task.id === taskId);
    }

    showEmailModal(emailData) {
        document.getElementById('email-to').value = emailData.to || '';
        document.getElementById('email-subject').value = emailData.subject || '';
        document.getElementById('email-body').value = emailData.body || '';
        
        const modal = new bootstrap.Modal(document.getElementById('emailModal'));
        modal.show();
    }

    toggleChat() {
        const chatWidget = document.getElementById('ava-chat');
        const chatToggle = document.getElementById('chat-toggle');
        
        if (chatWidget.style.display === 'none' || !chatWidget.style.display) {
            chatWidget.style.display = 'flex';
            chatToggle.style.display = 'none';
        } else {
            chatWidget.style.display = 'none';
            chatToggle.style.display = 'block';
        }
    }

    async sendAVAMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        
        // Add user message
        this.addChatMessage(message, 'user');
        
        // Clear input
        document.getElementById('chat-input').value = '';
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    user_id: 'Paresh',
                    context: {
                        tasks: this.tasks,
                        userProfile: this.userProfile
                    }
                })
            });
            
            const data = await response.json();
            this.addChatMessage(data.response, 'ava');
        } catch (error) {
            console.error('Error sending message to AVA:', error);
            this.addChatMessage('Sorry, I encountered an error. Please try again.', 'ava');
        }
    }

    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${sender === 'user' ? 'text-end' : ''}`;
        
        const alertClass = sender === 'user' ? 'alert-primary' : 'alert-light';
        const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        messageDiv.innerHTML = `
            <div class="alert ${alertClass}">
                <i class="${icon} me-2"></i>
                ${message}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showNotification(message, type = 'info') {
        // Simple notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    setupEventListeners() {
        // Chat input enter key
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (message) {
            this.sendAVAMessage(message);
        }
    }

    startPeriodicUpdates() {
        // Refresh data every 5 minutes
        setInterval(() => {
            this.loadTasks();
            this.loadDocuments();
            this.loadAISuggestions();
        }, 300000);
    }

    loadMockTasks() {
        // Mock data for demonstration
        this.tasks = {
            assignedToMe: [
                {
                    id: '1',
                    title: 'Review RFP Automation Proposal',
                    description: 'Analyze the technical feasibility and provide recommendations for the automation scope.',
                    priority: 'high',
                    status: 'pending',
                    assigned_to: 'Paresh',
                    due_date: '2024-01-15',
                    source_document: 'RFP Scope Automation.docx'
                },
                {
                    id: '2',
                    title: 'Finalize Meeting Schedule',
                    description: 'Coordinate with stakeholders to finalize the product strategy meeting.',
                    priority: 'medium',
                    status: 'in_progress',
                    assigned_to: 'Paresh',
                    due_date: '2024-01-12',
                    source_document: 'Meeting Minutes.docx'
                },
                {
                    id: '5',
                    title: 'Strategic Decision on AI Implementation',
                    description: 'Review AI implementation roadmap and make strategic decisions on priorities.',
                    priority: 'high',
                    status: 'pending',
                    assigned_to: 'Paresh',
                    due_date: '2024-01-18',
                    source_document: 'AI Strategy Document.docx'
                }
            ],
            assignedToOthers: [
                {
                    id: '3',
                    title: 'Implement API Integration',
                    description: 'Develop the backend API integration for the new automation features.',
                    priority: 'high',
                    status: 'pending',
                    assigned_to: 'Dev Team',
                    due_date: '2024-01-20',
                    source_document: 'Technical Specification.docx'
                },
                {
                    id: '6',
                    title: 'UI Design for Dashboard',
                    description: 'Create mockups and designs for the new dashboard interface.',
                    priority: 'medium',
                    status: 'in_progress',
                    assigned_to: 'Design Team',
                    due_date: '2024-01-22',
                    source_document: 'UI Requirements.docx'
                }
            ],
            completed: [
                {
                    id: '4',
                    title: 'Document Analysis Complete',
                    description: 'Analyzed the contract terms and extracted key requirements.',
                    priority: 'medium',
                    status: 'completed',
                    assigned_to: 'Paresh',
                    due_date: '2024-01-10',
                    source_document: 'Contract Agreement.docx'
                },
                {
                    id: '7',
                    title: 'Team Budget Review',
                    description: 'Completed quarterly budget review and approved resource allocation.',
                    priority: 'high',
                    status: 'completed',
                    assigned_to: 'Paresh',
                    due_date: '2024-01-08',
                    source_document: 'Budget Report.xlsx'
                }
            ]
        };
        
        this.renderTasks();
        this.updateTaskCounts();
    }

    async loadDocuments() {
        // Load document processing status
        try {
            const response = await fetch('/api/documents/status');
            const documents = await response.json();
            this.documents = documents;
            this.renderDocuments();
        } catch (error) {
            console.error('Error loading documents:', error);
            this.loadMockDocuments();
        }
    }

    loadMockDocuments() {
        this.documents = {
            processing: [
                {
                    id: '1',
                    name: 'New Contract.docx',
                    status: 'analyzing',
                    progress: 75,
                    uploaded_at: '2024-01-11T10:30:00Z'
                }
            ],
            completed: [
                {
                    id: '2',
                    name: 'RFP Scope Automation.docx',
                    status: 'completed',
                    progress: 100,
                    uploaded_at: '2024-01-10T14:20:00Z',
                    tasks_created: 5
                }
            ]
        };
        this.renderDocuments();
    }

    renderDocuments() {
        this.renderDocumentSection('processing-queue', this.documents.processing);
        this.renderDocumentSection('completed-documents', this.documents.completed);
        
        // Update document count
        document.getElementById('documents-processed').textContent = this.documents.completed.length;
    }

    renderDocumentSection(containerId, documents) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        if (documents.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-folder-open fa-2x mb-2"></i>
                    <p>No documents</p>
                </div>
            `;
            return;
        }

        documents.forEach(doc => {
            const docElement = document.createElement('div');
            docElement.className = 'mb-3 p-3 border rounded bg-white';
            
            const analysisTypeIcon = {
                'comprehensive': 'fas fa-microscope',
                'summary': 'fas fa-file-text',
                'questions': 'fas fa-question-circle',
                'actionItems': 'fas fa-tasks'
            };
            
            const progressColor = doc.progress < 30 ? 'bg-danger' : doc.progress < 70 ? 'bg-warning' : 'bg-success';
            
            docElement.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <i class="${analysisTypeIcon[doc.analysis_type] || 'fas fa-file'} text-primary"></i>
                            <h6 class="mb-0">${doc.name}</h6>
                        </div>
                        <div class="d-flex gap-2 align-items-center">
                            <small class="text-muted">${this.formatDate(doc.uploaded_at)}</small>
                            ${doc.analysis_type ? `<span class="badge bg-light text-dark">${doc.analysis_type}</span>` : ''}
                            ${doc.tasks_created ? `<span class="badge bg-info">${doc.tasks_created} tasks created</span>` : ''}
                        </div>
                    </div>
                    <div class="text-end" style="min-width: 120px;">
                        ${doc.progress !== undefined && doc.progress < 100 ? `
                            <div class="progress mb-2" style="width: 100px; height: 8px;">
                                <div class="progress-bar ${progressColor}" style="width: ${doc.progress}%"></div>
                            </div>
                            <small class="text-muted">${Math.round(doc.progress)}%</small>
                        ` : ''}
                        <div class="mt-1">
                            <span class="badge ${
                                doc.status === 'completed' ? 'bg-success' : 
                                doc.status === 'failed' ? 'bg-danger' : 
                                doc.status === 'analyzing' ? 'bg-info' : 'bg-warning'
                            }">${doc.status}</span>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(docElement);
        });
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }

    addToProcessingQueue(document) {
        this.documents.processing.push(document);
        this.renderDocuments();
        
        // Simulate progress updates
        this.simulateProgress(document.id);
    }

    updateProcessingStatus(docId, status, progress) {
        const doc = this.documents.processing.find(d => d.id === docId);
        if (doc) {
            doc.status = status;
            doc.progress = progress;
            
            if (status === 'completed') {
                // Move to completed
                this.documents.processing = this.documents.processing.filter(d => d.id !== docId);
                doc.tasks_created = Math.floor(Math.random() * 5) + 1; // Random task count
                this.documents.completed.unshift(doc);
                
                // Update document status via API
                this.updateDocumentStatusAPI('move_to_completed', doc);
            }
            
            this.renderDocuments();
        }
    }

    async updateDocumentStatusAPI(action, document) {
        try {
            await fetch('/api/documents/update-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: action,
                    document: document
                })
            });
        } catch (error) {
            console.error('Error updating document status:', error);
        }
    }

    simulateProgress(docId) {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            
            const doc = this.documents.processing.find(d => d.id === docId);
            if (doc) {
                doc.progress = Math.min(progress, 100);
                this.renderDocuments();
            }
        }, 1000);
    }
}

// Global functions for button clicks
function refreshSuggestions() {
    cockpit.loadAISuggestions();
}

function draftEmail(type) {
    cockpit.showEmailModal({
        to: '',
        subject: 'Follow-up Meeting Request',
        body: 'Hi,\n\nI hope this email finds you well. Based on our recent RFP analysis, I would like to schedule a follow-up meeting to discuss the implementation timeline for the automation features.\n\nWould you be available for a 30-minute discussion next week? Please let me know your preferred time slots.\n\nBest regards,\nParesh'
    });
}

function addToTasks(title) {
    // Add task functionality
    cockpit.showNotification(`Task "${title}" added to your list`, 'success');
}

function draftStatusUpdate() {
    cockpit.showEmailModal({
        to: 'stakeholders@company.com',
        subject: 'Project Status Update - High Priority Tasks',
        body: 'Dear Team,\n\nI wanted to provide you with an update on the current status of our high-priority tasks:\n\n1. Task 1 - Currently in progress, expected completion by [date]\n2. Task 2 - Awaiting approval, requires action by [date]\n3. Task 3 - Completed successfully\n\nPlease let me know if you need any additional information or have concerns about the timeline.\n\nBest regards,\nParesh'
    });
}

function showOverdueTasks() {
    cockpit.showNotification('Displaying overdue tasks...', 'info');
}

function uploadDocument() {
    document.getElementById('documentInput').click();
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('startAnalysisBtn').disabled = false;
        cockpit.showNotification(`File selected: ${file.name}`, 'info');
        
        // Update UI to show selected file
        const uploadArea = document.querySelector('.upload-area');
        uploadArea.innerHTML = `
            <i class="fas fa-file-alt fa-3x text-success mb-3"></i>
            <h5 class="text-success">File Selected: ${file.name}</h5>
            <p class="text-secondary">Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <button class="btn btn-outline" onclick="clearFileSelection()">
                <i class="fas fa-times"></i> Clear Selection
            </button>
        `;
        
        // Enable start analysis button
        const startBtn = document.getElementById('startAnalysisBtn');
        startBtn.disabled = false;
        startBtn.onclick = () => startDocumentAnalysis(file);
    }
}

function clearFileSelection() {
    document.getElementById('documentInput').value = '';
    document.getElementById('startAnalysisBtn').disabled = true;
    
    // Reset upload area
    const uploadArea = document.querySelector('.upload-area');
    uploadArea.innerHTML = `
        <input type="file" id="documentInput" class="d-none" accept=".pdf,.doc,.docx,.txt" onchange="handleFileSelect(event)">
        <i class="fas fa-cloud-upload-alt fa-3x text-secondary mb-3"></i>
        <h5>Drop your document here or click to upload</h5>
        <p class="text-secondary">Supports PDF, DOC, DOCX, TXT files</p>
        <button class="btn btn-smart" onclick="document.getElementById('documentInput').click()">
            Choose File
        </button>
    `;
}

async function startDocumentAnalysis(file) {
    const analysisType = document.getElementById('analysisType').value;
    const priorityLevel = document.getElementById('priorityLevel').value;
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', 'Paresh');
        formData.append('analysis_type', analysisType);
        formData.append('priority', priorityLevel);
        
        // Show processing in queue
        const processingDoc = {
            id: Date.now().toString(),
            name: file.name,
            status: 'analyzing',
            progress: 0,
            uploaded_at: new Date().toISOString(),
            analysis_type: analysisType
        };
        
        cockpit.addToProcessingQueue(processingDoc);
        cockpit.showNotification('Starting document analysis...', 'info');
        
        // Disable the form
        document.getElementById('startAnalysisBtn').disabled = true;
        document.getElementById('startAnalysisBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        // Upload and process document
        const response = await fetch('/api/upload-document-modern', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            cockpit.showNotification('Document uploaded successfully!', 'success');
            
            // Update processing status
            cockpit.updateProcessingStatus(processingDoc.id, 'completed', 100);
            
            // Refresh data
            setTimeout(() => {
                cockpit.loadTasks();
                cockpit.loadDocuments();
                clearFileSelection();
            }, 2000);
            
        } else {
            throw new Error('Upload failed');
        }
        
    } catch (error) {
        console.error('Error uploading document:', error);
        cockpit.showNotification('Error uploading document', 'error');
        cockpit.updateProcessingStatus(processingDoc.id, 'failed', 0);
    }
}

function refreshDocumentStatus() {
    cockpit.loadDocuments();
    cockpit.showNotification('Document status refreshed', 'info');
}

function copyEmail() {
    const emailBody = document.getElementById('email-body').value;
    navigator.clipboard.writeText(emailBody).then(() => {
        cockpit.showNotification('Email copied to clipboard!', 'success');
    });
}

function regenerateEmail() {
    cockpit.showNotification('Regenerating email with AI...', 'info');
    // Implement email regeneration logic
}

function sendMessage() {
    cockpit.sendMessage();
}

function toggleChat() {
    cockpit.toggleChat();
}

// Initialize the Digital Cockpit
let cockpit;
document.addEventListener('DOMContentLoaded', () => {
    cockpit = new DigitalCockpit();
});
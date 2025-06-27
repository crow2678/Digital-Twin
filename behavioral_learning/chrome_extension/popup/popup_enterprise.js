// ===================================================================
// ENTERPRISE POPUP.JS - Digital Twin Chrome Extension
// Enhanced Enterprise-Grade Interface with Advanced Features
// ===================================================================

class EnterpriseDigitalTwinPopup {
    constructor() {
        this.isInitialized = false;
        this.selectedEnergyLevel = null;
        this.syncInterval = null;
        this.initializePopup();
    }
    
    async initializePopup() {
        try {
            console.log('🚀 Initializing Enterprise Digital Twin popup...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve));
            }
            
            this.attachEventListeners();
            this.initializeCharacterCounters();
            this.loadDashboardData();
            this.loadInsights();
            this.startSyncMonitoring();
            
            this.isInitialized = true;
            this.updateStatus('Ready to capture productivity data', 'success');
            
            console.log('✅ Enterprise popup initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing popup:', error);
            this.updateStatus('Initialization error', 'error');
        }
    }
    
    attachEventListeners() {
        try {
            // Tab buttons
            const tabButtons = document.querySelectorAll('.tab-btn');
            tabButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const tabName = btn.dataset.tab;
                    this.switchTab(tabName);
                });
            });

            // Energy level buttons
            const energyButtons = document.querySelectorAll('.energy-btn');
            energyButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.selectEnergyLevel(btn);
                });
            });
            
            // Form buttons
            const logBtn = document.getElementById('log-activity');
            if (logBtn) {
                logBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.saveActivity();
                });
            }
            
            const clearBtn = document.getElementById('clear-form');
            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.clearForm();
                });
            }
            
            // Sync button
            const syncBtn = document.getElementById('syncStatus');
            if (syncBtn) {
                syncBtn.addEventListener('click', () => {
                    this.manualSync();
                });
            }

            // Quick action buttons
            const openDashboardBtn = document.getElementById('openDashboardBtn');
            if (openDashboardBtn) {
                openDashboardBtn.addEventListener('click', () => {
                    this.openDashboard();
                });
            }

            const syncDataBtn = document.getElementById('syncDataBtn');
            if (syncDataBtn) {
                syncDataBtn.addEventListener('click', () => {
                    this.manualSync();
                });
            }
            
            console.log('✅ Event listeners attached successfully');
        } catch (error) {
            console.error('❌ Error attaching event listeners:', error);
        }
    }
    
    initializeCharacterCounters() {
        const counters = [
            { input: 'meeting-title', counter: 'title-count', max: 100 },
            { input: 'meeting-notes', counter: 'notes-count', max: 500 },
            { input: 'action-items', counter: 'actions-count', max: 300 },
            { input: 'quick-note', counter: 'note-count', max: 200 }
        ];
        
        counters.forEach(({ input, counter, max }) => {
            const inputEl = document.getElementById(input);
            const counterEl = document.getElementById(counter);
            
            if (inputEl && counterEl) {
                inputEl.addEventListener('input', () => {
                    const count = inputEl.value.length;
                    counterEl.textContent = count;
                    
                    // Update counter styling based on usage
                    const parent = counterEl.parentElement;
                    parent.classList.remove('warning', 'danger');
                    
                    if (count > max * 0.9) {
                        parent.classList.add('danger');
                    } else if (count > max * 0.75) {
                        parent.classList.add('warning');
                    }
                });
            }
        });
    }
    
    selectEnergyLevel(button) {
        // Remove selection from all buttons
        document.querySelectorAll('.energy-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select clicked button
        button.classList.add('selected');
        this.selectedEnergyLevel = parseInt(button.dataset.level);
        
        console.log('Energy level selected:', this.selectedEnergyLevel);
    }
    
    async saveActivity() {
        try {
            this.updateStatus('Saving activity...', 'info');
            
            // Collect form data
            const activityData = {
                type: 'manual_input',
                meeting_title: document.getElementById('meeting-title')?.value || '',
                meeting_type: document.getElementById('meeting-type')?.value || '',
                meeting_outcome: document.getElementById('meeting-outcome')?.value || '',
                meeting_notes: document.getElementById('meeting-notes')?.value || '',
                action_items: document.getElementById('action-items')?.value || '',
                energy_level: this.selectedEnergyLevel,
                priority_level: document.getElementById('priority-level')?.value || 'medium',
                quick_note: document.getElementById('quick-note')?.value || '',
                timestamp: Date.now(),
                source: 'enterprise_popup',
                version: '2.0'
            };
            
            // Validate required fields
            if (!activityData.meeting_title) {
                this.showNotification('Please enter a meeting title', 'warning');
                return;
            }
            
            console.log('Saving activity data:', activityData);
            
            // Send to background script
            if (typeof chrome !== 'undefined' && chrome.runtime) {
                try {
                    const response = await new Promise((resolve, reject) => {
                        chrome.runtime.sendMessage({
                            source: 'enterprise_popup',
                            action: 'save_activity',
                            data: activityData
                        }, (response) => {
                            if (chrome.runtime.lastError) {
                                reject(chrome.runtime.lastError);
                            } else {
                                resolve(response);
                            }
                        });
                    });
                    
                    console.log('✅ Activity saved successfully:', response);
                    this.showNotification('✅ Activity saved to Digital Twin!', 'success');
                    this.updateStatus('Activity saved successfully', 'success');
                    
                    // Clear form after successful save
                    this.clearForm();
                    
                    // Refresh dashboard data
                    setTimeout(() => {
                        this.loadDashboardData();
                    }, 1000);
                    
                } catch (error) {
                    console.error('❌ Error sending to background:', error);
                    this.showNotification('⚠️ Error saving activity', 'error');
                    this.updateStatus('Save error - will retry', 'warning');
                }
            } else {
                console.error('❌ Chrome runtime not available');
                this.showNotification('❌ Extension error', 'error');
            }
            
        } catch (error) {
            console.error('❌ Error in saveActivity:', error);
            this.showNotification('❌ Error saving activity', 'error');
            this.updateStatus('Save failed', 'error');
        }
    }
    
    clearForm() {
        try {
            // Clear all form fields
            const fields = [
                'meeting-title', 'meeting-type', 'meeting-outcome',
                'meeting-notes', 'action-items', 'quick-note'
            ];
            
            fields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.value = '';
                }
            });
            
            // Reset character counters
            const counters = ['title-count', 'notes-count', 'actions-count', 'note-count'];
            counters.forEach(counterId => {
                const counter = document.getElementById(counterId);
                if (counter) {
                    counter.textContent = '0';
                    counter.parentElement.classList.remove('warning', 'danger');
                }
            });
            
            // Clear energy level selection
            document.querySelectorAll('.energy-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            this.selectedEnergyLevel = null;
            
            // Reset priority to medium
            const prioritySelect = document.getElementById('priority-level');
            if (prioritySelect) {
                prioritySelect.value = 'medium';
            }
            
            this.updateStatus('Form cleared', 'info');
            console.log('✅ Form cleared');
        } catch (error) {
            console.error('❌ Error clearing form:', error);
        }
    }
    
    async loadDashboardData() {
        try {
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const result = await new Promise((resolve) => {
                    chrome.storage.local.get(['behavioralEvents'], (result) => {
                        resolve(result);
                    });
                });
                
                const events = result.behavioralEvents || [];
                const today = new Date().toDateString();
                const todayEvents = events.filter(event => 
                    new Date(event.timestamp).toDateString() === today
                );
                
                this.updateDashboardMetrics(todayEvents);
                this.updateActivityFeed(events.slice(-5));
                
                console.log(`📊 Dashboard updated with ${todayEvents.length} events for today`);
            }
        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
        }
    }
    
    updateDashboardMetrics(events) {
        try {
            // Count meetings
            const meetings = events.filter(e => e.type === 'manual_input' && e.meeting_title);
            document.getElementById('meetings-today').textContent = meetings.length;
            
            // Count completed tasks/action items
            const tasks = events.filter(e => e.action_items && e.action_items.length > 0);
            document.getElementById('tasks-completed').textContent = tasks.length;
            
            // Calculate focus time (mock for now)
            const focusTime = Math.floor(events.length * 0.5); // Rough estimation
            document.getElementById('focus-time').textContent = focusTime + 'h';
            
        } catch (error) {
            console.error('❌ Error updating dashboard metrics:', error);
        }
    }
    
    updateActivityFeed(recentEvents) {
        try {
            const feedContainer = document.getElementById('activity-feed');
            if (!feedContainer) return;
            
            if (!recentEvents || recentEvents.length === 0) {
                feedContainer.innerHTML = '<div class="activity-item"><i class="fas fa-info-circle"></i><span>No recent activity</span></div>';
                return;
            }
            
            const activityHtml = recentEvents.map(event => {
                const time = new Date(event.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                const icon = this.getActivityIcon(event.type);
                const description = this.getActivityDescription(event);
                
                return `
                    <div class="activity-item">
                        <i class="${icon}"></i>
                        <span>${time} - ${description}</span>
                    </div>
                `;
            }).join('');
            
            feedContainer.innerHTML = activityHtml;
        } catch (error) {
            console.error('❌ Error updating activity feed:', error);
        }
    }
    
    getActivityIcon(eventType) {
        const icons = {
            'manual_input': 'fas fa-edit',
            'salesforce_navigation': 'fas fa-building',
            'general_page_visit': 'fas fa-globe',
            'general_focus_session': 'fas fa-brain',
            'default': 'fas fa-circle'
        };
        return icons[eventType] || icons.default;
    }
    
    getActivityDescription(event) {
        switch (event.type) {
            case 'manual_input':
                return event.meeting_title || 'Activity logged';
            case 'salesforce_navigation':
                return `Salesforce: ${event.page_type || 'Navigation'}`;
            case 'general_page_visit':
                return `Visited ${event.domain || 'website'}`;
            case 'general_focus_session':
                return `Focus session: ${Math.round((event.focus_time_ms || 0) / 60000)}min`;
            default:
                return 'Activity recorded';
        }
    }
    
    loadInsights() {
        try {
            // Load AI insights (mock data for now)
            const insights = [
                {
                    icon: '🎯',
                    title: 'Peak Performance',
                    description: 'Your most productive hours are between 9-11 AM. Schedule important meetings during this window.'
                },
                {
                    icon: '📈',
                    title: 'Meeting Success Rate',
                    description: 'Your meeting outcomes improved by 15% this week. Great job on preparation!'
                },
                {
                    icon: '⚡',
                    title: 'Energy Patterns',
                    description: 'You report highest energy levels on Tuesdays and Wednesdays. Plan accordingly.'
                }
            ];
            
            const container = document.getElementById('insights-container');
            if (container) {
                container.innerHTML = insights.map(insight => `
                    <div class="insight-card">
                        <div class="insight-icon">${insight.icon}</div>
                        <div class="insight-content">
                            <h6>${insight.title}</h6>
                            <p>${insight.description}</p>
                        </div>
                    </div>
                `).join('');
            }
            
            console.log('💡 Insights loaded');
        } catch (error) {
            console.error('❌ Error loading insights:', error);
        }
    }
    
    startSyncMonitoring() {
        // Update last sync time
        this.updateLastSync();
        
        // Set up periodic sync monitoring
        this.syncInterval = setInterval(() => {
            this.checkSyncStatus();
        }, 30000); // Check every 30 seconds
    }
    
    async checkSyncStatus() {
        try {
            // Check if data needs to be synced
            const response = await fetch('http://localhost:8000/health', {
                signal: AbortSignal.timeout(5000)
            });
            
            if (response.ok) {
                this.updateConnectionStatus('active');
                this.updateDataStatus('success');
            } else {
                this.updateConnectionStatus('warning');
                this.updateDataStatus('warning');
            }
        } catch (error) {
            this.updateConnectionStatus('error');
            this.updateDataStatus('error');
            console.warn('Sync check failed:', error.message);
        }
    }
    
    async manualSync() {
        try {
            const syncIcon = document.getElementById('syncStatus');
            if (syncIcon) {
                syncIcon.classList.add('syncing');
            }
            
            this.updateStatus('Synchronizing...', 'info');
            
            // Trigger sync via background script
            if (typeof chrome !== 'undefined' && chrome.runtime) {
                chrome.runtime.sendMessage({
                    source: 'enterprise_popup',
                    action: 'manual_sync'
                });
            }
            
            // Simulate sync delay
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            this.showNotification('✅ Data synchronized successfully', 'success');
            this.updateStatus('Sync completed', 'success');
            this.updateLastSync();
            
        } catch (error) {
            console.error('❌ Sync error:', error);
            this.showNotification('⚠️ Sync failed - will retry automatically', 'warning');
        } finally {
            const syncIcon = document.getElementById('syncStatus');
            if (syncIcon) {
                syncIcon.classList.remove('syncing');
            }
        }
    }
    
    updateConnectionStatus(status) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.connection-status span');
        
        if (statusDot) {
            statusDot.className = `status-dot status-${status}`;
        }
        
        if (statusText) {
            const statusTexts = {
                'active': 'Connected',
                'warning': 'Limited',
                'error': 'Offline'
            };
            statusText.textContent = statusTexts[status] || 'Unknown';
        }
    }
    
    updateDataStatus(status) {
        const dataIcon = document.querySelector('.data-indicator i');
        const indicator = document.querySelector('.data-indicator');
        
        if (indicator) {
            indicator.className = `data-indicator ${status}`;
        }
    }
    
    updateLastSync() {
        const lastSyncEl = document.getElementById('last-sync');
        if (lastSyncEl) {
            lastSyncEl.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
    }
    
    updateStatus(message, type = 'info') {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status-text ${type}`;
        }
    }

    switchTab(tabName) {
        try {
            console.log('🔄 Switching to tab:', tabName);
            
            // Hide all tab contents
            const allTabs = document.querySelectorAll('.tab-content');
            console.log('Found tab contents:', allTabs.length);
            allTabs.forEach(tab => {
                tab.classList.remove('active');
                console.log('Removed active from:', tab.id);
            });
            
            // Remove active class from all tab buttons
            const allBtns = document.querySelectorAll('.tab-btn');
            console.log('Found tab buttons:', allBtns.length);
            allBtns.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            const targetTab = document.getElementById(tabName + 'Tab');
            console.log('Target tab element:', targetTab);
            if (targetTab) {
                targetTab.classList.add('active');
                console.log('✅ Activated tab:', tabName + 'Tab');
            } else {
                console.error('❌ Tab not found:', tabName + 'Tab');
            }
            
            // Activate selected tab button
            const targetBtn = document.querySelector(`[data-tab="${tabName}"]`);
            console.log('Target button element:', targetBtn);
            if (targetBtn) {
                targetBtn.classList.add('active');
                console.log('✅ Activated button for tab:', tabName);
            } else {
                console.error('❌ Button not found for tab:', tabName);
            }
            
            console.log('✅ Successfully switched to tab:', tabName);
        } catch (error) {
            console.error('❌ Error switching tab:', error);
        }
    }

    openDashboard() {
        try {
            chrome.tabs.create({ url: 'http://localhost:8080/' });
            console.log('✅ Opened dashboard in new tab');
        } catch (error) {
            console.error('❌ Error opening dashboard:', error);
        }
    }
    
    showNotification(message, type = 'info') {
        try {
            // Remove existing notifications
            const existing = document.querySelectorAll('.notification');
            existing.forEach(n => n.remove());
            
            // Create new notification
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            // Auto-remove after 3 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
            
            console.log(`📢 Notification (${type}):`, message);
        } catch (error) {
            console.error('❌ Error showing notification:', error);
        }
    }
}

// Legacy global functions for compatibility
function openDashboard() {
    if (window.popupInstance) {
        window.popupInstance.openDashboard();
    }
}

function syncData() {
    if (window.popupInstance) {
        window.popupInstance.manualSync();
    }
}

// ===================================================================
// INITIALIZATION
// ===================================================================

// Global popup instance
let popupInstance = null;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        popupInstance = new EnterpriseDigitalTwinPopup();
    });
} else {
    // DOM already ready
    popupInstance = new EnterpriseDigitalTwinPopup();
}

// Export for debugging
if (typeof window !== 'undefined') {
    window.popupInstance = popupInstance;
}

console.log('🚀 Enterprise popup script loaded successfully');
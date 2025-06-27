// ===================================================================
// POPUP.JS - Sales Hunter Digital Twin Chrome Extension
// Fixed version with proper event handling and CSP compliance
// ===================================================================

class SmartInputPopup {
  constructor() {
    this.isInitialized = false;
    this.initializePopup();
  }
  
  async initializePopup() {
    try {
      console.log('🎯 Initializing Sales Hunter popup...');
      
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        await new Promise(resolve => document.addEventListener('DOMContentLoaded', resolve));
      }
      
      this.attachEventListeners();
      await this.loadTodaysStats();
      this.isInitialized = true;
      
      console.log('✅ Popup initialized successfully');
    } catch (error) {
      console.error('❌ Error initializing popup:', error);
    }
  }
  
  attachEventListeners() {
    try {
      // Energy level buttons
      const energyButtons = document.querySelectorAll('.energy-btn');
      energyButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          // Remove selected class from all buttons
          energyButtons.forEach(b => b.classList.remove('selected'));
          // Add selected class to clicked button
          btn.classList.add('selected');
          console.log('Energy level selected:', btn.dataset.level);
        });
      });
      
      // Log input button
      const logInputBtn = document.getElementById('log-input');
      if (logInputBtn) {
        logInputBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.logManualInput();
        });
      }
      
      // Sync with twin button
      const syncTwinBtn = document.getElementById('sync-twin');
      if (syncTwinBtn) {
        syncTwinBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.syncWithDigitalTwin();
        });
      }
      
      // View analytics button
      const analyticsBtn = document.getElementById('view-analytics');
      if (analyticsBtn) {
        analyticsBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.openAnalyticsDashboard();
        });
      }
      
      // Add test data button for development (hidden in production)
      if (window.location.href.includes('chrome-extension://')) {
        const testBtn = document.createElement('button');
        testBtn.textContent = '🧪 Add Test Data';
        testBtn.style.cssText = 'position:absolute;top:5px;right:5px;font-size:10px;padding:4px;background:rgba(255,255,255,0.2);border:none;border-radius:4px;color:white;cursor:pointer;';
        testBtn.addEventListener('click', () => this.addTestData());
        document.body.appendChild(testBtn);
      }
      
      // Character counters
      const meetingNotes = document.getElementById('meeting-notes');
      const quickNote = document.getElementById('quick-note');
      
      if (meetingNotes) {
        meetingNotes.addEventListener('input', () => {
          const count = meetingNotes.value.length;
          document.getElementById('notes-count').textContent = count;
          
          // Change color based on limit
          const counter = document.getElementById('notes-count');
          if (count > 250) {
            counter.style.color = '#ff6b6b';
          } else if (count > 200) {
            counter.style.color = '#ffd93d';
          } else {
            counter.style.color = 'rgba(255, 255, 255, 0.7)';
          }
        });
      }
      
      if (quickNote) {
        quickNote.addEventListener('input', () => {
          const count = quickNote.value.length;
          document.getElementById('note-count').textContent = count;
          
          // Change color based on limit
          const counter = document.getElementById('note-count');
          if (count > 120) {
            counter.style.color = '#ff6b6b';
          } else if (count > 100) {
            counter.style.color = '#ffd93d';
          } else {
            counter.style.color = 'rgba(255, 255, 255, 0.7)';
          }
        });
      }
      
      console.log('✅ Event listeners attached successfully');
    } catch (error) {
      console.error('❌ Error attaching event listeners:', error);
    }
  }
  
  async logManualInput() {
    try {
      console.log('📝 Logging manual input...');
      
      const meetingTitle = document.getElementById('meeting-title')?.value || '';
      const meetingOutcome = document.getElementById('meeting-outcome')?.value || '';
      const meetingNotes = document.getElementById('meeting-notes')?.value || '';
      const selectedEnergyBtn = document.querySelector('.energy-btn.selected');
      const energyLevel = selectedEnergyBtn ? parseInt(selectedEnergyBtn.dataset.level) : null;
      const quickNote = document.getElementById('quick-note')?.value || '';
      
      const inputData = {
        type: 'manual_input',
        meeting_title: meetingTitle,
        meeting_outcome: meetingOutcome,
        meeting_notes: meetingNotes,
        energy_level: energyLevel,
        quick_note: quickNote,
        timestamp: Date.now(),
        source: 'popup_manual_entry'
      };
      
      console.log('Input data collected:', inputData);
      
      // Send to background script
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        try {
          const response = await new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({
              source: 'popup',
              data: inputData
            }, (response) => {
              if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
              } else {
                resolve(response);
              }
            });
          });
          
          console.log('✅ Message sent to background script:', response);
          this.showNotification('✅ Activity logged!');
          
          // Clear inputs after successful submission
          this.clearInputs();
          
        } catch (error) {
          console.error('❌ Error sending to background:', error);
          this.showNotification('⚠️ Error logging activity');
        }
      } else {
        console.error('❌ Chrome runtime not available');
        this.showNotification('❌ Extension error');
      }
      
    } catch (error) {
      console.error('❌ Error in logManualInput:', error);
      this.showNotification('❌ Error logging activity');
    }
  }
  
  clearInputs() {
    try {
      // Clear form inputs
      const meetingTitle = document.getElementById('meeting-title');
      if (meetingTitle) meetingTitle.value = '';
      
      const meetingSelect = document.getElementById('meeting-outcome');
      if (meetingSelect) meetingSelect.value = '';
      
      const meetingNotes = document.getElementById('meeting-notes');
      if (meetingNotes) {
        meetingNotes.value = '';
        document.getElementById('notes-count').textContent = '0';
      }
      
      const quickNote = document.getElementById('quick-note');
      if (quickNote) {
        quickNote.value = '';
        document.getElementById('note-count').textContent = '0';
      }
      
      // Clear energy level selection
      document.querySelectorAll('.energy-btn').forEach(btn => {
        btn.classList.remove('selected');
      });
      
      console.log('✅ Inputs cleared');
    } catch (error) {
      console.error('❌ Error clearing inputs:', error);
    }
  }
  
  async loadTodaysStats() {
    try {
      console.log('📊 Loading today\'s stats...');
      
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
        
        this.updateStatsDisplay(todayEvents);
        this.updateLiveActivity(events.slice(-5)); // Show last 5 events
        console.log(`✅ Loaded ${todayEvents.length} events for today`);
        
        // Set up auto-refresh only once
        if (!this.refreshInterval) {
          this.refreshInterval = setInterval(() => {
            this.refreshStats();
          }, 3000);
        }
      } else {
        console.warn('⚠️ Chrome storage not available');
      }
    } catch (error) {
      console.error('❌ Error loading stats:', error);
    }
  }
  
  async refreshStats() {
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
        
        this.updateStatsDisplay(todayEvents);
        this.updateLiveActivity(events.slice(-5));
      }
    } catch (error) {
      console.error('❌ Error refreshing stats:', error);
    }
  }
  
  updateStatsDisplay(events) {
    try {
      // Calculate Salesforce time
      const salesforceEvents = events.filter(e => 
        e.type && e.type.includes('salesforce')
      );
      const totalSalesforceTime = salesforceEvents.reduce((total, event) => {
        return total + (event.time_spent_ms || 0);
      }, 0);
      
      const salesforceTimeEl = document.getElementById('salesforce-time');
      if (salesforceTimeEl) {
        salesforceTimeEl.textContent = Math.round(totalSalesforceTime / 60000) + 'm';
      }
      
      // Count emails sent
      const emailsSent = events.filter(e => 
        e.type === 'outlook_email_sent'
      ).length;
      
      const emailsEl = document.getElementById('emails-sent');
      if (emailsEl) {
        emailsEl.textContent = emailsSent.toString();
      }
      
      // Count research sessions
      const researchSessions = events.filter(e => 
        e.type === 'research_activity'
      ).length;
      
      const researchEl = document.getElementById('research-sessions');
      if (researchEl) {
        researchEl.textContent = researchSessions.toString();
      }
      
      // Total events count
      const totalEventsEl = document.getElementById('total-events');
      if (totalEventsEl) {
        totalEventsEl.textContent = events.length.toString();
      }
      
      // Update status indicator
      const statusEl = document.querySelector('.status-indicator');
      if (statusEl) {
        statusEl.style.backgroundColor = events.length > 0 ? '#4CAF50' : '#FF5722';
        statusEl.title = events.length > 0 ? 'Active - tracking data' : 'No data collected today';
      }
      
      // Generate insights
      this.generateInsights(events);
      
      console.log('✅ Stats display updated');
    } catch (error) {
      console.error('❌ Error updating stats display:', error);
    }
  }
  
  updateLiveActivity(recentEvents) {
    try {
      const liveFeed = document.getElementById('live-feed');
      if (!liveFeed) return;
      
      if (!recentEvents || recentEvents.length === 0) {
        liveFeed.innerHTML = '<p class="activity-item">No recent activity</p>';
        return;
      }
      
      const activityHtml = recentEvents.map(event => {
        const time = new Date(event.timestamp).toLocaleTimeString();
        const icon = this.getActivityIcon(event.type);
        const description = this.getActivityDescription(event);
        
        return `<p class="activity-item">
          <span class="activity-time">${time}</span>
          <span class="activity-icon">${icon}</span>
          <span class="activity-desc">${description}</span>
        </p>`;
      }).join('');
      
      liveFeed.innerHTML = activityHtml;
    } catch (error) {
      console.error('❌ Error updating live activity:', error);
    }
  }
  
  getActivityIcon(eventType) {
    const icons = {
      'salesforce_navigation': '💼',
      'salesforce_click': '🖱️',
      'salesforce_time_tracking': '⏱️',
      'outlook_email_sent': '📧',
      'general_page_visit': '🌐',
      'general_focus_session': '🎯',
      'tab_switch': '🔄',
      'manual_input': '✍️',
      'default': '📊'
    };
    return icons[eventType] || icons.default;
  }
  
  getActivityDescription(event) {
    switch (event.type) {
      case 'salesforce_navigation':
        return `Navigated to ${event.page_type || 'Salesforce'}`;
      case 'salesforce_click':
        return `Clicked: ${event.action || 'action'}`;
      case 'salesforce_time_tracking':
        return `Spent ${Math.round((event.time_spent_ms || 0) / 1000)}s on page`;
      case 'outlook_email_sent':
        return 'Email sent';
      case 'general_page_visit':
        return `Visited ${event.domain || 'site'}`;
      case 'general_focus_session':
        return `Focus session: ${Math.round((event.focus_time_ms || 0) / 60000)}min`;
      case 'tab_switch':
        return 'Switched tabs';
      case 'manual_input':
        return event.meeting_outcome || 'Manual entry logged';
      default:
        return 'Activity recorded';
    }
  }

  generateInsights(events) {
    try {
      const insights = [];
      
      if (events.length > 10) {
        const salesforceEvents = events.filter(e => 
          e.type && e.type.includes('salesforce')
        ).length;
        const researchEvents = events.filter(e => 
          e.type && e.type.includes('research')
        ).length;
        
        if (salesforceEvents > researchEvents * 2) {
          insights.push('🎯 Heavy Salesforce focus today - good pipeline management!');
        } else if (researchEvents > salesforceEvents) {
          insights.push('🔍 Research-heavy day - building strong prospect knowledge!');
        }
        
        const hourlyDistribution = this.analyzeHourlyPattern(events);
        if (hourlyDistribution.peak) {
          insights.push(`⚡ Peak activity at ${hourlyDistribution.peak}:00 - your productive hour!`);
        }
      } else {
        insights.push('📈 Start using your tools to see behavioral insights here!');
        insights.push('🎯 Visit Salesforce, research prospects, or send emails to begin tracking');
      }
      
      const insightsEl = document.getElementById('insights-content');
      if (insightsEl) {
        insightsEl.innerHTML = insights
          .map(insight => `<p class="insight">${insight}</p>`)
          .join('');
      }
      
      console.log('✅ Insights generated');
    } catch (error) {
      console.error('❌ Error generating insights:', error);
    }
  }
  
  analyzeHourlyPattern(events) {
    try {
      const hourCounts = {};
      events.forEach(event => {
        const hour = new Date(event.timestamp).getHours();
        hourCounts[hour] = (hourCounts[hour] || 0) + 1;
      });
      
      const peakHour = Object.keys(hourCounts).reduce((a, b) => 
        hourCounts[a] > hourCounts[b] ? a : b
      );
      
      return { peak: peakHour };
    } catch (error) {
      console.error('❌ Error analyzing hourly pattern:', error);
      return {};
    }
  }
  
  async syncWithDigitalTwin() {
    try {
      console.log('🔄 Syncing with Digital Twin...');
      this.showNotification('🔄 Syncing with Digital Twin...');
      
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await new Promise((resolve) => {
          chrome.storage.local.get(['behavioralEvents'], (result) => {
            resolve(result);
          });
        });
        
        const events = result.behavioralEvents || [];
        
        try {
          const response = await fetch('http://localhost:8000/sync-behavioral-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: 'Paresh',
              events: events,
              sync_timestamp: new Date().toISOString()
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            console.log('✅ Sync successful:', result);
            this.showNotification('✅ Synced with Digital Twin!');
          } else {
            throw new Error(`HTTP ${response.status}`);
          }
        } catch (apiError) {
          console.log('⚠️ API not available:', apiError.message);
          this.showNotification('⚠️ Sync will be available when Digital Twin API is ready');
        }
      } else {
        throw new Error('Chrome storage not available');
      }
    } catch (error) {
      console.error('❌ Error syncing:', error);
      this.showNotification('❌ Sync error');
    }
  }
  
  openAnalyticsDashboard() {
    try {
      console.log('📈 Opening analytics dashboard...');
      
      if (typeof chrome !== 'undefined' && chrome.tabs) {
        chrome.tabs.create({ 
          url: chrome.runtime.getURL('analytics/dashboard.html')
        });
      } else {
        console.warn('⚠️ Chrome tabs API not available');
        this.showNotification('⚠️ Analytics dashboard not available');
      }
    } catch (error) {
      console.error('❌ Error opening dashboard:', error);
      this.showNotification('❌ Dashboard error');
    }
  }
  
  showNotification(message) {
    try {
      // Remove any existing notifications
      const existingNotifications = document.querySelectorAll('.notification');
      existingNotifications.forEach(n => n.remove());
      
      // Create new notification
      const notification = document.createElement('div');
      notification.className = 'notification';
      notification.textContent = message;
      document.body.appendChild(notification);
      
      // Auto-remove after 3 seconds
      setTimeout(() => {
        if (notification.parentNode) {
          notification.remove();
        }
      }, 3000);
      
      console.log('📢 Notification shown:', message);
    } catch (error) {
      console.error('❌ Error showing notification:', error);
    }
  }
  
  async addTestData() {
    try {
      const testEvents = [
        {
          type: 'salesforce_navigation',
          page_type: 'opportunity_detail',
          timestamp: Date.now() - 60000,
          id: 'test1',
          processed_at: Date.now()
        },
        {
          type: 'salesforce_click',
          action: 'edit_record',
          timestamp: Date.now() - 120000,
          id: 'test2',
          processed_at: Date.now()
        },
        {
          type: 'general_page_visit',
          domain: 'linkedin.com',
          timestamp: Date.now() - 180000,
          id: 'test3',
          processed_at: Date.now()
        },
        {
          type: 'outlook_email_sent',
          timestamp: Date.now() - 240000,
          id: 'test4',
          processed_at: Date.now()
        },
        {
          type: 'manual_input',
          meeting_outcome: 'discovery-successful',
          timestamp: Date.now() - 300000,
          id: 'test5',
          processed_at: Date.now()
        }
      ];
      
      if (typeof chrome !== 'undefined' && chrome.storage) {
        const result = await new Promise((resolve) => {
          chrome.storage.local.get(['behavioralEvents'], (result) => {
            resolve(result);
          });
        });
        
        const existingEvents = result.behavioralEvents || [];
        const updatedEvents = [...existingEvents, ...testEvents];
        
        await new Promise((resolve) => {
          chrome.storage.local.set({ behavioralEvents: updatedEvents }, () => {
            resolve();
          });
        });
        
        this.showNotification('🧪 Test data added successfully!');
        this.refreshStats();
      }
    } catch (error) {
      console.error('❌ Error adding test data:', error);
      this.showNotification('❌ Error adding test data');
    }
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
    popupInstance = new SmartInputPopup();
  });
} else {
  // DOM already ready
  popupInstance = new SmartInputPopup();
}

// Export for debugging
if (typeof window !== 'undefined') {
  window.popupInstance = popupInstance;
}

console.log('🎯 Popup script loaded successfully');
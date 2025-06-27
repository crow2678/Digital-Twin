// ===================================================================
// BACKGROUND.JS - Simple Fix for Extension Context Errors
// Based on your original 78-line version with minimal changes
// ===================================================================

class SalesHunterTracker {
  constructor() {
    this.isTracking = true;
    this.sessionData = {};
    this.behavioralPatterns = {};
    this.setupEventListeners();
    console.log('🎯 Sales Hunter Tracker initialized');
  }
  
  setupEventListeners() {
    try {
      // Tab change detection
      if (chrome.tabs && chrome.tabs.onActivated) {
        chrome.tabs.onActivated.addListener((activeInfo) => {
          this.logTabSwitch(activeInfo);
        });
      }
      
      // Window focus changes  
      if (chrome.windows && chrome.windows.onFocusChanged) {
        chrome.windows.onFocusChanged.addListener((windowId) => {
          this.logFocusChange(windowId);
        });
      }
      
      // Message handling from content scripts
      if (chrome.runtime && chrome.runtime.onMessage) {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
          try {
            this.handleContentScriptMessage(message, sender);
            sendResponse({status: 'received'});
          } catch (error) {
            console.error('❌ Error handling message:', error);
            sendResponse({status: 'error'});
          }
          return true;
        });
      }
      
      console.log('📡 Event listeners setup complete');
    } catch (error) {
      console.error('❌ Error setting up event listeners:', error);
    }
  }
  
  logTabSwitch(activeInfo) {
    try {
      const timestamp = Date.now();
      if (chrome.tabs && chrome.tabs.get) {
        chrome.tabs.get(activeInfo.tabId, (tab) => {
          if (chrome.runtime.lastError) {
            // Normal during development - just ignore
            return;
          }
          if (tab && tab.url) {
            this.recordEvent({
              type: 'tab_switch',
              url: tab.url,
              timestamp: timestamp,
              domain: new URL(tab.url).hostname
            });
          }
        });
      }
    } catch (error) {
      // Ignore tab switch errors - normal during development
    }
  }
  
  logFocusChange(windowId) {
    try {
      this.recordEvent({
        type: 'window_focus_change',
        windowId: windowId,
        timestamp: Date.now()
      });
    } catch (error) {
      // Ignore focus change errors
    }
  }
  
  handleContentScriptMessage(message, sender) {
    try {
      console.log('📨 Message from content script:', message.source, message.data?.type);
      
      // Process different types of behavioral data
      switch (message.source) {
        case 'salesforce':
          this.processSalesforceData(message.data);
          break;
        case 'outlook':
          this.processOutlookData(message.data);
          break;
        case 'research':
          this.processResearchData(message.data);
          break;
        case 'general':
          this.processGeneralData(message.data);
          break;
        case 'popup':
          this.processPopupData(message.data);
          break;
      }
      
      // Store the event
      this.recordEvent(message.data);
    } catch (error) {
      console.error('❌ Error processing message:', error);
    }
  }
  
  processSalesforceData(data) {
    console.log('💼 Salesforce activity:', data.type);
  }
  
  processOutlookData(data) {
    console.log('📧 Outlook activity:', data.type);
  }
  
  processResearchData(data) {
    console.log('🔍 Research activity:', data.type);
  }
  
  processGeneralData(data) {
    console.log('🌐 General browser activity:', data.type);
  }
  
  processPopupData(data) {
    console.log('🎛️ Popup interaction:', data.type);
  }
  
  recordEvent(eventData) {
    try {
      if (!chrome.storage || !chrome.storage.local) {
        return;
      }
      
      // Store locally
      chrome.storage.local.get(['behavioralEvents'], (result) => {
        if (chrome.runtime.lastError) {
          return;
        }
        
        const events = result.behavioralEvents || [];
        events.push({
          ...eventData,
          id: this.generateEventId(),
          processed_at: Date.now()
        });
        
        // Keep last 1000 events
        if (events.length > 1000) {
          events.splice(0, events.length - 1000);
        }
        
        chrome.storage.local.set({ behavioralEvents: events }, () => {
          if (!chrome.runtime.lastError) {
            console.log('💾 Event stored:', eventData.type);
          }
        });
        
        // Try to sync with digital twin
        this.syncWithDigitalTwin(eventData);
      });
    } catch (error) {
      // Ignore storage errors during development
    }
  }
  
  generateEventId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }
  
  async syncWithDigitalTwin(eventData) {
    try {
      const response = await fetch('http://localhost:8000/behavioral-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'Paresh', // Updated user ID
          event_data: eventData,
          timestamp: new Date().toISOString()
        })
      });
      
      if (response.ok) {
        console.log('🔄 Synced with Digital Twin API');
      }
    } catch (error) {
      // Ignore API errors when server isn't running
    }
  }
  
  // Method to get stats for popup
  async getStats() {
    return new Promise((resolve) => {
      try {
        chrome.storage.local.get(['behavioralEvents'], (result) => {
          if (chrome.runtime.lastError) {
            resolve({});
            return;
          }
          
          const events = result.behavioralEvents || [];
          const today = new Date().toDateString();
          const todayEvents = events.filter(event => 
            new Date(event.timestamp).toDateString() === today
          );
          
          resolve({
            totalEvents: events.length,
            todayEvents: todayEvents.length,
            salesforceTime: this.calculateSalesforceTime(todayEvents),
            emailsSent: this.countEmailsSent(todayEvents),
            researchSessions: this.countResearchSessions(todayEvents)
          });
        });
      } catch (error) {
        resolve({});
      }
    });
  }
  
  calculateSalesforceTime(events) {
    const salesforceEvents = events.filter(e => e.type?.includes('salesforce'));
    return salesforceEvents.reduce((total, event) => {
      return total + (event.time_spent_ms || 0);
    }, 0);
  }
  
  countEmailsSent(events) {
    return events.filter(e => e.type === 'outlook_email_sent').length;
  }
  
  countResearchSessions(events) {
    return events.filter(e => e.type === 'research_activity').length;
  }
}

// Initialize tracker
const tracker = new SalesHunterTracker();

// Handle extension installation
if (chrome.runtime && chrome.runtime.onInstalled) {
  chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
      console.log('🎉 Sales Hunter Digital Twin Tracker installed!');
      
      // Set up initial data
      if (chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({
          behavioralEvents: [],
          installDate: Date.now(),
          userId: 'Paresh' // Updated user ID
        });
      }
    }
  });
}

// Keep service worker alive
if (chrome.runtime && chrome.runtime.onStartup) {
  chrome.runtime.onStartup.addListener(() => {
    console.log('🚀 Sales Hunter Tracker startup');
  });
}
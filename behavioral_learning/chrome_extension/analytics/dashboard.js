// Sales Hunter Dashboard - External JavaScript File
// This fixes CSP inline script issues

class SalesHunterDashboard {
  constructor() {
    this.data = null;
    this.isExtensionContext = typeof chrome !== 'undefined' && chrome.storage;
    this.apiUrl = 'http://localhost:8000';
    this.debugLog = [];
    this.init();
  }

  init() {
    this.log('🚀 Sales Hunter Dashboard initializing...');
    this.setupEventListeners();
    this.loadBehavioralData();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.refreshData());
    }

    // Handle visibility changes
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.log('👁️ Page visible, refreshing data...');
        this.refreshData();
      }
    });
  }

  log(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    this.debugLog.push(logEntry);
    console.log(message);
    
    // Keep only last 20 log entries
    if (this.debugLog.length > 20) {
      this.debugLog.shift();
    }
    
    this.updateDebugDisplay();
  }

  updateDebugDisplay() {
    const debugElement = document.getElementById('debug-info');
    if (debugElement) {
      debugElement.innerHTML = '<strong>Debug Console:</strong><br>' + 
        this.debugLog.slice(-10).join('<br>');
    }
  }

  async loadBehavioralData() {
    this.log('📊 Loading behavioral data...');
    
    try {
      const data = await this.tryMultipleDataSources();
      
      if (data && data.total_events > 0) {
        this.log(`✅ Data loaded: ${data.total_events} events`);
        this.data = data;
        this.updateConnectionStatus(true);
        this.renderDashboard();
      } else {
        throw new Error('No valid data found');
      }
    } catch (error) {
      this.log(`❌ Error: ${error.message}`);
      this.updateConnectionStatus(false, error.message);
      this.showNoDataMessage();
    }
  }

  async tryMultipleDataSources() {
    const sources = [
      { name: 'Extension Storage', fn: () => this.loadFromExtensionStorage() },
      { name: 'Digital Twin API', fn: () => this.loadFromDigitalTwinAPI() },
      { name: 'Local Storage', fn: () => this.loadFromLocalStorage() }
    ];

    for (const source of sources) {
      try {
        this.log(`🔍 Trying ${source.name}...`);
        const data = await source.fn();
        if (data && data.total_events > 0) {
          this.log(`✅ ${source.name} successful`);
          return data;
        }
      } catch (error) {
        this.log(`⚠️ ${source.name} failed: ${error.message}`);
      }
    }

    return null;
  }

  async loadFromExtensionStorage() {
    if (!this.isExtensionContext) {
      throw new Error('Not in extension context');
    }

    return new Promise((resolve, reject) => {
      chrome.storage.local.get(['behavioralEvents'], (result) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }

        const events = result.behavioralEvents || [];
        this.log(`📦 Extension: ${events.length} events found`);

        if (events.length === 0) {
          reject(new Error('No events in extension storage'));
          return;
        }

        const processedData = this.processExtensionEvents(events);
        resolve(processedData);
      });
    });
  }

  async loadFromDigitalTwinAPI() {
    const response = await fetch(`${this.apiUrl}/user/Paresh/stats`);
    if (!response.ok) {
      throw new Error(`API ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    this.log(`🌐 API: ${data.total_events || 0} events`);
    return data;
  }

  async loadFromLocalStorage() {
    const storedData = localStorage.getItem('salesHunterBehavioralData');
    if (!storedData) {
      throw new Error('No data in localStorage');
    }
    
    const data = JSON.parse(storedData);
    this.log(`💾 LocalStorage: ${data.total_events || 0} events`);
    return data;
  }

  processExtensionEvents(events) {
    this.log('🔄 Processing extension events...');
    
    const eventTypes = {};
    const domains = {};
    const today = new Date().toDateString();
    const todayEvents = events.filter(event => 
      new Date(event.timestamp).toDateString() === today
    );

    events.forEach(event => {
      const type = event.type || 'unknown';
      eventTypes[type] = (eventTypes[type] || 0) + 1;

      const domain = event.domain || event.url?.split('/')[2] || 'unknown';
      domains[domain] = (domains[domain] || 0) + 1;
    });

    return {
      user_id: 'Paresh',
      total_events: events.length,
      processed_events: 0,
      event_types: eventTypes,
      domains: domains,
      today_events: todayEvents.length,
      session_info: {
        last_activity: new Date().toISOString(),
        total_events: events.length
      },
      data_source: 'extension_storage'
    };
  }

  updateConnectionStatus(connected, errorMessage = '') {
    const statusElement = document.getElementById('connection-status');
    const statusText = document.getElementById('status-text');
    
    if (connected) {
      statusElement.className = 'connection-status status-connected';
      statusText.innerHTML = `✅ Connected (${this.data?.total_events || 0} events tracked)`;
    } else {
      statusElement.className = 'connection-status status-disconnected';
      statusText.innerHTML = `❌ Connection failed: ${errorMessage}`;
    }
  }

  renderDashboard() {
    if (!this.data) return;

    this.log('🎨 Rendering dashboard...');
    this.updateOverviewStats();
    this.renderEventChart();
    this.renderDomainList();
    this.renderActivityTimeline();
    this.calculateProductivityMetrics();
    this.generateInsights();
    this.saveToLocalStorage();
  }

  updateOverviewStats() {
    if (!this.data) return;

    const elements = {
      'total-events': this.data.total_events.toLocaleString(),
      'unique-domains': this.getUniqueDomainCount(),
      'salesforce-events': this.getSalesforceEventCount(),
      'research-events': this.getResearchEventCount(),
      'email-events': this.getEmailEventCount(),
      'focus-score': this.calculateFocusScore()
    };

    Object.entries(elements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
  }

  getUniqueDomainCount() {
    if (!this.data.domains) return 0;
    return Object.keys(this.data.domains).filter(domain => 
      domain !== 'null' && domain !== 'unknown' && 
      domain !== 'extensions' && domain !== 'newtab'
    ).length;
  }

  getSalesforceEventCount() {
    if (!this.data.event_types) return 0;
    return Object.entries(this.data.event_types)
      .filter(([type]) => type.toLowerCase().includes('salesforce'))
      .reduce((sum, [, count]) => sum + count, 0);
  }

  getResearchEventCount() {
    if (!this.data.event_types) return 0;
    const researchTypes = ['linkedin_action', 'research_activity'];
    const linkedinDomain = this.data.domains?.['www.linkedin.com'] || 0;
    const eventCount = researchTypes.reduce((sum, type) => 
      sum + (this.data.event_types[type] || 0), 0
    );
    return eventCount + Math.min(linkedinDomain, 50);
  }

  getEmailEventCount() {
    if (!this.data.domains) return 0;
    const emailDomains = ['mail.google.com', 'm365.cloud.microsoft', 'outlook.com'];
    return emailDomains.reduce((sum, domain) => 
      sum + (this.data.domains[domain] || 0), 0
    );
  }

  calculateFocusScore() {
    if (!this.data.event_types) return 0;
    
    const focusSessions = this.data.event_types.general_focus_session || 0;
    const rapidSwitching = this.data.event_types.general_rapid_switching || 0;
    const tabSwitches = this.data.event_types.tab_switch || 0;
    
    let score = 50;
    score += focusSessions * 10;
    score -= rapidSwitching * 2;
    score -= Math.min(tabSwitches * 0.1, 20);
    
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  renderEventChart() {
    if (!this.data?.event_types) return;

    const canvas = document.getElementById('event-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const eventTypes = Object.entries(this.data.event_types)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
    
    if (eventTypes.length === 0) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#7f8c8d';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('No event data available', canvas.width/2, canvas.height/2);
      return;
    }

    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#f5576c',
      '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
    ];
    
    const maxValue = Math.max(...eventTypes.map(([, count]) => count));
    const barWidth = canvas.width / eventTypes.length - 10;
    const barMaxHeight = canvas.height - 60;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    eventTypes.forEach(([type, count], index) => {
      const barHeight = (count / maxValue) * barMaxHeight;
      const x = index * (barWidth + 10) + 5;
      const y = canvas.height - barHeight - 30;
      
      ctx.fillStyle = colors[index % colors.length];
      ctx.fillRect(x, y, barWidth, barHeight);
      
      ctx.fillStyle = '#2c3e50';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(count.toString(), x + barWidth/2, y - 5);
      
      ctx.save();
      ctx.translate(x + barWidth/2, canvas.height - 5);
      ctx.rotate(-Math.PI/4);
      ctx.font = '10px Arial';
      ctx.textAlign = 'right';
      ctx.fillText(this.formatEventType(type), 0, 0);
      ctx.restore();
    });
  }

  formatEventType(type) {
    return type.replace('general_', '').replace(/_/g, ' ').substring(0, 15);
  }

  renderDomainList() {
    if (!this.data?.domains) return;

    const domainList = document.getElementById('domain-list');
    if (!domainList) return;
    
    const domains = Object.entries(this.data.domains)
      .filter(([domain, count]) => 
        domain !== 'null' && domain !== 'unknown' && 
        domain !== 'extensions' && domain !== 'newtab' && count > 1
      )
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15);
    
    if (domains.length === 0) {
      domainList.innerHTML = '<div class="loading">No domain data available</div>';
      return;
    }

    domainList.innerHTML = domains.map(([domain, count]) => `
      <div class="domain-item">
        <div class="domain-name">${this.formatDomainName(domain)}</div>
        <div class="domain-count">${count}</div>
      </div>
    `).join('');
  }

  formatDomainName(domain) {
    const formatMap = {
      'salesforce': '🏢 Salesforce CRM',
      'linkedin': '🔗 LinkedIn',
      'google': '📧 Gmail',
      'microsoft': '💼 Microsoft',
      'chatgpt': '🤖 ChatGPT',
      'claude': '🧠 Claude AI',
      'safelite': '🚗 Safelite',
      'americanexpress': '💳 American Express',
      'verizon': '📱 Verizon',
      'apple': '🍎 Apple'
    };

    for (const [key, emoji] of Object.entries(formatMap)) {
      if (domain.includes(key)) return emoji;
    }

    return domain.length > 30 ? domain.substring(0, 27) + '...' : domain;
  }

  renderActivityTimeline() {
    const timeline = document.getElementById('event-timeline');
    if (!timeline) return;
    
    if (!this.data?.event_types) {
      timeline.innerHTML = '<div class="loading">No activity data available</div>';
      return;
    }

    const recentEvents = this.generateTimelineFromEventTypes();
    
    timeline.innerHTML = recentEvents.map(event => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">${event.description}</div>
        <div class="timeline-time">${event.time}</div>
      </div>
    `).join('');
  }

  generateTimelineFromEventTypes() {
    if (!this.data?.event_types) return [];

    const events = [];
    const now = new Date();
    const eventTypes = Object.entries(this.data.event_types)
      .filter(([, count]) => count > 0)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    eventTypes.forEach(([type, count], index) => {
      const time = new Date(now - (index * 15 * 60 * 1000));
      events.push({
        description: this.getEventDescription(type, count),
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    });

    return events;
  }

  getEventDescription(eventType, count) {
    const descriptions = {
      'window_focus_change': `🔄 Application focus changes (${count})`,
      'general_time_tracking': `⏱️ Time tracking updates (${count})`,
      'tab_switch': `📑 Browser tab switches (${count})`,
      'general_page_visit': `🌐 Page visits (${count})`,
      'general_engagement': `👆 Page interactions (${count})`,
      'salesforce_navigation': `🏢 Salesforce navigation (${count})`,
      'linkedin_action': `🔗 LinkedIn activities (${count})`,
      'research_activity': `🔍 Research sessions (${count})`
    };
    
    return descriptions[eventType] || `📝 ${eventType.replace(/_/g, ' ')} (${count})`;
  }

  calculateProductivityMetrics() {
    if (!this.data?.event_types) return;

    // Multitasking index
    const tabSwitches = this.data.event_types.tab_switch || 0;
    const rapidSwitching = this.data.event_types.general_rapid_switching || 0;
    const multitaskScore = Math.min((tabSwitches + rapidSwitching * 2) / 50, 1) * 100;
    
    this.updateMetric('multitask', {
      desc: `${tabSwitches + rapidSwitching} switches - ${multitaskScore > 70 ? 'High' : multitaskScore > 40 ? 'Moderate' : 'Low'} multitasking`,
      progress: multitaskScore
    });
    
    // Work focus
    const workEvents = this.getWorkRelatedEventCount();
    const workFocusPercentage = Math.min((workEvents / this.data.total_events) * 100, 100);
    
    this.updateMetric('work-focus', {
      desc: `${workFocusPercentage.toFixed(1)}% work activity - ${workFocusPercentage > 60 ? 'High' : workFocusPercentage > 30 ? 'Moderate' : 'Low'} focus`,
      progress: workFocusPercentage
    });
    
    // Research depth
    const researchEvents = this.getResearchEventCount();
    const researchPercentage = Math.min((researchEvents / 100) * 100, 100);
    
    this.updateMetric('research-depth', {
      desc: `${researchEvents} research activities - ${researchPercentage > 50 ? 'Deep' : researchPercentage > 20 ? 'Moderate' : 'Light'} research`,
      progress: researchPercentage
    });
  }

  updateMetric(metricName, data) {
    const descElement = document.getElementById(`${metricName}-desc`);
    const progressElement = document.getElementById(`${metricName}-progress`);
    
    if (descElement) descElement.textContent = data.desc;
    if (progressElement) progressElement.style.width = `${data.progress}%`;
  }

  getWorkRelatedEventCount() {
    if (!this.data?.domains) return 0;

    const workDomains = ['salesforce', 'sharepoint', 'microsoft', 'navan', 'darwinbox'];
    return Object.entries(this.data.domains)
      .filter(([domain]) => workDomains.some(wd => domain.includes(wd)))
      .reduce((sum, [, count]) => sum + count, 0);
  }

  generateInsights() {
    if (!this.data) return;

    const insights = document.getElementById('behavioral-insights');
    if (!insights) return;
    
    const insightsList = [];
    
    // Analyze patterns dynamically
    const totalEvents = this.data.total_events;
    const tabSwitches = this.data.event_types?.tab_switch || 0;
    const focusSessions = this.data.event_types?.general_focus_session || 0;
    
    // Multitasking insight
    if (tabSwitches > 200) {
      insightsList.push({
        title: '🔄 High Multitasking Detected',
        description: `You switched between ${tabSwitches} tabs. Consider using focus techniques to reduce context switching and improve productivity.`
      });
    } else if (tabSwitches > 100) {
      insightsList.push({
        title: '📊 Moderate Multitasking',
        description: `${tabSwitches} tab switches detected. You're managing multiple tasks effectively.`
      });
    }
    
    // Domain-specific insights
    if (this.data.domains) {
      // Safelite analysis
      const safeliteActivity = this.data.domains['www.safelite.com'] || 0;
      if (safeliteActivity > 20) {
        insightsList.push({
          title: '🚗 Safelite Research Focus',
          description: `${safeliteActivity} interactions with Safelite suggest active prospect research. Consider logging key insights in your CRM.`
        });
      }
      
      // LinkedIn insight
      const linkedinActivity = this.data.domains['www.linkedin.com'] || 0;
      if (linkedinActivity > 50) {
        insightsList.push({
          title: '🔗 Strong LinkedIn Presence',
          description: `${linkedinActivity} LinkedIn interactions show excellent social selling activity. Keep building those relationships!`
        });
      }
      
      // AI usage insight
      const aiUsage = (this.data.domains['chatgpt.com'] || 0) + (this.data.domains['claude.ai'] || 0);
      if (aiUsage > 40) {
        insightsList.push({
          title: '🤖 AI-Enhanced Productivity',
          description: `${aiUsage} AI tool interactions show you're leveraging technology to boost your sales efficiency.`
        });
      }
    }
    
    // Focus session insight
    if (focusSessions < 5 && totalEvents > 100) {
      insightsList.push({
        title: '🎯 Focus Opportunity',
        description: 'Low deep focus sessions detected. Consider time-blocking for complex sales tasks to improve concentration.'
      });
    } else if (focusSessions > 10) {
      insightsList.push({
        title: '🎯 Excellent Focus Habits',
        description: `${focusSessions} deep focus sessions show great concentration skills. This drives high performance!`
      });
    }
    
    // Data source insight
    if (this.data.data_source) {
      insightsList.push({
        title: '📊 Data Source',
        description: `Analytics powered by ${this.data.data_source.replace('_', ' ')} with real-time behavioral tracking.`
      });
    }
    
    // Default message if no insights
    if (insightsList.length === 0) {
      insightsList.push({
        title: '📈 Building Your Profile',
        description: 'Continue using your browser normally. More insights will appear as we collect more behavioral data.'
      });
    }
    
    insights.innerHTML = insightsList.map(insight => `
      <div class="insight-item">
        <div class="insight-title">${insight.title}</div>
        <div class="insight-description">${insight.description}</div>
      </div>
    `).join('');
  }

  showNoDataMessage() {
    // Show helpful message when no data is available
    const sections = [
      'total-events', 'unique-domains', 'salesforce-events', 
      'research-events', 'email-events', 'focus-score'
    ];
    
    sections.forEach(id => {
      const element = document.getElementById(id);
      if (element) element.textContent = '0';
    });
    
    // Show setup instructions
    const insights = document.getElementById('behavioral-insights');
    if (insights) {
      insights.innerHTML = `
        <div class="insight-item">
          <div class="insight-title">🚀 Getting Started</div>
          <div class="insight-description">
            Your Chrome extension is installed but no data is available yet. Here's how to start tracking:
            <br><br>
            1. Visit websites normally (Salesforce, LinkedIn, etc.)<br>
            2. The extension automatically tracks your behavior<br>
            3. Refresh this dashboard to see your analytics<br>
            4. For API integration, ensure the Digital Twin server is running
          </div>
        </div>
        <div class="insight-item">
          <div class="insight-title">🔧 Troubleshooting</div>
          <div class="insight-description">
            If you're not seeing data:<br>
            • Check that the extension is enabled<br>
            • Ensure popup permissions are granted<br>
            • Try visiting some work-related websites<br>
            • Check browser console for any errors
          </div>
        </div>
      `;
    }
    
    // Clear charts
    const canvas = document.getElementById('event-chart');
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#7f8c8d';
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', canvas.width/2, canvas.height/2);
    }
    
    const domainList = document.getElementById('domain-list');
    if (domainList) {
      domainList.innerHTML = '<div class="loading">No domain data available</div>';
    }
    
    const timeline = document.getElementById('event-timeline');
    if (timeline) {
      timeline.innerHTML = '<div class="loading">No activity data available</div>';
    }
  }

  async refreshData() {
    this.log('🔄 Manual refresh triggered...');
    const statusText = document.getElementById('status-text');
    if (statusText) {
      statusText.innerHTML = '🔄 Refreshing data...';
    }
    
    await this.loadBehavioralData();
  }

  startAutoRefresh() {
    // Auto-refresh every 30 seconds
    setInterval(() => {
      this.log('⏰ Auto-refresh...');
      this.loadBehavioralData();
    }, 30000);
  }

  saveToLocalStorage() {
    if (this.data) {
      try {
        localStorage.setItem('salesHunterBehavioralData', JSON.stringify(this.data));
        this.log('💾 Data cached to localStorage');
      } catch (error) {
        this.log(`⚠️ Failed to cache data: ${error.message}`);
      }
    }
  }
}

// Initialize dashboard when DOM is ready
let dashboard;

function initDashboard() {
  dashboard = new SalesHunterDashboard();
}

// Check if DOM is already loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}

// Export for debugging
window.salesHunterDashboard = dashboard;
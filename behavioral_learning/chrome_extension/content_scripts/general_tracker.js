// ===================================================================
// CONTENT-SCRIPTS/GENERAL-TRACKER.JS - FIXED VERSION WITH PROPER INITIALIZATION
// Complete General Browser Behavior Tracking for Sales Hunter
// ===================================================================

class GeneralBrowserTracker {
  constructor() {
    // *** CRITICAL FIX: Initialize ALL properties first, regardless of Chrome context ***
    this.sessionStart = Date.now();
    this.currentDomain = window.location?.hostname || 'unknown';
    this.currentUrl = window.location?.href || 'unknown';
    this.workRelatedDomains = [];
    this.tabSwitchCount = 0;
    this.focusSessionCount = 0;
    this.totalActiveTime = 0;
    this.workTime = 0;          // *** FIX: Always initialize ***
    this.personalTime = 0;      // *** FIX: Always initialize ***
    this.learningTime = 0;      // *** FIX: Always initialize ***
    this.dailyStats = null;
    this.isActive = false;      // *** FIX: Track if tracker is active ***
    
    // Check if extension context is available
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.log('🔧 Chrome extension context not available, tracker will not run');
      return; // Exit early but properties are initialized
    }
    
    // Check if we have valid window context
    if (!window.location || !window.location.hostname) {
      console.log('🔧 Invalid window context, tracker will not run');
      return;
    }
    
    try {
      // Now safely initialize everything else
      this.workRelatedDomains = this.loadWorkDomains();
      this.dailyStats = this.loadDailyStats();
      this.isActive = true; // Mark as active
      
      console.log('🎯 General tracker initialized for:', this.currentDomain);
      this.setupTracking();
      this.startPeriodicReporting();
    } catch (error) {
      console.error('❌ Error initializing general tracker:', error);
      this.isActive = false;
    }
  }
  
  loadWorkDomains() {
    try {
      // Comprehensive list of work-related domains for sales hunters
      return [
        // CRM & Sales Tools
        'salesforce.com', 'lightning.force.com', 'my.salesforce.com',
        'hubspot.com', 'pipedrive.com', 'zoho.com', 'freshworks.com',
        'monday.com', 'airtable.com', 'notion.so',
        
        // Email & Communication
        'outlook.com', 'office.com', 'microsoft.com', 'office365.com',
        'gmail.com', 'google.com', 'docs.google.com', 'drive.google.com',
        'slack.com', 'teams.microsoft.com', 'zoom.us', 'webex.com',
        
        // Prospecting & Research Tools
        'linkedin.com', 'zoominfo.com', 'apollo.io', 'outreach.io',
        'salesloft.com', 'mixmax.com', 'yesware.com', 'mailchimp.com',
        'constantcontact.com', 'hunter.io', 'clearbit.com',
        
        // Scheduling & Productivity
        'calendly.com', 'acuityscheduling.com', 'meetings.hubspot.com',
        'when2meet.com', 'doodle.com', 'trello.com', 'asana.com',
        
        // Analytics & Reporting
        'tableau.com', 'powerbi.microsoft.com', 'analytics.google.com',
        'mixpanel.com', 'amplitude.com'
      ];
    } catch (error) {
      console.error('❌ Error loading work domains:', error);
      return [];
    }
  }
  
  loadDailyStats() {
    try {
      const today = new Date().toDateString();
      const stored = localStorage.getItem('dailyBrowserStats');
      if (stored) {
        const stats = JSON.parse(stored);
        if (stats.date === today) {
          // *** CRITICAL FIX: Ensure sitesVisited is always a Set ***
          if (Array.isArray(stats.sitesVisited)) {
            stats.sitesVisited = new Set(stats.sitesVisited);
          } else if (!stats.sitesVisited) {
            stats.sitesVisited = new Set();
          }
          
          // *** CRITICAL FIX: Ensure peakHours is properly initialized ***
          if (!stats.peakHours || typeof stats.peakHours !== 'object') {
            stats.peakHours = {};
          }
          
          return stats;
        }
      }
    } catch (error) {
      console.log('📊 Could not load daily stats, creating new:', error);
    }
    
    // Initialize new daily stats with proper structure
    return {
      date: new Date().toDateString(),
      workTime: 0,
      personalTime: 0,
      learningTime: 0,
      focusSessions: 0,
      tabSwitches: 0,
      sitesVisited: new Set(), // Always initialize as Set
      peakHours: {} // Always initialize as empty object
    };
  }
  
  saveDailyStats() {
    try {
      // *** FIX: Check if dailyStats exists before using ***
      if (!this.dailyStats) return;
      
      // Update current stats
      this.dailyStats.workTime = this.workTime || 0;
      this.dailyStats.personalTime = this.personalTime || 0;
      this.dailyStats.learningTime = this.learningTime || 0;
      this.dailyStats.focusSessions = this.focusSessionCount || 0;
      this.dailyStats.tabSwitches = this.tabSwitchCount || 0;
      
      // *** FIX: Convert Set to Array for storage ***
      const statsToStore = {
        ...this.dailyStats,
        sitesVisited: Array.from(this.dailyStats.sitesVisited || [])
      };
      
      localStorage.setItem('dailyBrowserStats', JSON.stringify(statsToStore));
    } catch (error) {
      console.log('📊 Could not save daily stats:', error);
    }
  }
  
  setupTracking() {
    try {
      // *** FIX: Only setup tracking if tracker is active ***
      if (!this.isActive) return;
      
      this.trackInitialPageLoad();
      this.trackProductivityPatterns();
      this.trackFocusTime();
      this.trackMultitasking();
      this.trackWorkVsNonWork();
      this.trackScrollAndEngagement();
      this.trackTimeOfDayPatterns();
    } catch (error) {
      console.error('❌ Error setting up tracking:', error);
    }
  }
  
  trackInitialPageLoad() {
    try {
      const pageData = {
        type: 'general_page_visit',
        domain: this.currentDomain,
        url: this.currentUrl,
        is_work_related: this.isWorkRelated(this.currentDomain),
        site_category: this.categorizeSite(this.currentDomain),
        page_title: document.title || 'Unknown',
        referrer: document.referrer || '',
        load_time: Date.now() - this.sessionStart,
        timestamp: Date.now()
      };
      
      // *** CRITICAL FIX: Ensure sitesVisited is a Set before calling add ***
      if (this.dailyStats && this.dailyStats.sitesVisited && typeof this.dailyStats.sitesVisited.add === 'function') {
        this.dailyStats.sitesVisited.add(this.currentDomain);
      } else if (this.dailyStats) {
        console.log('🔧 Fixing sitesVisited Set...');
        this.dailyStats.sitesVisited = new Set([this.currentDomain]);
      }
      
      this.sendToBackground(pageData);
    } catch (error) {
      console.error('❌ Error tracking initial page load:', error);
    }
  }
  
  trackWorkVsNonWork() {
    try {
      // *** FIX: Only track if active ***
      if (!this.isActive) return;
      
      let lastCategoryTime = Date.now();
      let currentCategory = this.categorizeSite(this.currentDomain);
      
      // Track time allocation by category
      const updateTimeAllocation = () => {
        try {
          const now = Date.now();
          const timeSpent = now - lastCategoryTime;
          
          // *** FIX: Ensure properties exist before updating ***
          switch (currentCategory) {
            case 'work':
              this.workTime = (this.workTime || 0) + timeSpent;
              break;
            case 'personal':
              this.personalTime = (this.personalTime || 0) + timeSpent;
              break;
            case 'learning':
              this.learningTime = (this.learningTime || 0) + timeSpent;
              break;
          }
          
          lastCategoryTime = now;
        } catch (error) {
          console.error('❌ Error updating time allocation:', error);
        }
      };
      
      // Update on visibility change
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          updateTimeAllocation();
        } else {
          lastCategoryTime = Date.now();
          currentCategory = this.categorizeSite(this.currentDomain);
        }
      });
      
      // Periodic reporting every 2 minutes
      setInterval(() => {
        try {
          updateTimeAllocation();
          
          const totalTime = (this.workTime || 0) + (this.personalTime || 0) + (this.learningTime || 0);
          if (totalTime > 0) {
            this.sendToBackground({
              type: 'general_work_balance',
              work_time_ms: this.workTime || 0,
              personal_time_ms: this.personalTime || 0,
              learning_time_ms: this.learningTime || 0,
              work_percentage: Math.round(((this.workTime || 0) / totalTime) * 100),
              current_category: currentCategory,
              productivity_score: this.calculateProductivityScore(),
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error in periodic work balance reporting:', error);
        }
      }, 120000); // Every 2 minutes
    } catch (error) {
      console.error('❌ Error setting up work/non-work tracking:', error);
    }
  }
  
  // *** FIX: Safe implementation for remaining tracking methods ***
  trackProductivityPatterns() {
    try {
      if (!this.isActive) return;
      
      let pageStartTime = Date.now();
      let isVisible = !document.hidden;
      let activeTimeAccumulator = 0;
      
      document.addEventListener('visibilitychange', () => {
        try {
          const currentTime = Date.now();
          
          if (document.hidden && isVisible) {
            const activeTime = currentTime - pageStartTime;
            activeTimeAccumulator += activeTime;
            this.totalActiveTime = (this.totalActiveTime || 0) + activeTime;
            
            this.sendToBackground({
              type: 'general_time_tracking',
              domain: this.currentDomain,
              active_time_ms: activeTime,
              accumulated_time_ms: activeTimeAccumulator,
              is_work_related: this.isWorkRelated(this.currentDomain),
              site_category: this.categorizeSite(this.currentDomain),
              timestamp: currentTime
            });
            
            isVisible = false;
          } else if (!document.hidden) {
            pageStartTime = currentTime;
            isVisible = true;
          }
        } catch (error) {
          console.error('❌ Error in visibility tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up productivity tracking:', error);
    }
  }
  
  trackFocusTime() {
    try {
      if (!this.isActive) return;
      
      let focusStartTime = Date.now();
      let lastInteractionTime = Date.now();
      let currentFocusSession = 0;
      const FOCUS_THRESHOLD = 60000;
      const INTERACTION_TIMEOUT = 30000;
      
      const interactionEvents = ['click', 'scroll', 'keypress', 'mousemove'];
      
      interactionEvents.forEach(eventType => {
        document.addEventListener(eventType, () => {
          try {
            const now = Date.now();
            const timeSinceLastInteraction = now - lastInteractionTime;
            
            if (timeSinceLastInteraction > INTERACTION_TIMEOUT) {
              if (currentFocusSession > FOCUS_THRESHOLD && this.isWorkRelated(this.currentDomain)) {
                this.focusSessionCount = (this.focusSessionCount || 0) + 1;
                this.sendToBackground({
                  type: 'general_focus_session',
                  domain: this.currentDomain,
                  focus_time_ms: currentFocusSession,
                  session_number: this.focusSessionCount,
                  site_category: this.categorizeSite(this.currentDomain),
                  timestamp: now
                });
              }
              
              focusStartTime = now;
              currentFocusSession = 0;
            }
            
            lastInteractionTime = now;
            currentFocusSession = now - focusStartTime;
          } catch (error) {
            console.error('❌ Error in interaction tracking:', error);
          }
        }, { passive: true });
      });
    } catch (error) {
      console.error('❌ Error setting up focus tracking:', error);
    }
  }
  
  trackMultitasking() {
    try {
      if (!this.isActive) return;
      
      let tabSwitchTimes = [];
      let lastVisibilityChange = Date.now();
      
      document.addEventListener('visibilitychange', () => {
        try {
          const now = Date.now();
          
          if (!document.hidden) {
            const timeSinceLastSwitch = now - lastVisibilityChange;
            tabSwitchTimes.push(timeSinceLastSwitch);
            
            if (tabSwitchTimes.length > 10) {
              tabSwitchTimes.shift();
            }
            
            if (timeSinceLastSwitch < 5000) {
              this.tabSwitchCount = (this.tabSwitchCount || 0) + 1;
              
              const recentSwitches = tabSwitchTimes.filter(time => time < 60000).length;
              
              this.sendToBackground({
                type: 'general_rapid_switching',
                switch_count: this.tabSwitchCount,
                time_between_ms: timeSinceLastSwitch,
                switching_velocity: recentSwitches,
                current_domain: this.currentDomain,
                is_work_related: this.isWorkRelated(this.currentDomain),
                pattern_intensity: this.calculateSwitchingIntensity(tabSwitchTimes),
                timestamp: now
              });
            }
            
            lastVisibilityChange = now;
          }
        } catch (error) {
          console.error('❌ Error in multitasking tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up multitasking tracking:', error);
    }
  }
  
  trackScrollAndEngagement() {
    try {
      if (!this.isActive) return;
      
      let scrollDepth = 0;
      let maxScrollDepth = 0;
      let scrollEvents = 0;
      let clickEvents = 0;
      
      window.addEventListener('scroll', () => {
        try {
          scrollEvents++;
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
          const documentHeight = document.documentElement.scrollHeight - window.innerHeight;
          
          if (documentHeight > 0) {
            scrollDepth = Math.round((scrollTop / documentHeight) * 100);
            maxScrollDepth = Math.max(maxScrollDepth, scrollDepth);
          }
        } catch (error) {
          console.error('❌ Error in scroll tracking:', error);
        }
      }, { passive: true });
      
      document.addEventListener('click', () => {
        clickEvents++;
      });
      
      setInterval(() => {
        try {
          if (scrollEvents > 0 || clickEvents > 0) {
            this.sendToBackground({
              type: 'general_engagement',
              domain: this.currentDomain,
              scroll_events: scrollEvents,
              click_events: clickEvents,
              max_scroll_depth: maxScrollDepth,
              current_scroll_depth: scrollDepth,
              engagement_score: this.calculateEngagementScore(scrollEvents, clickEvents, maxScrollDepth),
              site_category: this.categorizeSite(this.currentDomain),
              timestamp: Date.now()
            });
            
            scrollEvents = 0;
            clickEvents = 0;
          }
        } catch (error) {
          console.error('❌ Error in engagement reporting:', error);
        }
      }, 30000);
    } catch (error) {
      console.error('❌ Error setting up scroll and engagement tracking:', error);
    }
  }
  
  trackTimeOfDayPatterns() {
    try {
      if (!this.isActive || !this.dailyStats) return;
      
      const hour = new Date().getHours();
      
      if (!this.dailyStats.peakHours || typeof this.dailyStats.peakHours !== 'object') {
        this.dailyStats.peakHours = {};
      }
      
      if (!this.dailyStats.peakHours[hour]) {
        this.dailyStats.peakHours[hour] = {
          workTime: 0,
          focusSessions: 0,
          productivity: 0
        };
      }
      
      setInterval(() => {
        try {
          const currentHour = new Date().getHours();
          
          if (!this.dailyStats.peakHours[currentHour]) {
            this.dailyStats.peakHours[currentHour] = {
              workTime: 0,
              focusSessions: 0,
              productivity: 0
            };
          }
          
          if (this.isWorkRelated(this.currentDomain)) {
            this.dailyStats.peakHours[currentHour].workTime += 60000;
            this.dailyStats.peakHours[currentHour].productivity = this.calculateProductivityScore();
          }
        } catch (error) {
          console.error('❌ Error in time pattern tracking:', error);
        }
      }, 60000);
    } catch (error) {
      console.error('❌ Error setting up time-of-day tracking:', error);
    }
  }
  
  startPeriodicReporting() {
    try {
      if (!this.isActive) return;
      
      setInterval(() => {
        try {
          this.sendToBackground({
            type: 'general_periodic_report',
            session_duration_ms: Date.now() - this.sessionStart,
            total_active_time_ms: this.totalActiveTime || 0,
            focus_sessions_count: this.focusSessionCount || 0,
            tab_switches_count: this.tabSwitchCount || 0,
            work_time_ms: this.workTime || 0,
            personal_time_ms: this.personalTime || 0,
            learning_time_ms: this.learningTime || 0,
            productivity_score: this.calculateProductivityScore(),
            current_domain: this.currentDomain,
            current_category: this.categorizeSite(this.currentDomain),
            daily_stats: this.dailyStats ? {
              ...this.dailyStats,
              sitesVisited: Array.from(this.dailyStats.sitesVisited || [])
            } : null,
            timestamp: Date.now()
          });
          
          this.saveDailyStats();
        } catch (error) {
          console.error('❌ Error in periodic reporting:', error);
        }
      }, 300000);
    } catch (error) {
      console.error('❌ Error setting up periodic reporting:', error);
    }
  }
  
  // *** UTILITY METHODS WITH SAFE DEFAULTS ***
  categorizeSite(domain) {
    try {
      if (this.isWorkRelated(domain)) {
        return 'work';
      } else if (this.isPersonalSite(domain)) {
        return 'personal';
      } else if (this.isNewsOrLearning(domain)) {
        return 'learning';
      } else {
        return 'other';
      }
    } catch (error) {
      console.error('❌ Error categorizing site:', error);
      return 'unknown';
    }
  }
  
  isWorkRelated(domain) {
    try {
      if (!this.workRelatedDomains || !Array.isArray(this.workRelatedDomains)) {
        return false;
      }
      return this.workRelatedDomains.some(workDomain => 
        domain && domain.includes(workDomain)
      );
    } catch (error) {
      console.error('❌ Error checking work relation:', error);
      return false;
    }
  }
  
  isPersonalSite(domain) {
    try {
      const personalDomains = [
        'facebook.com', 'instagram.com', 'twitter.com', 'x.com',
        'youtube.com', 'netflix.com', 'amazon.com', 'reddit.com',
        'tiktok.com', 'pinterest.com', 'snapchat.com', 'whatsapp.com',
        'spotify.com', 'twitch.tv', 'discord.com', 'telegram.org'
      ];
      
      return personalDomains.some(personalDomain => 
        domain && domain.includes(personalDomain)
      );
    } catch (error) {
      console.error('❌ Error checking personal site:', error);
      return false;
    }
  }
  
  isNewsOrLearning(domain) {
    try {
      const learningDomains = [
        'news.', 'techcrunch.com', 'forbes.com', 'harvard.edu', 'mit.edu',
        'coursera.com', 'udemy.com', 'linkedin.com/learning', 'edx.org',
        'salesforce.com/trailhead', 'hubspot.com/academy', 'pluralsight.com',
        'wikipedia.org', 'medium.com', 'stack', 'github.com',
        'salesforce.com/blog', 'hubspot.com/blog', 'blog.',
        'cnn.com', 'bbc.com', 'reuters.com', 'bloomberg.com'
      ];
      
      return learningDomains.some(learningDomain => 
        domain && domain.includes(learningDomain)
      );
    } catch (error) {
      console.error('❌ Error checking learning site:', error);
      return false;
    }
  }
  
  calculateProductivityScore() {
    try {
      const totalTime = (this.workTime || 0) + (this.personalTime || 0) + (this.learningTime || 0);
      if (totalTime === 0) return 0;
      
      const workPercentage = ((this.workTime || 0) / totalTime) * 100;
      const learningPercentage = ((this.learningTime || 0) / totalTime) * 100;
      const focusScore = (this.focusSessionCount || 0) * 10;
      const multitaskingPenalty = Math.min((this.tabSwitchCount || 0) * 2, 30);
      
      let score = workPercentage + (learningPercentage * 0.7) + focusScore - multitaskingPenalty;
      
      return Math.max(0, Math.min(100, Math.round(score)));
    } catch (error) {
      console.error('❌ Error calculating productivity score:', error);
      return 0;
    }
  }
  
  calculateEngagementScore(scrollEvents, clickEvents, maxScrollDepth) {
    try {
      const scrollScore = Math.min((scrollEvents || 0) * 2, 30);
      const clickScore = Math.min((clickEvents || 0) * 5, 40);
      const depthScore = Math.min((maxScrollDepth || 0) * 0.3, 30);
      
      return Math.round(scrollScore + clickScore + depthScore);
    } catch (error) {
      console.error('❌ Error calculating engagement score:', error);
      return 0;
    }
  }
  
  calculateSwitchingIntensity(switchTimes) {
    try {
      if (!switchTimes || switchTimes.length < 3) return 'low';
      
      const averageTime = switchTimes.reduce((a, b) => a + b, 0) / switchTimes.length;
      
      if (averageTime < 2000) return 'very_high';
      if (averageTime < 5000) return 'high';
      if (averageTime < 15000) return 'medium';
      return 'low';
    } catch (error) {
      console.error('❌ Error calculating switching intensity:', error);
      return 'unknown';
    }
  }
  
  sendToBackground(data) {
    try {
      // *** FIX: Only send if tracker is active and data is valid ***
      if (!this.isActive || !data) return;
      
      if (typeof chrome !== 'undefined' && 
          chrome.runtime && 
          chrome.runtime.sendMessage && 
          !chrome.runtime.lastError) {
        
        // *** FIX: Ensure data contains safe values ***
        const safeData = {
          ...data,
          work_time_ms: this.workTime || 0,
          personal_time_ms: this.personalTime || 0,
          learning_time_ms: this.learningTime || 0,
          focus_sessions_count: this.focusSessionCount || 0,
          tab_switches_count: this.tabSwitchCount || 0,
          total_active_time_ms: this.totalActiveTime || 0
        };
        
        chrome.runtime.sendMessage({
          source: 'general',
          data: safeData
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.log('🔧 Extension context changed (normal during development)');
          } else if (response && response.status === 'received') {
            console.log('📨 General data sent successfully');
          }
        });
      } else {
        console.log('🔧 Chrome extension context not available');
      }
    } catch (error) {
      console.log('🔧 Chrome extension communication error (normal during development)');
    }
  }
  
  // Public method to get current stats (for popup interface)
  getCurrentStats() {
    try {
      return {
        sessionDuration: Date.now() - this.sessionStart,
        totalActiveTime: this.totalActiveTime || 0,
        workTime: this.workTime || 0,
        personalTime: this.personalTime || 0,
        learningTime: this.learningTime || 0,
        focusSessions: this.focusSessionCount || 0,
        tabSwitches: this.tabSwitchCount || 0,
        productivityScore: this.calculateProductivityScore(),
        currentCategory: this.categorizeSite(this.currentDomain),
        dailyStats: this.dailyStats ? {
          ...this.dailyStats,
          sitesVisited: Array.from(this.dailyStats.sitesVisited || [])
        } : null,
        isActive: this.isActive
      };
    } catch (error) {
      console.error('❌ Error getting current stats:', error);
      return { isActive: false };
    }
  }
}

// ===================================================================
// SAFE INITIALIZATION - MOVED OUTSIDE THE CLASS
// ===================================================================

try {
  // Initialize general tracking
  const generalTracker = new GeneralBrowserTracker();

  // Make tracker available globally for popup interface
  if (typeof window !== 'undefined') {
    window.salesHunterTracker = generalTracker;
  }

  // Handle messages from popup
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      try {
        if (request.action === 'getStats') {
          sendResponse(generalTracker.getCurrentStats());
        }
      } catch (error) {
        console.error('❌ Error handling message:', error);
        sendResponse({ isActive: false });
      }
      return true;
    });
  }

  console.log('🎯 Sales Hunter General Tracker initialized successfully for:', window.location.hostname);
} catch (error) {
  console.error('❌ Critical error initializing General Tracker:', error);
}
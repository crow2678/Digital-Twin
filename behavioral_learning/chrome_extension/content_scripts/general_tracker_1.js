// ===================================================================
// CONTENT-SCRIPTS/GENERAL-TRACKER.JS - COMPLETE FIXED VERSION
// Complete General Browser Behavior Tracking for Sales Hunter
// ===================================================================

class GeneralBrowserTracker {
  constructor() {
    // Check if extension context is available first
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.log('🔧 Chrome extension context not available, tracker will not run');
      return;
    }
    
    try {
      this.sessionStart = Date.now();
      this.currentDomain = window.location.hostname;
      this.currentUrl = window.location.href;
      this.workRelatedDomains = this.loadWorkDomains();
      this.tabSwitchCount = 0;
      this.focusSessionCount = 0;
      this.totalActiveTime = 0;
      this.workTime = 0;
      this.personalTime = 0;
      this.learningTime = 0;
      this.dailyStats = this.loadDailyStats();
      
      console.log('🎯 General tracker initialized for:', this.currentDomain);
      this.setupTracking();
      this.startPeriodicReporting();
    } catch (error) {
      console.error('❌ Error initializing general tracker:', error);
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
          // *** FIX: Convert sitesVisited array back to Set ***
          if (Array.isArray(stats.sitesVisited)) {
            stats.sitesVisited = new Set(stats.sitesVisited);
          } else if (!stats.sitesVisited) {
            stats.sitesVisited = new Set();
          }
          return stats;
        }
      }
    } catch (error) {
      console.log('📊 Could not load daily stats, creating new:', error);
    }
    
    // Initialize new daily stats
    return {
      date: new Date().toDateString(),
      workTime: 0,
      personalTime: 0,
      learningTime: 0,
      focusSessions: 0,
      tabSwitches: 0,
      sitesVisited: new Set(), // *** FIX: Ensure this is always a Set ***
      peakHours: {}
    };
  }
  
  saveDailyStats() {
    try {
      this.dailyStats.workTime = this.workTime;
      this.dailyStats.personalTime = this.personalTime;
      this.dailyStats.learningTime = this.learningTime;
      this.dailyStats.focusSessions = this.focusSessionCount;
      this.dailyStats.tabSwitches = this.tabSwitchCount;
      
      // *** FIX: Convert Set to Array for storage ***
      const statsToStore = {
        ...this.dailyStats,
        sitesVisited: Array.from(this.dailyStats.sitesVisited)
      };
      
      localStorage.setItem('dailyBrowserStats', JSON.stringify(statsToStore));
    } catch (error) {
      console.log('📊 Could not save daily stats:', error);
    }
  }
  
  setupTracking() {
    try {
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
        page_title: document.title,
        referrer: document.referrer,
        load_time: Date.now() - this.sessionStart,
        timestamp: Date.now()
      };
      
      // *** FIX: Ensure sitesVisited is a Set before calling add ***
      if (this.dailyStats.sitesVisited && typeof this.dailyStats.sitesVisited.add === 'function') {
        this.dailyStats.sitesVisited.add(this.currentDomain);
      } else {
        console.log('🔧 Fixing sitesVisited Set...');
        this.dailyStats.sitesVisited = new Set([this.currentDomain]);
      }
      
      this.sendToBackground(pageData);
    } catch (error) {
      console.error('❌ Error tracking initial page load:', error);
    }
  }
  
  trackProductivityPatterns() {
    try {
      let pageStartTime = Date.now();
      let isVisible = !document.hidden;
      let activeTimeAccumulator = 0;
      
      // Track visibility changes
      document.addEventListener('visibilitychange', () => {
        try {
          const currentTime = Date.now();
          
          if (document.hidden) {
            if (isVisible) {
              // Page becoming hidden - calculate active time
              const activeTime = currentTime - pageStartTime;
              activeTimeAccumulator += activeTime;
              this.totalActiveTime += activeTime;
              
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
            }
          } else {
            // Page becoming visible
            pageStartTime = currentTime;
            isVisible = true;
          }
        } catch (error) {
          console.error('❌ Error in visibility tracking:', error);
        }
      });
      
      // Track page unload
      window.addEventListener('beforeunload', () => {
        try {
          if (isVisible) {
            const finalActiveTime = Date.now() - pageStartTime;
            activeTimeAccumulator += finalActiveTime;
            this.totalActiveTime += finalActiveTime;
            
            this.sendToBackground({
              type: 'general_session_end',
              domain: this.currentDomain,
              final_active_time_ms: finalActiveTime,
              total_session_time_ms: activeTimeAccumulator,
              is_work_related: this.isWorkRelated(this.currentDomain),
              site_category: this.categorizeSite(this.currentDomain),
              timestamp: Date.now()
            });
            
            this.saveDailyStats();
          }
        } catch (error) {
          console.error('❌ Error in beforeunload tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up productivity tracking:', error);
    }
  }
  
  trackFocusTime() {
    try {
      let focusStartTime = Date.now();
      let lastInteractionTime = Date.now();
      let currentFocusSession = 0;
      const FOCUS_THRESHOLD = 60000; // 1 minute minimum for focus session
      const INTERACTION_TIMEOUT = 30000; // 30 seconds of inactivity = end of focus
      
      // Track user interactions for focus measurement
      const interactionEvents = ['click', 'scroll', 'keypress', 'mousemove'];
      
      interactionEvents.forEach(eventType => {
        document.addEventListener(eventType, () => {
          try {
            const now = Date.now();
            const timeSinceLastInteraction = now - lastInteractionTime;
            
            // If it's been too long since last interaction, start new focus session
            if (timeSinceLastInteraction > INTERACTION_TIMEOUT) {
              // End previous focus session if it was long enough
              if (currentFocusSession > FOCUS_THRESHOLD && this.isWorkRelated(this.currentDomain)) {
                this.focusSessionCount++;
                this.sendToBackground({
                  type: 'general_focus_session',
                  domain: this.currentDomain,
                  focus_time_ms: currentFocusSession,
                  session_number: this.focusSessionCount,
                  site_category: this.categorizeSite(this.currentDomain),
                  timestamp: now
                });
              }
              
              // Start new focus session
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
      let tabSwitchTimes = [];
      let lastVisibilityChange = Date.now();
      
      document.addEventListener('visibilitychange', () => {
        try {
          const now = Date.now();
          
          if (!document.hidden) {
            // Tab became visible - user switched to this tab
            const timeSinceLastSwitch = now - lastVisibilityChange;
            tabSwitchTimes.push(timeSinceLastSwitch);
            
            // Keep only last 10 switches for pattern analysis
            if (tabSwitchTimes.length > 10) {
              tabSwitchTimes.shift();
            }
            
            // Detect rapid switching pattern
            if (timeSinceLastSwitch < 5000) { // Less than 5 seconds
              this.tabSwitchCount++;
              
              // Calculate switching velocity (switches per minute)
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
  
  calculateSwitchingIntensity(switchTimes) {
    try {
      if (switchTimes.length < 3) return 'low';
      
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
  
  trackWorkVsNonWork() {
    try {
      let lastCategoryTime = Date.now();
      let currentCategory = this.categorizeSite(this.currentDomain);
      
      // Track time allocation by category
      const updateTimeAllocation = () => {
        try {
          const now = Date.now();
          const timeSpent = now - lastCategoryTime;
          
          switch (currentCategory) {
            case 'work':
              this.workTime += timeSpent;
              break;
            case 'personal':
              this.personalTime += timeSpent;
              break;
            case 'learning':
              this.learningTime += timeSpent;
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
          
          const totalTime = this.workTime + this.personalTime + this.learningTime;
          if (totalTime > 0) {
            this.sendToBackground({
              type: 'general_work_balance',
              work_time_ms: this.workTime,
              personal_time_ms: this.personalTime,
              learning_time_ms: this.learningTime,
              work_percentage: Math.round((this.workTime / totalTime) * 100),
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
  
  trackScrollAndEngagement() {
    try {
      let scrollDepth = 0;
      let maxScrollDepth = 0;
      let scrollEvents = 0;
      let clickEvents = 0;
      
      // Track scroll behavior
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
      
      // Track click engagement
      document.addEventListener('click', () => {
        clickEvents++;
      });
      
      // Report engagement metrics every 30 seconds
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
            
            // Reset counters
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
      const hour = new Date().getHours();
      
      // Track hourly productivity patterns
      if (!this.dailyStats.peakHours[hour]) {
        this.dailyStats.peakHours[hour] = {
          workTime: 0,
          focusSessions: 0,
          productivity: 0
        };
      }
      
      // Update hourly stats every minute
      setInterval(() => {
        try {
          const currentHour = new Date().getHours();
          if (this.isWorkRelated(this.currentDomain)) {
            this.dailyStats.peakHours[currentHour].workTime += 60000; // 1 minute
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
      // Comprehensive status report every 5 minutes
      setInterval(() => {
        try {
          this.sendToBackground({
            type: 'general_periodic_report',
            session_duration_ms: Date.now() - this.sessionStart,
            total_active_time_ms: this.totalActiveTime,
            focus_sessions_count: this.focusSessionCount,
            tab_switches_count: this.tabSwitchCount,
            work_time_ms: this.workTime,
            personal_time_ms: this.personalTime,
            learning_time_ms: this.learningTime,
            productivity_score: this.calculateProductivityScore(),
            current_domain: this.currentDomain,
            current_category: this.categorizeSite(this.currentDomain),
            daily_stats: {
              ...this.dailyStats,
              sitesVisited: Array.from(this.dailyStats.sitesVisited)
            },
            timestamp: Date.now()
          });
          
          this.saveDailyStats();
        } catch (error) {
          console.error('❌ Error in periodic reporting:', error);
        }
      }, 300000); // Every 5 minutes
    } catch (error) {
      console.error('❌ Error setting up periodic reporting:', error);
    }
  }
  
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
      return this.workRelatedDomains.some(workDomain => 
        domain.includes(workDomain)
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
        domain.includes(personalDomain)
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
        domain.includes(learningDomain)
      );
    } catch (error) {
      console.error('❌ Error checking learning site:', error);
      return false;
    }
  }
  
  calculateProductivityScore() {
    try {
      const totalTime = this.workTime + this.personalTime + this.learningTime;
      if (totalTime === 0) return 0;
      
      const workPercentage = (this.workTime / totalTime) * 100;
      const learningPercentage = (this.learningTime / totalTime) * 100;
      const focusScore = this.focusSessionCount * 10; // Bonus for focus sessions
      const multitaskingPenalty = Math.min(this.tabSwitchCount * 2, 30); // Max 30 point penalty
      
      // Calculate base score
      let score = workPercentage + (learningPercentage * 0.7) + focusScore - multitaskingPenalty;
      
      // Normalize to 0-100 scale
      return Math.max(0, Math.min(100, Math.round(score)));
    } catch (error) {
      console.error('❌ Error calculating productivity score:', error);
      return 0;
    }
  }
  
  calculateEngagementScore(scrollEvents, clickEvents, maxScrollDepth) {
    try {
      // Simple engagement scoring algorithm
      const scrollScore = Math.min(scrollEvents * 2, 30); // Max 30 points
      const clickScore = Math.min(clickEvents * 5, 40); // Max 40 points  
      const depthScore = Math.min(maxScrollDepth * 0.3, 30); // Max 30 points
      
      return Math.round(scrollScore + clickScore + depthScore);
    } catch (error) {
      console.error('❌ Error calculating engagement score:', error);
      return 0;
    }
  }
  
  sendToBackground(data) {
    try {
      if (typeof chrome !== 'undefined' && 
          chrome.runtime && 
          chrome.runtime.sendMessage && 
          !chrome.runtime.lastError) {
        
        chrome.runtime.sendMessage({
          source: 'general',
          data: data
        }, (response) => {
          // Handle response or ignore errors
          if (chrome.runtime.lastError) {
            // Extension context invalidated - normal during development
            console.log('🔧 Extension context changed (normal during development)');
          } else if (response && response.status === 'received') {
            console.log('📨 General data sent successfully');
          }
        });
      } else {
        console.log('🔧 Chrome extension context not available');
      }
    } catch (error) {
      // Extension context might not be available - this is normal
      console.log('🔧 Chrome extension communication error (normal during development)');
    }
  }
  
  // Public method to get current stats (for popup interface)
  getCurrentStats() {
    try {
      return {
        sessionDuration: Date.now() - this.sessionStart,
        totalActiveTime: this.totalActiveTime,
        workTime: this.workTime,
        personalTime: this.personalTime,
        learningTime: this.learningTime,
        focusSessions: this.focusSessionCount,
        tabSwitches: this.tabSwitchCount,
        productivityScore: this.calculateProductivityScore(),
        currentCategory: this.categorizeSite(this.currentDomain),
        dailyStats: {
          ...this.dailyStats,
          sitesVisited: Array.from(this.dailyStats.sitesVisited)
        }
      };
    } catch (error) {
      console.error('❌ Error getting current stats:', error);
      return {};
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
        sendResponse({});
      }
      return true;
    });
  }

  console.log('🎯 Sales Hunter General Tracker initialized successfully for:', window.location.hostname);
} catch (error) {
  console.error('❌ Critical error initializing General Tracker:', error);
}
// ===================================================================
// CONTENT-SCRIPTS/RESEARCH-TRACKER.JS
// Complete Updated Research Tracker with Error Handling
// ===================================================================

class ResearchTracker {
  constructor() {
    // Safe initialization to prevent undefined errors
    this.workTime = 0;
    this.personalTime = 0;
    this.learningTime = 0;
    this.researchSession = {
      startTime: Date.now(),
      pagesVisited: 0,
      companiesResearched: new Set(),
      toolsUsed: new Set()
    };
    
    // Check if we're in a valid extension context
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.log('🔧 Chrome extension context not available, tracker will not run');
      return;
    }
    
    // Validate current page
    if (!window.location || !window.location.hostname) {
      console.log('🔧 Invalid page context, tracker will not run');
      return;
    }
    
    console.log('🔍 Research tracker initialized for:', window.location.hostname);
    
    try {
      this.setupTracking();
    } catch (error) {
      console.error('❌ Error setting up research tracking:', error);
    }
  }
  
  setupTracking() {
    try {
      this.identifyResearchTarget();
      this.trackResearchDepth();
      this.trackToolUsage();
    } catch (error) {
      console.error('❌ Error in setupTracking:', error);
    }
  }
  
  identifyResearchTarget() {
    try {
      const hostname = window.location.hostname;
      const path = window.location.pathname;
      
      let researchType = 'unknown';
      let target = '';
      
      if (hostname.includes('linkedin.com')) {
        if (path.includes('/company/')) {
          researchType = 'company_research';
          target = this.extractLinkedInCompany();
        } else if (path.includes('/in/')) {
          researchType = 'person_research';
          target = this.extractLinkedInPerson();
        }
      } else if (hostname.includes('zoominfo.com')) {
        researchType = 'contact_intelligence';
        target = this.extractZoomInfoTarget();
      } else if (hostname.includes('apollo.io')) {
        researchType = 'prospecting_tool';
        target = 'apollo_prospecting';
      } else if (this.isCompanyWebsite(hostname)) {
        researchType = 'company_website';
        target = hostname;
      }
      
      if (researchType !== 'unknown') {
        this.researchSession.pagesVisited++;
        this.researchSession.companiesResearched.add(target);
        this.researchSession.toolsUsed.add(researchType);
        
        this.sendToBackground({
          type: 'research_activity',
          research_type: researchType,
          target: target,
          session_pages: this.researchSession.pagesVisited,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.error('❌ Error identifying research target:', error);
    }
  }
  
  extractLinkedInCompany() {
    try {
      const companyName = document.querySelector('h1')?.textContent?.trim() ||
                         document.querySelector('.org-top-card-summary__title')?.textContent?.trim() ||
                         document.querySelector('[data-test-id="company-name"]')?.textContent?.trim();
      return companyName || 'unknown_company';
    } catch (error) {
      console.error('❌ Error extracting LinkedIn company:', error);
      return 'unknown_company';
    }
  }
  
  extractLinkedInPerson() {
    try {
      const personName = document.querySelector('h1')?.textContent?.trim() ||
                        document.querySelector('.text-heading-xlarge')?.textContent?.trim() ||
                        document.querySelector('.pv-text-details__left-panel h1')?.textContent?.trim();
      return personName || 'unknown_person';
    } catch (error) {
      console.error('❌ Error extracting LinkedIn person:', error);
      return 'unknown_person';
    }
  }
  
  extractZoomInfoTarget() {
    try {
      // Try to extract company or person being researched in ZoomInfo
      const title = document.title;
      return title.split(' - ')[0] || 'zoominfo_research';
    } catch (error) {
      console.error('❌ Error extracting ZoomInfo target:', error);
      return 'zoominfo_research';
    }
  }
  
  isCompanyWebsite(hostname) {
    try {
      // Simple heuristic to identify potential company websites
      const excludedDomains = [
        'google.com', 'microsoft.com', 'salesforce.com', 'linkedin.com',
        'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com',
        'gmail.com', 'outlook.com', 'yahoo.com', 'amazon.com', 'apple.com',
        'netflix.com', 'reddit.com', 'wikipedia.org', 'github.com'
      ];
      
      return !excludedDomains.some(domain => hostname.includes(domain)) &&
             !hostname.includes('search') &&
             hostname.split('.').length >= 2 &&
             !hostname.includes('localhost');
    } catch (error) {
      console.error('❌ Error checking if company website:', error);
      return false;
    }
  }
  
  trackResearchDepth() {
    try {
      // Track how deep the research goes (number of pages on same domain)
      let timeOnPage = Date.now();
      
      document.addEventListener('visibilitychange', () => {
        try {
          if (document.hidden) {
            const sessionTime = Date.now() - timeOnPage;
            this.sendToBackground({
              type: 'research_depth',
              time_spent_ms: sessionTime,
              pages_in_session: this.researchSession.pagesVisited,
              timestamp: Date.now()
            });
          } else {
            timeOnPage = Date.now();
          }
        } catch (error) {
          console.error('❌ Error in visibility tracking:', error);
        }
      });
      
      // Track page unload
      window.addEventListener('beforeunload', () => {
        try {
          const totalSessionTime = Date.now() - this.researchSession.startTime;
          this.sendToBackground({
            type: 'research_session_end',
            total_time_ms: totalSessionTime,
            pages_visited: this.researchSession.pagesVisited,
            companies_researched: Array.from(this.researchSession.companiesResearched),
            tools_used: Array.from(this.researchSession.toolsUsed),
            timestamp: Date.now()
          });
        } catch (error) {
          console.error('❌ Error in beforeunload tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up research depth tracking:', error);
    }
  }
  
  trackToolUsage() {
    try {
      // Track specific actions within research tools
      setTimeout(() => {
        this.attachToolSpecificTracking();
      }, 2000);
    } catch (error) {
      console.error('❌ Error setting up tool usage tracking:', error);
    }
  }
  
  attachToolSpecificTracking() {
    try {
      const hostname = window.location.hostname;
      
      if (hostname.includes('linkedin.com')) {
        this.trackLinkedInActions();
      } else if (hostname.includes('zoominfo.com')) {
        this.trackZoomInfoActions();
      } else if (hostname.includes('apollo.io')) {
        this.trackApolloActions();
      }
    } catch (error) {
      console.error('❌ Error attaching tool-specific tracking:', error);
    }
  }
  
  trackLinkedInActions() {
    try {
      // Track LinkedIn-specific research actions
      document.addEventListener('click', (event) => {
        try {
          const element = event.target;
          const action = this.identifyLinkedInAction(element);
          
          if (action) {
            this.sendToBackground({
              type: 'linkedin_action',
              action: action,
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error tracking LinkedIn click:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up LinkedIn tracking:', error);
    }
  }
  
  identifyLinkedInAction(element) {
    try {
      const text = element.textContent?.toLowerCase() || '';
      const ariaLabel = element.getAttribute('aria-label')?.toLowerCase() || '';
      const className = element.className || '';
      
      if (text.includes('connect') || ariaLabel.includes('connect')) {
        return 'connect_request';
      }
      if (text.includes('message') || ariaLabel.includes('message')) {
        return 'send_message';
      }
      if (text.includes('follow') || ariaLabel.includes('follow')) {
        return 'follow_company';
      }
      if (element.closest && element.closest('[data-control-name*="contact_see_more"]')) {
        return 'view_contact_info';
      }
      if (text.includes('save') || ariaLabel.includes('save')) {
        return 'save_profile';
      }
      if (className.includes('profile') || text.includes('profile')) {
        return 'view_profile';
      }
      
      return null;
    } catch (error) {
      console.error('❌ Error identifying LinkedIn action:', error);
      return null;
    }
  }
  
  trackZoomInfoActions() {
    try {
      // Track ZoomInfo-specific research actions
      document.addEventListener('click', (event) => {
        try {
          const element = event.target;
          const text = element.textContent?.toLowerCase() || '';
          
          if (text.includes('email') || text.includes('phone')) {
            this.sendToBackground({
              type: 'zoominfo_contact_reveal',
              contact_type: text.includes('email') ? 'email' : 'phone',
              timestamp: Date.now()
            });
          } else if (text.includes('export') || text.includes('download')) {
            this.sendToBackground({
              type: 'zoominfo_export',
              action: 'data_export',
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error tracking ZoomInfo click:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up ZoomInfo tracking:', error);
    }
  }
  
  trackApolloActions() {
    try {
      // Track Apollo.io-specific prospecting actions
      document.addEventListener('click', (event) => {
        try {
          const element = event.target;
          const text = element.textContent?.toLowerCase() || '';
          
          if (text.includes('add to sequence') || text.includes('sequence')) {
            this.sendToBackground({
              type: 'apollo_sequence',
              action: 'add_to_sequence',
              timestamp: Date.now()
            });
          } else if (text.includes('save') || text.includes('bookmark')) {
            this.sendToBackground({
              type: 'apollo_save',
              action: 'save_prospect',
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error tracking Apollo click:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up Apollo tracking:', error);
    }
  }
  
  function sendToBackground(data) {
  try {
    if (typeof chrome !== 'undefined' && 
        chrome.runtime && 
        chrome.runtime.sendMessage && 
        !chrome.runtime.lastError) {
      
      chrome.runtime.sendMessage({
        source: 'general', // Change to correct source: 'salesforce', 'outlook', 'research', 'general'
        data: data
      }, (response) => {
        // SILENT ERROR HANDLING - no console spam
        if (chrome.runtime.lastError) {
          // Extension context changed - normal during development
          // Don't log anything to avoid spam
        } else if (response && response.status === 'received') {
          // Only log successful sends occasionally
          if (Math.random() < 0.1) { // 10% chance
            console.log('📨 Data sent successfully');
          }
        }
      });
    }
  } catch (error) {
    // Silent error handling - no console spam
  }
}
  
  // Public method to get current research stats
  getCurrentStats() {
    try {
      return {
        researchSession: this.researchSession,
        workTime: this.workTime,
        personalTime: this.personalTime,
        learningTime: this.learningTime,
        currentUrl: window.location.href,
        currentDomain: window.location.hostname
      };
    } catch (error) {
      console.error('❌ Error getting current stats:', error);
      return {};
    }
  }
}

// ===================================================================
// SAFE INITIALIZATION
// ===================================================================

try {
  // Only initialize on relevant research sites
  const hostname = window.location.hostname;
  const relevantSites = [
    'linkedin.com',
    'zoominfo.com', 
    'apollo.io',
    'hunter.io',
    'clearbit.com',
    'salesnavigator.linkedin.com'
  ];
  
  // Check if this is a relevant site OR a potential company website
  const isRelevantSite = relevantSites.some(site => hostname.includes(site));
  const isCompanyWebsite = !hostname.includes('google.com') && 
                          !hostname.includes('facebook.com') && 
                          !hostname.includes('youtube.com') &&
                          !hostname.includes('localhost') &&
                          hostname.split('.').length >= 2;
  
  if (isRelevantSite || isCompanyWebsite) {
    // Initialize research tracking
    const researchTracker = new ResearchTracker();
    
    // Make tracker available globally for debugging
    if (typeof window !== 'undefined') {
      window.researchTracker = researchTracker;
    }
    
    // Handle messages from popup/background
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        try {
          if (request.action === 'getResearchStats') {
            sendResponse(researchTracker.getCurrentStats());
          }
        } catch (error) {
          console.error('❌ Error handling message:', error);
          sendResponse({});
        }
        return true;
      });
    }
    
    console.log('🔍 Research tracker initialized successfully for:', hostname);
  } else {
    console.log('🔧 Research tracker skipping non-research site:', hostname);
  }
  
} catch (error) {
  console.error('❌ Critical error initializing research tracker:', error);
}
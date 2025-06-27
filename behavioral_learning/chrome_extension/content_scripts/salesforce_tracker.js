// ===================================================================
// CONTENT-SCRIPTS/SALESFORCE-TRACKER.JS - FIXED VERSION
// ===================================================================

class SalesforceTracker {
  constructor() {
    // Check if extension context is available
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.log('🔧 Chrome extension context not available, script will not run');
      return;
    }
    
    this.sessionStart = Date.now();
    this.currentPage = '';
    this.dealFocusTime = {};
    this.navigationCount = 0;
    
    console.log('🎯 Salesforce tracker initialized successfully');
    this.setupTracking();
  }
  
  setupTracking() {
    try {
      // Track page changes in Salesforce Lightning
      this.observeURLChanges();
      this.trackClicks();
      this.trackTimeOnPage();
      this.identifyDealFocus();
    } catch (error) {
      console.error('❌ Error setting up Salesforce tracking:', error);
    }
  }
  
  observeURLChanges() {
    try {
      let currentUrl = location.href;
      
      const observer = new MutationObserver(() => {
        try {
          if (location.href !== currentUrl) {
            this.onPageChange(currentUrl, location.href);
            currentUrl = location.href;
          }
        } catch (error) {
          console.error('❌ Error in URL observation:', error);
        }
      });
      
      observer.observe(document, { subtree: true, childList: true });
    } catch (error) {
      console.error('❌ Error setting up URL observation:', error);
    }
  }
  
  onPageChange(oldUrl, newUrl) {
    try {
      this.navigationCount++;
      
      const pageData = {
        type: 'salesforce_navigation',
        from_url: oldUrl,
        to_url: newUrl,
        page_type: this.identifyPageType(newUrl),
        navigation_count: this.navigationCount,
        timestamp: Date.now()
      };
      
      this.sendToBackground(pageData);
    } catch (error) {
      console.error('❌ Error in page change tracking:', error);
    }
  }
  
  identifyPageType(url) {
    try {
      if (url.includes('/lightning/o/Opportunity/')) return 'opportunity_list';
      if (url.includes('/lightning/r/Opportunity/')) return 'opportunity_detail';
      if (url.includes('/lightning/o/Account/')) return 'account_list';
      if (url.includes('/lightning/r/Account/')) return 'account_detail';
      if (url.includes('/lightning/o/Contact/')) return 'contact_list';
      if (url.includes('/lightning/r/Contact/')) return 'contact_detail';
      if (url.includes('/lightning/page/home')) return 'home_dashboard';
      if (url.includes('/lightning/o/Task/')) return 'activities';
      if (url.includes('/analytics/')) return 'reports_dashboard';
      return 'other';
    } catch (error) {
      console.error('❌ Error identifying page type:', error);
      return 'unknown';
    }
  }
  
  trackClicks() {
    try {
      document.addEventListener('click', (event) => {
        try {
          const element = event.target;
          const clickData = this.analyzeClick(element);
          
          if (clickData) {
            this.sendToBackground({
              type: 'salesforce_click',
              ...clickData,
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error in click tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up click tracking:', error);
    }
  }
  
  analyzeClick(element) {
    try {
      // Check for important Salesforce actions
      const buttonText = element.textContent?.trim().toLowerCase() || '';
      const className = element.className || ''; // Fix: ensure className is always a string
      const parentText = element.parentElement?.textContent?.trim().toLowerCase() || '';
      
      // Important actions to track
      if (buttonText === 'edit') return { action: 'edit_record' };
      if (buttonText === 'save') return { action: 'save_record' };
      if (buttonText === 'new') return { action: 'create_new' };
      if (buttonText === 'delete') return { action: 'delete_record' };
      if (buttonText.includes('log a call')) return { action: 'log_call' };
      if (buttonText.includes('new task')) return { action: 'new_task' };
      if (buttonText.includes('new event')) return { action: 'new_event' };
      
      // Report/Dashboard clicks - Fix: check if className is string before using includes
      if (typeof className === 'string' && (className.includes('reportChart') || className.includes('dashboard'))) {
        return { action: 'view_report', report_type: 'dashboard_widget' };
      }
      
      return null;
    } catch (error) {
      console.error('❌ Error analyzing click:', error);
      return null;
    }
  }
  
  trackTimeOnPage() {
    try {
      let pageStartTime = Date.now();
      
      // Track when user leaves/returns to page
      document.addEventListener('visibilitychange', () => {
        try {
          if (document.hidden) {
            // Page hidden - calculate time spent
            const timeSpent = Date.now() - pageStartTime;
            this.sendToBackground({
              type: 'salesforce_time_tracking',
              page_type: this.identifyPageType(location.href),
              time_spent_ms: timeSpent,
              timestamp: Date.now()
            });
          } else {
            // Page visible again
            pageStartTime = Date.now();
          }
        } catch (error) {
          console.error('❌ Error in visibility tracking:', error);
        }
      });
    } catch (error) {
      console.error('❌ Error setting up time tracking:', error);
    }
  }
  
  identifyDealFocus() {
    try {
      // Extract deal/opportunity information from current page
      setTimeout(() => {
        try {
          const dealInfo = this.extractDealInformation();
          if (dealInfo) {
            this.sendToBackground({
              type: 'salesforce_deal_focus',
              deal_info: dealInfo,
              timestamp: Date.now()
            });
          }
        } catch (error) {
          console.error('❌ Error extracting deal info:', error);
        }
      }, 2000); // Wait for page to load
    } catch (error) {
      console.error('❌ Error setting up deal focus tracking:', error);
    }
  }
  
  extractDealInformation() {
    try {
      // Try to extract opportunity name and details
      const opportunityName = document.querySelector('[data-aura-class="forceOutputLookup"] a')?.textContent ||
                             document.querySelector('.slds-page-header__title')?.textContent;
      
      const accountName = document.querySelector('[title*="Account"]')?.textContent;
      const dealStage = document.querySelector('[data-aura-class*="stage"]')?.textContent;
      const dealAmount = document.querySelector('[title*="Amount"]')?.textContent;
      
      if (opportunityName) {
        return {
          opportunity_name: opportunityName.trim(),
          account_name: accountName?.trim(),
          stage: dealStage?.trim(),
          amount: dealAmount?.trim()
        };
      }
      
      return null;
    } catch (error) {
      console.error('❌ Error extracting deal information:', error);
      return null;
    }
  }
  
  sendToBackground(data) {
    try {
      if (typeof chrome !== 'undefined' && 
          chrome.runtime && 
          chrome.runtime.sendMessage && 
          !chrome.runtime.lastError) {
        
        chrome.runtime.sendMessage({
          source: 'salesforce',
          data: data
        }, (response) => {
          if (chrome.runtime.lastError) {
            // Extension context changed - normal during development
          } else if (response && response.status === 'received') {
            console.log('📨 Salesforce data sent successfully');
          }
        });
      }
    } catch (error) {
      // Silent error handling
    }
  }
}

// ===================================================================
// SAFE INITIALIZATION - MOVED OUTSIDE THE CLASS
// ===================================================================

try {
  // Check if this is a Salesforce site before initializing
  if (window.location.hostname.includes('salesforce.com') || 
      window.location.hostname.includes('lightning.force.com')) {
    
    // Initialize Salesforce tracking
    const salesforceTracker = new SalesforceTracker();
    
    // Make tracker available globally for debugging
    if (typeof window !== 'undefined') {
      window.salesforceTracker = salesforceTracker;
    }
    
    console.log('🎯 Salesforce tracker initialized for:', window.location.hostname);
  } else {
    console.log('🔧 Salesforce tracker skipping non-Salesforce site');
  }
} catch (error) {
  console.error('❌ Critical error initializing Salesforce tracker:', error);
}
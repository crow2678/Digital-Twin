class OutlookWebTracker {
  constructor() {
    this.emailsSent = 0;
    this.emailsRead = 0;
    this.sessionStart = Date.now();
    this.setupTracking();
  }
  
  setupTracking() {
    this.trackEmailActions();
    this.trackCalendarUsage();
    this.trackNavigationPatterns();
  }
  
  trackEmailActions() {
    // Monitor email composition
    this.observeEmailComposition();
    
    // Track email reading behavior
    this.trackEmailReading();
    
    // Monitor send button clicks
    this.trackEmailSending();
  }
  
  observeEmailComposition() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        // Check for compose window opening
        if (mutation.type === 'childList') {
          const composeElements = mutation.addedNodes;
          for (let node of composeElements) {
            if (node.nodeType === 1 && 
                (node.className?.includes('compose') || 
                 node.querySelector?.('[data-app-section="Compose"]'))) {
              this.onComposeStart();
            }
          }
        }
      });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
  }
  
  onComposeStart() {
    const composeStartTime = Date.now();
    
    this.sendToBackground({
      type: 'outlook_email_compose_start',
      timestamp: composeStartTime
    });
    
    // Try to track compose completion
    setTimeout(() => {
      this.trackComposeCompletion(composeStartTime);
    }, 1000);
  }
  
  trackComposeCompletion(startTime) {
    // Look for send button and attach listener
    const sendButton = document.querySelector('[data-testid="send-button"]') ||
                      document.querySelector('[aria-label*="Send"]') ||
                      document.querySelector('button[title*="Send"]');
    
    if (sendButton) {
      sendButton.addEventListener('click', () => {
        const composeTime = Date.now() - startTime;
        this.emailsSent++;
        
        this.sendToBackground({
          type: 'outlook_email_sent',
          compose_time_ms: composeTime,
          emails_sent_today: this.emailsSent,
          timestamp: Date.now()
        });
      });
    }
  }
  
  trackEmailReading() {
    // Track when emails are opened/read
    document.addEventListener('click', (event) => {
      const element = event.target;
      
      // Check if clicking on an email in the list
      if (this.isEmailListItem(element)) {
        this.emailsRead++;
        
        this.sendToBackground({
          type: 'outlook_email_opened',
          emails_read_today: this.emailsRead,
          timestamp: Date.now()
        });
      }
    });
  }
  
  isEmailListItem(element) {
    // Check if element or parent is an email list item
    let current = element;
    while (current && current !== document.body) {
      if (current.getAttribute?.('role') === 'option' ||
          current.className?.includes('email') ||
          current.className?.includes('message') ||
          current.getAttribute?.('data-convid')) {
        return true;
      }
      current = current.parentElement;
    }
    return false;
  }
  
  trackCalendarUsage() {
    // Monitor calendar interactions
    const calendarButtons = document.querySelectorAll('[title*="Calendar"]');
    calendarButtons.forEach(button => {
      button.addEventListener('click', () => {
        this.sendToBackground({
          type: 'outlook_calendar_access',
          timestamp: Date.now()
        });
      });
    });
  }
  
  trackNavigationPatterns() {
    // Track folder navigation
    document.addEventListener('click', (event) => {
      const element = event.target;
      const folderName = this.identifyFolder(element);
      
      if (folderName) {
        this.sendToBackground({
          type: 'outlook_folder_navigation',
          folder: folderName,
          timestamp: Date.now()
        });
      }
    });
  }
  
  identifyFolder(element) {
    const text = element.textContent?.trim().toLowerCase();
    if (text?.includes('inbox')) return 'inbox';
    if (text?.includes('sent')) return 'sent';
    if (text?.includes('draft')) return 'drafts';
    if (text?.includes('deleted')) return 'deleted';
    if (text?.includes('junk')) return 'junk';
    return null;
  }
  
function sendToBackground(data) {
  try {
    if (typeof chrome !== 'undefined' && 
        chrome.runtime && 
        chrome.runtime.sendMessage && 
        !chrome.runtime.lastError) {
      
      chrome.runtime.sendMessage({
        source: 'outlook', // Change to correct source: 'salesforce', 'outlook', 'research', 'general'
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

	// Also add this initialization check at the top of each content script:
	if (typeof chrome === 'undefined' || !chrome.runtime) {
	  console.log('🔧 Chrome extension context not available, script will not run');
	  // Exit early if no extension context
	} else {
	  // Your existing script code here
	  console.log('🎯 Content script initialized successfully');
	}
}

// Initialize Outlook tracking
if (window.location.hostname.includes('outlook.com') || 
    window.location.hostname.includes('office.com')) {
  const outlookTracker = new OutlookWebTracker();
}
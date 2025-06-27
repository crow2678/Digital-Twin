class DigitalTwinAPIConnector {
  constructor() {
    this.apiUrl = 'http://localhost:8000'; // Your digital twin API
    this.userId = 'Paresh';
    this.retryCount = 0;
    this.maxRetries = 3;
  }
  
  async sendBehavioralData(eventData) {
    try {
      const response = await fetch(`${this.apiUrl}/behavioral-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          event_data: eventData,
          timestamp: new Date().toISOString(),
          source: 'chrome_extension'
        })
      });
      
      if (response.ok) {
        console.log('Behavioral data sent to Digital Twin successfully');
        this.retryCount = 0;
        return true;
      } else {
        throw new Error(`API responded with status: ${response.status}`);
      }
    } catch (error) {
      console.log('Digital Twin API not available yet:', error.message);
      
      // Store for later sync when API is available
      this.queueForLaterSync(eventData);
      return false;
    }
  }
  
  queueForLaterSync(eventData) {
    chrome.storage.local.get(['pendingSyncData'], (result) => {
      const pendingData = result.pendingSyncData || [];
      pendingData.push({
        data: eventData,
        timestamp: Date.now(),
        retryCount: 0
      });
      
      // Keep only last 500 pending items
      if (pendingData.length > 500) {
        pendingData.splice(0, pendingData.length - 500);
      }
      
      chrome.storage.local.set({ pendingSyncData: pendingData });
    });
  }
  
  async syncPendingData() {
    chrome.storage.local.get(['pendingSyncData'], async (result) => {
      const pendingData = result.pendingSyncData || [];
      
      if (pendingData.length === 0) return;
      
      console.log(`Attempting to sync ${pendingData.length} pending behavioral events`);
      
      const syncedItems = [];
      for (const item of pendingData) {
        const success = await this.sendBehavioralData(item.data);
        if (success) {
          syncedItems.push(item);
        }
      }
      
      // Remove successfully synced items
      const remainingData = pendingData.filter(item => !syncedItems.includes(item));
      chrome.storage.local.set({ pendingSyncData: remainingData });
      
      if (syncedItems.length > 0) {
        console.log(`Successfully synced ${syncedItems.length} behavioral events`);
      }
    });
  }
  
  // Try to sync pending data every 5 minutes
  startPeriodicSync() {
    setInterval(() => {
      this.syncPendingData();
    }, 5 * 60 * 1000); // 5 minutes
  }
}
/**
 * Simple Voice Intelligence System
 * Real-time voice transcription for Digital Twin
 */

class VoiceProcessor {
    constructor(apiUrl = 'http://localhost:8001') {
        this.apiUrl = apiUrl;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.stream = null;
        this.audioChunks = [];
        this.chunkDuration = 5000; // 5 seconds for stable processing
        
        console.log('VoiceProcessor initialized with API:', this.apiUrl);
    }
    
    async startRecording() {
        console.log('🎙️ Starting voice recording...');
        
        if (this.isRecording) {
            console.warn('Already recording');
            return;
        }
        
        try {
            // Request microphone permission
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            console.log('✅ Microphone access granted');
            
            // Create MediaRecorder
            const mimeType = this.getSupportedMimeType();
            console.log('Using MIME type:', mimeType);
            
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: mimeType
            });
            
            // Reset audio chunks
            this.audioChunks = [];
            
            // Set up event handlers
            this.mediaRecorder.ondataavailable = (event) => {
                console.log('📊 Audio data available:', event.data.size, 'bytes');
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                console.log('🛑 Recording stopped, processing audio...');
                this.processAudioChunks();
            };
            
            this.mediaRecorder.onerror = (event) => {
                console.error('❌ MediaRecorder error:', event.error);
                this.handleError('Recording error: ' + event.error);
            };
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            console.log('✅ Recording started successfully');
            
            // Show live indicator
            this.updateRecordingUI(true);
            
        } catch (error) {
            console.error('❌ Failed to start recording:', error);
            this.handleError('Failed to access microphone: ' + error.message);
            throw error;
        }
    }
    
    stopRecording() {
        console.log('🛑 Stopping voice recording...');
        
        if (!this.isRecording) {
            console.warn('Not currently recording');
            return;
        }
        
        this.isRecording = false;
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        if (this.stream) {
            this.stream.getTracks().forEach(track => {
                track.stop();
                console.log('🔇 Audio track stopped');
            });
        }
        
        this.updateRecordingUI(false);
        console.log('✅ Recording stopped');
    }
    
    async processAudioChunks() {
        if (this.audioChunks.length === 0) {
            console.warn('No audio data to process');
            return;
        }
        
        console.log('🔄 Processing', this.audioChunks.length, 'audio chunks...');
        
        try {
            // Combine all chunks into one blob
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            console.log('📦 Created audio blob:', audioBlob.size, 'bytes');
            
            // Send to transcription API
            const result = await this.transcribeAudio(audioBlob);
            
            if (result && result.text) {
                console.log('✅ Transcription result:', result.text);
                this.displayTranscription(result);
                this.analyzeTranscription(result);
            } else {
                console.warn('No transcription result received');
            }
            
        } catch (error) {
            console.error('❌ Processing error:', error);
            this.handleError('Failed to process audio: ' + error.message);
        }
    }
    
    async transcribeAudio(audioBlob) {
        // Check if Whisper service is available first
        try {
            const healthCheck = await fetch(`${this.apiUrl}/health`, { 
                method: 'GET',
                timeout: 2000 
            });
            
            if (healthCheck.ok) {
                console.log('🤖 Sending audio to Whisper API...');
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                
                const response = await fetch(`${this.apiUrl}/transcribe`, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('✅ Whisper API response:', result);
                    return result;
                }
            }
        } catch (error) {
            console.log('ℹ️ Whisper service not available, using Web Speech API');
        }
        
        // Fallback to Web Speech API
        return await this.fallbackWebSpeechAPI(audioBlob);
    }
    
    async fallbackWebSpeechAPI(audioBlob) {
        console.log('🔄 Trying Web Speech API fallback...');
        
        return new Promise((resolve) => {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                console.warn('Speech recognition not supported');
                resolve({ text: 'Speech recognition not available', confidence: 0 });
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onresult = (event) => {
                const result = event.results[0];
                const transcript = result[0].transcript;
                const confidence = result[0].confidence || 0.5;
                
                console.log('✅ Web Speech API result:', transcript);
                resolve({
                    text: transcript,
                    confidence: confidence,
                    source: 'web_speech_api'
                });
            };
            
            recognition.onerror = (event) => {
                console.error('Web Speech API error:', event.error);
                resolve({ text: 'Speech recognition failed', confidence: 0 });
            };
            
            recognition.start();
        });
    }
    
    displayTranscription(result) {
        const container = document.getElementById('liveTranscriptionContent');
        if (!container) {
            console.warn('Transcription container not found');
            return;
        }
        
        // Clear "start speaking" message
        if (container.querySelector('.text-muted')) {
            container.innerHTML = '';
        }
        
        // Create transcription element
        const transcriptionElement = document.createElement('div');
        transcriptionElement.className = 'transcription-chunk';
        transcriptionElement.innerHTML = `
            <div class="timestamp">${new Date().toLocaleTimeString()}</div>
            <div class="text">${result.text}</div>
            <div class="meta">
                <span class="confidence">Confidence: ${Math.round((result.confidence || 0.5) * 100)}%</span>
                ${result.source ? `<span class="source">Source: ${result.source}</span>` : ''}
            </div>
        `;
        
        container.appendChild(transcriptionElement);
        
        // Auto-scroll
        container.scrollTop = container.scrollHeight;
        
        // Show the transcription panel
        const panel = document.getElementById('liveTranscription');
        if (panel) {
            panel.style.display = 'block';
        }
    }
    
    analyzeTranscription(result) {
        // Simple action item detection
        const text = result.text.toLowerCase();
        const actionWords = ['need to', 'should', 'must', 'will', 'todo', 'action item'];
        const urgentWords = ['urgent', 'asap', 'immediately', 'critical'];
        
        const hasActionItems = actionWords.some(word => text.includes(word));
        const isUrgent = urgentWords.some(word => text.includes(word));
        
        if (hasActionItems) {
            this.showActionNotification('Action item detected in speech');
        }
        
        if (isUrgent) {
            this.showUrgentNotification('Urgent keyword detected');
        }
        
        // Send to collaboration intelligence if available
        this.sendToCollaborationIntelligence(result);
    }
    
    async sendToCollaborationIntelligence(result) {
        try {
            const params = new URLSearchParams({
                platform: 'voice',
                channel: 'meeting',
                user: 'current_user',
                text: result.text
            });
            const response = await fetch(`http://localhost:8001/dev/simulate-message?${params}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const analysis = await response.json();
                console.log('📊 Collaboration analysis:', analysis);
            }
        } catch (error) {
            console.warn('Failed to send to collaboration intelligence:', error);
        }
    }
    
    showActionNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'action-item-notification';
        notification.innerHTML = `
            <div class="notification-header">
                <i class="fas fa-tasks"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    showUrgentNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'action-item-notification';
        notification.style.background = 'linear-gradient(45deg, #dc3545, #ff6b6b)';
        notification.innerHTML = `
            <div class="notification-header">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    updateRecordingUI(isRecording) {
        // Update voice level indicator
        const indicator = document.querySelector('.voice-level-indicator');
        if (indicator) {
            if (isRecording) {
                indicator.style.transform = 'scaleX(0.5)';
                indicator.style.animation = 'pulse 1s infinite';
            } else {
                indicator.style.transform = 'scaleX(0)';
                indicator.style.animation = 'none';
            }
        }
        
        // Dispatch events for UI updates
        window.dispatchEvent(new CustomEvent('voiceRecordingStatus', {
            detail: { isRecording }
        }));
    }
    
    handleError(message) {
        console.error('VoiceProcessor Error:', message);
        
        // Show error notification
        window.dispatchEvent(new CustomEvent('voiceError', {
            detail: { error: message }
        }));
        
        // Reset state
        this.isRecording = false;
        this.updateRecordingUI(false);
    }
    
    getSupportedMimeType() {
        const types = [
            'audio/webm;codecs=opus',
            'audio/webm',
            'audio/mp4',
            'audio/wav'
        ];
        
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        return 'audio/webm'; // Fallback
    }
    
    // Public methods for external control
    toggle() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }
    
    getStatus() {
        return {
            isRecording: this.isRecording,
            hasStream: !!this.stream,
            apiUrl: this.apiUrl
        };
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceProcessor;
} else {
    window.VoiceProcessor = VoiceProcessor;
}

// Log that VoiceProcessor is available
console.log('✅ VoiceProcessor class loaded and available on window object');

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎙️ Voice Processor ready for initialization');
    
    // Auto-initialize if initialization function exists
    if (typeof window.initializeVoiceWidget === 'function') {
        console.log('🔄 Auto-initializing voice widget...');
        window.initializeVoiceWidget();
    }
});
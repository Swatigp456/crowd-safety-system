// static/js/realtime.js
// Real-time alert system JavaScript

class CrowdSafetyAPI {
    constructor() {
        this.baseURL = '/api/';
        this.wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.wsURL = `${this.wsProtocol}//${window.location.host}/ws/`;
        this.alertSocket = null;
        this.crowdSocket = null;
        this.userLocation = null;
        this.alertCallbacks = [];
        this.crowdCallbacks = [];
        
        this.initWebSockets();
        this.initLocationTracking();
    }
    
    // Initialize WebSocket connections
    initWebSockets() {
        // Alerts WebSocket
        this.alertSocket = new WebSocket(`${this.wsURL}alerts/`);
        this.alertSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleAlert(data);
        };
        
        this.alertSocket.onerror = (error) => {
            console.error('Alert WebSocket error:', error);
        };
        
        // Crowd data WebSocket
        this.crowdSocket = new WebSocket(`${this.wsURL}crowd/`);
        this.crowdSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleCrowdData(data);
        };
        
        this.crowdSocket.onerror = (error) => {
            console.error('Crowd WebSocket error:', error);
        };
    }
    
    // Handle incoming alerts
    handleAlert(alert) {
        console.log('New alert received:', alert);
        
        // Show notification
        this.showNotification(alert);
        
        // Play sound for emergency alerts
        if (alert.priority === 'emergency') {
            this.playAlertSound();
        }
        
        // Call all registered callbacks
        this.alertCallbacks.forEach(callback => callback(alert));
    }
    
    // Handle incoming crowd data
    handleCrowdData(data) {
        console.log('Crowd data update:', data);
        this.crowdCallbacks.forEach(callback => callback(data));
    }
    
    // Show browser notification
    showNotification(alert) {
        // Check if browser supports notifications
        if (!("Notification" in window)) {
            console.log("Browser doesn't support notifications");
            return;
        }
        
        // Request permission if not granted
        if (Notification.permission === "granted") {
            this.createNotification(alert);
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    this.createNotification(alert);
                }
            });
        }
        
        // Also show toast notification
        this.showToastNotification(alert);
    }
    
    // Create browser notification
    createNotification(alert) {
        const icon = alert.priority === 'emergency' ? '🚨' : '⚠️';
        const notification = new Notification(`${icon} ${alert.title}`, {
            body: alert.message,
            icon: '/static/images/alert-icon.png',
            tag: `alert-${alert.id}`,
            requireInteraction: alert.priority === 'emergency'
        });
        
        notification.onclick = () => {
            window.focus();
            if (alert.latitude && alert.longitude) {
                window.location.href = `/monitoring/?lat=${alert.latitude}&lng=${alert.longitude}`;
            } else {
                window.location.href = '/alerts/';
            }
        };
    }
    
    // Show toast notification
    showToastNotification(alert) {
        const priorityColors = {
            emergency: 'danger',
            high: 'warning',
            medium: 'info',
            low: 'secondary'
        };
        
        const toastHtml = `
            <div class="toast show" role="alert" style="min-width: 300px; margin-bottom: 10px;">
                <div class="toast-header bg-${priorityColors[alert.priority]} text-white">
                    <strong class="me-auto">
                        ${alert.priority === 'emergency' ? '🚨 EMERGENCY' : '⚠️ ALERT'}
                    </strong>
                    <small>Just now</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    <h6>${alert.title}</h6>
                    <p>${alert.message}</p>
                    ${alert.location ? `<small class="text-muted">📍 ${alert.location}</small>` : ''}
                    <div class="mt-2">
                        <button class="btn btn-sm btn-primary" onclick="viewAlertOnMap(${alert.latitude}, ${alert.longitude})">
                            View Map
                        </button>
                        <button class="btn btn-sm btn-success" onclick="acknowledgeAlert(${alert.id})">
                            Acknowledge
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        $('#notificationArea').prepend(toastHtml);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            $('.toast').last().fadeOut();
        }, 10000);
    }
    
    // Play alert sound
    playAlertSound() {
        const audio = new Audio('/static/sounds/emergency.mp3');
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
    
    // Get recent alerts via REST API
    async getRecentAlerts(limit = 50) {
        try {
            const response = await fetch(`${this.baseURL}alerts/`, {
                headers: {
                    'Authorization': `Token ${this.getAuthToken()}`
                }
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching alerts:', error);
            return { status: 'error', alerts: [] };
        }
    }
    
    // Send alert via REST API
    async sendAlert(alertData) {
        try {
            const response = await fetch(`${this.baseURL}alerts/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Authorization': `Token ${this.getAuthToken()}`
                },
                body: JSON.stringify(alertData)
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error sending alert:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    // Acknowledge alert
    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`${this.baseURL}alerts/${alertId}/acknowledge/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Authorization': `Token ${this.getAuthToken()}`
                }
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error acknowledging alert:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    // Trigger panic button
    async triggerPanic(message = 'Emergency!') {
        if (!this.userLocation) {
            throw new Error('Location not available');
        }
        
        const panicData = {
            latitude: this.userLocation.lat,
            longitude: this.userLocation.lng,
            message: message,
            location: this.userLocation.address || 'Unknown'
        };
        
        try {
            const response = await fetch(`${this.baseURL}panic/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'Authorization': `Token ${this.getAuthToken()}`
                },
                body: JSON.stringify(panicData)
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error triggering panic:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    // Get real-time crowd data
    async getCrowdData() {
        try {
            const response = await fetch(`${this.baseURL}crowd/`, {
                headers: {
                    'Authorization': `Token ${this.getAuthToken()}`
                }
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching crowd data:', error);
            return { status: 'error', data: [] };
        }
    }
    
    // Initialize location tracking
    initLocationTracking() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    };
                    this.updateServerLocation();
                },
                (error) => {
                    console.error('Geolocation error:', error);
                }
            );
            
            // Track location every 30 seconds
            setInterval(() => {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        this.userLocation = {
                            lat: position.coords.latitude,
                            lng: position.coords.longitude,
                            accuracy: position.coords.accuracy
                        };
                        this.updateServerLocation();
                    }
                );
            }, 30000);
        }
    }
    
    // Update server with current location
    updateServerLocation() {
        if (this.userLocation) {
            fetch('/accounts/update-location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: `latitude=${this.userLocation.lat}&longitude=${this.userLocation.lng}`
            });
        }
    }
    
    // Get CSRF token from cookies
    getCSRFToken() {
        const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }
    
    // Get auth token (if using token authentication)
    getAuthToken() {
        return localStorage.getItem('auth_token') || '';
    }
    
    // Register callback for alerts
    onAlert(callback) {
        this.alertCallbacks.push(callback);
    }
    
    // Register callback for crowd data
    onCrowdData(callback) {
        this.crowdCallbacks.push(callback);
    }
}

// Initialize global API object
window.crowdSafetyAPI = new CrowdSafetyAPI();

// Helper functions for templates
function viewAlertOnMap(lat, lng) {
    if (lat && lng) {
        window.location.href = `/monitoring/?lat=${lat}&lng=${lng}`;
    } else {
        window.location.href = '/monitoring/';
    }
}

async function acknowledgeAlert(alertId) {
    const result = await window.crowdSafetyAPI.acknowledgeAlert(alertId);
    if (result.status === 'success') {
        // Update UI
        $(`button[data-alert-id="${alertId}"]`).text('Acknowledged').prop('disabled', true);
    }
}

async function sendAlert() {
    const alertData = {
        title: $('#alertTitle').val(),
        message: $('#alertMessage').val(),
        alert_type: $('#alertType').val(),
        priority: $('#alertPriority').val(),
        location: $('#alertLocation').val(),
        latitude: $('#alertLatitude').val(),
        longitude: $('#alertLongitude').val(),
        send_to_all: $('#sendToAll').is(':checked')
    };
    
    const result = await window.crowdSafetyAPI.sendAlert(alertData);
    
    if (result.status === 'success') {
        alert('Alert sent successfully!');
        $('#sendAlertModal').modal('hide');
        location.reload();
    } else {
        alert('Error: ' + result.message);
    }
}

async function triggerPanic() {
    if (confirm('⚠️ EMERGENCY: Are you sure you want to trigger panic alert?')) {
        const message = prompt('Optional: Enter details about the emergency', 'Help needed!');
        const result = await window.crowdSafetyAPI.triggerPanic(message || 'Emergency!');
        
        if (result.status === 'success') {
            alert('🚨 Emergency alert sent! Security has been notified.');
        } else {
            alert('Error: ' + result.message);
        }
    }
}

// Auto-refresh alerts every minute
setInterval(async () => {
    const alerts = await window.crowdSafetyAPI.getRecentAlerts();
    if (alerts.status === 'success' && alerts.alerts.length > 0) {
        // Update alert count in navbar
        const unreadCount = alerts.alerts.filter(a => !a.read).length;
        if (unreadCount > 0) {
            $('#alertBadge').text(unreadCount).show();
        } else {
            $('#alertBadge').hide();
        }
    }
}, 60000);

// Export for use in templates
window.viewAlertOnMap = viewAlertOnMap;
window.acknowledgeAlert = acknowledgeAlert;
window.sendAlert = sendAlert;
window.triggerPanic = triggerPanic;
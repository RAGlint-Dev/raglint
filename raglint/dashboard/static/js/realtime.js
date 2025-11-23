/**
 * RAGLint Real-time Updates via WebSocket
 */

class RAGLintWebSocket {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.handlers = {
            connected: [],
            run_update: [],
            metric_update: [],
            error: []
        };
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.trigger('connected', {});
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.trigger('error', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected. Reconnecting...');
                setTimeout(() => this.connect(), this.reconnectInterval);
            };
        } catch (e) {
            console.error('Failed to connect to WebSocket:', e);
            setTimeout(() => this.connect(), this.reconnectInterval);
        }
    }

    handleMessage(data) {
        const { type, ...payload } = data;

        if (type === 'pong') {
            console.log('Received pong:', payload.timestamp);
        } else if (this.handlers[type]) {
            this.trigger(type, payload);
        }
    }

    on(event, handler) {
        if (this.handlers[event]) {
            this.handlers[event].push(handler);
        }
    }

    trigger(event, data) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(handler => handler(data));
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    ping() {
        this.send({ type: 'ping' });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Auto-connect if on a page that needs real-time updates
document.addEventListener('DOMContentLoaded', () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/runs`;

    const socket = new RAGLintWebSocket(wsUrl);

    socket.on('connected', () => {
        const indicator = document.getElementById('realtime-indicator');
        if (indicator) {
            indicator.className = 'badge bg-success';
            indicator.textContent = 'Live';
        }
    });

    socket.on('error', () => {
        const indicator = document.getElementById('realtime-indicator');
        if (indicator) {
            indicator.className = 'badge bg-danger';
            indicator.textContent = 'Disconnected';
        }
    });

    // Connect
    socket.connect();

    // Ping every 30 seconds to keep connection alive
    setInterval(() => socket.ping(), 30000);

    // Make socket globally available
    window.raglintSocket = socket;
});

// src/services/websocket.ts
class WebSocketService {
    private ws: WebSocket | null = null
    private reconnectTimer: number | null = null
    private messageHandlers: ((data: any) => void)[] = []

    connect(token: string) {
        if (this.ws?.readyState === WebSocket.OPEN) return
        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}?token=${token}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
            console.log('WebSocket connected')
            if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
        }

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                this.messageHandlers.forEach(handler => handler(data))
            } catch (e) {
                console.error('WS message parse error', e)
            }
        }

        this.ws.onclose = () => {
            console.log('WebSocket disconnected, reconnecting in 3s...')
            this.reconnectTimer = setTimeout(() => {
                const token = localStorage.getItem('access_token')
                if (token) this.connect(token)
            }, 3000)
        }

        this.ws.onerror = (error) => {
            console.error('WebSocket error', error)
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close()
            this.ws = null
        }
        if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    }

    onMessage(handler: (data: any) => void) {
        this.messageHandlers.push(handler)
        return () => {
            this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
        }
    }
}

export const wsService = new WebSocketService()
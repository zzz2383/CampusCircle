type MessageHandler = (data: any) => void

class WebSocketService {
    private ws: WebSocket | null = null
    private reconnectTimer: number | null = null
    private heartbeatTimer: number | null = null
    private messageHandlers: MessageHandler[] = []
    private reconnectAttempts = 0
    private maxReconnectAttempts = 10
    private reconnectDelay = 3000
    private isIntentionalClose = false

    /**
     * 建立 WebSocket 连接
     * @param token JWT token
     */
    connect(token: string) {
        if (this.ws?.readyState === WebSocket.OPEN) return
        this.isIntentionalClose = false
        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}?token=${token}`
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
            console.log('[WebSocket] connected')
            this.reconnectAttempts = 0
            this.startHeartbeat()
        }

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                this.messageHandlers.forEach(handler => handler(data))
            } catch (e) {
                console.error('[WebSocket] parse error', e)
            }
        }

        this.ws.onclose = (event) => {
            console.log(`[WebSocket] closed, code=${event.code}, reason=${event.reason}`)
            this.stopHeartbeat()
            if (!this.isIntentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectTimer = window.setTimeout(() => {
                    this.reconnectAttempts++
                    console.log(`[WebSocket] reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
                    this.connect(token)
                }, this.reconnectDelay)
            }
        }

        this.ws.onerror = (error) => {
            console.error('[WebSocket] error', error)
        }
    }

    /**
     * 断开连接（主动）
     */
    disconnect() {
        this.isIntentionalClose = true
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer)
            this.reconnectTimer = null
        }
        this.stopHeartbeat()
        if (this.ws) {
            this.ws.close()
            this.ws = null
        }
    }

    /**
     * 注册消息监听器
     */
    onMessage(handler: MessageHandler) {
        this.messageHandlers.push(handler)
        // 返回取消注册函数
        return () => {
            this.messageHandlers = this.messageHandlers.filter(h => h !== handler)
        }
    }

    /**
     * 发送消息（如果连接可用）
     */
    send(data: any) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data))
        } else {
            console.warn('[WebSocket] not open, cannot send')
        }
    }

    private startHeartbeat() {
        this.heartbeatTimer = window.setInterval(() => {
            if (this.ws?.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }))
            }
        }, 30000) // 每30秒发送一次心跳
    }

    private stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer)
            this.heartbeatTimer = null
        }
    }

    get isConnected() {
        return this.ws?.readyState === WebSocket.OPEN
    }
}

export const wsService = new WebSocketService()
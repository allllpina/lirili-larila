const WS_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:1313').replace(/^http/, 'ws');

export type WSCategory = 'boards' | 'pages' | 'tasks' | 'projects';
export type WSOperation = 'create' | 'edit' | 'move' | 'delete';

export interface WSMessage {
    category: WSCategory;
    operation: WSOperation;
    content: any;
}

type MessageHandler = (message: WSMessage) => void;

export class SocketService {
    private socket: WebSocket | null = null;
    private projectId: string;
    private handlers: MessageHandler[] = [];
    private reconnectInterval: any = null;

    constructor(projectId: string){
        this.projectId = projectId;
    }

    public connect(){
        const token = localStorage.getItem('token');
        if (!token){
            console.error("WS: No token found");
            return;
        };

        const url = `${WS_BASE_URL}/lirililarila/projects/ws/${this.projectId}?token=${token}`;

        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log(`🟢 WS Connected to project ${this.projectId}`);

            if(this.reconnectInterval) {
                clearInterval(this.reconnectInterval);
                this.reconnectInterval = null;
            }
        };

        this.socket.onmessage = (event) => {
            try {
                const data: WSMessage = JSON.parse(event.data);
                this.handlers.forEach(handler => handler(data));
            } catch (e) {
                console.error("WS Parse Error:", e);
            }
        };

        this.socket.onclose = () => {
            console.log('🔴 WS Disconnected. Reconnecting...');
            this.attemptReconnect();
        };

        this.socket.onerror = (error) => {
            console.error('WS Error:', error);
            this.socket?.close();
        };
    }

    private attemptReconnect() {
        if (!this.reconnectInterval) {
            this.reconnectInterval = setInterval(() => {
                if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
                    this.connect();
                }
            }, 3000); // Пробуємо кожні 3 сек
        }
    }

    public disconnect() {
        if (this.reconnectInterval) clearInterval(this.reconnectInterval);
        if (this.socket) {
            this.socket.onclose = null; // Прибираємо хендлер, щоб не реконектився
            this.socket.close();
            this.socket = null;
        }
    }

    public onMessage(handler: MessageHandler) {
        this.handlers.push(handler);
        // Повертаємо функцію відписки
        return () => {
            this.handlers = this.handlers.filter(h => h !== handler);
        };
    }
}
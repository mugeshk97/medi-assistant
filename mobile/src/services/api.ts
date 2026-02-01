import axios, { AxiosInstance } from 'axios';
import { ChatRequest, Thread, ChatHistoryResponse } from '../types';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000/api/v1';

class ApiService {
    private client: AxiosInstance;
    private authToken: string | null = null;

    constructor() {
        this.client = axios.create({
            baseURL: API_URL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor for logging
        this.client.interceptors.request.use(
            (config) => {
                console.log('API Request:', config.method?.toUpperCase(), config.url);
                return config;
            },
            (error) => {
                console.error('Request Error:', error);
                return Promise.reject(error);
            }
        );

        // Response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('API Error:', error.response?.data || error.message);
                // Handle 401 errors (unauthorized) - token expired or invalid
                if (error.response?.status === 401) {
                    this.authToken = null;
                }
                throw error;
            }
        );
    }

    /**
     * Set authentication token for API requests
     */
    setAuthToken(token: string | null) {
        this.authToken = token;
        if (token) {
            this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.client.defaults.headers.common['Authorization'];
        }
    }

    /**
     * Register a new user
     */
    async register(email: string, username: string, password: string) {
        const response = await this.client.post('/auth/register', {
            email,
            username,
            password
        });
        return response.data;
    }

    /**
     * Login user
     */
    async login(username: string, password: string) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await this.client.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    }

    /**
     * Get current user info
     */
    async getCurrentUser() {
        const response = await this.client.get('/auth/me');
        return response.data;
    }

    async sendMessage(
        request: Omit<ChatRequest, 'user_id'>,  // user_id now comes from JWT
        onChunk: (chunk: string) => void
    ): Promise<void> {
        try {
            const headers: Record<string, string> = {
                'Content-Type': 'application/json',
            };

            // Add auth header if token is set
            if (this.authToken) {
                headers['Authorization'] = `Bearer ${this.authToken}`;
            }

            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers,
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error('Response body is null');
            }

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                onChunk(chunk);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    /**
     * Get all threads for authenticated user
     */
    async getThreads(): Promise<Thread[]> {
        try {
            const response = await this.client.get<Thread[]>('/threads');  // No user_id needed
            return response.data;
        } catch (error) {
            console.error('Error fetching threads:', error);
            throw error;
        }
    }

    /**
     * Get chat history for a thread
     */
    async getChatHistory(threadId: string): Promise<ChatHistoryResponse> {
        try {
            const response = await this.client.get<ChatHistoryResponse>(
                `/history/${threadId}`  // No user_id query param needed
            );
            return response.data;
        } catch (error) {
            console.error('Error fetching chat history:', error);
            throw error;
        }
    }

    /**
     * Delete a thread
     */
    async deleteThread(threadId: string): Promise<void> {
        try {
            await this.client.delete(
                `/threads/${threadId}`  // No user_id query param needed
            );
        } catch (error) {
            console.error('Error deleting thread:', error);
            throw error;
        }
    }

    /**
     * Health check endpoint
     */
    async healthCheck(): Promise<boolean> {
        try {
            const response = await axios.get(`${API_URL.replace('/api/v1', '')}/health`);
            return response.data.status === 'ok';
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }
}

export default new ApiService();
export { ApiService };


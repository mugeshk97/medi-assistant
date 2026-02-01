export interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

export interface Thread {
    thread_id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface ChatRequest {
    message: string;
    thread_id: string;
    // user_id is now extracted from JWT token on backend
}

export interface ChatHistoryResponse {
    thread_id: string;
    messages: Message[];
}

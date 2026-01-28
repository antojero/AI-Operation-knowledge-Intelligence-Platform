import axios from 'axios';

// Phase 2: Direct Client-to-Backend or via Next.js Proxy?
// For SSE we usually go direct or via proxy.
// Authentication: We need to pass the JWT.

// We will assume a Next.js Proxy or Auth headers are handled.
// For now, let's target the Core API via a proxy or direct if CORS allowed.
// docker-compose maps backend-core:8000 and backend-agent:8001.
// Localhost: 8000, 8001.

const CORE_API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || 'http://localhost:8000/api';
const AGENT_API_URL = process.env.NEXT_PUBLIC_AGENT_API_URL || 'http://localhost:8001/agent';

export const apiClient = axios.create({
    baseURL: CORE_API_URL,
    withCredentials: true, // For cookies
    auth: {
        username: 'admin',
        password: 'admin' // Dev default
    },
    headers: {
        'Content-Type': 'application/json',
    },
});

export const agentClient = axios.create({
    baseURL: AGENT_API_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

export const triggerAgent = async (task: string) => {
    // Design: Agent Service for Runs.
    return agentClient.post('/run', { task });
};

export const uploadDocument = async (file: File, title: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    // Uploads go to backend-core
    return apiClient.post('/documents/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

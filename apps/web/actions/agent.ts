'use server'

import axios from 'axios';

const AGENT_API_URL = process.env.AGENT_API_URL || 'http://localhost:8001';

export async function startAgentRun(task: string) {
    try {
        const response = await axios.post(`${AGENT_API_URL}/agent/run`, {
            task: task
        });
        return { success: true, data: response.data };
    } catch (error: any) {
        console.error("Failed to start agent run:", error);
        return { success: false, error: error.message };
    }
}

export async function streamAgentRun(task: string) {
    // This is a placeholder. Streaming is handled client-side via EventSource.
    // However, we might need a server action to initiate or validate.
    return { url: `${AGENT_API_URL}/agent/stream`, task };
}

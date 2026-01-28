import { useState, useRef, useCallback } from 'react';

type AgentEvent =
    | { type: 'start'; thread_id: string }
    | { type: 'tool_start'; tool: string; input: any }
    | { type: 'tool_end'; tool: string; output: any }
    | { type: 'complete'; result: string }
    | { type: 'error'; message: string };

export function useAgentStream() {
    const [events, setEvents] = useState<AgentEvent[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [result, setResult] = useState<string | null>(null);

    const startStream = useCallback(async (task: string) => {
        setIsStreaming(true);
        setEvents([]);
        setResult(null);

        try {
            // Direct fetch to agent service (proxied or direct)
            // Using fetch because axios doesn't handle streams well natively without adapters
            const response = await fetch('http://localhost:8001/agent/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task })
            });

            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            setIsStreaming(false);
                            break;
                        }
                        try {
                            const event = JSON.parse(data) as AgentEvent;
                            setEvents(prev => [...prev, event]);
                            if (event.type === 'complete') {
                                setResult(event.result);
                            }
                        } catch (e) {
                            console.error('Failed to parse SSE event', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Streaming error:', error);
            setEvents(prev => [...prev, { type: 'error', message: String(error) }]);
        } finally {
            setIsStreaming(false);
        }
    }, []);

    return { events, isStreaming, result, startStream };
}

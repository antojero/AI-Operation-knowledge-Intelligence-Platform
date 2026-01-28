export type AgentEvent =
    | { type: 'start', thread_id: string }
    | { type: 'tool_start', tool: string, input: any }
    | { type: 'tool_end', tool: string, output: any }
    | { type: 'complete', result: string }
    | { type: 'error', message: string }
    | { type: 'source', title: string }
    | { type: 'search_complete', result: string, total_results: number };

/**
 * Fast direct search - bypasses LLM for instant results
 */
export async function fetchDirectSearch(
    query: string,
    onEvent: (event: AgentEvent) => void,
    onDone: () => void
) {
    try {
        onEvent({ type: 'start', thread_id: 'direct-search' });

        const response = await fetch('http://localhost:8001/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task: query })
        });

        if (!response.ok) {
            onEvent({ type: 'error', message: `Search failed: ${response.statusText}` });
            onDone();
            return;
        }

        const data = await response.json();
        console.log("[DEBUG] Direct Search Data:", data);

        if (data.status === 'success') {
            console.log("[DEBUG] Emitting search_complete");

            // Emit source events if available
            if (data.sources && Array.isArray(data.sources)) {
                data.sources.forEach((source: any) => {
                    onEvent({ type: 'source', title: source.title });
                });
            }

            onEvent({
                type: 'search_complete',
                result: data.answer,
                total_results: data.total_results || 1
            });
        } else {
            console.error("[DEBUG] Search failed:", data);
            onEvent({ type: 'error', message: data.answer || 'Search failed' });
        }

        onDone();
    } catch (e: any) {
        onEvent({ type: 'error', message: e.message });
        onDone();
    }
}

/**
 * LLM-powered agent stream (slower but more intelligent)
 */
export async function fetchAgentStream(
    task: string,
    onEvent: (event: AgentEvent) => void,
    onDone: () => void
) {
    const response = await fetch('http://localhost:8001/agent/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task })
    });

    if (!response.ok) {
        onEvent({ type: 'error', message: `Stream connection failed: ${response.statusText}` });
        onDone();
        return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                onDone();
                break;
            }

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        onDone();
                        return;
                    }
                    try {
                        const parsed = JSON.parse(data);
                        onEvent(parsed);
                    } catch (e) {
                        console.error("Error parsing stream data", e);
                    }
                }
            }
        }
    } catch (e: any) {
        onEvent({ type: 'error', message: e.message });
        onDone();
    }
}

/**
 * Smart fetch - uses direct search for document queries, LLM for complex tasks
 */
export async function fetchSmart(
    query: string,
    onEvent: (event: AgentEvent) => void,
    onDone: () => void
) {
    // Keywords that suggest a document/knowledge base query
    // Expanded to catch user intent "Explain..." or "What is..." in the context of their project
    const documentKeywords = [
        'file', 'document', 'abstract', 'hrms', 'policy', 'report', 'find', 'show me',
        'literature', 'survey', 'project', 'system', 'introduction', 'abstract', 'explain', 'what is'
    ];
    const isDocumentQuery = documentKeywords.some(keyword =>
        query.toLowerCase().includes(keyword)
    );

    // Default to Agent Stream for now to ensure robustness, but Direct Search is available if needed.
    // The user wants "stored in database ONLY" -> Direct Search is actually safer for that constraint.
    if (isDocumentQuery) {
        // Use fast direct search
        await fetchDirectSearch(query, onEvent, onDone);
    } else {
        // Use LLM-powered agent for complex reasoning
        await fetchAgentStream(query, onEvent, onDone);
    }
}

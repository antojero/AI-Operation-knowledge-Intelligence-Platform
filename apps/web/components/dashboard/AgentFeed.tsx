import { Activity, CheckCircle, Terminal, Cpu } from 'lucide-react';

export function AgentFeed({ events = [], isStreaming = false, result = null }: { events: any[], isStreaming: boolean, result: string | null }) {
    return (
        <div className="flex flex-col gap-6 max-w-3xl mx-auto pb-20">
            {events.length === 0 && !isStreaming && !result && (
                <div className="text-center text-muted-foreground py-10">
                    <p>Run an agent to see live results here.</p>
                </div>
            )}

            {/* Live Events Stream */}
            <div className="space-y-4">
                {events.map((event, i) => (
                    <div key={i} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <EventItem event={event} />
                    </div>
                ))}

                {isStreaming && (
                    <div className="flex items-center gap-3 text-muted-foreground animate-pulse p-4 border border-border/50 rounded-lg bg-muted/20">
                        <Cpu size={18} className="animate-spin" />
                        <span>Agent is thinking...</span>
                    </div>
                )}
            </div>

            {/* Final Result */}
            {result && (
                <div className="mt-8 p-6 rounded-lg border border-border bg-card shadow-xl animate-in zoom-in-95 duration-500">
                    <div className="flex items-center gap-2 mb-4 text-green-500 font-medium">
                        <CheckCircle size={20} />
                        <span>Mission Complete</span>
                    </div>
                    <div className="prose prose-invert max-w-none">
                        {/* Phase 6: Generative UI will replace this raw dump */}
                        <div className="whitespace-pre-wrap">{result}</div>
                    </div>
                </div>
            )}
        </div>
    );
}

function EventItem({ event }: { event: any }) {
    if (event.type === 'start') {
        return (
            <div className="flex items-center gap-3 text-sm text-muted-foreground border-b border-border/50 pb-2">
                <Activity size={16} />
                <span>Started run <span className="font-mono text-xs">{event.thread_id.slice(0, 8)}</span></span>
            </div>
        );
    }
    if (event.type === 'tool_start') {
        return (
            <div className="flex gap-3 text-sm p-3 rounded-lg bg-muted/30 border border-border/50">
                <Terminal size={16} className="mt-1 text-blue-400" />
                <div>
                    <span className="font-medium text-blue-400">Executing Tool: {event.tool}</span>
                    <div className="font-mono text-xs text-muted-foreground mt-1 truncate max-w-md">
                        {JSON.stringify(event.input)}
                    </div>
                </div>
            </div>
        );
    }
    return null;
}

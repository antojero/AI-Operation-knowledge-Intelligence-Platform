'use client';
import { useState } from 'react';
import { Search, ArrowRight, Loader2 } from 'lucide-react';
import { triggerAgent } from '@/lib/api';

export function CommandBar({ onRunStarted }: { onRunStarted?: (task: string) => void }) {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        // setLoading(true); // Don't block UI for streaming start
        try {
            // await triggerAgent(query); // Removed: handled by startStream now
            if (onRunStarted) onRunStarted(query);
            setQuery('');
        } catch (error) {
            console.error(error);
        } finally {
            // setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto mb-8">
            <form onSubmit={handleSubmit} className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-muted-foreground pb-2">
                    <Search size={20} />
                </div>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask the agent to research, analyze, or plan..."
                    className="w-full bg-background border-b border-border focus:border-blue-500 py-4 pl-12 pr-12 text-lg outline-none placeholder:text-muted-foreground/50 transition-all"
                    disabled={loading}
                    autoFocus
                />
                <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center pb-2 text-primary disabled:opacity-50"
                >
                    {loading ? <Loader2 className="animate-spin" /> : <ArrowRight />}
                </button>
            </form>
        </div>
    );
}

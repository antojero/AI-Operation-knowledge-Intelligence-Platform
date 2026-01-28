'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Clock, CheckCircle, AlertCircle, Loader2, FileText, RefreshCw, Zap, Search } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Button } from "@/components/ui/button";

interface AgentRun {
    id: string;
    task: string;
    agent_type: string;
    status: 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';
    cost_usd: string;
    created_at: string;
    input_params: any;
    output_result: any;
}

export default function HistoryPage() {
    const [runs, setRuns] = useState<AgentRun[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchRuns();
    }, []);

    const fetchRuns = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/agent/runs/');
            console.log("[DEBUG] History Runs:", response.data);
            setRuns(response.data);
        } catch (err: any) {
            console.error("Failed to fetch history", err);
            setError(err.response?.data?.detail || err.message || "Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 'bg-green-500/10 text-green-400 hover:bg-green-500/20 border-green-500/20';
            case 'FAILED': return 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border-red-500/20';
            case 'RUNNING': return 'bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 border-blue-500/20';
            default: return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-100">Agent History</h1>
                    <p className="text-slate-400 mt-2">View past missions, costs, and results.</p>
                </div>
                <div className="flex items-center gap-3">
                    <Badge variant="outline" className="px-4 py-2 border-slate-700 bg-slate-900 text-slate-300">
                        Total Runs: {runs.length}
                    </Badge>
                    <Button
                        onClick={fetchRuns}
                        variant="outline"
                        size="sm"
                        className="border-slate-700 hover:bg-slate-800"
                    >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="animate-spin text-blue-500 mb-4" size={40} />
                    <p className="text-slate-500">Loading agent history...</p>
                </div>
            ) : error ? (
                <Card className="bg-red-950/20 border-red-900/50">
                    <CardContent className="py-10 text-center">
                        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
                        <p className="text-red-400 font-semibold mb-2">Failed to Load History</p>
                        <p className="text-red-300/70 text-sm mb-4">{error}</p>
                        <Button onClick={fetchRuns} variant="outline" className="border-red-700 hover:bg-red-950">
                            Try Again
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <div className="flex flex-col space-y-4 max-w-5xl mx-auto pb-12">
                    {runs.length === 0 && (
                        <Card className="bg-slate-900/50 border-slate-800 text-center py-16">
                            <CardContent>
                                <FileText className="h-16 w-16 text-slate-700 mx-auto mb-4" />
                                <p className="text-slate-400 text-lg font-medium mb-2">No agent runs found yet</p>
                                <p className="text-slate-600 text-sm">Start a mission from the Command Center to see it here.</p>
                            </CardContent>
                        </Card>
                    )}

                    {runs.map((run) => (
                        <Card key={run.id} className="bg-slate-950/80 border-slate-800 hover:border-slate-700 transition-all hover:shadow-lg hover:shadow-blue-900/10">
                            <CardHeader className="pb-3 border-b border-white/5">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-3">
                                        <Badge variant="outline" className="text-slate-500 border-slate-700 font-mono text-[10px]">
                                            {run.id.slice(0, 8)}
                                        </Badge>
                                        {run.agent_type === 'direct_search' ? (
                                            <Badge variant="secondary" className="bg-blue-900/40 text-blue-300 border-blue-800 hover:bg-blue-900/60 p-1 px-2 text-[10px]">
                                                <Search size={10} className="mr-1" /> FAST SEARCH
                                            </Badge>
                                        ) : (
                                            <Badge variant="secondary" className="bg-purple-900/40 text-purple-300 border-purple-800 hover:bg-purple-900/60 p-1 px-2 text-[10px]">
                                                <Zap size={10} className="mr-1" /> AI AGENT
                                            </Badge>
                                        )}
                                        <div className="flex items-center gap-1 text-xs text-slate-500">
                                            <Clock size={12} />
                                            <span>{new Date(run.created_at).toLocaleString()}</span>
                                        </div>
                                        {(() => {
                                            // Safe token parsing
                                            let tokens = 0;
                                            try {
                                                if (run.output_result) {
                                                    const res = typeof run.output_result === 'string'
                                                        ? JSON.parse(run.output_result)
                                                        : run.output_result;
                                                    tokens = res.tokens || 0;
                                                }
                                            } catch (e) { console.error("Token parse error", e); }

                                            if (tokens > 0) {
                                                return (
                                                    <Badge variant="outline" className="ml-2 text-xs font-mono text-slate-500 border-slate-700 bg-slate-900/50">
                                                        {tokens} Tokens
                                                    </Badge>
                                                );
                                            }
                                            return null;
                                        })()}
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-xs font-mono text-slate-600">
                                            ${parseFloat(run.cost_usd || '0').toFixed(6)}
                                        </span>
                                        <Badge className={`${getStatusColor(run.status)} border text-[10px] px-2`}>
                                            {run.status}
                                        </Badge>
                                    </div>
                                </div>
                                <CardTitle className="text-lg font-semibold text-slate-100 leading-snug">
                                    {run.input_params?.task || run.task || "Unnamed Task"}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="pt-4">
                                {run.status === 'COMPLETED' && run.output_result && (
                                    <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
                                        <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
                                            {(() => {
                                                const resp = run.output_result.response;
                                                if (typeof resp === 'string') return resp;
                                                if (typeof resp === 'object') return JSON.stringify(resp, null, 2);
                                                return "No output available.";
                                            })()}
                                        </div>
                                    </div>
                                )}
                                {run.status === 'FAILED' && (
                                    <div className="p-3 bg-red-950/20 rounded border border-red-900/30 flex items-start gap-2">
                                        <AlertCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
                                        <span className="text-xs text-red-400">Task failed to complete.</span>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}

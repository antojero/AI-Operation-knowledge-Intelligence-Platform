'use client';

import { useState, useEffect } from 'react';
import { fetchSmart, AgentEvent } from '@/lib/agent-stream';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Play, CheckCircle, Terminal, Zap, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function AgentControl() {
    const [task, setTask] = useState('');
    const [isRunning, setIsRunning] = useState(false);
    const [logs, setLogs] = useState<AgentEvent[]>([]);
    const [result, setResult] = useState<string | null>(null);
    const [sources, setSources] = useState<string[]>([]); // Track unique sources
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        setIsMounted(true);
    }, []);

    const handleStart = async () => {
        if (!task.trim()) return;

        setIsRunning(true);
        setLogs([]);
        setResult(null);
        setSources([]);

        await fetchSmart(
            task,
            (event) => {
                console.log("[DEBUG] AgentControl Event:", event);
                if (event.type === 'complete' || event.type === 'search_complete') {
                    setResult(event.result);
                } else if (event.type === 'source') {
                    setSources(prev => {
                        if (prev.includes(event.title)) return prev;
                        return [...prev, event.title];
                    });
                } else {
                    setLogs(prev => [...prev, event]);
                }
            },
            () => {
                setIsRunning(false);
            }
        );
    };

    if (!isMounted) {
        return null; // Prevent hydration mismatch
    }

    return (
        <div className="h-full flex flex-col space-y-6">

            {/* Top Section: Split View (Input & Logs) */}
            <div className="grid lg:grid-cols-3 gap-6 flex-1 min-h-[500px]">

                {/* Left Column: Mission Control (1/3) */}
                <Card className="lg:col-span-1 border-slate-800 bg-slate-950 flex flex-col h-full shadow-2xl relative overflow-hidden">
                    {/* Decorative top gradient */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-600 to-indigo-600"></div>

                    <CardHeader className="border-b border-slate-800/50 pb-4">
                        <CardTitle className="flex items-center gap-2 text-xl text-white font-bold tracking-tight">
                            <Zap className="h-5 w-5 text-indigo-400" />
                            New Mission
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6 pt-6 flex-1 flex flex-col">
                        <div className="space-y-3">
                            <label className="text-xs font-semibold text-white uppercase tracking-wider ml-1">Mission Objective</label>
                            <Input
                                placeholder="Describe your task..."
                                value={task}
                                onChange={(e) => setTask(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && !isRunning && handleStart()}
                                disabled={isRunning}
                                className="bg-slate-900 border-slate-800 text-slate-100 placeholder:text-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 h-14 text-lg rounded-xl shadow-inner"
                            />
                            <Button
                                onClick={handleStart}
                                disabled={isRunning || !task}
                                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white h-12 text-base font-medium rounded-xl shadow-lg shadow-indigo-900/20 transition-all active:scale-[0.98]"
                            >
                                {isRunning ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Play className="mr-2 h-5 w-5" fill="currentColor" />}
                                Start Mission
                            </Button>
                        </div>

                        <div className="mt-auto pt-6 border-t border-slate-800/50">
                            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                                <strong className="text-slate-300 block mb-3 text-sm flex items-center gap-2">
                                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-400"></div>
                                    System Active
                                </strong>
                                <ul className="text-xs text-slate-500 space-y-2 font-medium">
                                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-slate-600" /> Powered by Gemini 2.0 Flash</li>
                                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-slate-600" /> Vector Memory Online</li>
                                    <li className="flex items-center gap-2"><CheckCircle className="h-3 w-3 text-slate-600" /> Live Web Search Enabled</li>
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Right Column: Live Terminal (2/3) */}
                <Card className="lg:col-span-2 border-slate-800 bg-black flex flex-col h-full min-h-[500px] lg:min-h-0 shadow-2xl overflow-hidden rounded-xl">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 py-3 px-4 border-b border-slate-800 bg-slate-900/40 backdrop-blur">
                        <CardTitle className="text-[10px] font-mono text-slate-500 uppercase tracking-widest flex items-center gap-2">
                            <Terminal className="h-3 w-3" />
                            Console_Output
                        </CardTitle>
                        {isRunning && (
                            <div className="flex items-center gap-2 px-2 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/20">
                                <span className="relative flex h-1.5 w-1.5">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-indigo-500"></span>
                                </span>
                                <span className="text-[10px] text-indigo-400 font-mono font-bold">EXECUTING</span>
                            </div>
                        )}
                    </CardHeader>
                    <CardContent className="flex-1 p-0 relative bg-black/50">
                        <ScrollArea className="h-full absolute inset-0">
                            <div className="p-4 space-y-1 font-mono text-sm leading-relaxed">
                                {logs.map((log, i) => (
                                    <div key={i} className="flex gap-3 animate-in fade-in slide-in-from-left-1 duration-150 group">
                                        <span className="text-slate-700 shrink-0 select-none w-14 text-right text-[10px] pt-1 opacity-50 group-hover:opacity-100 transition-opacity">
                                            {new Date().toLocaleTimeString().split(' ')[0]}
                                        </span>
                                        <div className="break-all whitespace-pre-wrap flex-1 border-l border-slate-800 pl-3 py-0.5">
                                            {log.type === 'start' && <span className="text-indigo-400 font-bold">🚀 Workflow Started: {log.thread_id.slice(0, 8)}</span>}
                                            {log.type === 'tool_start' && <span className="text-yellow-500">➜ Executing Tool: <span className="text-yellow-200 font-semibold">{log.tool}</span></span>}
                                            {log.type === 'tool_end' && <span className="text-emerald-500">✔ Completed: {log.tool}</span>}
                                            {log.type === 'error' && <span className="text-red-400 bg-red-950/20 px-1">✖ Error: {log.message}</span>}
                                        </div>
                                    </div>
                                ))}
                                {isRunning && (
                                    <div className="pl-[5.5rem] mt-2">
                                        <span className="inline-block w-2 h-4 bg-indigo-500 animate-pulse align-middle"></span>
                                    </div>
                                )}
                                {!isRunning && logs.length === 0 && !result && (
                                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                                        <div className="text-center">
                                            <Terminal className="h-20 w-20 text-slate-500 mx-auto mb-4" />
                                            <p className="text-slate-500 font-mono text-sm">System Ready.</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </div>

            {/* Bottom Section: Result (Full Width) */}
            {result && (
                <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <Card className="border-indigo-500/20 bg-slate-950 shadow-2xl relative overflow-hidden rounded-xl">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-purple-500"></div>
                        <CardHeader className="py-4 px-6 border-b border-white/5 bg-white/5 backdrop-blur-sm">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="h-8 w-8 rounded-full bg-indigo-500/20 flex items-center justify-center ring-1 ring-indigo-500/40">
                                        <CheckCircle className="h-4 w-4 text-indigo-400" />
                                    </div>
                                    <h3 className="text-lg font-bold text-slate-100 tracking-tight">Mission Result</h3>
                                </div>
                                {/* Sources Display */}
                                {sources.length > 0 && (
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Sources:</span>
                                        <div className="flex items-center gap-2">
                                            {sources.map((source, i) => (
                                                <span key={i} className="flex items-center gap-1 bg-indigo-500/20 text-indigo-200 text-xs px-2 py-1 rounded-md border border-indigo-500/30">
                                                    <FileText className="h-3 w-3" />
                                                    {source}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent className="p-8">
                            <div className="prose prose-invert prose-lg max-w-none prose-headings:text-white prose-p:text-white prose-strong:text-white prose-li:text-white prose-ul:text-white prose-ol:text-white prose-code:text-yellow-200 text-white">
                                <ReactMarkdown
                                    components={{
                                        pre: ({ node, ...props }) => <pre className="bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-x-auto shadow-inner my-6" {...props} />,
                                        code: ({ node, ...props }) => <code className="bg-slate-900/80 px-1.5 py-0.5 rounded border border-slate-700/50 font-mono text-sm" {...props} />,
                                        table: ({ node, ...props }) => <div className="overflow-x-auto my-6 border border-slate-800 rounded-lg"><table className="w-full text-left" {...props} /></div>,
                                        th: ({ node, ...props }) => <th className="bg-slate-900/80 p-4 font-semibold text-slate-200 border-b border-slate-800" {...props} />,
                                        td: ({ node, ...props }) => <td className="p-4 border-b border-slate-800/50 text-slate-400" {...props} />,
                                    }}
                                >
                                    {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
                                </ReactMarkdown>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}


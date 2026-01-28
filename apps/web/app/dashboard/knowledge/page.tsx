'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '@/lib/api';

export default function KnowledgePage() {
    const [file, setFile] = useState<File | null>(null);
    const [title, setTitle] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            // Auto-fill title if empty
            if (!title) {
                setTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
            }
        }
    };

    const handleUpload = async () => {
        if (!file || !title) return;

        setIsUploading(true);
        setUploadStatus('idle');
        setErrorMessage('');

        try {
            await uploadDocument(file, title);
            setUploadStatus('success');
            setFile(null);
            setTitle('');
        } catch (error: any) {
            console.error(error);
            setUploadStatus('error');
            setErrorMessage(error.response?.data?.error || "Failed to upload document");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
                    <p className="text-slate-400 mt-2">Upload documents to feed the AI's long-term memory.</p>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Upload Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Add New Document</CardTitle>
                        <CardDescription>Upload PDF or text files used for RAG (Retrieval Augmented Generation).</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <label htmlFor="title" className="text-sm font-medium">Document Title</label>
                            <Input
                                id="title"
                                type="text"
                                placeholder="e.g. Q3 Financial Report"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                            />
                        </div>

                        <div className="grid w-full max-w-sm items-center gap-1.5">
                            <label htmlFor="file" className="text-sm font-medium">File Source</label>
                            <Input
                                id="file"
                                type="file"
                                accept=".pdf,.txt,.md"
                                onChange={handleFileChange}
                            />
                        </div>

                        {uploadStatus === 'error' && (
                            <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/10 p-3 rounded-md">
                                <AlertCircle size={16} />
                                <span>{errorMessage}</span>
                            </div>
                        )}

                        {uploadStatus === 'success' && (
                            <div className="flex items-center gap-2 text-green-400 text-sm bg-green-400/10 p-3 rounded-md">
                                <CheckCircle size={16} />
                                <span>Document processed and embedded successfully!</span>
                            </div>
                        )}

                        <Button
                            className="w-full"
                            onClick={handleUpload}
                            disabled={!file || !title || isUploading}
                        >
                            {isUploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Processing & Embedding...
                                </>
                            ) : (
                                <>
                                    <Upload className="mr-2 h-4 w-4" />
                                    Upload & Index
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Info Card */}
                <Card className="bg-slate-900/50 border-slate-800">
                    <CardHeader>
                        <CardTitle className="text-lg">How Memory Works</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4 text-sm text-slate-400">
                        <p>
                            When you upload a document, the system automatically:
                        </p>
                        <ul className="list-disc pl-4 space-y-2">
                            <li><span className="text-white">Extracts text</span> from PDFs or text files.</li>
                            <li><span className="text-white">Chunks</span> the content into smaller, semantic pieces.</li>
                            <li><span className="text-white">Generates Embeddings</span> using the local Ollama model (`nomic-embed-text`).</li>
                            <li><span className="text-white">Stores Vectors</span> in the PostgreSQL `pgvector` database.</li>
                        </ul>
                        <p className="pt-2">
                            The <strong>AI Agents</strong> can then perform semantic search across this knowledge base to answer questions or perform research based on your private data.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

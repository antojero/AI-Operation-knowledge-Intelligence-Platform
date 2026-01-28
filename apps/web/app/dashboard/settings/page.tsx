"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { User, Lock, Key, Globe, Bell, Shield, Save } from "lucide-react";
import { useState } from "react";

export default function SettingsPage() {
    const [isLoading, setIsLoading] = useState(false);

    const handleSave = () => {
        setIsLoading(true);
        // Simulate API call
        setTimeout(() => setIsLoading(false), 1000);
    };

    return (
        <div className="space-y-6 max-w-4xl mx-auto pb-20">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-100">Settings</h1>
                <p className="text-slate-400 mt-2">Manage your account settings and system preferences.</p>
            </div>

            <div className="grid gap-6">
                {/* Profile Section */}
                <Card className="bg-slate-950 border-slate-800">
                    <CardHeader className="border-b border-slate-800 pb-4">
                        <div className="flex items-center gap-2">
                            <User className="w-5 h-5 text-blue-500" />
                            <div>
                                <CardTitle className="text-lg font-medium text-slate-100">Profile Information</CardTitle>
                                <CardDescription className="text-slate-500">Update your account details and profile info.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6 space-y-4">
                        <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Display Name</label>
                                <Input placeholder="JERO" className="bg-slate-900 border-slate-700" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Email Address</label>
                                <Input placeholder="jero@aiops.platform" type="email" className="bg-slate-900 border-slate-700" />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* API Configuration */}
                {/* <Card className="bg-slate-950 border-slate-800">
                    <CardHeader className="border-b border-slate-800 pb-4">
                        <div className="flex items-center gap-2">
                            <Key className="w-5 h-5 text-indigo-500" />
                            <div>
                                <CardTitle className="text-lg font-medium text-slate-100">API Configuration</CardTitle>
                                <CardDescription className="text-slate-500">Manage API keys for external services.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6 space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">OpenAI API Key</label>
                            <div className="relative">
                                <Input type="password" placeholder="sk-..." className="bg-slate-900 border-slate-700 pr-10" />
                                <Lock className="w-4 h-4 text-slate-500 absolute right-3 top-3" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Google Gemini Key</label>
                            <div className="relative">
                                <Input type="password" placeholder="AIza..." className="bg-slate-900 border-slate-700 pr-10" />
                                <Lock className="w-4 h-4 text-slate-500 absolute right-3 top-3" />
                            </div>
                        </div>
                    </CardContent>
                </Card> */}

                {/* System Preferences */}
                <Card className="bg-slate-950 border-slate-800">
                    <CardHeader className="border-b border-slate-800 pb-4">
                        <div className="flex items-center gap-2">
                            <Globe className="w-5 h-5 text-emerald-500" />
                            <div>
                                <CardTitle className="text-lg font-medium text-slate-100">System Preferences</CardTitle>
                                <CardDescription className="text-slate-500">Configure global system behavior.</CardDescription>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="pt-6 space-y-4">
                        <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-800">
                            <div className="flex items-center gap-3">
                                <Bell className="w-5 h-5 text-slate-400" />
                                <div>
                                    <p className="text-sm font-medium text-slate-200">Email Notifications</p>
                                    <p className="text-xs text-slate-500">Receive alerts when agents complete tasks.</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-emerald-500 font-medium">Enabled</span>
                            </div>
                        </div>
                        <div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-800">
                            <div className="flex items-center gap-3">
                                <Shield className="w-5 h-5 text-slate-400" />
                                <div>
                                    <p className="text-sm font-medium text-slate-200">Audit Logging</p>
                                    <p className="text-xs text-slate-500">Record all agent actions for security.</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-emerald-500 font-medium">Enabled</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>


            </div>
        </div >
    );
}

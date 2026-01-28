"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [djangoStatus, setDjangoStatus] = useState<string>("Checking...");
  const [fastApiStatus, setFastApiStatus] = useState<string>("Checking...");

  useEffect(() => {
    // Check Django Core
    fetch("http://localhost:8000/admin/login/")
      .then((res) => {
        if (res.status === 200) setDjangoStatus("Online (200 OK)");
        else setDjangoStatus(`Error (${res.status})`);
      })
      .catch((err) => setDjangoStatus("Offline (Check Console)"));

    // Check FastAPI Agent
    fetch("http://localhost:8001/")
      .then((res) => res.json())
      .then((data) => setFastApiStatus(`Online: ${data.service}`))
      .catch((err) => setFastApiStatus("Offline (Check Console)"));
  }, []);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)] bg-slate-950 text-white">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start max-w-2xl w-full">
        <h1 className="text-4xl font-bold tracking-tighter bg-gradient-to-r from-blue-400 to-emerald-400 text-transparent bg-clip-text">
          AI Operations Platform
        </h1>
        <p className="text-slate-400">
          Phase 0: System Foundation Status
        </p>

        <div className="grid gap-4 w-full">
          {/* Django Status Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/50 flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-lg text-blue-200">Core API (Django)</h3>
              <p className="text-sm text-slate-500">Business Logic & Auth</p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${djangoStatus.includes("Online") ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
              {djangoStatus}
            </div>
          </div>

          {/* FastAPI Status Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/50 flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-lg text-purple-200">Agent Service (FastAPI)</h3>
              <p className="text-sm text-slate-500">AI Execution Engine</p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${fastApiStatus.includes("Online") ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
              {fastApiStatus}
            </div>
          </div>
        </div>

        <div className="mt-8 p-4 bg-blue-950/30 border border-blue-900/50 rounded-lg text-sm text-blue-200">
          <strong>Project Flow:</strong> Phase 0 is complete. The backend is running.
          <br />
          Next: <strong>Phase 1 - AI Agents</strong>.
        </div>
      </main>
    </div>
  );
}

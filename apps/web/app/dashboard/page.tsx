import AgentControl from "@/components/agent/AgentControl";

export default function DashboardPage() {
    return (
        <div className="h-full flex flex-col">
            <div className="flex-1 h-full">
                <h1 className="text-3xl font-bold mb-6 tracking-tight text-slate-100">Command Center</h1>
                <AgentControl />
            </div>
        </div>
    );
}

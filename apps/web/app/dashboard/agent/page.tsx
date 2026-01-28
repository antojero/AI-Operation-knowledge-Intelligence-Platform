import AgentControl from "@/components/agent/AgentControl";

export default function AgentPage() {
    return (
        <div className="flex-1 space-y-4 p-8 pt-6">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">AI Command Center</h2>
                <div className="flex items-center space-x-2">
                    {/* Status indicators can go here */}
                </div>
            </div>
            <div className="h-10" /> {/* Spacer */}
            <AgentControl />
        </div>
    );
}

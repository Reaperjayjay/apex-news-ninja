import { useHealth } from "@/hooks/useHealth";
import { cn } from "@/lib/utils";
import { Wifi, WifiOff } from "lucide-react";

export const BackendStatus = () => {
    const { data, isError, isLoading } = useHealth();
    const isConnected = !isLoading && !isError && data?.status === "healthy";

    return (
        <div
            className={cn(
                "fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium shadow-lg transition-all duration-300",
                isConnected
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
            )}
        >
            {isConnected ? (
                <>
                    <Wifi className="h-3 w-3" />
                    <span>Connected</span>
                </>
            ) : (
                <>
                    <WifiOff className="h-3 w-3" />
                    <span>Disconnected</span>
                </>
            )}
        </div>
    );
};

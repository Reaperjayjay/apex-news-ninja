import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type HealthResponse = {
    status: string;
    service: string;
    environment: string;
    database: string;
};

export const useHealth = () => {
    return useQuery({
        queryKey: ["health"],
        queryFn: () => api.get<HealthResponse>("/health"),
        refetchInterval: 30000, // Check every 30 seconds
        retry: false,
    });
};

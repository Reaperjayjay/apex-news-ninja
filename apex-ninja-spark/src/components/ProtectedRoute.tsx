import { useAuth } from "@/context/AuthContext";
import { Navigate } from "react-router-dom";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
    const { isLoggedIn, isLoading } = useAuth();

    // 1. If we are still checking the token, show a spinner (or nothing)
    if (isLoading) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    // 2. If check is done and we are NOT logged in, kick them out
    if (!isLoggedIn) {
        return <Navigate to="/auth" replace />;
    }

    // 3. If logged in, let them in!
    return <>{children}</>;
};

export default ProtectedRoute;
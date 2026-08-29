import AppRoutes from "./routes/AppRoutes";
import { Toaster } from "./components/ui/sonner";
import ErrorBoundary from "./components/ErrorBoundary";
import { Analytics } from "@vercel/analytics/react";

export default function App() {
    return (
        <ErrorBoundary>
            <AppRoutes />
            <Toaster />
            <Analytics />
        </ErrorBoundary>
    );
}

import AppRoutes from "./routes/AppRoutes";
import { Toaster } from "./components/ui/sonner";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
    return (
        <ErrorBoundary>
            <AppRoutes />
            <Toaster />
        </ErrorBoundary>
    );
}

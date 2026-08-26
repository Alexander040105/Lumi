import { Component } from "react";

import { I18nContext } from "@/i18n";

export default class ErrorBoundary extends Component {
  static contextType = I18nContext;

  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    const message = error?.message ? `${error.name || "Error"}: ${error.message}` : String(error);
    console.error("ErrorBoundary caught:", message);
    console.error("Error object:", error);
    console.error("Component stack:", errorInfo?.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      const { t } = this.context || {};

      const isApiError = this.state.error?.message?.includes("fetch") ||
                         this.state.error?.message?.includes("Network") ||
                         this.state.error?.message?.includes("Request failed");

      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
          <div className="max-w-md w-full bg-card rounded-xl shadow-sm border border-border p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-foreground mb-2">
              {isApiError ? t?.("errorBoundary.connectionErrorTitle") : t?.("errorBoundary.genericErrorTitle")}
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              {isApiError
                ? t?.("errorBoundary.connectionErrorDescription")
                : this.state.error?.message || t?.("errorBoundary.genericErrorDescription")}
            </p>
            <button
              onClick={this.handleRetry}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90"
            >
              {t?.("errorBoundary.tryAgain")}
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

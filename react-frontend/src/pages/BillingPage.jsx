import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Check, Crown, Loader2 } from "lucide-react";

export default function BillingPage() {
  const { isPremium, effectivePlan, accessToken } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/billing/checkout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        toast.info(data.message || "Billing integration not yet active. Contact admin for upgrade.");
      }
    } catch {
      toast.error("Failed to start checkout.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Billing & Plans</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Free Plan */}
        <Card className={effectivePlan === "free" ? "border-primary" : "border-muted"}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Free
              {effectivePlan === "free" && (
                <span className="text-xs font-normal bg-muted px-2 py-0.5 rounded-full">
                  Current
                </span>
              )}
            </CardTitle>
            <CardDescription>For individuals getting started.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Basic Ecosim calculator
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                EnergyHub data & charts
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                3 AI Ecosim runs / month
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                5 EnergyHub AI insights / month
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                10 chat messages / month
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Save up to 3 simulations
              </li>
            </ul>
          </CardContent>
        </Card>

        {/* Premium Plan */}
        <Card className={isPremium ? "border-primary" : "border-muted"}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="h-5 w-5 text-amber-500" />
              Premium
              {isPremium && (
                <span className="text-xs font-normal bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                  Current
                </span>
              )}
            </CardTitle>
            <CardDescription>For power users and professionals.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Everything in Free
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Unlimited AI Ecosim runs
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Unlimited EnergyHub AI insights
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Unlimited chart analysis
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Unlimited chat messages
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Unlimited saved simulations
              </li>
              <li className="flex items-start gap-2">
                <Check className="h-4 w-4 text-green-600 mt-0.5 shrink-0" />
                Export results (PDF/CSV)
              </li>
            </ul>
            {!isPremium && (
              <Button className="w-full mt-2" onClick={handleCheckout} disabled={loading}>
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Upgrade to Premium"}
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

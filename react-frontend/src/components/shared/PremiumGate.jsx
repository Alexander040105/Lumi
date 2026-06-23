import { Lock } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export default function PremiumGate({ children, fallback = null }) {
  const { isPremium } = useAuth();
  const navigate = useNavigate();

  if (isPremium) return children;

  return (
    fallback || (
      <div className="flex flex-col items-center justify-center p-8 text-center border rounded-lg bg-muted/50 gap-3">
        <Lock className="w-8 h-8 text-muted-foreground" />
        <div>
          <p className="font-medium">Premium Feature</p>
          <p className="text-sm text-muted-foreground">
            Upgrade to Premium to unlock this feature.
          </p>
        </div>
        <Button size="sm" onClick={() => navigate("/billing")}>
          Upgrade
        </Button>
      </div>
    )
  );
}

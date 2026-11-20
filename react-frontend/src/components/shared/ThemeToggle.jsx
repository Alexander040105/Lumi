import { Moon, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n";
import { useTheme } from "@/hooks/useTheme";

export default function ThemeToggle() {
  const { t } = useI18n();
  const { theme, toggleTheme } = useTheme();

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      aria-label={t("common.toggleTheme")}
      className="h-9 w-9 rounded-full border-border/80"
    >
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </Button>
  );
}

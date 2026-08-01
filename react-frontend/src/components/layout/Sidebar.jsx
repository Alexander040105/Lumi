import { LayoutDashboard, Layers, Settings } from "lucide-react";

import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";

export default function Sidebar() {
  const { t } = useI18n();

  const items = [
    { label: t("layout.overview"), icon: LayoutDashboard },
    { label: t("layout.modules"), icon: Layers },
    { label: t("layout.settings"), icon: Settings }
  ];

  return (
    <aside className="hidden w-60 shrink-0 border-r bg-card/50 p-6 md:block">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary">{t("layout.workspace")}</p>
        <div className="space-y-1">
          {items.map((item) => (
            <Button key={item.label} variant="ghost" className="w-full justify-start gap-2 text-muted-foreground hover:bg-muted hover:text-foreground">
              <item.icon size={16} />
              {item.label}
            </Button>
          ))}
        </div>
      </div>
    </aside>
  );
}

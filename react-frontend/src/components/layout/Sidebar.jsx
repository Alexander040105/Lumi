import { LayoutDashboard, Layers, Settings } from "lucide-react";

import { Button } from "@/components/ui/button";

const items = [
  { label: "Overview", icon: LayoutDashboard },
  { label: "Modules", icon: Layers },
  { label: "Settings", icon: Settings }
];

export default function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r bg-background p-6 md:block">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase text-muted-foreground">Workspace</p>
        <div className="space-y-1">
          {items.map((item) => (
            <Button key={item.label} variant="ghost" className="w-full justify-start gap-2">
              <item.icon size={16} />
              {item.label}
            </Button>
          ))}
        </div>
      </div>
    </aside>
  );
}

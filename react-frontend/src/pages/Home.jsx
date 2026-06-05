import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <section className="page-container stack">
      <div className="space-y-3 rounded-xl bg-gradient-to-br from-card to-muted/40 p-6 shadow-sm border">
        <Badge variant="default" className="bg-primary text-primary-foreground">Lumi Environmental Intelligence</Badge>
        <h1 className="text-primary">Renewable energy insights for every community.</h1>
        <p>
          A clean UI foundation with Supabase auth, FastAPI integration, and a scalable component
          system ready for dashboards and environmental data workflows.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/dashboard">
            <Button>Open dashboard</Button>
          </Link>
          <Link to="/ecosim">
            <Button variant="outline">Try Ecosim</Button>
          </Link>
        </div>
      </div>

      <div className="grid-cards">
        {["Auth ready", "Design system", "API connected", "Dark mode"].map((title) => (
          <Card key={title}>
            <CardHeader>
              <CardTitle>{title}</CardTitle>
              <CardDescription>Production-ready defaults and clean structure.</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Extend the starter with your own domain modules and routes.</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}

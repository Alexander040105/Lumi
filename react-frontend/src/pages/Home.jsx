import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <section className="page-container stack">
      <div className="space-y-3">
        <Badge variant="secondary">React + Tailwind + shadcn/ui</Badge>
        <h1>Build your next full-stack product faster.</h1>
        <p>
          A clean UI foundation with Supabase auth, FastAPI integration, and a scalable component
          system ready for dashboards and SaaS workflows.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link to="/dashboard">
            <Button>Open dashboard</Button>
          </Link>
          <Link to="/login">
            <Button variant="outline">Go to login</Button>
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

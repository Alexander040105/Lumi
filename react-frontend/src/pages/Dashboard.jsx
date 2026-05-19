import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { getProtectedMe, getHealth } from "../services/apiClient";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

const formSchema = z.object({
  label: z.string().min(2, "Label must be at least 2 characters")
});

export default function Dashboard() {
  const { accessToken, user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: { label: "" }
  });

  useEffect(() => {
    if (!accessToken) return;

    Promise.all([getProtectedMe(accessToken), getHealth()])
      .then(([me, healthStatus]) => {
        setProfile(me.user);
        setHealth(healthStatus);
      })
      .catch((err) => setError(err.message));
  }, [accessToken]);

  const onSubmit = (values) => {
    toast.success(`Saved: ${values.label}`);
    form.reset();
  };

  return (
    <section className="page-container stack">
      <div className="page-header">
        <div className="space-y-2">
          <h1>Dashboard</h1>
          <p>Signed in as {user?.email || "unknown"}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline">Open filters</Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Filters</SheetTitle>
                <SheetDescription>Use filters to narrow down data.</SheetDescription>
              </SheetHeader>
              <div className="mt-4 space-y-2 text-sm text-muted-foreground">
                Add filtering controls here.
              </div>
            </SheetContent>
          </Sheet>
          <Dialog>
            <DialogTrigger asChild>
              <Button>Create item</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create item</DialogTitle>
                <DialogDescription>Connect this dialog to your form logic.</DialogDescription>
              </DialogHeader>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {error && <Card className="border-destructive text-destructive">{error}</Card>}

      {!profile && !error && <LoadingSkeleton />}

      {profile && (
        <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <Card>
            <CardHeader>
              <CardTitle>JWT Claims</CardTitle>
              <CardDescription>Validated by FastAPI.</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-xs text-muted-foreground">
                {JSON.stringify(profile, null, 2)}
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API Health</CardTitle>
              <CardDescription>Live status from FastAPI.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Badge variant={health?.status === "ok" ? "default" : "secondary"}>
                {health?.status || "unknown"}
              </Badge>
              <p className="text-sm text-muted-foreground">Service: {health?.service || "-"}</p>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    Quick actions
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem>Refresh status</DropdownMenuItem>
                  <DropdownMenuItem>View logs</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick form</CardTitle>
              <CardDescription>Example of form + input + validation.</CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="label"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Label</FormLabel>
                        <FormControl>
                          <Input placeholder="New label" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Button type="submit">Save</Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Recent activity</CardTitle>
          <CardDescription>Example table layout.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Module</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Owner</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {["Auth", "Billing", "Analytics"].map((row) => (
                <TableRow key={row}>
                  <TableCell>{row}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">In progress</Badge>
                  </TableCell>
                  <TableCell>Team Lumi</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </section>
  );
}

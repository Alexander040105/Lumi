import { Link } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  BrainCircuit,
  ChevronRight,
  Database,
  FlaskConical,
  Globe,
  LayoutDashboard,
  Lightbulb,
  Microscope,
  Monitor,
  Server,
  Users,
  Zap
} from "lucide-react";

import { useI18n } from "@/i18n";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import CitationSources from "@/components/shared/CitationSources";
import ExpandableBlock from "@/components/shared/ExpandableBlock";

function SectionHeading({ badge, title, subtitle }) {
  return (
    <div className="mx-auto max-w-3xl text-center space-y-4">
      {badge && (
        <Badge variant="secondary" className="text-xs font-medium tracking-wide uppercase">
          {badge}
        </Badge>
      )}
      <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
        {title}
      </h2>
      {subtitle && (
        <p className="text-lg text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}

function ValueCard({ icon: Icon, title, description }) {
  return (
    <Card className="border-border/60 bg-card/80 transition-all hover:border-primary/30 hover:shadow-md">
      <CardHeader className="space-y-3">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <Icon className="h-6 w-6" />
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-sm leading-relaxed">{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}

function TechItem({ icon: Icon, title, items }) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card p-6 transition-all hover:border-primary/30 hover:shadow-md">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <ul className="mt-3 space-y-2">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-brand-success" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function About() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/50" />
        <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-accent/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />

        <div className="relative page-container py-16 sm:py-24">
          <div className="mx-auto max-w-4xl text-center space-y-6">
            <Badge
              variant="outline"
              className="border-primary/30 bg-primary/5 text-primary px-3 py-1 text-sm"
            >
              {t("about.hero.badge")}
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              {t("about.hero.title")}{" "}
              <span className="bg-gradient-to-r from-primary to-brand-success bg-clip-text text-transparent">
                {t("about.hero.titleHighlight")}
              </span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
              {t("about.hero.subtitle")}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link to="/energyhub">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  {t("about.hero.exploreEnergyData")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.hero.compareEnergyOptions")}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ABOUT LUMI */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <div className="grid gap-12 lg:grid-cols-2 items-start">
          <div className="space-y-6">
            <Badge variant="secondary" className="uppercase tracking-wide text-xs">
              {t("about.problem.badge")}
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("about.problem.title")}
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              {t("about.problem.paragraph1")}
            </p>
            <CitationSources ids={t("about.problem.citations")} className="mt-2" />
          </div>
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
                <div className="text-3xl font-bold text-primary">{t("about.problem.stats.fossilShare.value")}</div>
                <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.fossilShare.label")}</div>
                <div className="text-xs text-muted-foreground mt-1">{t("about.problem.stats.fossilShare.description")}</div>
              </div>
              <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
                <div className="text-3xl font-bold text-primary">{t("about.problem.stats.renewableShare.value")}</div>
                <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.renewableShare.label")}</div>
                <div className="text-xs text-muted-foreground mt-1">{t("about.problem.stats.renewableShare.description")}</div>
              </div>
              <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6 sm:col-span-2">
                <div className="text-3xl font-bold text-primary">{t("about.problem.stats.barriers.value")}</div>
                <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.barriers.label")}</div>
                <div className="text-xs text-muted-foreground mt-1">{t("about.problem.stats.barriers.description")}</div>
              </div>
            </div>
            <div className="flex flex-col items-center gap-2 rounded-xl border border-border/60 bg-card/50 p-4 text-center">
              <p className="text-sm text-muted-foreground">{t("about.problem.viewSourcesPrompt")}</p>
              <CitationSources ids={t("about.problem.citations")} />
            </div>
          </div>
        </div>
      </section>

      {/* MISSION & VISION */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge={t("about.mission.badge")}
            title={t("about.mission.title")}
            subtitle={t("about.mission.subtitle")}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <ValueCard
              icon={Globe}
              title={t("about.mission.mission.title")}
              description={t("about.mission.mission.description")}
            />
            <ValueCard
              icon={Lightbulb}
              title={t("about.mission.vision.title")}
              description={t("about.mission.vision.description")}
            />
          </div>
        </div>
      </section>

      {/* WHO CAN USE LUMI */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("about.beneficiaries.badge")}
          title={t("about.beneficiaries.title")}
          subtitle={t("about.beneficiaries.subtitle")}
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <BookOpen className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.beneficiaries.students.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                {t("about.beneficiaries.students.description")}
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <Users className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.beneficiaries.households.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                {t("about.beneficiaries.households.description")}
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <Globe className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.beneficiaries.communities.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                {t("about.beneficiaries.communities.description")}
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        <div className="flex justify-center">
          <CitationSources ids={t("about.beneficiaries.citations")} />
        </div>
      </section>

      {/* SYSTEM OVERVIEW */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge={t("about.system.badge")}
            title={t("about.system.title")}
            subtitle={t("about.system.subtitle")}
          />

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: BarChart3, key: "energyHub" },
              { icon: Zap, key: "ecosim" },
              { icon: BrainCircuit, key: "ai" },
              { icon: Database, key: "dataViz" }
            ].map(({ icon: Icon, key }) => (
              <div key={key} className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                  <Icon className="h-7 w-7" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">{t(`about.system.${key}.title`)}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  {t(`about.system.${key}.description`)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECHNOLOGY STACK */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("about.technology.badge")}
          title={t("about.technology.title")}
          subtitle={t("about.technology.subtitle")}
        />

        <ExpandableBlock title={t("about.technology.viewTechnical")} className="max-w-4xl mx-auto">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <TechItem
              icon={Monitor}
              title={t("about.technology.frontend.title")}
              items={t("about.technology.frontend.items")}
            />
            <TechItem
              icon={Server}
              title={t("about.technology.backend.title")}
              items={t("about.technology.backend.items")}
            />
            <TechItem
              icon={Database}
              title={t("about.technology.database.title")}
              items={t("about.technology.database.items")}
            />
            <TechItem
              icon={BrainCircuit}
              title={t("about.technology.ai.title")}
              items={t("about.technology.ai.items")}
            />
          </div>
        </ExpandableBlock>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-primary/5 to-accent/5 p-6 sm:p-8">
          <h3 className="text-xl font-semibold text-foreground text-center">
            {t("about.technology.impact.title")}
          </h3>
          <p className="mx-auto mt-3 max-w-2xl text-muted-foreground leading-relaxed text-center">
            {t("about.technology.impact.description")}
          </p>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {(t("about.technology.impact.features") || []).map((feature, i) => (
              <div key={i} className="text-center space-y-2">
                <h4 className="font-semibold text-foreground">{feature.title}</h4>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="border-t border-border/40 bg-muted/20">
        <div className="page-container py-12">
          <div className="mx-auto max-w-4xl space-y-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              {t("citationSources.title")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("citationSources.description")}
            </p>
            <CitationSources ids={[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]} />
          </div>
        </div>
      </section>

      {/* FOOTER CTA */}
      <section className="relative overflow-hidden border-t border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="relative page-container py-16 sm:py-20">
          <div className="mx-auto max-w-3xl text-center space-y-6">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("about.footer.title")}
            </h2>
            <p className="mx-auto max-w-xl text-lg text-muted-foreground leading-relaxed">
              {t("about.footer.subtitle")}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/energyhub">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  {t("about.footer.exploreMyArea")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.footer.compareEnergyOptions")}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

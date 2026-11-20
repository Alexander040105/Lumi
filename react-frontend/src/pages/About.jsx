import { Link } from "react-router-dom";
import {
  BarChart3,
  BrainCircuit,
  Cog,
  Database,
  Layers,
  Leaf,
  TriangleAlert,
  Waypoints,
  Zap
} from "lucide-react";

import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";
import CitationSources from "@/components/shared/CitationSources";

const REVISED = "/assets/revised/about";

const BENEFICIARY_IMAGES = [
  "households",
  "doe",
  "denr",
  "ngcp",
  "future-researchers"
];

const MODULE_ICONS = {
  energyHub: BarChart3,
  ecosim: Zap,
  ai: BrainCircuit,
  dataViz: Database
};

const TECH_BADGE_ASSETS = [
  `${REVISED}/python-logo.webp`,
  `${REVISED}/fastapi-logo.webp`,
  `${REVISED}/react-logo.webp`,
  `${REVISED}/postgresql-logo.webp`,
  null
];

function StatCard({ icon: Icon, value, label, description }) {
  return (
    <div className="bg-card p-6">
      <Icon className="h-6 w-6 text-primary" aria-hidden="true" />
      <div className="mt-3 text-3xl font-extrabold text-foreground">{value}</div>
      <div className="mt-1 text-sm font-semibold text-primary">{label}</div>
      <div className="mt-1 text-xs leading-relaxed text-muted-foreground">{description}</div>
    </div>
  );
}

export default function About() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="page-container py-10 sm:py-16">
        <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <h1 className="text-3xl font-extrabold leading-[1.15] tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              {t("about.hero.title")}{" "}
              <span className="mt-1 block text-primary">
                {t("about.hero.titleHighlight")}
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
              {t("about.hero.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Button asChild className="h-12 gap-2 rounded-full bg-primary px-6 text-base font-medium text-primary-foreground shadow-sm hover:bg-primary/90">
                <Link to="/ecosim">
                  <Zap className="h-4 w-4 fill-current" aria-hidden="true" />
                  {t("about.hero.compareEnergyOptions")}
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-12 gap-2 rounded-full border-border bg-muted/40 px-6 text-base font-medium text-foreground hover:bg-muted">
                <Link to="/energyhub">
                  <BarChart3 className="h-4 w-4 text-primary" aria-hidden="true" />
                  {t("about.hero.exploreEnergyData")}
                </Link>
              </Button>
            </div>
          </div>
          <div className="rounded-3xl bg-sky-200 p-4 sm:p-6 lg:col-span-5">
            <img
              src={`${REVISED}/header-family.webp`}
              alt=""
              className="w-full rounded-2xl object-contain"
            />
          </div>
        </div>
      </section>

      {/* WHY LUMI + STATS ROW */}
      <section className="page-container">
        <div className="grid grid-cols-1 gap-px overflow-hidden rounded-3xl border border-border/80 bg-border/60 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-card p-6">
            <img
              src={`${REVISED}/why-lumi-created.webp`}
              alt=""
              className="h-16 w-auto object-contain"
              loading="lazy"
            />
            <h2 className="mt-4 text-lg font-semibold text-primary">
              {t("about.problem.title")}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {t("about.problem.paragraph1")}
            </p>
          </div>
          <StatCard
            icon={Waypoints}
            value={t("about.problem.stats.fossilShare.value")}
            label={t("about.problem.stats.fossilShare.label")}
            description={t("about.problem.stats.fossilShare.description")}
          />
          <StatCard
            icon={Leaf}
            value={t("about.problem.stats.renewableShare.value")}
            label={t("about.problem.stats.renewableShare.label")}
            description={t("about.problem.stats.renewableShare.description")}
          />
          <StatCard
            icon={TriangleAlert}
            value={t("about.problem.stats.barriers.value")}
            label={t("about.problem.stats.barriers.label")}
            description={t("about.problem.stats.barriers.description")}
          />
        </div>
      </section>

      {/* MISSION & VISION */}
      <section className="page-container py-16 sm:py-20">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="flex items-center gap-6 rounded-2xl border border-border/80 bg-card p-6 transition-shadow hover:shadow-md">
            <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-xl border border-border/80">
              <img
                src={`${REVISED}/mission.webp`}
                alt=""
                className="h-16 w-16 object-contain"
                loading="lazy"
              />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-primary">
                {t("about.mission.mission.title")}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {t("about.mission.mission.description")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 rounded-2xl border border-border/80 bg-card p-6 transition-shadow hover:shadow-md">
            <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-xl border border-border/80">
              <img
                src={`${REVISED}/vision.webp`}
                alt=""
                className="h-16 w-16 object-contain"
                loading="lazy"
              />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-primary">
                {t("about.mission.vision.title")}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {t("about.mission.vision.description")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* WHO CAN USE LUMI — dark forest banner */}
      <section className="page-container">
        <div className="rounded-3xl bg-brand-dark p-8 text-white sm:p-12">
          <div className="mx-auto max-w-3xl space-y-4 text-center">
            <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              {t("about.beneficiaries.title")}
            </h2>
            <p className="text-lg leading-relaxed text-white/80">
              {t("about.beneficiaries.subtitle")}
            </p>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {(t("about.beneficiaries.items") || []).map((item, index) => (
              <div
                key={item.title}
                className="flex flex-col items-center rounded-2xl bg-card p-5 text-center"
              >
                <img
                  src={`${REVISED}/${BENEFICIARY_IMAGES[index]}.webp`}
                  alt=""
                  className="h-28 w-auto object-contain"
                  loading="lazy"
                />
                <h3 className="mt-4 text-sm font-semibold leading-snug text-primary">
                  {item.title}
                </h3>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* STRUCTURE + TECHNOLOGY STACK */}
      <section className="page-container py-16 sm:py-20">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-border/80 bg-card p-8">
            <div className="flex items-center gap-3">
              <Layers className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
              <h2 className="text-xl font-semibold text-primary">
                {t("about.system.title")}
              </h2>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {t("about.system.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap gap-6">
              {["energyHub", "ecosim", "ai", "dataViz"].map((key) => {
                const Icon = MODULE_ICONS[key];
                return (
                  <div key={key} className="flex flex-col items-center gap-2 text-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-xl border border-border/80 text-primary">
                      <Icon className="h-7 w-7" aria-hidden="true" />
                    </div>
                    <div className="text-xs font-semibold text-foreground">
                      {t(`about.system.${key}.title`)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div className="rounded-2xl border border-border/80 bg-card p-8">
            <div className="flex items-center gap-3">
              <Cog className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
              <h2 className="text-xl font-semibold text-primary">
                {t("about.technology.title")}
              </h2>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {t("about.technology.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap gap-6">
              {(t("about.technology.badges") || []).map((name, index) => (
                <div key={name} className="flex flex-col items-center gap-2 text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-xl border border-border/80">
                    {TECH_BADGE_ASSETS[index] ? (
                      <img src={TECH_BADGE_ASSETS[index]} alt="" className="h-8 w-8 object-contain" loading="lazy" />
                    ) : (
                      <BrainCircuit className="h-7 w-7 text-primary" aria-hidden="true" />
                    )}
                  </div>
                  <div className="text-xs font-semibold text-foreground">{name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="page-container pb-16 sm:pb-20">
        <div className="flex flex-col items-start gap-4 rounded-2xl border border-border/80 bg-muted/30 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-muted-foreground">
            <strong className="font-semibold text-foreground">{t("citationSources.title")}:</strong>{" "}
            {t("citationSources.description")}
          </p>
          <CitationSources
            ids={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]}
            className="shrink-0"
          />
        </div>
      </section>

      {/* FOOTER CTA */}
      <section className="page-container pb-16 sm:pb-20">
        <div className="grid grid-cols-1 items-center gap-8 rounded-3xl border border-border/80 bg-muted/30 p-8 sm:p-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <img
              src={`${REVISED}/ready-to-explore.webp`}
              alt=""
              className="w-full rounded-2xl object-contain"
              loading="lazy"
            />
          </div>
          <div className="lg:col-span-7">
            <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              {t("about.footer.title")}
            </h2>
            <p className="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">
              {t("about.footer.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Button asChild className="h-12 gap-2 rounded-full bg-primary px-6 text-base font-medium text-primary-foreground shadow-sm hover:bg-primary/90">
                <Link to="/ecosim">
                  <Zap className="h-4 w-4 fill-current" aria-hidden="true" />
                  {t("about.footer.compareEnergyOptions")}
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-12 gap-2 rounded-full border-border bg-muted/40 px-6 text-base font-medium text-foreground hover:bg-muted">
                <Link to="/energyhub">
                  <BarChart3 className="h-4 w-4 text-primary" aria-hidden="true" />
                  {t("about.footer.exploreMyArea")}
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

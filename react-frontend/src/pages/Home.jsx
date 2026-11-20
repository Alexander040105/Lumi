import { Link } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  BrainCircuit,
  Clock,
  Database,
  Droplets,
  Leaf,
  Lightbulb,
  LineChart,
  MapPin,
  Scale,
  Sun,
  Wind,
  Zap
} from "lucide-react";

import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";
import CitationSources from "@/components/shared/CitationSources";

function SectionHeading({ title, subtitle }) {
  return (
    <div className="mx-auto max-w-3xl text-center space-y-4">
      <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
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

const REVISED = "/assets/revised/home";

function MetricCard({ icon: Icon, value, label, sub }) {
  return (
    <div className="flex items-start gap-4 rounded-2xl border border-border/80 bg-card p-5 transition-shadow hover:shadow-md">
      <div className="rounded-full bg-primary/10 p-2.5 text-primary">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <div className="text-2xl font-bold text-foreground">{value}</div>
        <div className="text-sm font-semibold text-foreground">{label}</div>
        <div className="text-xs text-muted-foreground">{sub}</div>
      </div>
    </div>
  );
}

function ToolCard({ icon: Icon, title, description, tags, image, imageAlt }) {
  return (
    <div className="flex flex-col rounded-2xl border border-border/80 bg-card p-6 transition-all hover:border-primary/40 hover:shadow-md">
      <div className="flex items-center gap-2">
        <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        {description}
      </p>
      <img
        src={image}
        alt={imageAlt}
        className="mx-auto my-4 h-40 w-auto max-w-full object-contain"
        loading="lazy"
      />
      <div className="mt-auto flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center rounded-full bg-muted/70 px-2.5 py-1 text-xs font-medium text-foreground"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

function StepCard({ number, icon: Icon, title, description }) {
  const { t } = useI18n();
  return (
    <div className="relative flex flex-col items-center text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-xl border border-white/30 bg-white/10 text-white">
        <Icon className="h-7 w-7" aria-hidden="true" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="text-xs font-bold uppercase tracking-wider text-white">
          {t("home.howItWorks.step")} {number}
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="mx-auto max-w-xs text-sm leading-relaxed text-white/80">
          {description}
        </p>
      </div>
    </div>
  );
}

function EnergyTypeCard({ icon: Icon, title, header, description, citationIds, badgeClass, image, imageAlt }) {
  const { t } = useI18n();
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border/80 bg-card p-6 transition-all hover:border-primary/40 hover:shadow-md">
      <div className="flex items-center gap-2">
        <Icon className="h-6 w-6 text-primary" aria-hidden="true" />
        <h3 className="text-xl font-semibold text-foreground">{title}</h3>
      </div>
      <span className={`w-fit rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${badgeClass}`}>
        {header}
      </span>
      <div className="flex items-center gap-4">
        <div className="flex-1 space-y-4">
          <p className="text-sm leading-relaxed text-muted-foreground">
            {description}
          </p>
          {citationIds?.length > 0 && (
            <CitationSources ids={citationIds} dialogLabel={t("home.references.viewSources")} />
          )}
        </div>
        <img
          src={image}
          alt={imageAlt}
          className="h-32 w-32 shrink-0 object-contain sm:h-36 sm:w-36"
          loading="lazy"
        />
      </div>
    </div>
  );
}

export default function Home() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="page-container py-10 sm:py-16">
        <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <h1 className="text-3xl font-extrabold leading-[1.15] tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              {t("home.hero.title")}{" "}
              <span className="mt-1 block text-primary">
                {t("home.hero.titleHighlight")}
              </span>
            </h1>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
              {t("home.hero.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Button asChild className="h-12 gap-2 rounded-full bg-primary px-6 text-base font-medium text-primary-foreground shadow-sm hover:bg-primary/90">
                <Link to="/ecosim">
                  <Zap className="h-4 w-4 fill-current" aria-hidden="true" />
                  {t("home.cta.tryEcosim")}
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-12 gap-2 rounded-full border-border bg-muted/40 px-6 text-base font-medium text-foreground hover:bg-muted">
                <Link to="/energyhub">
                  <BarChart3 className="h-4 w-4 text-primary" aria-hidden="true" />
                  {t("home.cta.tryEnergyHub")}
                </Link>
              </Button>
            </div>
          </div>
          <div className="lg:col-span-5">
            <img
              src={`${REVISED}/header-graphic.webp`}
              alt=""
              className="w-full rounded-3xl object-contain"
            />
          </div>
        </div>
      </section>

      {/* KEY METRICS */}
      <section className="page-container">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { icon: MapPin, key: "regionsCovered" },
            { icon: Leaf, key: "energySources" },
            { icon: Database, key: "dataPoints" },
            { icon: Clock, key: "aiInsights" }
          ].map(({ icon, key }) => (
            <MetricCard
              key={key}
              icon={icon}
              value={t(`home.stats.${key}.value`)}
              label={t(`home.stats.${key}.label`)}
              sub={t(`home.stats.${key}.sub`)}
            />
          ))}
        </div>
      </section>

      {/* INTELLIGENT TOOLS */}
      <section className="page-container space-y-10 py-16 sm:py-20">
        <SectionHeading
          title={t("home.features.title")}
          subtitle={t("home.features.subtitle")}
        />
        <div className="grid gap-6 md:grid-cols-3">
          <ToolCard
            icon={BarChart3}
            title={t("home.features.energyHub.title")}
            description={t("home.features.energyHub.description")}
            tags={t("home.features.energyHub.tags")}
            image={`${REVISED}/energyhub-graphic.webp`}
            imageAlt=""
          />
          <ToolCard
            icon={Zap}
            title={t("home.features.ecosim.title")}
            description={t("home.features.ecosim.description")}
            tags={t("home.features.ecosim.tags")}
            image={`${REVISED}/ecosim-graphic.webp`}
            imageAlt=""
          />
          <ToolCard
            icon={BrainCircuit}
            title={t("home.features.ai.title")}
            description={t("home.features.ai.description")}
            tags={t("home.features.ai.tags")}
            image={`${REVISED}/clear-explanations.webp`}
            imageAlt=""
          />
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="bg-brand-dark text-white">
        <div className="page-container space-y-12 py-16 sm:py-20">
          <div className="mx-auto max-w-3xl space-y-4 text-center">
            <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              {t("home.howItWorks.title")}
            </h2>
            <p className="text-lg leading-relaxed text-white/80">
              {t("home.howItWorks.subtitle")}
            </p>
          </div>

          <div className="relative grid gap-10 md:grid-cols-4">
            <div className="absolute left-[12.5%] right-[12.5%] top-7 hidden h-px bg-white/20 md:block" aria-hidden="true" />
            {t("home.howItWorks.steps").map((step, index) => {
              const icons = [MapPin, LineChart, Scale, Lightbulb];
              const Icon = icons[index];
              return (
                <StepCard
                  key={step.title}
                  number={index + 1}
                  icon={Icon}
                  title={step.title}
                  description={step.description}
                />
              );
            })}
          </div>
        </div>
      </section>

      {/* RENEWABLE ENERGY */}
      <section className="page-container space-y-10 py-16 sm:py-20">
        <SectionHeading
          title={t("home.renewable.title")}
          subtitle={t("home.renewable.subtitle")}
        />
        <div className="grid gap-6 lg:grid-cols-3">
          {[
            { icon: Sun, key: "solar", badgeClass: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300" },
            { icon: Wind, key: "wind", badgeClass: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300" },
            { icon: Droplets, key: "hydro", badgeClass: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300" }
          ].map(({ icon, key, badgeClass }) => (
            <EnergyTypeCard
              key={key}
              icon={icon}
              title={t(`home.renewable.${key}.title`)}
              header={t(`home.renewable.${key}.header`)}
              description={t(`home.renewable.${key}.description`)}
              citationIds={t(`home.renewable.${key}.citations`)}
              badgeClass={badgeClass}
              image={`${REVISED}/${key}-energy.webp`}
              imageAlt=""
            />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="page-container">
        <div className="grid grid-cols-1 items-center gap-8 rounded-3xl border border-border/80 bg-muted/30 p-8 sm:p-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <img
              src={`${REVISED}/sunny-family-solar-home.webp`}
              alt=""
              className="w-full rounded-2xl object-contain"
              loading="lazy"
            />
          </div>
          <div className="lg:col-span-7">
            <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              {t("home.cta.title")}
            </h2>
            <p className="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">
              {t("home.cta.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Button asChild className="h-12 gap-2 rounded-full bg-primary px-6 text-base font-medium text-primary-foreground shadow-sm hover:bg-primary/90">
                <Link to="/ecosim">
                  <Zap className="h-4 w-4 fill-current" aria-hidden="true" />
                  {t("home.cta.tryEcosim")}
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-12 gap-2 rounded-full border-border bg-muted/40 px-6 text-base font-medium text-foreground hover:bg-muted">
                <Link to="/energyhub">
                  <BarChart3 className="h-4 w-4 text-primary" aria-hidden="true" />
                  {t("home.cta.tryEnergyHub")}
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* DATA & RESEARCH */}
      <section className="page-container py-12">
        <div className="flex flex-col items-start gap-4 rounded-2xl border border-border/80 bg-muted/30 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
          <p className="flex items-start gap-2 text-sm text-muted-foreground">
            <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
            <span>
              <strong className="font-semibold text-foreground">{t("home.references.title")}:</strong>{" "}
              {t("home.references.intro")}
            </span>
          </p>
          <CitationSources
            ids={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]}
            dialogLabel={t("home.references.viewSources")}
            className="shrink-0"
          />
        </div>
      </section>
    </div>
  );
}

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
  Zap
} from "lucide-react";

import { useI18n, Trans } from "@/i18n";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function Cite({ children }) {
  return (
    <span className="text-sm font-medium text-primary/80">
      {" "}({children})
    </span>
  );
}

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
                  {t("about.hero.tryEnergyHub")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.hero.tryEcosim")}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ABOUT LUMI */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <div className="grid gap-12 lg:grid-cols-2 items-center">
          <div className="space-y-6">
            <Badge variant="secondary" className="uppercase tracking-wide text-xs">
              {t("about.problem.badge")}
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("about.problem.title")}
            </h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                <Trans
                  k="about.problem.paragraph1"
                  components={{
                    c1: <Cite>Gonocruz et al., 2024</Cite>,
                    c2: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>,
                    c3: <Cite>Wong et al., 2023</Cite>
                  }}
                />
              </p>
              <p>
                <Trans
                  k="about.problem.paragraph2"
                  components={{
                    c1: <Cite>Lenain, 2026</Cite>,
                    c2: <Cite>Esiri et al., 2024; Aguilera et al., 2024</Cite>
                  }}
                />
              </p>
              <p>
                <Trans
                  k="about.problem.paragraph3"
                  components={{
                    c1: <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>
                  }}
                />
              </p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.fossilShare.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.fossilShare.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.fossilShare.description"
                  components={{ c1: <Cite>Gonocruz et al., 2024</Cite> }}
                />
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.renewableShare.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.renewableShare.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.renewableShare.description"
                  components={{ c1: <Cite>Gonocruz et al., 2024</Cite> }}
                />
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6 sm:col-span-2">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.barriers.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.barriers.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.barriers.description"
                  components={{ c1: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025</Cite> }}
                />
              </div>
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

      {/* RESEARCH BACKGROUND */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("about.research.badge")}
          title={t("about.research.title")}
          subtitle={t("about.research.subtitle")}
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <BookOpen className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.educational.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.educational.description"
                  components={{ c1: <Cite>Aguilera et al., 2024</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <Microscope className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.decisionSupport.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.decisionSupport.description"
                  components={{ c1: <Cite>Estévez et al., 2021; Witt &amp; Klumpp, 2021</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <FlaskConical className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.researchGroundwork.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.researchGroundwork.description"
                  components={{ c1: <Cite>Bassetti, 2024</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-card to-muted/30 p-6 sm:p-8">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            {t("about.research.problemStatement.title")}
          </h3>
          <p className="text-muted-foreground leading-relaxed">
            <Trans
              k="about.research.problemStatement.description"
              components={{
                c1: <Cite>Wong et al., 2023</Cite>,
                c2: <Cite>Gonocruz et al., 2024</Cite>,
                c3: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>,
                c4: <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>
              }}
            />
          </p>
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
              { icon: BarChart3, key: "energyHub", cites: { c1: <Cite>"Dashboard," 2026; What Is Data Visualization?, n.d.</Cite>, c2: <Cite>Das et al., 2022; Bandara et al., 2026</Cite> } },
              { icon: Zap, key: "ecosim", cites: { c1: <Cite>Shatnawi et al., 2021</Cite> } },
              { icon: BrainCircuit, key: "ai", cites: { c1: <Cite>Panagoulias et al., 2023</Cite>, c2: <Cite>Algburi et al., 2025</Cite> } },
              { icon: Database, key: "dataViz", cites: { c1: <Cite>What Is Data Visualization?, n.d.</Cite>, c2: <Cite>Mustafa &amp; Al-Yozbaky, 2025</Cite> } }
            ].map(({ icon: Icon, key, cites }) => (
              <div key={key} className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                  <Icon className="h-7 w-7" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">{t(`about.system.modules.${key}.title`)}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  <Trans k={`about.system.modules.${key}.description`} components={cites} />
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

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-primary/5 to-accent/5 p-6 sm:p-8 text-center">
          <h3 className="text-xl font-semibold text-foreground">
            {t("about.technology.impact.title")}
          </h3>
          <p className="mx-auto mt-3 max-w-2xl text-muted-foreground leading-relaxed">
            {t("about.technology.impact.description")}
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            {t("about.technology.impact.tags").map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full bg-card border border-border/60 px-3 py-1 text-xs font-medium text-muted-foreground"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="border-t border-border/40 bg-muted/20">
        <div className="page-container py-12">
          <div className="mx-auto max-w-4xl space-y-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              {t("about.references")}
            </h3>
            <ol className="space-y-3 text-xs text-muted-foreground list-decimal list-inside">
              <li>
                Abdullah, A. G., Utami, H. P., Gunawan, B., Ratmono, B. M., & Pasaribu, N. T. (2025).
                Multi-criteria decision-making for wind power project feasibility: Trends, techniques, and future directions.
                <em> Cleaner Engineering and Technology</em>, 27, 100987.
              </li>
              <li>
                Aguilera, F., Reyes, R., Schueftan, A., Zerriffi, H., & Sanhueza, R. (2024).
                Understanding the role of people&apos;s preferences and perceptions in the analysis of residential energy transition: A meta-analysis.
                <em> Energy for Sustainable Development</em>, 82, 101534.
              </li>
              <li>
                Algburi, S., Kareem, S. S. a. A., Sapaev, I., Mukhitdinov, O., Hassan, Q., Khalaf, D. H., & Jabbar, F. I. (2025).
                The role of artificial intelligence in accelerating renewable energy adoption for global energy transformation.
                <em> Unconventional Resources</em>, 8, 100229.
              </li>
              <li>
                Bandara, A., Pandukabhaya, M., Ratnayake, K., Godaliyadda, R., Ekanayake, P., & Ekanayake, J. (2026).
                LSTM based model for weather-based Solar Irradiance Prediction for Long-Term PV Energy Planning.
                In <em>2025 IEEE 19th International Conference on Industrial and Information Systems (ICIIS)</em> (pp. 376–381).
              </li>
              <li>
                Bassetti, (2024). Environmental intelligence. <em>EcoMagazine</em>.
              </li>
              <li>
                Bączkiewicz, A., Wątróbski, J., Jankowski, J., & Sałabun, W. (2024).
                Multi-criteria Temporal Intelligent Decision Support System for Sustainable Energy Mix assessment.
                In <em>Lecture notes in computer science</em> (pp. 95–106).
              </li>
              <li>
                Beriro, D., Nathanail, J., Salazar, J., Kingdon, A., Marchant, A., Richardson, S., et al. (2022).
                A decision support system to assess the feasibility of onshore renewable energy infrastructure.
                <em> Renewable and Sustainable Energy Reviews</em>, 168, 112771.
              </li>
              <li>
                Das, U. K., Tey, K. S., Idris, M. Y. I. B., Mekhilef, S., Seyedmahmoudian, M., Stojcevski, A., & Horan, B. (2022).
                Optimized support Vector Regression-Based model for solar power generation forecasting on the basis of online weather reports.
                <em> IEEE Access</em>, 10, 15594–15604.
              </li>
              <li>
                Esiri, A. E., Kwakye, J. M., Ekechukwu, D. E., Ogundipe, O. B., & Ikevuje, A. H. (2024).
                Public perception and policy development in the transition to renewable energy.
                <em> Magna Scientia Advanced Research and Reviews</em>, 8(2), 228–237.
              </li>
              <li>
                Estévez, R. A., Espinoza, V., Ponce Oliva, R. D., Vásquez-Lavín, F., & Gelcich, S. (2021).
                Multi-criteria decision analysis for renewable energies: research trends, gaps and the challenge of improving participation.
                <em> Sustainability</em>, 13(6), 3515.
              </li>
              <li>
                Gonocruz, R. a. T., Yoshida, Y., Silava, N. E., Aguirre, R. A., Maguindayao, E. J. H., Ozawa, A., & Santiago, J. V. (2024).
                A multi-scenario evaluation of the energy transition mechanism in the Philippines towards decarbonization.
                <em> Journal of Cleaner Production</em>, 438, 140819.
              </li>
              <li>
                Lenain (2026). The Philippines&apos; climate adaptation initiatives. <em>Encyclopedia Britannica</em>.
              </li>
              <li>
                Mustafa, A. T., & Al-Yozbaky, O. S. A. (2025).
                Forecasting energy demand and generation using time series models: A comparative analysis of classical, grey, fuzzy, and intelligent approaches.
                <em> Franklin Open</em>, 12, 100350.
              </li>
              <li>
                Panagoulias, D. P., Sarmas, E., Marinakis, V., Virvou, M., Tsihrintzis, G. A., & Doukas, H. (2023).
                Intelligent Decision Support for Energy Management: A methodology for Tailored explainability of Artificial intelligence analytics.
                <em> Electronics</em>, 12(21), 4430.
              </li>
              <li>
                Rana, M., Mamun, M. a. A., Hossain, M. K., Rekha, R. S., & Alam, S. M. S. (2025).
                Understanding the adoption of renewable energy technologies by households in South Asia: a theory of planned behavior perspective.
                <em> Discover Sustainability</em>, 6(1).
              </li>
              <li>
                Shatnawi, N., Abu-Qdais, H., & Qdais, F. A. (2021).
                Selecting renewable energy options: an application of multi-criteria decision making for Jordan.
                <em> Sustainability Science Practice and Policy</em>, 17(1), 209–219.
              </li>
              <li>
                What Is Data Visualization? Definition, Examples, And Learning Resources. (n.d.). Tableau.
                https://www.tableau.com/visualization/what-is-data-visualization
              </li>
              <li>
                Witt, T., & Klumpp, M. (2021).
                Multi-period multi-criteria decision making under uncertainty: a renewable energy transition case from Germany.
                <em> Sustainability</em>, 13(11), 6300.
              </li>
              <li>
                Wong, G., Wong, K., Lau, T., Lee, J., & Kok, Y. (2023).
                Study of intention to use renewable energy technology in Malaysia using TAM and TPB.
                <em> Renewable Energy</em>, 221, 119787.
              </li>
              <li>
                Zhindon-Almeida, R. G., & Ruiz-Carrillo, J. A. (2025).
                Factors Influencing the Adoption of Renewable Energies in Developing Countries.
                <em> Sustainable Development</em>, 33(5), 7222–7244.
              </li>
            </ol>
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
                  {t("about.footer.tryEnergyHub")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.footer.launchEcosim")}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

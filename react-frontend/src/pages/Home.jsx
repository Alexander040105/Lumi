import { Link } from "react-router-dom";
import {
  BarChart3,
  BrainCircuit,
  Database,
  Droplets,
  LineChart,
  Lightbulb,
  MapPin,
  Sun,
  TrendingUp,
  Wind,
  Zap,
  ArrowRight,
  ChevronRight
} from "lucide-react";

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

function FeatureCard({ icon: Icon, title, description, tags }) {
  return (
    <Card className="group relative overflow-hidden border-border/60 bg-card/80 backdrop-blur-sm transition-all hover:border-primary/40 hover:shadow-lg">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary via-accent to-brand-success opacity-0 transition-opacity group-hover:opacity-100" />
      <CardHeader className="space-y-3">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <Icon className="h-6 w-6" />
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-sm leading-relaxed">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
            >
              {tag}
            </span>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function StepCard({ number, icon: Icon, title, description }) {
  return (
    <div className="relative flex flex-col items-center text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl border-2 border-primary-foreground/40 bg-primary-foreground/15 text-primary-foreground shadow-lg">
        <Icon className="h-7 w-7" />
      </div>
      <div className="mt-5 space-y-2">
        <div className="text-xs font-bold uppercase tracking-wider text-primary-foreground/70">
          Step {number}
        </div>
        <h3 className="text-lg font-semibold text-primary-foreground">{title}</h3>
        <p className="text-sm leading-relaxed text-primary-foreground/85 max-w-xs">
          {description}
        </p>
      </div>
    </div>
  );
}

function EnergyTypeCard({ icon: Icon, title, description, stat, colorClass }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-card p-6 transition-all hover:shadow-lg hover:border-primary/30">
      <div className={`absolute -right-4 -top-4 h-24 w-24 rounded-full opacity-10 ${colorClass}`} />
      <div className="space-y-4">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-xl font-semibold text-foreground">{title}</h3>
        <p className="text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
        <div className="pt-2">
          <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {stat}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="relative overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/50" />
        <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-accent/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />

        <div className="relative page-container py-20 sm:py-28">
          <div className="mx-auto max-w-4xl text-center space-y-8">
            <div className="flex justify-center">
              <img
                src="/lumi-logo.png"
                alt="LUMI Logo"
                className="h-20 w-auto object-contain drop-shadow-sm sm:h-24"
              />
            </div>

            <div className="space-y-4">
              <Badge
                variant="outline"
                className="border-primary/30 bg-primary/5 text-primary px-3 py-1 text-sm"
              >
                Environmental Intelligence for the Philippines
              </Badge>
              <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
                Data-Driven Insights for a{" "}
                <span className="bg-gradient-to-r from-primary to-brand-success bg-clip-text text-transparent">
                  Sustainable Future
                </span>
              </h1>
              <p className="mx-auto max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
                LUMI transforms complex climate and energy data into accessible,
                actionable insights. Evaluate renewable energy options, understand
                regional climate patterns, and make informed decisions backed by
                predictive analytics and AI-powered recommendations.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/dashboard">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  Explore Dashboard
                </Button>
              </Link>
              <Link to="/about">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  Learn More
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 gap-4 pt-8 sm:grid-cols-4">
              {[
                { label: "Regions Covered", value: "17+", sub: "Luzon, Visayas, Mindanao" },
                { label: "Energy Sources", value: "3", sub: "Solar, Wind, Hydro" },
                { label: "Data Points", value: "10K+", sub: "Climate & energy records" },
                { label: "AI Insights", value: "Real-time", sub: "Gemini-powered analysis" }
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-xl border border-border/50 bg-card/60 p-4 backdrop-blur-sm"
                >
                  <div className="text-2xl font-bold text-primary sm:text-3xl">{stat.value}</div>
                  <div className="text-sm font-medium text-foreground">{stat.label}</div>
                  <div className="text-xs text-muted-foreground">{stat.sub}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="relative border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge="Platform Modules"
            title="Intelligent Tools for Energy Decisions"
            subtitle="LUMI combines interactive dashboards, predictive forecasting, and AI-driven recommendations to bridge the gap between technical climate data and public understanding."
          />

          <div className="grid gap-6 md:grid-cols-3">
            <FeatureCard
              icon={BarChart3}
              title="EnergyHub"
              description="Interactive climate and energy dashboard displaying temperature trends, rainfall patterns, energy consumption, and electricity demand across Philippine regions with AI-generated interpretations."
              tags={["Regional Filtering", "KPIs & Charts", "AI Insights", "NGCP & OpenWeather"]}
            />
            <FeatureCard
              icon={Zap}
              title="Ecosim"
              description="A rule-based recommendation and simulation engine that evaluates solar, wind, and hydro feasibility per region. Input your monthly bill and consumption to see estimated costs, savings, and environmental impact."
              tags={["What-If Scenarios", "Cost Analysis", "ROI Estimation", "Source Comparison"]}
            />
            <FeatureCard
              icon={BrainCircuit}
              title="AI Intelligence"
              description="Powered by Gemini API, LUMI delivers contextual explanations for every chart, forecast, and recommendation. Natural language insights make complex environmental data understandable for everyone."
              tags={["Natural Language", "Chart Explanations", "Recommendations", "Comparative Summaries"]}
            />
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="relative overflow-hidden bg-primary text-primary-foreground">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYtMi42ODYgNi02cy0yLjY4Ni02LTYtNi02IDIuNjg2LTYgNiAyLjY4NiA2IDYgNnptMCAzMGMzLjMxNCAwIDYtMi42ODYgNi02cy0yLjY4Ni02LTYtNi02IDIuNjg2LTYgNiAyLjY4NiA2IDYgNnptLTE4LTE1YzMuMzE0IDAgNi0yLjY4NiA2LTZzLTIuNjg2LTYtNi02LTYgMi42ODYtNiA2IDIuNjg2IDYgNiA2eiIgZmlsbD0iI2ZmZiIgZmlsbC1vcGFjaXR5PSIwLjAzIi8+PC9nPjwvc3ZnPg==')] opacity-30" />
        <div className="page-container py-20 sm:py-24 space-y-16">
          <div className="mx-auto max-w-3xl text-center space-y-4">
            <Badge className="bg-primary-foreground/10 text-primary-foreground border-primary-foreground/20 uppercase tracking-wide">
              How LUMI Works
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              From Raw Data to Clear Decisions
            </h2>
            <p className="text-lg text-primary-foreground/80 leading-relaxed">
              LUMI simplifies the journey from scattered climate and energy information
              to confident renewable energy choices.
            </p>
          </div>

          <div className="relative grid gap-12 md:grid-cols-4">
            {/* Connector line for desktop */}
            <div className="hidden md:block absolute top-8 left-[12.5%] right-[12.5%] h-0.5 bg-primary-foreground/40" />

            <StepCard
              number={1}
              icon={Database}
              title="Data Collection"
              description="Aggregates public climate and energy datasets from NGCP, OpenWeather, and regional statistics into a unified, queryable foundation."
            />
            <StepCard
              number={2}
              icon={LineChart}
              title="Climate & Energy Analysis"
              description="Visualizes temperature trends, rainfall patterns, energy consumption, and demand across Luzon, Visayas, and Mindanao."
            />
            <StepCard
              number={3}
              icon={BrainCircuit}
              title="AI Processing"
              description="Applies rule-based logic and Gemini-powered AI to interpret patterns, generate forecasts, and produce contextual recommendations."
            />
            <StepCard
              number={4}
              icon={Lightbulb}
              title="Decision Support"
              description="Presents actionable insights, what-if simulations, and costed recommendations so users can choose the best renewable path forward."
            />
          </div>
        </div>
      </section>

      {/* RENEWABLE ENERGY */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge="Renewable Energy Evaluation"
          title="Solar, Wind & Hydro Analysis"
          subtitle="LUMI evaluates the feasibility of three core renewable energy sources tailored to Philippine regional conditions, helping users understand suitability, costs, and environmental benefits."
        />

        <div className="grid gap-6 sm:grid-cols-3">
          <EnergyTypeCard
            icon={Sun}
            title="Solar Energy"
            description="Evaluates solar irradiance, peak sun hours, and rooftop potential per region. Research shows Filipinos in Metro Manila demonstrate a strong preference for solar over biomass, wind, and small-scale hydropower, and community-based solar initiatives have provided positive impacts in island communities."
            stat="Palanca-Tan et al., 2024; Franco & Taeihagh, 2024"
            colorClass="bg-accent"
          />
          <EnergyTypeCard
            icon={Wind}
            title="Wind Energy"
            description="Analyzes wind speed patterns and turbine viability for coastal and elevated areas. Studies in the Philippines confirm that combining multi-criteria decision methods with machine learning yields accurate site selection for wind power, providing policymakers and investors with objective feasibility data."
            stat="Cerna et al., 2023; Abdullah et al., 2025"
            colorClass="bg-brand-success"
          />
          <EnergyTypeCard
            icon={Droplets}
            title="Hydro Energy"
            description="Assesses rainfall trends, river flow data, and micro-hydro opportunities. Research on hybrid renewable systems in Southern Philippines identifies hydropower as a viable component alongside solar and wind, with socio-environmental and techno-economic factors determining site suitability."
            stat="Tarife et al., 2023"
            colorClass="bg-primary"
          />
        </div>

        {/* Insight banner */}
        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-card to-muted/30 p-6 sm:p-8">
          <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">
                Why the Philippines Needs Renewable Intelligence
              </h3>
              <p className="text-sm text-muted-foreground max-w-xl">
                The Philippine grid relies on fossil fuels for approximately 70.5% of energy production
                <Cite>Gonocruz et al., 2024</Cite>. In developing countries like the Philippines, financial
                limitations, governance challenges, and societal resistance remain significant barriers
                <Cite>Zhindon-Almeida & Ruiz-Carrillo, 2025</Cite>. Public perception and education also
                significantly shape adoption intentions <Cite>Esiri et al., 2024; Aguilera et al., 2024</Cite>.
                LUMI closes this gap by transforming fragmented technical data into accessible,
                cost-inclusive insights.
              </p>
            </div>
            <Link to="/about">
              <Button variant="outline" className="shrink-0 gap-2">
                Read the Research
                <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden border-t border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="relative page-container py-20 sm:py-24">
          <div className="mx-auto max-w-3xl rounded-3xl border border-border/60 bg-card/80 p-8 text-center shadow-xl backdrop-blur-sm sm:p-12">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg mb-6">
              <TrendingUp className="h-8 w-8" />
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Start Analyzing Your Energy Future
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground leading-relaxed">
              Whether you are a student, homeowner, policymaker, or researcher, LUMI gives you
              the clarity to evaluate renewable energy with confidence backed by real data.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <Link to="/ecosim">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <Zap className="h-5 w-5" />
                  Try Ecosim
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <MapPin className="h-5 w-5" />
                  Explore by Region
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="border-t border-border/40 bg-muted/20">
        <div className="page-container py-12">
          <div className="mx-auto max-w-4xl space-y-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              References
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
                Cerna, P. D., Evangelista, R. S., Castillo, C. M., Muallam-Darkis, J. A., Velasco, M. a. C.,
                Legaspi, J. P., Darkis, A. T., & Gatdula, M. M. (2023).
                Wind Power Plant Site Selection using Integrated Machine Learning and Multiple-Criteria Decision Making Technique.
                <em> E3S Web of Conferences</em>, 405, 02030.
              </li>
              <li>
                Esiri, A. E., Kwakye, J. M., Ekechukwu, D. E., Ogundipe, O. B., & Ikevuje, A. H. (2024).
                Public perception and policy development in the transition to renewable energy.
                <em> Magna Scientia Advanced Research and Reviews</em>, 8(2), 228–237.
              </li>
              <li>
                Franco, M. Q., & Taeihagh, A. (2024).
                Sustainable energy adoption in poor rural areas: A comparative case perspective from the Philippines.
                <em> Energy for Sustainable Development</em>, 79, 101389.
              </li>
              <li>
                Gonocruz, R. a. T., Yoshida, Y., Silava, N. E., Aguirre, R. A., Maguindayao, E. J. H., Ozawa, A., & Santiago, J. V. (2024).
                A multi-scenario evaluation of the energy transition mechanism in the Philippines towards decarbonization.
                <em> Journal of Cleaner Production</em>, 438, 140819.
              </li>
              <li>
                Palanca-Tan, R., Del Barrio Alvarez, D., Palanca, R. S., Tan, N. M. P., Castillo, G. B.,
                Saplala, D. C. A., & Wang, N. (2024).
                Households&apos; Preferences for Alternative Renewable Energy Technologies: An Attribute-Based Choice Experiment survey in Metro Manila, Philippines.
                <em> International Journal of Sustainable Development and Planning</em>, 19(1), 1–10.
              </li>
              <li>
                Tarife, R., Nakanishi, Y., Zhou, Y., Estoperez, N., & Tahud, A. (2023).
                Integrated GIS and Fuzzy-AHP Framework for Suitability Analysis of hybrid Renewable Energy Systems: a case in Southern Philippines.
                <em> Sustainability</em>, 15(3), 2372.
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
    </div>
  );
}


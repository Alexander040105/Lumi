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
              About the System
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              Understanding{" "}
              <span className="bg-gradient-to-r from-primary to-brand-success bg-clip-text text-transparent">
                LUMI
              </span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
              A research-driven environmental intelligence system built to bridge the divide
              between complex climate data and the communities who need it most.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link to="/dashboard">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <LayoutDashboard className="h-5 w-5" />
                  Open Dashboard
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  Try Simulation
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
              The Problem We Address
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Why LUMI Was Developed
            </h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                The Philippine electrical grid has a capacity of approximately 27.0 GW and is
                heavily dependent on fossil fuels, which make up around 70.5% of the country&apos;s
                energy production, with coal alone accounting for 43.1%, while only 29.5% comes
                from renewables <Cite>Gonocruz et al., 2024</Cite>. In developing countries such as
                the Philippines, financial limitations, governance challenges, and societal resistance
                have been identified as persistent barriers to renewable energy adoption
                <Cite>Zhindon-Almeida & Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>. Despite growing
                awareness, renewable energy remains poorly understood and is often perceived as an
                expensive investment <Cite>Wong et al., 2023</Cite>.
              </p>
              <p>
                Furthermore, fragmented climate and energy-related data are often presented in
                complex formats, hindering public understanding and utilization
                <Cite>Lenain, 2026</Cite>. Public perception and education significantly shape
                adoption intentions, and increasing climate awareness can shift sentiment in favor
                of renewables <Cite>Esiri et al., 2024; Aguilera et al., 2024</Cite>. LUMI was
                developed to close this gap by transforming overwhelming technical datasets into
                clear, visual, and actionable insights with cost-inclusive transparency.
              </p>
              <p>
                Unlike generic information websites, LUMI is an interactive decision-support platform
                grounded in research on multi-criteria decision analysis and intelligent decision
                support systems <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>, allowing
                users to simulate scenarios, compare energy sources, and understand regional climate
                patterns in the context of real energy demand.
              </p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">70.5%</div>
              <div className="text-sm font-medium text-foreground mt-1">Fossil Fuel Share</div>
              <div className="text-xs text-muted-foreground mt-1">
                Of the Philippines&apos; energy production comes from fossil fuels, with coal at 43.1%
                <Cite>Gonocruz et al., 2024</Cite>
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">29.5%</div>
              <div className="text-sm font-medium text-foreground mt-1">Renewable Share</div>
              <div className="text-xs text-muted-foreground mt-1">
                Only about 29.5% of the country&apos;s energy is generated from renewable sources
                <Cite>Gonocruz et al., 2024</Cite>
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6 sm:col-span-2">
              <div className="text-3xl font-bold text-primary">3 Barriers</div>
              <div className="text-sm font-medium text-foreground mt-1">To Adoption</div>
              <div className="text-xs text-muted-foreground mt-1">
                Financial limitations, governance challenges, and societal resistance hinder renewable
                transition in developing countries <Cite>Zhindon-Almeida & Ruiz-Carrillo, 2025</Cite>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MISSION & VISION */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge="Guiding Principles"
            title="Mission & Vision"
            subtitle="LUMI is guided by a commitment to environmental literacy and democratized access to energy intelligence."
          />

          <div className="grid gap-6 md:grid-cols-2">
            <ValueCard
              icon={Globe}
              title="Mission"
              description="To democratize environmental intelligence by transforming complex climate and energy data into accessible, actionable insights that empower every Filipino to understand, evaluate, and transition toward renewable energy solutions with confidence and transparency."
            />
            <ValueCard
              icon={Lightbulb}
              title="Vision"
              description="A future where data-driven sustainability is within reach of every community. We envision a Philippines where students, households, and policymakers alike make informed energy decisions rooted in clear analytics, reducing fossil fuel dependence and accelerating national climate resilience."
            />
          </div>
        </div>
      </section>

      {/* RESEARCH BACKGROUND */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge="Research Foundation"
          title="The Need for Environmental Intelligence"
          subtitle="LUMI is built on a recognized research gap: the absence of user-friendly, data-driven tools for renewable energy evaluation in the Philippines."
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <BookOpen className="h-6 w-6" />
              </div>
              <CardTitle>Educational Resource</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                Research shows that education significantly affects people&apos;s perception of energy
                sources and their willingness to transition <Cite>Aguilera et al., 2024</Cite>. LUMI
                serves as a living case study that makes abstract climate concepts tangible through
                interactive visualizations, directly supporting classroom and community learning.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <Microscope className="h-6 w-6" />
              </div>
              <CardTitle>Decision Support</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                Studies confirm that multi-criteria decision analysis improves social impact and
                policy comprehension in renewable energy planning <Cite>Estévez et al., 2021; Witt & Klumpp, 2021</Cite>.
                Government agencies can use LUMI to identify high-potential zones and craft strategies
                backed by structured evaluation rather than assumptions.
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <FlaskConical className="h-6 w-6" />
              </div>
              <CardTitle>Research Groundwork</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                Environmental intelligence, defined as the use of machine learning and AI to
                simulate predicted environment models <Cite>Bassetti, 2024</Cite>, is a growing field.
                LUMI demonstrates the practical application of rule-based AI and predictive analytics
                in tackling real-world environmental challenges, creating a foundation for future systems.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-card to-muted/30 p-6 sm:p-8">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            Research Problem Statement
          </h3>
          <p className="text-muted-foreground leading-relaxed">
            Despite growing public awareness of renewable energy, it remains poorly understood and
            perceived as costly <Cite>Wong et al., 2023</Cite>. With approximately 70.5% of the
            Philippines&apos; energy production coming from fossil fuels <Cite>Gonocruz et al., 2024</Cite>,
            the lack of a system that educates the public and allows them to evaluate renewable
            energy options results in continued dependence on unsustainable sources. In developing
            countries, barriers such as financial limitations, governance challenges, and societal
            resistance significantly affect adoption intentions <Cite>Zhindon-Almeida & Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>.
            LUMI directly addresses this gap by providing an intuitive platform for data-driven
            evaluation and informed decision-making grounded in multi-criteria and predictive methods
            <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>.
          </p>
        </div>
      </section>

      {/* SYSTEM OVERVIEW */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge="System Architecture"
            title="How LUMI Is Structured"
            subtitle="LUMI integrates four interconnected modules that guide users from raw environmental data to confident renewable energy decisions."
          />

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                <BarChart3 className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">EnergyHub</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                Interactive dashboard for climate patterns, energy consumption, and demand trends.
                Dashboards that use graphical visualizations improve comprehension of complex data
                <Cite>"Dashboard," 2026; What Is Data Visualization?, n.d.</Cite>, while meteorological
                data is a critical input for predicting renewable energy output <Cite>Das et al., 2022; Bandara et al., 2026</Cite>.
              </p>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                <Zap className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">Ecosim</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                Rule-based recommendation and what-if simulation engine comparing solar, wind, and
                hydro with real costing and savings estimates. Studies confirm that technical criteria
                hold the most weight (53.6%) in renewable energy decision-making, followed by environmental
                impact (29.0%) <Cite>Shatnawi et al., 2021</Cite>.
              </p>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                <BrainCircuit className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">AI Analysis</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                AI-powered natural language explanations for charts, forecasts, and recommendations.
                Explainable artificial intelligence ensures insights are tailored to user needs and
                unambiguous <Cite>Panagoulias et al., 2023</Cite>, while AI can effectively optimize
                renewable energy by predicting supply and demand <Cite>Algburi et al., 2025</Cite>.
              </p>
            </div>
            <div className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                <Database className="h-7 w-7" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">Data Visualization</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                Unified visual analytics including KPIs, trend charts, comparative graphs, and
                regional overview panels. Data visualization is defined as the representation of data
                using graphics to make patterns accessible <Cite>What Is Data Visualization?, n.d.</Cite>,
                and classical forecasting models are sufficient when seasonal patterns are predictable
                <Cite>Mustafa & Al-Yozbaky, 2025</Cite>.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* TECHNOLOGY STACK */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge="Built With Modern Tools"
          title="Technology Stack"
          subtitle="LUMI uses a modern, scalable architecture designed for performance, accessibility, and seamless integration of AI and environmental data services."
        />

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <TechItem
            icon={Monitor}
            title="Frontend"
            items={["React 18 + Vite", "Tailwind CSS", "shadcn/ui Components", "React Router", "Lucide Icons"]}
          />
          <TechItem
            icon={Server}
            title="Backend"
            items={["FastAPI (Python)", "RESTful API Design", "Pydantic Validation", "Async Data Processing"]}
          />
          <TechItem
            icon={Database}
            title="Database"
            items={["Supabase PostgreSQL", "Row Level Security", "Real-time Sync", "Secure Auth"]}
          />
          <TechItem
            icon={BrainCircuit}
            title="AI & ML"
            items={["Gemini API (Google)", "Rule-Based Engine", "Predictive Analytics", "Trend Forecasting"]}
          />
        </div>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-primary/5 to-accent/5 p-6 sm:p-8 text-center">
          <h3 className="text-xl font-semibold text-foreground">
            Designed for Real-World Impact
          </h3>
          <p className="mx-auto mt-3 max-w-2xl text-muted-foreground leading-relaxed">
            Every technology choice in LUMI serves the goal of making environmental intelligence
            fast, accessible, and understandable. From responsive mobile layouts to AI-generated
            explanations, the architecture supports users across all backgrounds and devices.
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            {["Responsive Design", "Dark Mode Support", "Accessibility First", "Performance Optimized"].map(
              (tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center rounded-full bg-card border border-border/60 px-3 py-1 text-xs font-medium text-muted-foreground"
                >
                  {tag}
                </span>
              )
            )}
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
              Ready to Explore LUMI?
            </h2>
            <p className="mx-auto max-w-xl text-lg text-muted-foreground leading-relaxed">
              Dive into regional climate data, run renewable energy simulations, and discover
              actionable insights tailored to the Philippines.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/dashboard">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  Go to Dashboard
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  Launch Ecosim
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

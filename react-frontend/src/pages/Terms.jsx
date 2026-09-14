import { useI18n } from "@/i18n";

export default function Terms() {
  const { t } = useI18n();

  return (
    <section className="page-container stack prose max-w-4xl">
      <h1>Terms & Conditions</h1>
      <p className="text-muted-foreground">Effective date: {new Date().toLocaleDateString()}</p>

      <h2>1. Nature of the Service</h2>
      <p>
        LUMI provides renewable energy feasibility estimates for Philippine municipalities. The
        results are generated from public data, geospatial models, and AI-assisted analysis and
        are intended for educational and preliminary planning purposes only.
      </p>

      <h2>2. Not Professional Advice</h2>
      <p>
        The output of LUMI is not a substitute for professional engineering, financial, legal, or
        regulatory advice. Always consult a qualified renewable energy provider, licensed engineer,
        or relevant government authority before making investment or installation decisions.
      </p>

      <h2>3. Data Accuracy</h2>
      <p>
        We strive to use reliable public and open data sources, but we cannot guarantee the
        accuracy, completeness, or currency of any dataset. Conditions on the ground (e.g., shading,
        local grid rules, equipment performance, and site-specific factors) are not captured by
        LUMI.
      </p>

      <h2>4. User Conduct</h2>
      <p>
        You agree not to abuse the service, attempt to access data you are not authorized to view,
        or use LUMI outputs to mislead third parties.
      </p>

      <h2>5. Limitation of Liability</h2>
      <p>
        LUMI and its operators are not liable for any losses, damages, or decisions made based on
        information obtained through the platform.
      </p>

      <h2>6. Changes to These Terms</h2>
      <p>
        These terms may be updated as the platform evolves. Continued use of the service after an
        update constitutes acceptance of the new terms.
      </p>
    </section>
  );
}

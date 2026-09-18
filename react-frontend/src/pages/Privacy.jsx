import { useI18n } from "@/i18n";

export default function Privacy() {
  const { t } = useI18n();

  return (
    <section className="page-container stack max-w-4xl">
      <h1>Privacy Policy</h1>
      <p className="text-muted-foreground">Effective date: {new Date().toLocaleDateString()}</p>

      <h2>1. Information We Collect</h2>
      <p>
        LUMI collects the minimum information needed to provide the service: your email address
        (for authentication), saved simulation inputs and results, and anonymous usage analytics.
      </p>

      <h2>2. How We Use Your Data</h2>
      <p>
        We use your data to authenticate you, save simulations you choose to store, enforce usage
        limits, and improve the platform. We do not sell your personal information.
      </p>

      <h2>3. Data Storage</h2>
      <p>
        Account and simulation data are stored in Supabase (PostgreSQL) with Row Level Security
        enabled. You can only access and modify your own data through the authenticated API.
      </p>

      <h2>4. Cookies and Analytics</h2>
      <p>
        LUMI uses essential cookies for authentication and may use anonymous analytics to understand
        usage patterns. No third-party advertising cookies are used.
      </p>

      <h2>5. Your Rights</h2>
      <p>
        You can update your profile, delete saved simulations, and request account deletion by
        contacting support.
      </p>

      <h2>6. Contact</h2>
      <p>
        For privacy questions, email{" "}
        <a href="mailto:alexanderjonsolis0401@gmail.com" className="text-primary hover:underline">
          alexanderjonsolis0401@gmail.com
        </a>
        .
      </p>
    </section>
  );
}

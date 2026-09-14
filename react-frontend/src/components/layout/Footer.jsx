import { Link } from "react-router-dom";
import { Sun } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t bg-background/95 py-8">
      <div className="page-container grid gap-6 md:grid-cols-3">
        <div className="space-y-2">
          <div className="flex items-center gap-2 font-semibold">
            <Sun className="h-5 w-5 text-primary" />
            <span>LUMI</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Renewable energy feasibility intelligence for Philippine municipalities.
          </p>
        </div>

        <nav className="flex flex-col gap-2 text-sm">
          <Link to="/" className="hover:text-primary">Home</Link>
          <Link to="/about" className="hover:text-primary">About</Link>
          <Link to="/energyhub" className="hover:text-primary">Energy Hub</Link>
          <Link to="/ecosim" className="hover:text-primary">EcoSim</Link>
        </nav>

        <nav className="flex flex-col gap-2 text-sm">
          <Link to="/terms" className="hover:text-primary">Terms & Conditions</Link>
          <Link to="/privacy" className="hover:text-primary">Privacy Policy</Link>
          <a
            href="mailto:alexanderjonsolis0401@gmail.com"
            className="hover:text-primary"
          >
            Contact
          </a>
        </nav>
      </div>

      <div className="page-container mt-8 text-center text-xs text-muted-foreground">
        &copy; {new Date().getFullYear()} LUMI. All rights reserved. Estimates only — consult a
        renewable energy provider for precise calculations.
      </div>
    </footer>
  );
}

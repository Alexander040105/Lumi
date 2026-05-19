import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>Page not found</h1>
        <p>The page you requested does not exist.</p>
      </div>
      <Link to="/" className="text-sm text-primary">
        Go home
      </Link>
    </section>
  );
}

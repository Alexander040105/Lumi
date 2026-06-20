import { Link } from "react-router-dom";

export default function AdminDashboard() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Admin Portal</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link
          to="/admin/users"
          className="p-6 border rounded-lg hover:bg-muted transition-colors"
        >
          <h2 className="text-lg font-semibold">User Management</h2>
          <p className="text-sm text-muted-foreground mt-2">
            View and manage registered users.
          </p>
        </Link>
        <Link
          to="/admin/analytics"
          className="p-6 border rounded-lg hover:bg-muted transition-colors"
        >
          <h2 className="text-lg font-semibold">Analytics</h2>
          <p className="text-sm text-muted-foreground mt-2">
            View system usage metrics and trends.
          </p>
        </Link>
        <Link
          to="/admin/config"
          className="p-6 border rounded-lg hover:bg-muted transition-colors"
        >
          <h2 className="text-lg font-semibold">System Config</h2>
          <p className="text-sm text-muted-foreground mt-2">
            Toggle features and adjust system settings.
          </p>
        </Link>
        <Link
          to="/admin/moderate"
          className="p-6 border rounded-lg hover:bg-muted transition-colors"
        >
          <h2 className="text-lg font-semibold">Content Moderation</h2>
          <p className="text-sm text-muted-foreground mt-2">
            Review chat sessions and flag inappropriate content.
          </p>
        </Link>
      </div>
    </div>
  );
}

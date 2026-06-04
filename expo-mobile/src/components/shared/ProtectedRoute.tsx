import { useAuth } from '@/hooks/useAuth';
import LoadingSkeleton from './LoadingSkeleton';

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { session, loading } = useAuth();

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (!session) {
    return null;
  }

  return children;
}

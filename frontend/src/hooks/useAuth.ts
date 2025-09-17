import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export function useAuth() {
  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => apiClient.getCurrentUser(),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const isAuthenticated = !!user && !error;
  const isAdmin = user?.role === 'admin';
  const isResearcher = user?.role === 'researcher' || isAdmin;

  return {
    user,
    isLoading,
    isAuthenticated,
    isAdmin,
    isResearcher,
    error,
    refetch,
  };
}
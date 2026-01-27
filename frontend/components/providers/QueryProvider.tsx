/**
 * Query Provider Component
 * Wraps the app with React Query QueryClientProvider
 */

'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes - data doesn't change that frequently
            gcTime: 10 * 60 * 1000, // 10 minutes - keep in cache (formerly cacheTime in v4)
            refetchOnWindowFocus: false, // Don't refetch on window focus
            refetchOnMount: false, // Use cached data if available
            retry: 1, // Only retry once on failure
            retryDelay: 1000, // Wait 1 second before retry
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}


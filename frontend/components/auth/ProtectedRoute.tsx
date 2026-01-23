/**
 * Protected Route Component
 * Wraps pages that require authentication
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getAuthToken } from '@/lib/api/client';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  // TODO: Re-enable auth check once login page is set up
  // For now, bypass auth to allow development
  return <>{children}</>;
  
  /* Original auth code - uncomment when login is ready
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Check if user has token
    const token = getAuthToken();
    
    if (!token && !isLoading) {
      // No token, redirect to login
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Check if user has token
  const token = getAuthToken();
  
  // If no token, don't show loading - let redirect happen
  if (!token) {
    return null;
  }

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rocket-red mx-auto mb-4"></div>
          <p className="text-foreground-secondary">Loading...</p>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
  */
}


/**
 * Protected Route Component
 * Wraps pages that require authentication
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getAuthToken } from '@/lib/api/client';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Give a small delay to check auth state properly
    const checkAuth = async () => {
      // Small delay to ensure auth state is initialized
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const token = getAuthToken();
      
      if (!token && !isLoading) {
        // No token, redirect to landing page (where they can click Sign In to open modal)
        router.push('/landing');
        setIsChecking(false);
      } else if (token) {
        // Has token, allow access (even if still loading user data)
        setIsChecking(false);
      } else if (isLoading) {
        // Still loading, keep checking
        // This will resolve when isLoading becomes false
      }
    };
    
    checkAuth();
  }, [isAuthenticated, isLoading, router]);

  // Check if user has token
  const token = getAuthToken();
  
  // Show loading state while checking auth
  if (isLoading || isChecking || (!token && isLoading)) {
    return (
      <div 
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#000000'
        }}
      >
        <div className="text-center relative z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }
  
  // If no token after checking, don't render (redirect is happening)
  if (!token) {
    return null;
  }

  // User is authenticated, render children
  return <>{children}</>;
}


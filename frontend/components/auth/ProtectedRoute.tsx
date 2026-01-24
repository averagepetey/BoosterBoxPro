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

  // Admin users (john.petersen1818@gmail.com) have full access
  if (isAdmin) {
    return <>{children}</>;
  }

  // If subscription is required and user is not admin, show paywall message
  // TODO: Check actual subscription status when Stripe integration is complete
  if (requireSubscription && !isAdmin) {
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
        <div className="text-center relative z-10 max-w-md mx-auto p-8 bg-black/50 backdrop-blur-md rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-4">Subscription Required</h2>
          <p className="text-white/70 mb-6">
            This feature requires an active subscription. Please upgrade your account to access the full dashboard.
          </p>
          <button
            onClick={() => router.push('/landing')}
            className="px-6 py-3 bg-gradient-to-b from-yellow-400 to-yellow-500 text-black font-semibold rounded-full hover:opacity-90 transition-opacity"
          >
            View Plans
          </button>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}


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

  // Admin users (john.petersen1818@gmail.com) have full access
  if (isAdmin) {
    return <>{children}</>;
  }

  // If subscription is required and user is not admin, show paywall message
  // TODO: Check actual subscription status when Stripe integration is complete
  if (requireSubscription && !isAdmin) {
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
        <div className="text-center relative z-10 max-w-md mx-auto p-8 bg-black/50 backdrop-blur-md rounded-2xl border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-4">Subscription Required</h2>
          <p className="text-white/70 mb-6">
            This feature requires an active subscription. Please upgrade your account to access the full dashboard.
          </p>
          <button
            onClick={() => router.push('/landing')}
            className="px-6 py-3 bg-gradient-to-b from-yellow-400 to-yellow-500 text-black font-semibold rounded-full hover:opacity-90 transition-opacity"
          >
            View Plans
          </button>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}


/**
 * Protected Route Component
 * Wraps pages that require authentication
 * Admin users (john.petersen1818@gmail.com) have full access without paywall
 * Other users require subscription
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getAuthToken } from '../../lib/api/client';
import { useAuthModals } from './AuthModalsProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSubscription?: boolean; // If true, non-admin users need subscription
}

export function ProtectedRoute({ children, requireSubscription = false }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading, isAdmin, user } = useAuth();
  const { openSignup } = useAuthModals();
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

  // Admin users (john.petersen1818@gmail.com) have full access
  if (isAdmin) {
    return <>{children}</>;
  }

  // If subscription is required and user is not admin, check subscription status
  // Wait for user data to load before checking subscription
  if (requireSubscription && !isAdmin) {
    // If user data is still loading, show loading state
    if (isLoading || !user) {
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
    
    // Check if user has active access
    const hasActiveAccess = (
      user.subscription_status === 'active' ||
      user.subscription_status === 'trial' ||
      user.subscription_status === 'trialing' ||
      user.subscription_status === 'pioneer'
    );
    
    if (!hasActiveAccess) {
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
              onClick={openSignup}
              className="px-6 py-3 bg-gradient-to-b from-yellow-400 to-yellow-500 text-black font-semibold rounded-full hover:opacity-90 transition-opacity"
            >
              View Plans
            </button>
          </div>
        </div>
      );
    }
  }

  // User is authenticated, render children
  return <>{children}</>;
}

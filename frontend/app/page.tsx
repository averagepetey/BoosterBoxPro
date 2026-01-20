/**
 * Root Page
 * Redirects based on authentication status
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getAuthToken } from '@/lib/api/client';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    const token = getAuthToken();
    
    if (token) {
      // User is authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // User is not authenticated, redirect to landing page
      router.push('/landing');
    }
  }, [isAuthenticated, router]);

  // Show loading state while redirecting
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

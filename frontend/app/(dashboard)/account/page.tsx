/**
 * Account Page
 * User account management page
 */

'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { useAuth } from '@/hooks/useAuth';

export default function AccountPage() {
  const { user } = useAuth();

  return (
    <ProtectedRoute>
      <div className="min-h-screen marketplace-bg">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold text-white mb-6">Account</h1>
            
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold text-white mb-4">User Information</h2>
              {user && (
                <div className="space-y-2">
                  <div>
                    <span className="text-white/70">Email: </span>
                    <span className="text-white">{user.email}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}


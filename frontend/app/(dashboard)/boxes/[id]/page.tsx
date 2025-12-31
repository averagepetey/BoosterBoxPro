/**
 * Box Detail Page
 * Individual booster box details page
 */

'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { use } from 'react';
import Link from 'next/link';

export default function BoxDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return (
    <ProtectedRoute>
      <div className="min-h-screen marketplace-bg">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <Link 
              href="/dashboard"
              className="inline-flex items-center text-white/70 hover:text-white mb-6 transition-colors"
            >
              ← Back to Leaderboard
            </Link>
            
            <div className="glass-card p-8">
              <h1 className="text-3xl font-bold text-white mb-4">Box Details</h1>
              <div className="text-white/70 mb-6">
                <p>Box ID: {id}</p>
              </div>
              
              <div className="text-white/50">
                <p>Detailed box information coming soon...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}


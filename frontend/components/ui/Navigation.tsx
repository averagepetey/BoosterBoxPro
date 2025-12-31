/**
 * Navigation Component
 * Main navigation bar with logo and menu items
 */

'use client';

import { Logo } from './Logo';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export function Navigation() {
  const { user, logout } = useAuth();

  return (
    <nav className="glass-nav">
      <div className="container mx-auto">
        <div className="flex items-center justify-between h-16 px-4">
          {/* Logo - Always stays left */}
          <div className="flex-shrink-0 -ml-4">
            <Logo size="lg" href="/dashboard" />
          </div>
          
          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-white/85 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/account"
              className="text-white/85 hover:text-white transition-colors"
            >
              Account
            </Link>
            {user && (
              <span className="text-white/70 text-sm">
                {user.email}
              </span>
            )}
            <button
              onClick={logout}
              className="text-white/85 hover:text-white transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}


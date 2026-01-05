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
    <nav 
      className="glass-nav"
      style={{
        background: 'rgba(0, 0, 0, 0)',
        backdropFilter: 'blur(10px) saturate(120%)',
        WebkitBackdropFilter: 'blur(10px) saturate(120%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.03)'
      }}
    >
      <div className="w-full max-w-full">
        <div className="flex items-center justify-between h-16" style={{ paddingLeft: '1rem', paddingRight: '1rem' }}>
          {/* Logo - Always stays left */}
          <div className="flex-shrink-0">
            <Logo size="lg" href="/dashboard" />
          </div>
          
          {/* Navigation Links - Hug right corner with consistent padding */}
          <div className="flex items-center gap-6 flex-shrink-0">
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


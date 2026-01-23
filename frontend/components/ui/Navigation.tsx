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
    <nav className="bg-surface border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Logo size="md" href="/dashboard" />
          
          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-foreground-secondary hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/account"
              className="text-foreground-secondary hover:text-foreground transition-colors"
            >
              Account
            </Link>
            {user && (
              <span className="text-foreground-muted text-sm">
                {user.email}
              </span>
            )}
            <button
              onClick={logout}
              className="text-foreground-secondary hover:text-foreground transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}


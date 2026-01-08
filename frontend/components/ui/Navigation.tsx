/**
 * Navigation Component
 * Main navigation bar with logo and menu items
 * Mobile-optimized with hamburger menu
 */

'use client';

import { Logo } from './Logo';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useState } from 'react';

export function Navigation() {
  const { user, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav 
      className="glass-nav relative"
      style={{
        background: 'rgba(0, 0, 0, 0)',
        backdropFilter: 'blur(10px) saturate(120%)',
        WebkitBackdropFilter: 'blur(10px) saturate(120%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.03)'
      }}
    >
      <div className="w-full max-w-full">
        <div className="flex items-center justify-between min-h-[44px] sm:min-h-[64px] px-4 sm:px-6">
          {/* Logo - Responsive size: md on mobile, lg on desktop */}
          <div className="flex-shrink-0 py-2">
            <div className="block sm:hidden">
              <Logo size="md" href="/dashboard" />
            </div>
            <div className="hidden sm:block">
              <Logo size="lg" href="/dashboard" />
            </div>
          </div>
          
          {/* Desktop Navigation Links */}
          <div className="hidden sm:flex items-center gap-6 flex-shrink-0">
            <Link
              href="/dashboard"
              className="text-white/85 hover:text-white transition-colors min-h-[44px] flex items-center"
            >
              Dashboard
            </Link>
            <Link
              href="/account"
              className="text-white/85 hover:text-white transition-colors min-h-[44px] flex items-center"
            >
              Account
            </Link>
            {user && (
              <span className="text-white/70 text-sm min-h-[44px] flex items-center">
                {user.email}
              </span>
            )}
            <button
              onClick={logout}
              className="text-white/85 hover:text-white transition-colors min-h-[44px] flex items-center"
            >
              Logout
            </button>
          </div>

          {/* Mobile Hamburger Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="sm:hidden flex items-center justify-center min-h-[44px] min-w-[44px] text-white/85 hover:text-white transition-colors"
            aria-label="Toggle menu"
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {isMobileMenuOpen && (
          <div className="sm:hidden border-t border-white/10 bg-black/50 backdrop-blur-md">
            <div className="flex flex-col py-2">
              <Link
                href="/dashboard"
                onClick={closeMobileMenu}
                className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center"
              >
                Dashboard
              </Link>
              <Link
                href="/account"
                onClick={closeMobileMenu}
                className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center"
              >
                Account
              </Link>
              {user && (
                <div className="text-white/70 text-sm px-4 py-3 min-h-[44px] flex items-center border-b border-white/10">
                  {user.email}
                </div>
              )}
              <button
                onClick={() => {
                  closeMobileMenu();
                  logout();
                }}
                className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-left"
              >
                Logout
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}


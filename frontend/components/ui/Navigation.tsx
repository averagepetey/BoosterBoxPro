/**
 * Navigation Component
 * Main navigation bar with logo and menu items
 * Mobile-optimized with hamburger menu
 */

'use client';

import { Logo } from './Logo';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useState, useEffect, useRef } from 'react';
import { LoginModal } from '@/components/auth/LoginModal';
import { SignupModal } from '@/components/auth/SignupModal';
import { WelcomeHelpModal, getWelcomeSeen, setWelcomeSeen } from './WelcomeHelpModal';

interface NavigationProps {
  sticky?: boolean;
}

export function Navigation({ sticky = true }: NavigationProps) {
  const { user, logout, isAuthenticated, isAdmin } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const hasCheckedWelcome = useRef(false);
  const wasFirstTimeWelcome = useRef(false);

  useEffect(() => {
    if (!isAuthenticated || hasCheckedWelcome.current) return;
    hasCheckedWelcome.current = true;
    if (!getWelcomeSeen()) {
      wasFirstTimeWelcome.current = true;
      setIsHelpModalOpen(true);
    }
  }, [isAuthenticated]);

  const closeHelpModal = () => {
    if (wasFirstTimeWelcome.current) setWelcomeSeen();
    wasFirstTimeWelcome.current = false;
    setIsHelpModalOpen(false);
  };

  const openHelpModal = () => {
    wasFirstTimeWelcome.current = false;
    setIsHelpModalOpen(true);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <nav 
      className={`glass-nav relative ${sticky ? 'sticky top-0 z-50' : ''}`}
      style={{
        background: 'rgba(0, 0, 0, 0)',
        backdropFilter: 'blur(10px) saturate(120%)',
        WebkitBackdropFilter: 'blur(10px) saturate(120%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.03)'
      }}
    >
      <div className="w-full max-w-full">
        <div className="flex items-center justify-between h-[84px] sm:h-[60px] px-4 sm:px-6">
          {/* Logo - Responsive size: md on mobile, lg on desktop */}
          <div className="flex-shrink-0 py-1">
            <div className="block sm:hidden">
              <Logo size="md" href="/dashboard" />
            </div>
            <div className="hidden sm:block">
              <Logo size="lg" href="/dashboard" />
            </div>
          </div>
          
          {/* Desktop Navigation Links */}
          <div className="hidden sm:flex items-center gap-6 flex-shrink-0 h-full">
            {isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={openHelpModal}
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                  aria-label="Help / How to use"
                >
                  Help
                </button>
                {/* Admin-only: Screenshot Tool */}
                {isAdmin && (
                  <Link
                    href="/admin/screenshots"
                    className="text-yellow-400/85 hover:text-yellow-400 transition-colors flex items-center h-full"
                  >
                    📷 Admin Tools
                  </Link>
                )}
                <Link
                  href="/account"
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                >
                  Account
                </Link>
                {user && (
                  <span className="text-white/70 text-sm flex items-center h-full">
                    {user.email}
                    {isAdmin && <span className="ml-1 text-yellow-400 text-xs">(Admin)</span>}
                  </span>
                )}
                <button
                  onClick={logout}
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsLoginModalOpen(true)}
                  className="px-5 py-2 rounded-lg border border-white/40 text-white hover:bg-white/10 hover:border-white/70 font-medium transition-all flex items-center"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsSignupModalOpen(true)}
                  className="px-5 py-2 rounded-lg bg-yellow-400 text-black font-semibold hover:bg-yellow-300 transition-all"
                >
                  Sign Up
                </button>
              </>
            )}
          </div>

          {/* Mobile Hamburger Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="sm:hidden flex items-center justify-center min-h-[44px] min-w-[44px] text-white/85 hover:text-white transition-colors h-full"
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
              {isAuthenticated ? (
                <>
                  <Link
                    href="/dashboard"
                    onClick={closeMobileMenu}
                    className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center"
                  >
                    Dashboard
                  </Link>
                  <button
                    type="button"
                    onClick={() => { closeMobileMenu(); openHelpModal(); }}
                    className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-left w-full"
                  >
                    Help
                  </button>
                  {/* Admin-only: Screenshot Tool (Mobile) */}
                  {isAdmin && (
                    <Link
                      href="/admin/screenshots"
                      onClick={closeMobileMenu}
                      className="text-yellow-400/85 hover:text-yellow-400 transition-colors px-4 py-3 min-h-[44px] flex items-center"
                    >
                      📷 Admin Tools
                    </Link>
                  )}
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
                      {isAdmin && <span className="ml-1 text-yellow-400 text-xs">(Admin)</span>}
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
                </>
              ) : (
                <>
                  <button
                    onClick={() => {
                      setIsLoginModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-lg border border-white/40 text-white hover:bg-white/10 hover:border-white/70 font-medium transition-all min-h-[44px] flex items-center justify-center mx-4"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      setIsSignupModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-lg bg-yellow-400 text-black font-semibold hover:bg-yellow-300 transition-all text-center min-h-[44px] flex items-center justify-center mx-4 mt-2"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Login Modal */}
      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => setIsLoginModalOpen(false)}
        onSwitchToSignup={() => {
          setIsLoginModalOpen(false);
          setIsSignupModalOpen(true);
        }}
      />
      
      {/* Signup Modal */}
      <SignupModal 
        isOpen={isSignupModalOpen} 
        onClose={() => setIsSignupModalOpen(false)}
        onSwitchToLogin={() => {
          setIsSignupModalOpen(false);
          setIsLoginModalOpen(true);
        }}
      />

      {/* Welcome / Help Modal */}
      <WelcomeHelpModal
        isOpen={isHelpModalOpen}
        onClose={closeHelpModal}
      />
    </nav>
  );
}

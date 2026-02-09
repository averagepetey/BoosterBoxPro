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
import { ForgotPasswordModal } from '@/components/auth/ForgotPasswordModal';
import { WelcomeHelpModal, getWelcomeSeen, setWelcomeSeen } from './WelcomeHelpModal';

interface NavigationProps {
  sticky?: boolean;
}

export function Navigation({ sticky = true }: NavigationProps) {
  const { user, logout, isAuthenticated, isAdmin } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [isForgotPasswordModalOpen, setIsForgotPasswordModalOpen] = useState(false);
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
        borderBottom: 'none',
        backgroundImage: 'linear-gradient(to right, transparent, rgba(239, 68, 68, 0.12), transparent)',
        backgroundSize: '100% 1px',
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'bottom',
      }}
    >
      <div className="w-full max-w-full">
        <div className="flex items-center justify-between h-16 px-4 sm:px-6">
          {/* Logo + Brand Name */}
          <div className="flex-shrink-0 flex items-center gap-2.5">
            <Logo size="md" href="/dashboard" />
            <span className="hidden sm:inline text-lg font-bold" style={{ background: 'linear-gradient(180deg, #ef4444, #dc2626)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>BoosterBoxPro</span>
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
                <a href="#chrome-extension" className="text-sm text-white/50 hover:text-white transition-colors">Features</a>
                <a href="#pricing" className="text-sm text-white/50 hover:text-white transition-colors">Pricing</a>
                <div className="w-px h-5 bg-white/10" />
                <button
                  onClick={() => setIsLoginModalOpen(true)}
                  className="px-4 py-1.5 rounded-lg border border-white/20 text-sm text-white/80 hover:text-white hover:bg-white/5 hover:border-white/40 font-medium transition-all"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsSignupModalOpen(true)}
                  className="px-4 py-1.5 rounded-lg bg-yellow-400 text-sm text-black font-semibold hover:bg-yellow-300 hover:shadow-[0_0_16px_rgba(250,204,21,0.35)] transition-all"
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
                  <a href="#chrome-extension" onClick={closeMobileMenu} className="text-white/60 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-sm">Features</a>
                  <a href="#pricing" onClick={closeMobileMenu} className="text-white/60 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-sm">Pricing</a>
                  <div className="border-t border-white/10 mx-4 my-1" />
                  <button
                    onClick={() => {
                      setIsLoginModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-lg border border-white/20 text-white/80 hover:text-white hover:bg-white/5 hover:border-white/40 font-medium transition-all min-h-[44px] flex items-center justify-center mx-4 text-sm"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      setIsSignupModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-lg bg-yellow-400 text-black font-semibold hover:bg-yellow-300 hover:shadow-[0_0_16px_rgba(250,204,21,0.35)] transition-all text-center min-h-[44px] flex items-center justify-center mx-4 mt-2 text-sm"
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
        onForgotPassword={() => {
          setIsLoginModalOpen(false);
          setIsForgotPasswordModalOpen(true);
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

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={isForgotPasswordModalOpen}
        onClose={() => setIsForgotPasswordModalOpen(false)}
        onSwitchToLogin={() => {
          setIsForgotPasswordModalOpen(false);
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

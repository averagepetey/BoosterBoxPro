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
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsSignupModalOpen(true)}
                  className="px-4 py-2 rounded-full bg-green-500 hover:bg-green-600 text-white font-semibold transition-colors"
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
                    className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-left"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      setIsSignupModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-full bg-green-500 hover:bg-green-600 text-white font-semibold transition-colors text-center min-h-[44px] flex items-center justify-center mx-4 mt-2"
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
    </nav>
  );
}


          
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
                  className="text-white/85 hover:text-white transition-colors flex items-center h-full"
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsSignupModalOpen(true)}
                  className="px-4 py-2 rounded-full bg-green-500 hover:bg-green-600 text-white font-semibold transition-colors"
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
                    className="text-white/85 hover:text-white transition-colors px-4 py-3 min-h-[44px] flex items-center text-left"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      setIsSignupModalOpen(true);
                      closeMobileMenu();
                    }}
                    className="px-4 py-3 rounded-full bg-green-500 hover:bg-green-600 text-white font-semibold transition-colors text-center min-h-[44px] flex items-center justify-center mx-4 mt-2"
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
    </nav>
  );
}


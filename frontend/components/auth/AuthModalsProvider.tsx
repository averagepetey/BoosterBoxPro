/**
 * Auth Modals Provider
 * Provides a context for managing login and signup modals across the app
 */

'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { LoginModal } from './LoginModal';
import { SignupModal } from './SignupModal';

interface AuthModalsContextType {
  openLogin: () => void;
  openSignup: () => void;
  closeAll: () => void;
}

const AuthModalsContext = createContext<AuthModalsContextType | undefined>(undefined);

export function AuthModalsProvider({ children }: { children: ReactNode }) {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);

  const openLogin = () => {
    setIsSignupModalOpen(false);
    setIsLoginModalOpen(true);
  };

  const openSignup = () => {
    setIsLoginModalOpen(false);
    setIsSignupModalOpen(true);
  };

  const closeAll = () => {
    setIsLoginModalOpen(false);
    setIsSignupModalOpen(false);
  };

  return (
    <AuthModalsContext.Provider value={{ openLogin, openSignup, closeAll }}>
      {children}
      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => setIsLoginModalOpen(false)}
        onSwitchToSignup={openSignup}
      />
      <SignupModal 
        isOpen={isSignupModalOpen} 
        onClose={() => setIsSignupModalOpen(false)}
        onSwitchToLogin={openLogin}
      />
    </AuthModalsContext.Provider>
  );
}

export function useAuthModals() {
  const context = useContext(AuthModalsContext);
  if (context === undefined) {
    throw new Error('useAuthModals must be used within an AuthModalsProvider');
  }
  return context;
}


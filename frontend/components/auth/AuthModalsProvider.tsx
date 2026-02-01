/**
 * Auth Modals Provider
 * Provides a context for managing login and signup modals across the app
 */

'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { LoginModal } from './LoginModal';
import { SignupModal } from './SignupModal';
import { ForgotPasswordModal } from './ForgotPasswordModal';

interface AuthModalsContextType {
  openLogin: () => void;
  openSignup: () => void;
  openForgotPassword: () => void;
  closeAll: () => void;
}

const AuthModalsContext = createContext<AuthModalsContextType | undefined>(undefined);

export function AuthModalsProvider({ children }: { children: ReactNode }) {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false);
  const [isForgotPasswordModalOpen, setIsForgotPasswordModalOpen] = useState(false);

  const openLogin = () => {
    setIsSignupModalOpen(false);
    setIsForgotPasswordModalOpen(false);
    setIsLoginModalOpen(true);
  };

  const openSignup = () => {
    setIsLoginModalOpen(false);
    setIsForgotPasswordModalOpen(false);
    setIsSignupModalOpen(true);
  };

  const openForgotPassword = () => {
    setIsLoginModalOpen(false);
    setIsSignupModalOpen(false);
    setIsForgotPasswordModalOpen(true);
  };

  const closeAll = () => {
    setIsLoginModalOpen(false);
    setIsSignupModalOpen(false);
    setIsForgotPasswordModalOpen(false);
  };

  return (
    <AuthModalsContext.Provider value={{ openLogin, openSignup, openForgotPassword, closeAll }}>
      {children}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSwitchToSignup={openSignup}
        onForgotPassword={openForgotPassword}
      />
      <SignupModal
        isOpen={isSignupModalOpen}
        onClose={() => setIsSignupModalOpen(false)}
        onSwitchToLogin={openLogin}
      />
      <ForgotPasswordModal
        isOpen={isForgotPasswordModalOpen}
        onClose={() => setIsForgotPasswordModalOpen(false)}
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

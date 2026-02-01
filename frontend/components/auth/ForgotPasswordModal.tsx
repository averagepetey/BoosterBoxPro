'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import Image from 'next/image';
import { useAuth } from '@/hooks/useAuth';

interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin?: () => void;
}

export function ForgotPasswordModal({ isOpen, onClose, onSwitchToLogin }: ForgotPasswordModalProps) {
  const { forgotPassword, isForgotPasswordPending } = useAuth();
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); return () => setMounted(false); }, []);

  useEffect(() => {
    if (!isOpen) { setEmail(''); setSent(false); setError(''); }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) { document.body.style.overflow = 'hidden'; }
    else { document.body.style.overflow = 'unset'; }
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email) { setError('Email is required'); return; }
    try {
      await forgotPassword({ email });
      setSent(true);
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    }
  };

  if (!isOpen || !mounted) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', WebkitBackdropFilter: 'blur(4px)' }}
      onClick={onClose}
    >
      <div
        className="relative bg-[#0a0a0a] border border-white/10 rounded-2xl w-full max-w-md p-6 sm:p-8 shadow-2xl"
        style={{ boxShadow: '0 20px 60px rgba(0,0,0,0.8)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <button onClick={onClose} className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors p-2" aria-label="Close">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="text-center mb-6">
          <Image src="/images/BoosterProTextLogo.png" alt="BoosterBoxPro" width={200} height={60} className="h-12 sm:h-16 w-auto mx-auto mb-4" />
        </div>

        <h2 className="text-2xl font-extrabold text-white mb-2 text-center">Reset Password</h2>
        <p className="text-sm text-white/70 text-center mb-6">
          {sent ? 'Check your email for a reset link.' : 'Enter your email and we\'ll send you a reset link.'}
        </p>

        {sent ? (
          <div className="space-y-4">
            <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 text-center">
              <p className="text-green-400 text-sm">If an account with that email exists, a password reset link has been sent.</p>
            </div>
            <button
              type="button"
              onClick={() => { onClose(); onSwitchToLogin?.(); }}
              className="w-full py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold transition-all text-base min-h-[44px]"
            >
              Back to Sign In
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
            <div>
              <label htmlFor="forgot-email" className="block text-sm font-medium text-white mb-2">Email</label>
              <input
                id="forgot-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white text-base placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all min-h-[44px]"
                placeholder="you@example.com"
              />
            </div>
            <button
              type="submit"
              disabled={isForgotPasswordPending}
              className="w-full py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-all text-base min-h-[44px]"
            >
              {isForgotPasswordPending ? 'Sending...' : 'Send Reset Link'}
            </button>
            <p className="text-center text-sm text-white/70">
              <button type="button" onClick={() => { onClose(); onSwitchToLogin?.(); }} className="text-green-400 hover:text-green-300 underline">
                Back to Sign In
              </button>
            </p>
          </form>
        )}
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}

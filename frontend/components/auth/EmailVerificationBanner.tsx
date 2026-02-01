'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export function EmailVerificationBanner() {
  const { user, resendVerification, isResendVerificationPending } = useAuth();
  const [dismissed, setDismissed] = useState(false);
  const [sent, setSent] = useState(false);

  if (!user || user.email_verified || dismissed) return null;

  const handleResend = async () => {
    try {
      await resendVerification();
      setSent(true);
    } catch {
      // ignore
    }
  };

  return (
    <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3 mb-6 flex items-center justify-between gap-3">
      <div className="flex-1">
        <p className="text-yellow-400 text-sm">
          {sent
            ? 'Verification email sent! Check your inbox.'
            : 'Please verify your email address. Check your inbox for a verification link.'}
        </p>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        {!sent && (
          <button
            onClick={handleResend}
            disabled={isResendVerificationPending}
            className="text-xs px-3 py-1.5 rounded bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 transition-colors disabled:opacity-50"
          >
            {isResendVerificationPending ? 'Sending...' : 'Resend Email'}
          </button>
        )}
        <button
          onClick={() => setDismissed(true)}
          className="text-white/40 hover:text-white/70 transition-colors p-1"
          aria-label="Dismiss"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

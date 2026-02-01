'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { verifyEmail } from '@/lib/api/auth';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setErrorMessage('No verification token provided.');
      return;
    }

    verifyEmail(token)
      .then(() => setStatus('success'))
      .catch((err) => {
        setStatus('error');
        setErrorMessage(err.message || 'Verification failed.');
      });
  }, [token]);

  if (status === 'loading') {
    return (
      <div className="text-center space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-green-400 border-t-transparent mx-auto" />
        <p className="text-white/70">Verifying your email...</p>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-white">Email Verified</h2>
        <p className="text-white/70 text-sm">Your email address has been verified successfully.</p>
        <a href="/dashboard" className="inline-block py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold transition-all">
          Go to Dashboard
        </a>
      </div>
    );
  }

  return (
    <div className="text-center space-y-4">
      <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto">
        <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h2 className="text-xl font-bold text-white">Verification Failed</h2>
      <p className="text-white/70 text-sm">{errorMessage}</p>
      <a href="/landing" className="inline-block py-3 px-6 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium transition-all">
        Go to Home
      </a>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Image src="/images/BoosterProTextLogo.png" alt="BoosterBoxPro" width={200} height={60} className="h-12 w-auto mx-auto" />
        </div>
        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-6 sm:p-8">
          <Suspense fallback={<div className="text-center text-white/50">Loading...</div>}>
            <VerifyEmailContent />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

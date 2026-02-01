'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { resetPassword } from '@/lib/api/auth';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await resetPassword({ token, new_password: newPassword, confirm_new_password: confirmPassword });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="text-center">
        <p className="text-red-400 mb-4">Invalid reset link. No token provided.</p>
        <a href="/landing" className="text-green-400 hover:text-green-300 underline">Go to Home</a>
      </div>
    );
  }

  if (success) {
    return (
      <div className="text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-white">Password Reset</h2>
        <p className="text-white/70 text-sm">Your password has been reset successfully.</p>
        <a href="/landing" className="inline-block py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold transition-all">
          Sign In
        </a>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-extrabold text-white text-center mb-2">Set New Password</h2>
      <p className="text-sm text-white/70 text-center mb-4">Enter your new password below.</p>

      {error && (
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <div>
        <label htmlFor="new-password" className="block text-sm font-medium text-white mb-2">New Password</label>
        <input
          id="new-password"
          type="password"
          required
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all min-h-[44px]"
          placeholder="Min 8 chars, 1 upper, 1 lower, 1 digit"
        />
      </div>

      <div>
        <label htmlFor="confirm-password" className="block text-sm font-medium text-white mb-2">Confirm Password</label>
        <input
          id="confirm-password"
          type="password"
          required
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all min-h-[44px]"
          placeholder="Re-enter your new password"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-all min-h-[44px]"
      >
        {loading ? 'Resetting...' : 'Reset Password'}
      </button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Image src="/images/BoosterProTextLogo.png" alt="BoosterBoxPro" width={200} height={60} className="h-12 w-auto mx-auto" />
        </div>
        <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-6 sm:p-8">
          <Suspense fallback={<div className="text-center text-white/50">Loading...</div>}>
            <ResetPasswordForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

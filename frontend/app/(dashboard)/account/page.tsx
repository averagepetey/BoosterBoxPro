/**
 * Account Page
 * User profile, plan status, security settings, and billing management
 */

'use client';

import { useState } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { useAuth } from '@/hooks/useAuth';
import { updateProfile, changePassword, createPortalSession, getSubscriptionInfo } from '@/lib/api/user';
import { useQueryClient, useQuery } from '@tanstack/react-query';

function formatDate(iso: string | undefined | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
}

function planLabel(status: string): string {
  switch (status) {
    case 'pioneer':
      return 'Pioneer';
    case 'active':
      return 'Pro+';
    case 'trial':
    case 'trialing':
      return 'Trial';
    case 'cancelled':
      return 'Cancelled';
    case 'expired':
      return 'Expired';
    default:
      return status;
  }
}

function planBadgeColor(status: string): string {
  switch (status) {
    case 'pioneer':
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'active':
      return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    case 'trial':
    case 'trialing':
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    default:
      return 'bg-white/10 text-white/60 border-white/20';
  }
}

export default function AccountPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Discord handle
  const [discord, setDiscord] = useState('');
  const [discordLoaded, setDiscordLoaded] = useState(false);
  const [discordSaving, setDiscordSaving] = useState(false);
  const [discordMsg, setDiscordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Change password
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [pwSaving, setPwSaving] = useState(false);
  const [pwMsg, setPwMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Billing portal
  const [portalLoading, setPortalLoading] = useState(false);

  // Subscription info (for Stripe customer check)
  const { data: subInfo } = useQuery({
    queryKey: ['subscriptionInfo'],
    queryFn: getSubscriptionInfo,
    enabled: !!user,
    retry: false,
  });

  // Initialize discord state from user data once
  if (user && !discordLoaded) {
    setDiscord(user.discord_handle || '');
    setDiscordLoaded(true);
  }

  const handleDiscordSave = async () => {
    setDiscordSaving(true);
    setDiscordMsg(null);
    try {
      await updateProfile({ discord_handle: discord });
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setDiscordMsg({ type: 'success', text: 'Discord handle saved.' });
    } catch (err: any) {
      setDiscordMsg({ type: 'error', text: err.message || 'Failed to save.' });
    } finally {
      setDiscordSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwMsg(null);

    if (pwForm.newPw !== pwForm.confirm) {
      setPwMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    if (pwForm.newPw.length < 8) {
      setPwMsg({ type: 'error', text: 'Password must be at least 8 characters.' });
      return;
    }

    setPwSaving(true);
    try {
      await changePassword({
        current_password: pwForm.current,
        new_password: pwForm.newPw,
        confirm_new_password: pwForm.confirm,
      });
      setPwForm({ current: '', newPw: '', confirm: '' });
      setPwMsg({ type: 'success', text: 'Password changed successfully.' });
    } catch (err: any) {
      setPwMsg({ type: 'error', text: err.message || 'Failed to change password.' });
    } finally {
      setPwSaving(false);
    }
  };

  const handleManageBilling = async () => {
    setPortalLoading(true);
    try {
      const url = await createPortalSession();
      window.location.href = url;
    } catch (err: any) {
      alert(err.message || 'Unable to open billing portal.');
      setPortalLoading(false);
    }
  };

  const subscriptionStatus = user?.subscription_status || 'inactive';
  const hasStripeCustomer = !!subInfo?.stripe_customer_id;

  return (
    <ProtectedRoute>
      <div className="min-h-screen marketplace-bg">
        <Navigation />
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto space-y-6">
            <h1 className="text-3xl font-bold text-white">Account</h1>

            {/* -------- Profile Section -------- */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
              <h2 className="text-lg font-semibold text-white mb-4">Profile</h2>
              {user && (
                <div className="space-y-4">
                  {/* Email (read-only) + verification status */}
                  <div>
                    <label className="block text-xs font-medium text-white/60 mb-1">Email</label>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm">
                        {user.email}
                      </div>
                      {user.email_verified ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-[10px] font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Verified
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-[10px] font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                          Unverified
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Auth provider */}
                  {user.auth_provider === 'google' && (
                    <div>
                      <label className="block text-xs font-medium text-white/60 mb-1">Sign-in Method</label>
                      <div className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white/70 text-sm flex items-center gap-2">
                        <svg className="w-4 h-4" viewBox="0 0 24 24">
                          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4" />
                          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                        </svg>
                        Signed in with Google
                      </div>
                    </div>
                  )}

                  {/* Discord handle */}
                  <div>
                    <label className="block text-xs font-medium text-white/60 mb-1">Discord Handle</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={discord}
                        onChange={(e) => {
                          setDiscord(e.target.value);
                          setDiscordMsg(null);
                        }}
                        placeholder="yourname"
                        maxLength={37}
                        className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/20 text-white text-sm placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                      />
                      <button
                        onClick={handleDiscordSave}
                        disabled={discordSaving}
                        className="px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white text-sm font-medium transition-colors"
                      >
                        {discordSaving ? 'Saving...' : 'Save'}
                      </button>
                    </div>
                    {discordMsg && (
                      <p className={`mt-1 text-xs ${discordMsg.type === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                        {discordMsg.text}
                      </p>
                    )}
                  </div>

                  {/* Member Since + Last Login */}
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    <div>
                      <label className="block text-xs font-medium text-white/60 mb-1">Member Since</label>
                      <p className="text-sm text-white">{formatDate(user.created_at)}</p>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-white/60 mb-1">Account ID</label>
                      <p className="text-sm text-white/50 truncate">{user.id}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* -------- Plan Section -------- */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
              <h2 className="text-lg font-semibold text-white mb-4">Plan</h2>
              <div className="flex items-center gap-3 mb-3">
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${planBadgeColor(subscriptionStatus)}`}
                >
                  {planLabel(subscriptionStatus)}
                </span>
                {subscriptionStatus === 'pioneer' && (
                  <span className="text-xs text-white/50">Early access member</span>
                )}
              </div>

              {subscriptionStatus === 'pioneer' && (
                <p className="text-sm text-white/60 leading-relaxed">
                  You have full access to all Pro+ features as a Pioneer member.
                  When paid plans launch, Pioneers will be notified with a special upgrade offer.
                </p>
              )}

              {(subscriptionStatus === 'active' || subscriptionStatus === 'trial') && (
                <p className="text-sm text-white/60 leading-relaxed">
                  You have an active Pro+ subscription with full access to all features.
                </p>
              )}

              {(subscriptionStatus === 'expired' || subscriptionStatus === 'cancelled') && (
                <p className="text-sm text-white/60 leading-relaxed">
                  Your subscription is no longer active. Renew to regain full access.
                </p>
              )}
            </div>

            {/* -------- Security Section -------- */}
            {user?.auth_provider !== 'google' && (
            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
              <h2 className="text-lg font-semibold text-white mb-4">Security</h2>
              <form onSubmit={handlePasswordChange} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-white/60 mb-1">Current Password</label>
                  <input
                    type="password"
                    value={pwForm.current}
                    onChange={(e) => { setPwForm((p) => ({ ...p, current: e.target.value })); setPwMsg(null); }}
                    required
                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/20 text-white text-sm placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    placeholder="Enter current password"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-white/60 mb-1">New Password</label>
                  <input
                    type="password"
                    value={pwForm.newPw}
                    onChange={(e) => { setPwForm((p) => ({ ...p, newPw: e.target.value })); setPwMsg(null); }}
                    required
                    minLength={8}
                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/20 text-white text-sm placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    placeholder="At least 8 characters"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-white/60 mb-1">Confirm New Password</label>
                  <input
                    type="password"
                    value={pwForm.confirm}
                    onChange={(e) => { setPwForm((p) => ({ ...p, confirm: e.target.value })); setPwMsg(null); }}
                    required
                    minLength={8}
                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/20 text-white text-sm placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
                    placeholder="Confirm new password"
                  />
                </div>
                <p className="text-[10px] text-white/40">
                  Must be 8+ characters with uppercase, lowercase, and a number.
                </p>
                <button
                  type="submit"
                  disabled={pwSaving}
                  className="px-5 py-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white text-sm font-medium border border-white/20 transition-colors"
                >
                  {pwSaving ? 'Changing...' : 'Change Password'}
                </button>
                {pwMsg && (
                  <p className={`text-xs ${pwMsg.type === 'success' ? 'text-green-400' : 'text-red-400'}`}>
                    {pwMsg.text}
                  </p>
                )}
              </form>
            </div>
            )}

            {/* -------- Billing Section (only for Stripe customers) -------- */}
            {hasStripeCustomer && (
              <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
                <h2 className="text-lg font-semibold text-white mb-4">Billing</h2>
                <p className="text-sm text-white/60 mb-4">
                  Manage your payment method, view invoices, and update billing details.
                </p>
                <button
                  onClick={handleManageBilling}
                  disabled={portalLoading}
                  className="px-5 py-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-50 text-white text-sm font-medium border border-white/20 transition-colors"
                >
                  {portalLoading ? 'Opening...' : 'Manage Billing'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

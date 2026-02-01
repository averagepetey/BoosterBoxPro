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
                  {/* Email (read-only) */}
                  <div>
                    <label className="block text-xs font-medium text-white/60 mb-1">Email</label>
                    <div className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm">
                      {user.email}
                    </div>
                  </div>

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

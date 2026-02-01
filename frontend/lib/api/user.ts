/**
 * User API
 * Functions for user profile, subscription, and billing management
 */

import { getApiBaseUrl, getAuthToken, setAuthToken } from '@/lib/api/client';

function authHeaders(): Record<string, string> {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// --- Profile ---

export interface UpdateProfileRequest {
  discord_handle?: string;
}

export interface ProfileResponse {
  id: string;
  email: string;
  discord_handle: string | null;
  subscription_status: string;
  created_at: string | null;
}

export async function updateProfile(data: UpdateProfileRequest): Promise<ProfileResponse> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/users/me/profile`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update profile' }));
    throw new Error(error.detail || 'Failed to update profile');
  }

  return response.json();
}

// --- Change Password ---

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  confirm_new_password: string;
}

export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/auth/change-password`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to change password' }));
    throw new Error(error.detail || 'Failed to change password');
  }

  // The endpoint returns a new access token — store it
  const result = await response.json();
  if (result.access_token) {
    setAuthToken(result.access_token);
  }
}

// --- Subscription ---

export interface SubscriptionInfo {
  has_access: boolean;
  subscription_status: string;
  trial_active: boolean;
  days_remaining_in_trial: number | null;
  stripe_customer_id: string | null;
  stripe_subscription_id: string | null;
}

export async function getSubscriptionInfo(): Promise<SubscriptionInfo> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/users/me/subscription`, {
    method: 'GET',
    headers: authHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get subscription info' }));
    throw new Error(error.detail || 'Failed to get subscription info');
  }

  return response.json();
}

// --- Billing Portal ---

export async function createPortalSession(): Promise<string> {
  const response = await fetch(`${getApiBaseUrl()}/api/v1/payment/create-portal-session`, {
    method: 'POST',
    headers: authHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create portal session' }));
    throw new Error(error.detail || 'Failed to create billing portal session');
  }

  const data = await response.json();
  return data.url;
}

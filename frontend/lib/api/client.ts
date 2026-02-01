/**
 * API Client Utilities
 * Helper functions for API communication
 */

const AUTH_TOKEN_KEY = 'auth_token';

export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function removeAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function getApiBaseUrl(): string {
  // Use environment variable if set
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Production default
  return 'https://boosterboxpro.onrender.com';
}


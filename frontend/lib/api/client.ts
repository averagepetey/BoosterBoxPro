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
  
  // In browser, use the same hostname as the frontend (works for mobile)
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If accessing via IP address (mobile), use that IP for API
    // If localhost, keep localhost
    return `http://${hostname}:8000`;
  }
  
  // Server-side fallback
  return 'http://localhost:8000';
}


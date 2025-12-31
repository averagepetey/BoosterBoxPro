/**
 * Landing Page (Simplified - to be built later)
 * Redirects to login if not authenticated, otherwise dashboard
 */

import { redirect } from 'next/navigation';

export default function Home() {
  // For now, redirect to login
  // TODO: Build out full landing page with hero, features, pricing
  redirect('/login');
  
  // Fallback (won't be reached due to redirect)
  return null;
}

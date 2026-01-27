import { redirect } from 'next/navigation';

/**
 * Root route: send visitors to the landing page.
 * /landing is the marketing page; /dashboard is the app (requires auth).
 */
export default function Home() {
  redirect('/landing');
}

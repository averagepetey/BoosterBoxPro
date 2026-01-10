import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to landing page for now
  // Later we can add logic to redirect authenticated users to dashboard
  redirect('/landing');
}

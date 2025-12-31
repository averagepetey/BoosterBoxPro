/**
 * Login Page
 */

import { Logo } from '@/components/ui/Logo';
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Logo size="lg" showText />
        </div>

        {/* Login Card */}
        <div className="bg-surface border border-border rounded-lg p-8 shadow-lg">
          <h1 className="text-2xl font-bold text-foreground mb-2">Welcome Back</h1>
          <p className="text-foreground-secondary mb-6">
            Sign in to access your dashboard
          </p>

          <LoginForm />
        </div>
      </div>
    </main>
  );
}


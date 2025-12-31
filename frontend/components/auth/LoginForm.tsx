/**
 * Login Form Component
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { useState } from 'react';
import Link from 'next/link';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { login, isLoggingIn, loginError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormData) => {
    login(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-foreground-secondary mb-2">
          Email
        </label>
        <input
          id="email"
          type="email"
          {...register('email')}
          className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-rocket-red focus:border-transparent"
          placeholder="you@example.com"
          autoComplete="email"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-error">{errors.email.message}</p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-foreground-secondary mb-2">
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            {...register('password')}
            className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-rocket-red focus:border-transparent pr-12"
            placeholder="Enter your password"
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-foreground-muted hover:text-foreground transition-colors"
          >
            {showPassword ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-sm text-error">{errors.password.message}</p>
        )}
      </div>

      {/* Remember Me */}
      <div className="flex items-center">
        <input
          id="remember"
          type="checkbox"
          className="w-4 h-4 rounded border-border bg-surface text-rocket-red focus:ring-rocket-red"
        />
        <label htmlFor="remember" className="ml-2 text-sm text-foreground-secondary">
          Remember me
        </label>
      </div>

      {/* Error Message */}
      {loginError && (
        <div className="p-3 bg-error/10 border border-error/20 rounded-lg">
          <p className="text-sm text-error">
            {loginError instanceof Error
              ? loginError.message
              : 'Invalid email or password'}
          </p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoggingIn}
        className="w-full py-3 bg-rocket-red text-white rounded-lg font-semibold hover:bg-rocket-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoggingIn ? 'Logging in...' : 'Login'}
      </button>

      {/* Register Link */}
      <p className="text-center text-sm text-foreground-secondary">
        Don't have an account?{' '}
        <Link href="/register" className="text-rocket-red hover:text-rocket-red-dark font-medium">
          Sign up
        </Link>
      </p>
    </form>
  );
}


/**
 * Register Form Component
 */

'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/useAuth';
import { useState } from 'react';
import Link from 'next/link';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  username: z.string().optional(),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const { register: registerUser, isRegistering, registerError } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterFormData) => {
    registerUser(data);
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

      {/* Username Field (Optional) */}
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-foreground-secondary mb-2">
          Username (Optional)
        </label>
        <input
          id="username"
          type="text"
          {...register('username')}
          className="w-full px-4 py-3 bg-surface border border-border rounded-lg text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-rocket-red focus:border-transparent"
          placeholder="Choose a username"
          autoComplete="username"
        />
        {errors.username && (
          <p className="mt-1 text-sm text-error">{errors.username.message}</p>
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
            placeholder="At least 8 characters"
            autoComplete="new-password"
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
        <p className="mt-1 text-xs text-foreground-muted">
          Must be at least 8 characters long
        </p>
      </div>

      {/* Terms Checkbox */}
      <div className="flex items-start">
        <input
          id="terms"
          type="checkbox"
          required
          className="mt-1 w-4 h-4 rounded border-border bg-surface text-rocket-red focus:ring-rocket-red"
        />
        <label htmlFor="terms" className="ml-2 text-sm text-foreground-secondary">
          I agree to the Terms of Service and Privacy Policy
        </label>
      </div>

      {/* Error Message */}
      {registerError && (
        <div className="p-3 bg-error/10 border border-error/20 rounded-lg">
          <p className="text-sm text-error">
            {registerError instanceof Error
              ? registerError.message
              : 'Registration failed. Please try again.'}
          </p>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isRegistering}
        className="w-full py-3 bg-rocket-red text-white rounded-lg font-semibold hover:bg-rocket-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isRegistering ? 'Creating account...' : 'Create Account'}
      </button>

      {/* Login Link */}
      <p className="text-center text-sm text-foreground-secondary">
        Already have an account?{' '}
        <Link href="/login" className="text-rocket-red hover:text-rocket-red-dark font-medium">
          Sign in
        </Link>
      </p>
    </form>
  );
}


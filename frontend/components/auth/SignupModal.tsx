/**
 * Signup Modal Component
 * Popup modal for user registration — Pioneer program (free access)
 * Flow: Sign up → auto-login → Dashboard
 */

'use client';

import React, { useState, useEffect } from 'react';
import { getApiBaseUrl } from '../../lib/api/client';
import Image from 'next/image';
import { createPortal } from 'react-dom';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin?: () => void;
}

export function SignupModal({ isOpen, onClose, onSwitchToLogin }: SignupModalProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
    general?: string;
  }>({});

  const [isRegistering, setIsRegistering] = useState(false);

  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({ email: '', password: '', confirmPassword: '' });
      setErrors({});
      setIsRegistering(false);
    }
  }, [isOpen]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsRegistering(true);

    try {
      const apiBaseUrl = getApiBaseUrl();
      const fullUrl = `${apiBaseUrl}/api/v1/auth/register`;

      // Test connectivity first
      try {
        const healthCheck = await fetch(`${apiBaseUrl}/health`);
        if (!healthCheck.ok) throw new Error('Health check failed');
      } catch (healthError: any) {
        throw new Error(`Cannot reach backend server at ${apiBaseUrl}. The server may not be running or there is a network issue. Error: ${healthError.message}`);
      }

      // Register the user
      let registerResponse;
      try {
        registerResponse = await fetch(fullUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
            confirm_password: formData.confirmPassword,
          }),
        });
      } catch (fetchError: any) {
        if (fetchError.message.includes('Failed to fetch') || fetchError.message.includes('NetworkError')) {
          throw new Error(`Cannot connect to backend server at ${apiBaseUrl}. Please ensure the backend is running and CORS is configured correctly.`);
        }
        throw new Error(`Network error: ${fetchError.message}`);
      }

      if (!registerResponse.ok) {
        let errorDetail = 'Registration failed';
        try {
          const errorData = await registerResponse.json();
          errorDetail = errorData.detail || errorData.message || 'Registration failed';
        } catch {
          errorDetail = registerResponse.statusText || `HTTP ${registerResponse.status}`;
        }

        if (registerResponse.status === 404) {
          throw new Error(`Backend server not found. Please ensure the backend is running on ${apiBaseUrl}`);
        } else if (registerResponse.status === 500) {
          throw new Error(`Server error: ${errorDetail}. This usually means a database connection issue.`);
        }

        throw new Error(errorDetail);
      }

      // Auto-login after registration
      const loginResponse = await fetch(`${apiBaseUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      if (!loginResponse.ok) {
        throw new Error('Registration successful, but login failed. Please try logging in manually.');
      }

      const authData = await loginResponse.json();

      if (authData.access_token) {
        localStorage.setItem('auth_token', authData.access_token);
      }

      // Redirect straight to dashboard — no Stripe checkout
      onClose();
      window.location.href = '/dashboard';
    } catch (error: any) {
      console.error('Signup error:', error);
      setErrors({
        general: error.message || 'An error occurred. Please try again.',
      });
      setIsRegistering(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!isOpen || !mounted) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center p-4"
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)',
        WebkitBackdropFilter: 'blur(4px)',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
      }}
      onClick={onClose}
    >
      {/* Modal Container */}
      <div
        className="relative bg-[#0a0a0a] border border-white/10 rounded-2xl w-full max-w-md p-4 sm:p-5 shadow-2xl max-h-[95vh] overflow-y-auto"
        style={{
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/70 hover:text-white transition-colors p-1.5 z-10"
          aria-label="Close"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Logo */}
        <div className="text-center mb-1">
          <Image
            src="/images/BoosterProTextLogo.png"
            alt="BoosterBoxPro"
            width={480}
            height={144}
            className="h-28 sm:h-32 w-auto mx-auto"
          />
        </div>

        {/* Title */}
        <h2 className="text-xl sm:text-2xl font-extrabold text-white mb-0.5 text-center">
          Join the Pioneer Program
        </h2>
        <p className="text-xs text-white/70 text-center mb-2">
          Get full access for free as an early member.
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-2.5">
          {/* General Error */}
          {errors.general && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-2">
              <p className="text-xs text-red-400">{errors.general}</p>
            </div>
          )}

          {/* Email */}
          <div>
            <label htmlFor="signup-email" className="block text-xs font-medium text-white mb-1">
              Email
            </label>
            <input
              id="signup-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-3 py-2 rounded-lg bg-white/5 border backdrop-blur-sm text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all min-h-[40px] ${
                errors.email ? 'border-red-500' : 'border-white/20 focus:border-green-500'
              }`}
              placeholder="you@example.com"
            />
            {errors.email && (
              <p className="mt-0.5 text-xs text-red-400">{errors.email}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <label htmlFor="signup-password" className="block text-xs font-medium text-white mb-1">
              Password
            </label>
            <input
              id="signup-password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-3 py-2 rounded-lg bg-white/5 border backdrop-blur-sm text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all min-h-[40px] ${
                errors.password ? 'border-red-500' : 'border-white/20 focus:border-green-500'
              }`}
              placeholder="At least 8 characters"
            />
            {errors.password && (
              <p className="mt-0.5 text-xs text-red-400">{errors.password}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="signup-confirm-password" className="block text-xs font-medium text-white mb-1">
              Confirm Password
            </label>
            <input
              id="signup-confirm-password"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className={`w-full px-3 py-2 rounded-lg bg-white/5 border backdrop-blur-sm text-white text-sm placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all min-h-[40px] ${
                errors.confirmPassword ? 'border-red-500' : 'border-white/20 focus:border-green-500'
              }`}
              placeholder="Confirm your password"
            />
            {errors.confirmPassword && (
              <p className="mt-0.5 text-xs text-red-400">{errors.confirmPassword}</p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isRegistering}
            className="w-full py-2.5 px-4 rounded-lg bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-all text-sm min-h-[40px] shadow-lg mt-1"
          >
            {isRegistering ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Creating Account...
              </span>
            ) : (
              <span>Create Free Account</span>
            )}
          </button>

          {/* Terms */}
          <p className="text-[10px] text-white/60 text-center leading-tight mt-1.5">
            By signing up, you agree to our Terms of Service and Privacy Policy.
          </p>

          {/* Login Link */}
          <p className="text-center text-xs text-white/70 mt-2.5">
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => {
                onClose();
                if (onSwitchToLogin) {
                  onSwitchToLogin();
                }
              }}
              className="text-green-400 hover:text-green-300 underline font-medium"
            >
              Sign in
            </button>
          </p>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}

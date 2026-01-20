/**
 * Login Modal Component
 * Popup modal for user authentication
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Image from 'next/image';
import { createPortal } from 'react-dom';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToSignup?: () => void;
}

export function LoginModal({ isOpen, onClose, onSwitchToSignup }: LoginModalProps) {
  const router = useRouter();
  const { login, isLoggingIn, loginError, isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    general?: string;
  }>({});
  
  // Close modal on successful login
  useEffect(() => {
    if (isAuthenticated && isOpen) {
      onClose();
      router.push('/dashboard');
    }
  }, [isAuthenticated, isOpen, onClose, router]);
  
  // Reset form when modal closes
  useEffect(() => {
    if (!isOpen) {
      setFormData({ email: '', password: '' });
      setErrors({});
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
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      // Use the login function from useAuth hook
      // It will handle token storage and redirect
      login({
        email: formData.email,
        password: formData.password,
      });
    } catch (error: any) {
      console.error('Login error:', error);
      setErrors({
        general: error.message || 'An error occurred. Please try again.',
      });
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
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
        className="relative bg-[#0a0a0a] border border-white/10 rounded-2xl w-full max-w-md p-6 sm:p-8 shadow-2xl max-h-[90vh] overflow-y-auto"
        style={{
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors p-2"
          aria-label="Close"
        >
          <svg
            className="w-6 h-6"
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
        <div className="text-center mb-6">
          <Image
            src="/images/BoosterProTextLogo.png"
            alt="BoosterBoxPro"
            width={200}
            height={60}
            className="h-12 sm:h-16 w-auto mx-auto mb-4"
          />
        </div>
        
        {/* Title */}
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-2 text-center">
          Sign In
        </h2>
        <p className="text-sm text-white/70 text-center mb-6">
          Sign in to access your dashboard
        </p>
        
        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* General Error */}
          {errors.general && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
              <p className="text-sm text-red-400">{errors.general}</p>
            </div>
          )}
          
          {/* Login Error */}
          {loginError && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
              <p className="text-sm text-red-400">
                {loginError instanceof Error ? loginError.message : 'Login failed. Please try again.'}
              </p>
            </div>
          )}
          
          {/* Email */}
          <div>
            <label htmlFor="login-email" className="block text-sm font-medium text-white mb-2">
              Email
            </label>
            <input
              id="login-email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className={`w-full px-4 py-3 rounded-lg bg-white/5 border backdrop-blur-sm text-white text-base placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all min-h-[44px] ${
                errors.email ? 'border-red-500' : 'border-white/20 focus:border-green-500'
              }`}
              placeholder="you@example.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-400">{errors.email}</p>
            )}
          </div>
          
          {/* Password */}
          <div>
            <label htmlFor="login-password" className="block text-sm font-medium text-white mb-2">
              Password
            </label>
            <input
              id="login-password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleChange}
              className={`w-full px-4 py-3 rounded-lg bg-white/5 border backdrop-blur-sm text-white text-base placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all min-h-[44px] ${
                errors.password ? 'border-red-500' : 'border-white/20 focus:border-green-500'
              }`}
              placeholder="Enter your password"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-400">{errors.password}</p>
            )}
          </div>
          
          {/* Forgot Password Link */}
          <div className="text-right">
            <button
              type="button"
              className="text-sm text-green-400 hover:text-green-300 underline"
              onClick={() => {
                onClose();
                // TODO: Navigate to forgot password page
              }}
            >
              Forgot password?
            </button>
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoggingIn}
            className="w-full py-3 px-6 rounded-lg bg-green-500 hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold transition-all text-base min-h-[44px] shadow-lg"
          >
            {isLoggingIn ? (
              <span className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                Signing in...
              </span>
            ) : (
              <span>Sign In</span>
            )}
          </button>
          
          {/* Sign Up Link */}
          <p className="text-center text-sm text-white/70 mt-4">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={() => {
                onClose();
                if (onSwitchToSignup) {
                  onSwitchToSignup();
                } else {
                  router.push('/signup');
                }
              }}
              className="text-green-400 hover:text-green-300 underline font-medium"
            >
              Sign up
            </button>
          </p>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}


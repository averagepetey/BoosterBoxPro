/**
 * Authentication Hook
 * Manages authentication state and provides auth methods
 */

'use client';

import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import {
  login, register, getCurrentUser, logout,
  forgotPassword, resetPassword, googleAuth, resendVerification,
  LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest, GoogleAuthRequest, UserResponse,
} from '../lib/api/auth';
import { getAuthToken, setAuthToken } from '../lib/api/client';

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const posthog = usePostHog();

  // Check if user is authenticated (has token)
  const isAuthenticated = typeof window !== 'undefined' && !!getAuthToken();

  // Get current user
  const {
    data: user,
    isLoading: isLoadingUser,
    error: userError,
  } = useQuery<UserResponse>({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
    // Don't throw errors for unauthenticated users (expected state)
    throwOnError: (error: any) => {
      // Only throw if it's not an authentication-related error
      return !error?.isUnauthenticated;
    },
  });

  // Identify returning users (already have a stored auth token)
  useEffect(() => {
    if (user && posthog) {
      posthog.identify(user.id, {
        email: user.email,
        subscription_status: user.subscription_status,
      });
    }
  }, [user, posthog]);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => login(data),
    onSuccess: (data) => {
      posthog?.capture('user_logged_in', { auth_provider: 'email' });
      // Invalidate and refetch user data (PostHog identify happens via useEffect when currentUser loads)
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      // Get redirect URL from query params or default to dashboard
      if (typeof window !== 'undefined') {
        const searchParams = new URLSearchParams(window.location.search);
        const redirectUrl = searchParams.get('redirect') || '/dashboard';
        // Redirect to dashboard or requested URL
        router.push(redirectUrl);
        router.refresh(); // Refresh to update auth state
      } else {
        router.push('/dashboard');
      }
    },
    onError: (error: any) => {
      console.error('Login error:', error);
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => register(data),
    onSuccess: () => {
      posthog?.capture('user_signed_up', { auth_provider: 'email' });
      // After registration, redirect to login (user must login)
      router.push('/login?registered=true');
    },
    onError: (error: any) => {
      console.error('Registration error:', error);
    },
  });

  // Forgot password mutation
  const forgotPasswordMutation = useMutation({
    mutationFn: (data: ForgotPasswordRequest) => forgotPassword(data),
  });

  // Reset password mutation
  const resetPasswordMutation = useMutation({
    mutationFn: (data: ResetPasswordRequest) => resetPassword(data),
  });

  // Google auth mutation
  const googleAuthMutation = useMutation({
    mutationFn: (data: GoogleAuthRequest) => googleAuth(data),
    onSuccess: () => {
      posthog?.capture('user_logged_in', { auth_provider: 'google' });
      // PostHog identify happens via useEffect when currentUser loads
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      router.push('/dashboard');
      router.refresh();
    },
  });

  // Resend verification mutation
  const resendVerificationMutation = useMutation({
    mutationFn: () => resendVerification(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  // Logout function
  const handleLogout = () => {
    posthog?.reset();
    logout();
    queryClient.clear();
    router.push('/landing');
  };

  // Check if user is admin
  const isAdmin = user?.is_admin ?? false;

  return {
    user,
    isAuthenticated,
    isAdmin,
    isLoading: isLoadingUser,
    error: userError,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout: handleLogout,
    forgotPassword: forgotPasswordMutation.mutateAsync,
    isForgotPasswordPending: forgotPasswordMutation.isPending,
    resetPassword: resetPasswordMutation.mutateAsync,
    isResetPasswordPending: resetPasswordMutation.isPending,
    googleLogin: googleAuthMutation.mutate,
    googleLoginAsync: googleAuthMutation.mutateAsync,
    isGoogleLoginPending: googleAuthMutation.isPending,
    googleLoginError: googleAuthMutation.error,
    resendVerification: resendVerificationMutation.mutateAsync,
    isResendVerificationPending: resendVerificationMutation.isPending,
  };
}

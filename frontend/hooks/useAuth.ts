/**
 * Authentication Hook
 * Manages authentication state and provides auth methods
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { login, register, getCurrentUser, logout, LoginRequest, RegisterRequest, UserResponse } from '@/lib/api/auth';
import { getAuthToken } from '@/lib/api/client';

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();

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
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => login(data),
    onSuccess: (data) => {
      // Invalidate and refetch user data
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
      // After registration, redirect to login (user must login)
      router.push('/login?registered=true');
    },
    onError: (error: any) => {
      console.error('Registration error:', error);
    },
  });

  // Logout function
  const handleLogout = () => {
    logout();
    queryClient.clear();
    router.push('/landing');
  };

  return {
    user,
    isAuthenticated,
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
  };
}


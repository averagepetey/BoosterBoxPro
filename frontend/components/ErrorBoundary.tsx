/**
 * Error Boundary Component
 * Catches React errors and displays a fallback UI
 */

'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)' }}>
          <div className="max-w-md w-full mx-4">
            <div 
              className="rounded-2xl p-8 text-center"
              style={{
                background: '#141414',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
              }}
            >
              <div className="text-6xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-white mb-2">Something went wrong</h1>
              <p className="text-white/70 text-sm mb-6">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <div className="flex gap-4 justify-center">
                <button
                  onClick={() => window.location.reload()}
                  className="px-6 py-2 rounded-lg font-semibold text-white bg-green-500 hover:bg-green-600 transition-colors"
                >
                  Reload Page
                </button>
                <button
                  onClick={() => this.setState({ hasError: false, error: null })}
                  className="px-6 py-2 rounded-lg font-semibold text-white/70 hover:text-white border border-white/30 hover:border-white/50 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}


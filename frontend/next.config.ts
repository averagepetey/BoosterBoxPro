import type { NextConfig } from "next";

/**
 * Security Headers Configuration
 * 
 * CRITICAL: Content-Security-Policy is the primary defense against XSS
 * when using localStorage for tokens.
 * 
 * Production CSP is STRICTER than development:
 * - Dev: unsafe-inline + unsafe-eval (for HMR, source maps)
 * - Prod: No unsafe-eval, stricter connect-src
 */

const isProd = process.env.NODE_ENV === 'production';

// API URL for connect-src (production should be your real domain)
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://boosterboxpro.onrender.com';

/**
 * CSP Directives
 * 
 * SECURITY NOTE on unsafe-inline:
 * - Style unsafe-inline is needed for Tailwind's dynamic styles
 * - Script unsafe-inline is kept for Next.js compatibility but should be
 *   replaced with nonce-based approach for maximum security (see TODO below)
 * 
 * TODO for maximum security:
 * 1. Implement nonce-based CSP for scripts
 * 2. Use next/script with strict CSP
 * 3. See: https://nextjs.org/docs/app/building-your-application/configuring/content-security-policy
 */
const cspDirectives = [
  "default-src 'self'",
  
  // Scripts: Production removes unsafe-eval (dev needs it for HMR)
  // unsafe-inline is kept but should eventually use nonces
  isProd 
    ? "script-src 'self' 'unsafe-inline'"  // No unsafe-eval in prod!
    : "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
  
  // Styles: unsafe-inline required for Tailwind
  "style-src 'self' 'unsafe-inline'",
  
  // Images: self + data URIs + external sources
  "img-src 'self' data: blob: https:",
  
  // Fonts: self + data URIs
  "font-src 'self' data:",
  
  // API connections: Strict in production
  isProd
    ? `connect-src 'self' ${apiUrl}`  // Only your API in prod
    : "connect-src 'self' http://localhost:8000 https://*.supabase.co wss://*.supabase.co",
  
  // Frames: deny all (clickjacking protection)
  "frame-ancestors 'none'",
  
  // Form submissions
  "form-action 'self'",
  
  // Base URI
  "base-uri 'self'",
  
  // Block mixed content
  "block-all-mixed-content",
  
  // Upgrade insecure requests in production
  isProd ? "upgrade-insecure-requests" : "",
].filter(Boolean).join('; ');

const securityHeaders = [
  {
    // Content Security Policy - PRIMARY XSS DEFENSE
    key: 'Content-Security-Policy',
    value: cspDirectives
  },
  {
    // Prevent clickjacking (backup for frame-ancestors)
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    // Prevent MIME type sniffing
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    // Referrer policy
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    // Permissions policy (formerly Feature-Policy)
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), payment=()'
  },
];

// Add HSTS in production only
if (process.env.NODE_ENV === 'production') {
  securityHeaders.push({
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains'
  });
}

const nextConfig: NextConfig = {
  // Root (/) → /landing so the app always shows the real landing page
  async redirects() {
    return [
      { source: '/', destination: '/landing', permanent: false },
    ];
  },

  // Security headers for all routes
  async headers() {
    return [
      {
        // Apply to all routes
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },

  // Keep serverless function under Vercel 250 MB limit (exclude dev + non-Linux deps)
  // Patterns resolved from project root (frontend/). See https://vercel.com/kb/guide/troubleshooting-function-250mb-limit
  outputFileTracingExcludes: {
    '*': [
      // macOS/Windows native binaries — Vercel runs Linux. ~98M from swc-darwin-arm64 alone.
      'node_modules/@next/swc-darwin-arm64/**',
      'node_modules/@next/swc-darwin-x64/**',
      'node_modules/@next/swc-win32-x64-msvc/**',
      'node_modules/@next/swc-win32-ia32-msvc/**',
      'node_modules/lightningcss-darwin-arm64/**',
      'node_modules/lightningcss-darwin-x64/**',
      'node_modules/lightningcss-win32-x64-msvc/**',
      // Dev / build-time only
      'node_modules/typescript/**',
      'node_modules/@types/**',
      'node_modules/eslint/**',
      'node_modules/@typescript-eslint/**',
      'node_modules/eslint-plugin-next/**',
      'node_modules/axe-core/**',
      'node_modules/caniuse-lite/**',
      'node_modules/es-abstract/**',
      'node_modules/@napi-rs/**',
      'node_modules/@babel/**',
      // Build cache / static — served by CDN
      '.next/cache/**',
      'public/**',
    ],
  },

  // Don’t bundle these into the function; load from runtime. Helps keep size down.
  // Disable x-powered-by header
  poweredByHeader: false,
};

export default nextConfig;

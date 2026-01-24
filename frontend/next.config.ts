import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;

 * Production CSP is STRICTER than development:
 * - Dev: unsafe-inline + unsafe-eval (for HMR, source maps)
 * - Prod: No unsafe-eval, stricter connect-src
 */

const isProd = process.env.NODE_ENV === 'production';

// API URL for connect-src (production should be your real domain)
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  
  // Disable x-powered-by header
  poweredByHeader: false,
};

export default nextConfig;

 * Production CSP is STRICTER than development:
 * - Dev: unsafe-inline + unsafe-eval (for HMR, source maps)
 * - Prod: No unsafe-eval, stricter connect-src
 */

const isProd = process.env.NODE_ENV === 'production';

// API URL for connect-src (production should be your real domain)
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  
  // Disable x-powered-by header
  poweredByHeader: false,
};

export default nextConfig;

import type { NextConfig } from "next";

/**
 * Security Headers Configuration
 * 
 * IMPORTANT: Content-Security-Policy is the primary defense against XSS
 * when using localStorage for tokens.
 */
const securityHeaders = [
  {
    // Content Security Policy - PRIMARY XSS DEFENSE
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      // Scripts: self + inline for Next.js hydration
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  // Next.js requires unsafe-eval in dev
      // Styles: self + inline for Tailwind
      "style-src 'self' 'unsafe-inline'",
      // Images: self + data URIs + external image hosts
      "img-src 'self' data: blob: https:",
      // Fonts: self + Google Fonts if used
      "font-src 'self' data:",
      // API connections: self + your API domain
      "connect-src 'self' http://localhost:8000 https://*.supabase.co wss://*.supabase.co",
      // Frames: deny all (clickjacking protection)
      "frame-ancestors 'none'",
      // Form submissions
      "form-action 'self'",
      // Base URI
      "base-uri 'self'",
      // Upgrade insecure requests in production
      process.env.NODE_ENV === 'production' ? "upgrade-insecure-requests" : "",
    ].filter(Boolean).join('; ')
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

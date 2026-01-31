'use client';

import Link from 'next/link';
import { Logo } from './Logo';

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-12 py-12 sm:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 md:gap-8">
          {/* Brand */}
          <div className="md:col-span-1">
            <Logo size="sm" showText />
            <p className="mt-3 text-sm text-white/40 leading-relaxed">
              Market intelligence for sealed TCG booster box collectors and investors.
            </p>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white/60 mb-4">
              Product
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/dashboard" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/landing#pricing" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/landing#faq" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  FAQ
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white/60 mb-4">
              Legal
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/terms" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-white/60 mb-4">
              Support
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/landing#faq" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Help &amp; FAQ
                </Link>
              </li>
              <li>
                <a href="mailto:support@boosterboxpro.com" className="text-sm text-white/40 hover:text-white/80 transition-colors">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/30">
            &copy; {new Date().getFullYear()} BoosterBoxPro. All rights reserved.
          </p>
          <p className="text-xs text-white/20">
            Market data is for informational purposes only and does not constitute financial advice.
          </p>
        </div>
      </div>
    </footer>
  );
}

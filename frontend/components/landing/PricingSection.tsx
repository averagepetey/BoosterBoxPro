/**
 * Pricing Section
 * Displays Pro+ tier with Pioneer early access messaging
 * Single card layout centered on page
 */

'use client';

import { useAuthModals } from '@/components/auth/AuthModalsProvider';

const proFeatures = [
  'Full leaderboard access',
  'Complete historical data',
  'Advanced metrics & analytics',
  'Volume tracking & buyout alerts',
  'Priority support',
];

export function PricingSection() {
  const { openSignup } = useAuthModals();

  return (
    <section
      id="pricing"
      className="relative w-full py-6 sm:py-8 lg:py-12 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-4 sm:mb-6 lg:mb-8">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-extrabold text-white mb-2 sm:mb-3 lg:mb-4 leading-tight">
            Pioneer{' '}
            <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,var(--gold,#F6C35A),var(--gold-2,#F4B942))]">
              Access.
            </span>
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-white/80 font-medium">
            Free during early access. Pro+ coming soon.
          </p>
        </div>

        {/* Single Pro+ Card */}
        <div className="max-w-sm mx-auto mb-4 sm:mb-6 lg:mb-8">
          <div
            className="relative bg-white/5 border border-green-500/50 rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm bg-white/10"
            style={{
              boxShadow:
                '0 0 30px rgba(34, 197, 94, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4)',
            }}
          >
            {/* Pioneer Badge */}
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs sm:text-sm font-bold bg-green-500 text-white">
              PIONEER ACCESS
            </div>

            {/* Tier Name */}
            <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-1 sm:mb-2 text-center">
              Pro+
            </h3>

            {/* Price */}
            <div className="text-center mb-2 sm:mb-3 lg:mb-4">
              <div className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-0.5">
                FREE
              </div>
              <div className="text-xs sm:text-sm text-white/60">
                <span className="line-through text-white/40">$10.50/mo</span>
                {' '}during early access
              </div>
            </div>

            {/* Description */}
            <p className="text-xs sm:text-sm text-white/70 text-center mb-3 sm:mb-4 leading-relaxed">
              Full access for early members. Join our community and help shape the platform.
            </p>

            {/* Features */}
            <div className="space-y-2 sm:space-y-2.5 mb-4 sm:mb-5 lg:mb-6">
              {proFeatures.map((feature, index) => (
                <div key={index} className="flex items-start gap-2">
                  <svg
                    className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-xs sm:text-sm text-white/80 leading-relaxed">
                    {feature}
                  </span>
                </div>
              ))}
            </div>

            {/* CTA Button */}
            <button
              onClick={openSignup}
              className="block w-full text-center px-4 py-2.5 sm:py-3 rounded-full font-semibold transition-all text-sm sm:text-base min-h-[44px] flex items-center justify-center relative overflow-hidden bg-[linear-gradient(180deg,#ef4444,#dc2626)] text-white shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:opacity-90 hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)]"
            >
              <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              <span className="relative z-10">Sign Up Free</span>
            </button>
          </div>
        </div>

        {/* Additional Info */}
        <div className="text-center mt-4 sm:mt-6">
          <p className="text-xs sm:text-sm text-white/60 mb-1">
            No credit card required. Full access as a Pioneer member.
          </p>
          <p className="text-[10px] sm:text-xs text-white/50">
            Join our Discord community to connect with other collectors.
          </p>
        </div>
      </div>
    </section>
  );
}

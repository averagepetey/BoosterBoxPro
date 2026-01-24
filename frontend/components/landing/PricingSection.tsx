/**
 * Pricing Section
 * Displays pricing tiers for BoosterBoxPro
 * Mobile-first: 1 column on mobile, 2 on tablet, 3 on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface PricingTier {
  id: number;
  tag?: string;
  tagColor?: string;
  name: string;
  price: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaHref: string;
  highlighted?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    id: 1,
    name: 'Free',
    price: 'FREE',
    description: 'Perfect for casual collectors tracking a few boxes.',
    features: [
      'Basic leaderboard access',
      'Limited historical data',
      'Community access',
      'Basic metrics'
    ],
    ctaText: 'Get Started',
    ctaHref: '/signup',
    highlighted: false
  },
  {
    id: 2,
    tag: 'POPULAR',
    tagColor: 'green',
    name: 'Premium',
    price: '$29',
    description: 'For serious collectors tracking multiple boxes.',
    features: [
      'Full leaderboard access',
      'Complete historical data',
      'Advanced metrics & analytics',
      'Volume tracking & buyout alerts',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: true
  },
  {
    id: 3,
    tag: 'BEST VALUE',
    tagColor: 'yellow',
    name: 'Pro',
    price: '$79',
    description: 'For investors managing large portfolios.',
    features: [
      'Everything in Premium',
      'Portfolio tracking',
      'Price alerts & notifications',
      'API access',
      'Chrome extension premium',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: false
  }
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
            Simple Pricing. Maximum <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))]">Value.</span>
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-white/80 font-medium">
            Start tracking for free. Upgrade for advanced features.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 mb-4 sm:mb-6 lg:mb-8">
          {pricingTiers.map((tier) => (
            <div
              key={tier.id}
              className={`relative bg-white/5 border rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm transition-all ${
                tier.highlighted
                  ? 'border-green-500/50 scale-105 sm:scale-105 lg:scale-110 bg-white/10'
                  : 'border-white/10 hover:bg-white/10 hover:border-white/20'
              }`}
              style={{
                boxShadow: tier.highlighted
                  ? '0 0 30px rgba(34, 197, 94, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4)'
                  : '0 4px 20px rgba(0, 0, 0, 0.3)'
              }}
            >
              {/* Tag */}
              {tier.tag && (
                <div className={`absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs sm:text-sm font-bold ${
                  tier.tagColor === 'green'
                    ? 'bg-green-500 text-white'
                    : 'bg-yellow-400 text-[#1b1b1b]'
                }`}>
                  {tier.tag}
                </div>
              )}

              {/* Tier Name */}
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-1 sm:mb-2 text-center">
                {tier.name}
              </h3>

              {/* Price */}
              <div className="text-center mb-2 sm:mb-3 lg:mb-4">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-0.5">
                  {tier.price}
                </div>
                {tier.price !== 'FREE' && (
                  <div className="text-xs sm:text-sm text-white/60">
                    per month
                  </div>
                )}
              </div>

              {/* Description */}
              <p className="text-xs sm:text-sm text-white/70 text-center mb-3 sm:mb-4 leading-relaxed">
                {tier.description}
              </p>

              {/* Features */}
              <div className="space-y-2 sm:space-y-2.5 mb-4 sm:mb-5 lg:mb-6">
                {tier.features.map((feature, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
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
                className={`block w-full text-center px-4 py-2.5 sm:py-3 rounded-full font-semibold transition-all text-sm sm:text-base min-h-[44px] flex items-center justify-center ${
                  tier.highlighted
                    ? 'bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] text-[#1b1b1b] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]'
                    : 'bg-white/12 border border-white/15 backdrop-blur-md hover:bg-white/20 text-white shadow-[0_10px_30px_rgba(0,0,0,0.18)]'
                }`}
              >
                {tier.ctaText}
              </button>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="text-center mt-4 sm:mt-6">
          <p className="text-xs sm:text-sm text-white/60 mb-1">
            All plans include a 14-day free trial. Cancel anytime.
          </p>
          <p className="text-[10px] sm:text-xs text-white/50">
            No credit card required to start.
          </p>
        </div>
      </div>
    </section>
  );
}


 * Displays pricing tiers for BoosterBoxPro
 * Mobile-first: 1 column on mobile, 2 on tablet, 3 on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface PricingTier {
  id: number;
  tag?: string;
  tagColor?: string;
  name: string;
  price: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaHref: string;
  highlighted?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    id: 1,
    name: 'Free',
    price: 'FREE',
    description: 'Perfect for casual collectors tracking a few boxes.',
    features: [
      'Basic leaderboard access',
      'Limited historical data',
      'Community access',
      'Basic metrics'
    ],
    ctaText: 'Get Started',
    ctaHref: '/signup',
    highlighted: false
  },
  {
    id: 2,
    tag: 'POPULAR',
    tagColor: 'green',
    name: 'Premium',
    price: '$29',
    description: 'For serious collectors tracking multiple boxes.',
    features: [
      'Full leaderboard access',
      'Complete historical data',
      'Advanced metrics & analytics',
      'Volume tracking & buyout alerts',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: true
  },
  {
    id: 3,
    tag: 'BEST VALUE',
    tagColor: 'yellow',
    name: 'Pro',
    price: '$79',
    description: 'For investors managing large portfolios.',
    features: [
      'Everything in Premium',
      'Portfolio tracking',
      'Price alerts & notifications',
      'API access',
      'Chrome extension premium',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: false
  }
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
            Simple Pricing. Maximum <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))]">Value.</span>
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-white/80 font-medium">
            Start tracking for free. Upgrade for advanced features.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 mb-4 sm:mb-6 lg:mb-8">
          {pricingTiers.map((tier) => (
            <div
              key={tier.id}
              className={`relative bg-white/5 border rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm transition-all ${
                tier.highlighted
                  ? 'border-green-500/50 scale-105 sm:scale-105 lg:scale-110 bg-white/10'
                  : 'border-white/10 hover:bg-white/10 hover:border-white/20'
              }`}
              style={{
                boxShadow: tier.highlighted
                  ? '0 0 30px rgba(34, 197, 94, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4)'
                  : '0 4px 20px rgba(0, 0, 0, 0.3)'
              }}
            >
              {/* Tag */}
              {tier.tag && (
                <div className={`absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs sm:text-sm font-bold ${
                  tier.tagColor === 'green'
                    ? 'bg-green-500 text-white'
                    : 'bg-yellow-400 text-[#1b1b1b]'
                }`}>
                  {tier.tag}
                </div>
              )}

              {/* Tier Name */}
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-1 sm:mb-2 text-center">
                {tier.name}
              </h3>

              {/* Price */}
              <div className="text-center mb-2 sm:mb-3 lg:mb-4">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-0.5">
                  {tier.price}
                </div>
                {tier.price !== 'FREE' && (
                  <div className="text-xs sm:text-sm text-white/60">
                    per month
                  </div>
                )}
              </div>

              {/* Description */}
              <p className="text-xs sm:text-sm text-white/70 text-center mb-3 sm:mb-4 leading-relaxed">
                {tier.description}
              </p>

              {/* Features */}
              <div className="space-y-2 sm:space-y-2.5 mb-4 sm:mb-5 lg:mb-6">
                {tier.features.map((feature, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
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
                className={`block w-full text-center px-4 py-2.5 sm:py-3 rounded-full font-semibold transition-all text-sm sm:text-base min-h-[44px] flex items-center justify-center ${
                  tier.highlighted
                    ? 'bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] text-[#1b1b1b] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]'
                    : 'bg-white/12 border border-white/15 backdrop-blur-md hover:bg-white/20 text-white shadow-[0_10px_30px_rgba(0,0,0,0.18)]'
                }`}
              >
                {tier.ctaText}
              </button>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="text-center mt-4 sm:mt-6">
          <p className="text-xs sm:text-sm text-white/60 mb-1">
            All plans include a 14-day free trial. Cancel anytime.
          </p>
          <p className="text-[10px] sm:text-xs text-white/50">
            No credit card required to start.
          </p>
        </div>
      </div>
    </section>
  );
}


 * Displays pricing tiers for BoosterBoxPro
 * Mobile-first: 1 column on mobile, 2 on tablet, 3 on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface PricingTier {
  id: number;
  tag?: string;
  tagColor?: string;
  name: string;
  price: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaHref: string;
  highlighted?: boolean;
}

const pricingTiers: PricingTier[] = [
  {
    id: 1,
    name: 'Free',
    price: 'FREE',
    description: 'Perfect for casual collectors tracking a few boxes.',
    features: [
      'Basic leaderboard access',
      'Limited historical data',
      'Community access',
      'Basic metrics'
    ],
    ctaText: 'Get Started',
    ctaHref: '/signup',
    highlighted: false
  },
  {
    id: 2,
    tag: 'POPULAR',
    tagColor: 'green',
    name: 'Premium',
    price: '$29',
    description: 'For serious collectors tracking multiple boxes.',
    features: [
      'Full leaderboard access',
      'Complete historical data',
      'Advanced metrics & analytics',
      'Volume tracking & buyout alerts',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: true
  },
  {
    id: 3,
    tag: 'BEST VALUE',
    tagColor: 'yellow',
    name: 'Pro',
    price: '$79',
    description: 'For investors managing large portfolios.',
    features: [
      'Everything in Premium',
      'Portfolio tracking',
      'Price alerts & notifications',
      'API access',
      'Chrome extension premium',
      'Priority support'
    ],
    ctaText: 'Start Free Trial',
    ctaHref: '/signup',
    highlighted: false
  }
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
            Simple Pricing. Maximum <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))]">Value.</span>
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-white/80 font-medium">
            Start tracking for free. Upgrade for advanced features.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 mb-4 sm:mb-6 lg:mb-8">
          {pricingTiers.map((tier) => (
            <div
              key={tier.id}
              className={`relative bg-white/5 border rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm transition-all ${
                tier.highlighted
                  ? 'border-green-500/50 scale-105 sm:scale-105 lg:scale-110 bg-white/10'
                  : 'border-white/10 hover:bg-white/10 hover:border-white/20'
              }`}
              style={{
                boxShadow: tier.highlighted
                  ? '0 0 30px rgba(34, 197, 94, 0.3), 0 4px 20px rgba(0, 0, 0, 0.4)'
                  : '0 4px 20px rgba(0, 0, 0, 0.3)'
              }}
            >
              {/* Tag */}
              {tier.tag && (
                <div className={`absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs sm:text-sm font-bold ${
                  tier.tagColor === 'green'
                    ? 'bg-green-500 text-white'
                    : 'bg-yellow-400 text-[#1b1b1b]'
                }`}>
                  {tier.tag}
                </div>
              )}

              {/* Tier Name */}
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-1 sm:mb-2 text-center">
                {tier.name}
              </h3>

              {/* Price */}
              <div className="text-center mb-2 sm:mb-3 lg:mb-4">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white mb-0.5">
                  {tier.price}
                </div>
                {tier.price !== 'FREE' && (
                  <div className="text-xs sm:text-sm text-white/60">
                    per month
                  </div>
                )}
              </div>

              {/* Description */}
              <p className="text-xs sm:text-sm text-white/70 text-center mb-3 sm:mb-4 leading-relaxed">
                {tier.description}
              </p>

              {/* Features */}
              <div className="space-y-2 sm:space-y-2.5 mb-4 sm:mb-5 lg:mb-6">
                {tier.features.map((feature, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
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
                className={`block w-full text-center px-4 py-2.5 sm:py-3 rounded-full font-semibold transition-all text-sm sm:text-base min-h-[44px] flex items-center justify-center ${
                  tier.highlighted
                    ? 'bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] text-[#1b1b1b] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]'
                    : 'bg-white/12 border border-white/15 backdrop-blur-md hover:bg-white/20 text-white shadow-[0_10px_30px_rgba(0,0,0,0.18)]'
                }`}
              >
                {tier.ctaText}
              </button>
            </div>
          ))}
        </div>

        {/* Additional Info */}
        <div className="text-center mt-4 sm:mt-6">
          <p className="text-xs sm:text-sm text-white/60 mb-1">
            All plans include a 14-day free trial. Cancel anytime.
          </p>
          <p className="text-[10px] sm:text-xs text-white/50">
            No credit card required to start.
          </p>
        </div>
      </div>
    </section>
  );
}


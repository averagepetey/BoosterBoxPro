/**
 * Chrome Extension Section
 * Showcases the Chrome extension with TCGplayer/eBay integration
 * Mobile-first: Stacked on mobile, split on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

export function ChromeExtensionSection() {
  const { openSignup } = useAuthModals();
  
  return (
    <section 
      id="chrome-extension"
      className="relative w-full pt-12 sm:pt-16 lg:pt-24 pb-6 sm:pb-8 lg:pb-12 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
          {/* Left Side - Content */}
          <div className="w-full lg:w-1/2 lg:pr-8">
            {/* Title */}
            <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight lb-title">
              Track While You <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#FFD700,#FFA500)]">Browse</span>
            </h2>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl lg:text-2xl text-white/90 mb-4 lg:mb-6 font-medium">
              Market data right where you need it.
            </p>

            {/* Description */}
            <p className="text-sm sm:text-base lg:text-lg text-white/70 mb-6 lg:mb-8 leading-relaxed">
              Don't switch between tabs. Our Chrome extension brings BoosterBoxPro market intelligence directly to TCGplayer and eBay. As you browse listings, see real-time floor prices, sales trends, and market insights instantly.
            </p>

            {/* Key Features */}
            <div className="space-y-3 sm:space-y-4 mb-6 lg:mb-8">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-base sm:text-lg font-semibold text-white mb-1">
                    Real-Time Price Comparison
                  </div>
                  <div className="text-sm sm:text-base text-white/70">
                    See floor price vs. listing price as you browse
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-base sm:text-lg font-semibold text-white mb-1">
                    Sales Velocity Indicators
                  </div>
                  <div className="text-sm sm:text-base text-white/70">
                    Know if a box is hot or cold before buying
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-base sm:text-lg font-semibold text-white mb-1">
                    Historical Trend Overlay
                  </div>
                  <div className="text-sm sm:text-base text-white/70">
                    View price trends directly on product pages
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <div>
                  <div className="text-base sm:text-lg font-semibold text-white mb-1">
                    Quick Access to Full Data
                  </div>
                  <div className="text-sm sm:text-base text-white/70">
                    Jump to detailed metrics with one click
                  </div>
                </div>
              </div>
            </div>

            {/* CTA Button */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-4">
              <button
                onClick={openSignup}
                className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
              >
                <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2 sm:mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
                <span>Install Chrome Extension</span>
              </button>
            </div>

            {/* Small text */}
            <p className="text-xs sm:text-sm text-white/60">
              Works on TCGplayer and eBay. Free to use.
            </p>
          </div>

          {/* Right Side - Browser Mockup */}
          <div className="w-full lg:w-1/2 lg:pl-8">
            <div 
              className="relative rounded-xl lg:rounded-3xl overflow-hidden border border-white/10"
              style={{
                boxShadow: '0 0 20px rgba(255, 255, 255, 0.3), 0 0 40px rgba(255, 255, 255, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
              }}
            >
              {/* Browser Chrome */}
              <div className="bg-white/5 border-b border-white/10 px-4 py-2 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-white/20" />
                  <div className="w-3 h-3 rounded-full bg-white/20" />
                  <div className="w-3 h-3 rounded-full bg-white/20" />
                </div>
                <div className="flex-1 bg-black/30 rounded px-3 py-1 text-xs text-white/60">
                  tcgplayer.com/product/one-piece-op-02...
                </div>
              </div>

              {/* Browser Content */}
              <div className="bg-white/5 p-6 sm:p-8">
                {/* Product Page Mockup */}
                <div className="space-y-4">
                  {/* Product Header */}
                  <div className="flex items-start gap-4">
                    <div className="w-20 h-20 sm:w-24 sm:h-24 bg-white/10 rounded-lg flex-shrink-0" />
                    <div className="flex-1">
                      <h3 className="text-base sm:text-lg font-bold text-white mb-2">
                        One Piece - OP-02 Paramount War Booster Box
                      </h3>
                      <div className="text-xl sm:text-2xl font-bold text-green-400 mb-2">
                        $285.50
                      </div>
                      <div className="text-sm text-white/70">
                        Seller: TCGPlayer Direct
                      </div>
                    </div>
                  </div>

                  {/* Extension Overlay Box */}
                  <div 
                    className="bg-green-500/20 border-2 border-green-500/50 rounded-lg p-4 mt-4"
                    style={{
                      boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)'
                    }}
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-5 h-5 rounded bg-green-500 flex items-center justify-center">
                        <span className="text-xs font-bold text-black">B</span>
                      </div>
                      <span className="text-sm font-semibold text-green-400">
                        BoosterBoxPro Data
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <div className="text-white/60 text-xs mb-1">Floor Price</div>
                        <div className="text-white font-semibold">$285.50</div>
                      </div>
                      <div>
                        <div className="text-white/60 text-xs mb-1">24h Change</div>
                        <div className="text-green-400 font-semibold">▲ +5.2%</div>
                      </div>
                      <div>
                        <div className="text-white/60 text-xs mb-1">Sales/Day</div>
                        <div className="text-white font-semibold">3.2</div>
                      </div>
                      <div>
                        <div className="text-white/60 text-xs mb-1">Volume (30d)</div>
                        <div className="text-white font-semibold">$850K</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Caption */}
            <p className="text-center text-xs sm:text-sm text-white/60 mt-4">
              Market data appears automatically as you browse
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

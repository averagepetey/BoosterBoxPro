/**
 * Hero Section Component
 * Split layout with marketing content on left, static analytics preview on right
 * Mobile-first: Stacked on mobile, split on desktop
 * 
 * NOTE: The analytics preview is completely static - no data fetching, no API calls.
 * All values are hardcoded for preview purposes only.
 */

'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

export function HeroSection() {
  const { openSignup } = useAuthModals();

  return (
    <section className="relative min-h-screen flex flex-col lg:flex-row items-center justify-between px-4 sm:px-6 lg:px-12 py-6 sm:py-8 lg:py-12 max-w-7xl mx-auto" style={{ marginTop: '-20px' }}>
      {/* Left Side - Marketing Content */}
      <div className="w-full lg:w-1/2 mb-6 lg:mb-0 lg:pr-8">
        {/* Live Market Indicator */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/20 border border-green-500/40 backdrop-blur-md mb-3 sm:mb-4">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs sm:text-sm font-medium text-green-400">
            LIVE DATA UPDATED DAILY
          </span>
        </div>

        {/* Main Headline */}
        <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-2 sm:mb-3 lg:mb-4 leading-tight lb-title" style={{ 
          textShadow: '0 0 20px rgba(255, 255, 255, 0.9), 0 0 40px rgba(255, 255, 255, 0.7), 0 0 60px rgba(255, 255, 255, 0.5), 0 4px 8px rgba(0, 0, 0, 0.8)'
        }}>
          Track the <span className="market-gradient-animated" style={{ 
            textShadow: 'none'
          }}>Market.</span>
        </h1>

        {/* Value Proposition */}
        <p className="text-base sm:text-lg lg:text-xl text-white/90 mb-2 sm:mb-3 lg:mb-4 font-medium">
          Stop guessing. Know exactly which One Piece boxes are going to pop next—right before they do.
        </p>

        {/* Detailed Explanation */}
        <p className="text-xs sm:text-sm lg:text-base text-white/70 mb-2 sm:mb-3 leading-relaxed">
          We've built the most comprehensive tracking tool for One Piece sealed booster boxes. Our software gives you insights you can't get anywhere else so you can make informed decisions.
        </p>
        <p className="text-xs sm:text-sm text-white/50 mb-4 sm:mb-5 lg:mb-6 leading-relaxed">
          Tracked on marketplaces across the internet selling One Piece TCG.
        </p>

        {/* Call-to-Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 mb-4 sm:mb-5 lg:mb-6">
          <button
            onClick={openSignup}
            className="inline-flex items-center justify-center px-5 py-2.5 sm:px-6 sm:py-3 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-sm sm:text-base min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
          >
            <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
            <span className="relative z-10">Join Now</span>
          </button>
          <button
            onClick={openSignup}
            className="inline-flex items-center justify-center px-5 py-2.5 sm:px-6 sm:py-3 rounded-full bg-white/12 border border-white/15 backdrop-blur-md hover:bg-white/20 text-white font-semibold transition-all text-sm sm:text-base min-h-[44px] shadow-[0_10px_30px_rgba(0,0,0,0.18)] hover:shadow-[0_0_20px_rgba(255,255,255,0.6),0_0_40px_rgba(255,255,255,0.4),0_0_60px_rgba(255,255,255,0.2)] lb-anim"
          >
            Start Free Trial
          </button>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-5 lg:mb-6">
          <div className="text-center">
            <div className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-0.5">
              17+
            </div>
            <div className="text-[10px] sm:text-xs text-white/60">
              BOXES TRACKED
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-0.5">
              Fastest
            </div>
            <div className="text-[10px] sm:text-xs text-white/60">
              DATA REFRESHES IN MARKET
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-0.5">
              24/7
            </div>
            <div className="text-[10px] sm:text-xs text-white/60">
              MONITORING
            </div>
          </div>
        </div>

        {/* Supported Marketplaces */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-3 sm:gap-4">
            <span className="text-xs sm:text-sm text-white/60">Tracked on:</span>
            <div className="flex items-center gap-2 sm:gap-3">
              <span className="text-xs sm:text-sm font-medium text-white/80">TCGplayer</span>
              <span className="text-white/40">•</span>
              <span className="text-xs sm:text-sm font-medium text-white/80">eBay</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Box Detail Preview (Advanced Analytics) */}
      <div className="w-full lg:w-1/2 lg:pl-8">
        {/* Box Detail Preview Card - Matches actual box detail page */}
        <div
          className="block rounded-xl lg:rounded-3xl p-2 sm:p-3 lg:p-4 transition-all lb-anim overflow-hidden"
          style={{
            background: '#141414',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            boxShadow: '0 0 20px rgba(239, 68, 68, 0.6), 0 0 40px rgba(239, 68, 68, 0.4), 0 0 60px rgba(239, 68, 68, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
          }}
        >
          {/* Header: Title, Subtitle, Image */}
          <div className="text-center mb-2 pb-2 border-b border-white/10">
            <h3 className="text-xs sm:text-sm font-bold text-white mb-0.5">One Piece - OP-13 Carrying on His Will Booster Box</h3>
            <div className="flex items-center justify-center gap-2 text-white/50 text-[9px] sm:text-[10px] mt-0.5">
              <span>OP-13</span>
            </div>
          </div>
          
          {/* Image */}
          <div className="flex justify-center mb-2 pb-2 border-b border-white/10">
            <div className="w-12 h-12 sm:w-16 sm:h-16">
              <Image
                src="/images/boxes/op-13.png"
                alt="OP-13 Carrying on His Will"
                width={64}
                height={64}
                className="w-full h-full object-contain rounded-lg"
              />
            </div>
          </div>

          {/* 3 Key Metrics - Top Row */}
          <div className="grid grid-cols-3 text-center mb-2 pb-2 border-b border-white/10">
            {/* Current Floor */}
            <div className="border-r border-white/10 pr-1 sm:pr-2">
              <div className="text-white/50 text-[9px] sm:text-[10px] mb-0.5">Current Floor</div>
              <div className="text-sm sm:text-base font-bold text-green-400">
                $397.74
              </div>
              <div className="text-[9px] sm:text-[10px] font-semibold marketplace-positive">
                ▲ +9.72%
              </div>
            </div>
            {/* Volume EMA */}
            <div className="border-r border-white/10 px-1 sm:px-2">
              <div className="text-white/50 text-[9px] sm:text-[10px] mb-0.5">Volume (7d EMA)</div>
              <div className="text-sm sm:text-base font-bold text-white">
                $94.5K
              </div>
            </div>
            {/* Days to +20% */}
            <div className="pl-1 sm:pl-2">
              <div className="text-white/50 text-[9px] sm:text-[10px] mb-0.5">Days to +20%</div>
              <div className="text-sm sm:text-base font-bold text-white">
                N/A
              </div>
              <div className="text-white/50 text-[9px] sm:text-[10px]">Estimated</div>
            </div>
          </div>

          {/* Metrics Grid - 4 columns */}
          <div className="grid grid-cols-4 text-center pb-1.5 mb-1.5 border-b border-white/10">
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Liquidity</div>
              <div className="text-xs sm:text-sm font-bold text-white/70">
                High
              </div>
            </div>
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Listed</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                20
              </div>
            </div>
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Sold/Day</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                26.7
              </div>
            </div>
            <div>
              <div className="text-white/50 text-[9px] sm:text-[10px]">Time to Sale</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                1 day
              </div>
            </div>
          </div>

          {/* Secondary Metrics Grid */}
          <div className="grid grid-cols-4 text-center pb-1.5 mb-2 border-b border-white/10">
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Rank</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                #1
              </div>
            </div>
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Top 10 Cards</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                $30.5K
              </div>
            </div>
            <div className="border-r border-white/10">
              <div className="text-white/50 text-[9px] sm:text-[10px]">Daily Vol</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                $13.5K
              </div>
            </div>
            <div>
              <div className="text-white/50 text-[9px] sm:text-[10px]">30d Avg Sold</div>
              <div className="text-xs sm:text-sm font-bold text-white">
                26.7/d
              </div>
            </div>
          </div>

          {/* Price Trends Section */}
          <div className="mb-2 pb-2 border-b border-white/10">
            <div className="flex items-center justify-between mb-1.5">
              <h4 className="text-[10px] sm:text-xs font-bold text-white">Price Trends</h4>
              {/* Time Range Buttons - Static Preview (Non-interactive) */}
              <div className="flex gap-0.5">
                {['7D', '30D', '90D', '1Y', 'ALL'].map((range) => (
                  <div
                    key={range}
                    className={`px-1 py-0.5 text-[7px] sm:text-[8px] rounded-full ${
                      range === '30D'
                        ? 'bg-white/20 text-white'
                        : 'bg-white/5 text-white/70'
                    }`}
                  >
                    {range}
                  </div>
                ))}
              </div>
            </div>
            {/* Mini Price Chart */}
            <div className="h-16 sm:h-20 w-full relative bg-white/5 rounded border border-white/10 p-1">
              <svg className="w-full h-full" viewBox="0 0 200 80" preserveAspectRatio="none">
                {/* Y-axis labels */}
                <text x="5" y="15" fill="rgba(255,255,255,0.4)" fontSize="8">$398</text>
                <text x="5" y="30" fill="rgba(255,255,255,0.4)" fontSize="8">$389</text>
                <text x="5" y="45" fill="rgba(255,255,255,0.4)" fontSize="8">$380</text>
                <text x="5" y="60" fill="rgba(255,255,255,0.4)" fontSize="8">$371</text>
                <text x="5" y="75" fill="rgba(255,255,255,0.4)" fontSize="8">$363</text>
                {/* X-axis labels */}
                <text x="10" y="90" fill="rgba(255,255,255,0.4)" fontSize="8">Dec 24</text>
                <text x="180" y="90" fill="rgba(255,255,255,0.4)" fontSize="8">Jan 2</text>
                {/* Grid lines */}
                <line x1="0" y1="15" x2="200" y2="15" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                <line x1="0" y1="30" x2="200" y2="30" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                <line x1="0" y1="45" x2="200" y2="45" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                <line x1="0" y1="60" x2="200" y2="60" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                <line x1="0" y1="75" x2="200" y2="75" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
                {/* Price line - upward trend */}
                <polyline
                  points="10,75 30,72 50,68 70,64 90,60 110,56 130,52 150,48 170,44 190,40"
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                {/* Area fill */}
                <polygon
                  points="10,75 30,72 50,68 70,64 90,60 110,56 130,52 150,48 170,44 190,40 190,80 10,80"
                  fill="url(#priceGradientPreview)"
                  opacity="0.2"
                />
                <defs>
                  <linearGradient id="priceGradientPreview" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          {/* Reprint Risk Status */}
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
            <span className="text-[10px] sm:text-xs font-bold text-white">Reprint Risk</span>
            <span className="text-green-400">🟢</span>
            <span className="text-[10px] sm:text-xs font-semibold marketplace-positive">Low</span>
          </div>

          {/* Gauges Row */}
          <div className="grid grid-cols-2 gap-1.5 sm:gap-2">
            {/* Liquidity Score Gauge */}
            <div className="bg-white/5 rounded-xl p-1.5 sm:p-2 border border-white/10">
              <h4 className="text-[9px] sm:text-[10px] font-bold text-white mb-1.5 text-center">Liquidity Score</h4>
              <div className="relative w-full h-10 sm:h-14">
                <svg className="w-full h-full" viewBox="0 0 200 100">
                  <path
                    d="M 20 80 A 80 80 0 0 1 180 80"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth="8"
                  />
                  <path
                    d="M 20 80 A 80 80 0 0 1 180 80"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.3)"
                    strokeWidth="8"
                    strokeDasharray="0 251"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center pt-2">
                  <span className="text-[10px] sm:text-xs font-bold text-white/70">N/A</span>
                </div>
              </div>
            </div>

            {/* Reprint Risk Gauge */}
            <div className="bg-white/5 rounded-xl p-1.5 sm:p-2 border border-white/10">
              <h4 className="text-[9px] sm:text-[10px] font-bold text-white mb-1.5 text-center">Reprint Risk</h4>
              <div className="relative w-full h-10 sm:h-14">
                <svg className="w-full h-full" viewBox="0 0 200 100">
                  <path
                    d="M 20 80 A 80 80 0 0 1 180 80"
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth="8"
                  />
                  <path
                    d="M 20 80 A 80 80 0 0 1 180 80"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="8"
                    strokeDasharray="84 251"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center pt-2">
                  <span className="text-[10px] sm:text-xs font-bold marketplace-positive">LOW</span>
                </div>
              </div>
            </div>
          </div>

          {/* Preview Footer */}
          <div className="mt-2 pt-2 border-t border-white/10 text-center">
            <Link
              href="/signup"
              className="inline-flex items-center justify-center px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-white text-[10px] sm:text-xs font-medium transition-all"
            >
              Get Started to View Full Analytics →
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

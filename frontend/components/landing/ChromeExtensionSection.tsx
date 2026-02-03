/**
 * Chrome Extension Section
 * Showcases the Chrome extension with TCGplayer/eBay integration
 * Mobile-first: Stacked on mobile, split on desktop
 */

'use client';

import { useRef, useEffect } from 'react';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

export function ChromeExtensionSection() {
  const { openSignup } = useAuthModals();
  const videoRef = useRef<HTMLVideoElement>(null);

  // Play video only when scrolled into view
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let hasPlayed = false;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          if (!hasPlayed) {
            video.currentTime = 0;
            hasPlayed = true;
          }
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      },
      { threshold: 0.15 }
    );

    observer.observe(video);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      id="chrome-extension"
      className="relative w-full pt-12 sm:pt-16 lg:pt-24 pb-6 sm:pb-8 lg:pb-12 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-[1400px] mx-auto">
        <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
          {/* Left Side - Content */}
          <div className="w-full lg:w-[36%] lg:shrink-0">
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
              Our Chrome extension surfaces BoosterBoxPro intelligence directly on TCGplayer and eBay. Track real-time floor prices, sales velocity, and days of inventory left before a 20% price jump — plus whether new supply is outpacing demand. Everything you need to make confident buy and sell decisions, right where you browse.
            </p>

            {/* Feature pills */}
            <div className="flex flex-wrap gap-2 sm:gap-3 mb-6 lg:mb-8">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-white">Real-Time Prices</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-white">Sales Velocity</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-white">Historical Trends</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                <svg className="w-4 h-4 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-white">Liquidity Scores</span>
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
              Works on TCGplayer and eBay.
            </p>
          </div>

          {/* Right Side - Extension demo video */}
          <div className="w-full lg:flex-1 lg:min-w-0">
            <div className="relative rounded-xl lg:rounded-3xl overflow-hidden border border-white/10 bg-black" style={{ boxShadow: '0 0 20px rgba(255, 255, 255, 0.3), 0 0 40px rgba(255, 255, 255, 0.2), 0 30px 80px rgba(0,0,0,0.2)' }}>
              <video
                ref={videoRef}
                muted
                loop
                playsInline
                preload="auto"
                className="w-full h-auto block"
                src="/videos/extension-demo.mp4"
              />
            </div>

            <p className="text-center text-xs sm:text-sm text-white/60 mt-4">
              Market data appears automatically as you browse
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

/**
 * Our Story Section
 * Tells the origin story of BoosterBoxPro
 * Mobile-first: Responsive text and spacing
 */

'use client';

import { useAuthModals } from '@/components/auth/AuthModalsProvider';

export function OurStorySection() {
  const { openSignup } = useAuthModals();
  return (
    <section 
      id="our-story"
      className="relative w-full py-12 sm:py-16 lg:py-24 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-4xl mx-auto">
        {/* Title */}
        <div className="text-center mb-8 sm:mb-10 lg:mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight">
            OUR <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">STORY</span>
          </h2>
        </div>

        {/* Body Text */}
        <div className="space-y-6 sm:space-y-8 text-center mb-8 sm:mb-10 lg:mb-12">
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            We didn't start as a software company.
          </p>
          
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            We started as One Piece collectors, spending countless hours manually tracking prices, sales, and market trends across dozens of marketplaces. We knew there had to be a better, faster way to understand the market. So, we built BoosterPro for ourselves.
          </p>
          
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            So you can stop guessing and be quicker to the best opportunities than anyone else in the market. After seeing its power, we realized we couldn't keep it to ourselves—our mission is to give you the exact insights we created for ourselves.
          </p>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8 font-medium">
            Ready to start tracking like a pro?
          </p>
          <button
            onClick={openSignup}
            className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
          >
            <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
            <span className="relative z-10">Get Started Free</span>
          </button>
        </div>
      </div>
    </section>
  );
}

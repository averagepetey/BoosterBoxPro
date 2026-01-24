/**
 * Our Story Section
 * Tells the origin story of BoosterBoxPro
 * Mobile-first: Responsive text and spacing
 */

'use client';

import Link from 'next/link';
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
            We started as One Piece collectors, spending countless hours manually tracking prices, sales, and market trends across dozens of marketplaces. We knew there had to be a better, faster way to understand the market. So, we built BoosterBoxPro for ourselves. A tool to cut through the noise, automate the tracking, and make data-driven decisions with confidence.
          </p>
          
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            After seeing its power, we realized we couldn't keep it to ourselves. Our mission is simple: to give you the exact insights we created for ourselves, so you can stop guessing and start making informed investment decisions.
          </p>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8 font-medium">
            Ready to start tracking like a pro?
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
            >
              <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              <span className="relative z-10">Get Started Free</span>
            </button>
            <Link
              href="#how-it-works"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              Learn How It Works
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


 * Tells the origin story of BoosterBoxPro
 * Mobile-first: Responsive text and spacing
 */

'use client';

import Link from 'next/link';
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
            We started as One Piece collectors, spending countless hours manually tracking prices, sales, and market trends across dozens of marketplaces. We knew there had to be a better, faster way to understand the market. So, we built BoosterBoxPro for ourselves. A tool to cut through the noise, automate the tracking, and make data-driven decisions with confidence.
          </p>
          
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            After seeing its power, we realized we couldn't keep it to ourselves. Our mission is simple: to give you the exact insights we created for ourselves, so you can stop guessing and start making informed investment decisions.
          </p>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8 font-medium">
            Ready to start tracking like a pro?
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
            >
              <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              <span className="relative z-10">Get Started Free</span>
            </button>
            <Link
              href="#how-it-works"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              Learn How It Works
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


 * Tells the origin story of BoosterBoxPro
 * Mobile-first: Responsive text and spacing
 */

'use client';

import Link from 'next/link';
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
            We started as One Piece collectors, spending countless hours manually tracking prices, sales, and market trends across dozens of marketplaces. We knew there had to be a better, faster way to understand the market. So, we built BoosterBoxPro for ourselves. A tool to cut through the noise, automate the tracking, and make data-driven decisions with confidence.
          </p>
          
          <p className="text-sm sm:text-base lg:text-lg text-white/80 leading-relaxed">
            After seeing its power, we realized we couldn't keep it to ourselves. Our mission is simple: to give you the exact insights we created for ourselves, so you can stop guessing and start making informed investment decisions.
          </p>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8 font-medium">
            Ready to start tracking like a pro?
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,#ef4444,#dc2626)] hover:opacity-90 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(239,68,68,0.35)] hover:shadow-[0_0_20px_rgba(239,68,68,0.8),0_0_40px_rgba(239,68,68,0.6),0_0_60px_rgba(239,68,68,0.4)] relative overflow-hidden lb-anim"
            >
              <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              <span className="relative z-10">Get Started Free</span>
            </button>
            <Link
              href="#how-it-works"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              Learn How It Works
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


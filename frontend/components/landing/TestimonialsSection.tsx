/**
 * Testimonials Section
 * Carousel showing reviews from community members
 * Mobile-first: Single card on mobile, two cards on desktop
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Testimonial {
  id: number;
  username: string;
  handle: string;
  profilePicture: string;
  rating: number;
  review: string;
  date: string;
}

const testimonials: Testimonial[] = [
  {
    id: 1,
    username: 'AlexCollector',
    handle: '@alexcollects',
    profilePicture: '👤',
    rating: 5,
    review: "Between the ease of use and comprehensive data, I've been able to track my collection's value and make informed buying decisions. The real-time metrics are incredibly valuable.",
    date: '2 weeks ago'
  },
  {
    id: 2,
    username: 'MarketWatcher',
    handle: '@marketpro',
    profilePicture: '👤',
    rating: 5,
    review: "As someone who has tried tracking prices manually, BoosterBoxPro has been a game-changer. The dashboard makes it easy to spot trends and opportunities.",
    date: '1 month ago'
  },
  {
    id: 3,
    username: 'OnePieceInvestor',
    handle: '@opinvestor',
    profilePicture: '👤',
    rating: 5,
    review: "The Chrome extension is amazing - having market data right on TCGplayer and eBay pages has completely changed how I shop for boxes.",
    date: '3 weeks ago'
  },
  {
    id: 4,
    username: 'DataDriven',
    handle: '@datatracker',
    profilePicture: '👤',
    rating: 5,
    review: "Spotting buyouts before they happen has given me a huge edge. The volume tracking feature is something you can't get anywhere else.",
    date: '1 week ago'
  },
  {
    id: 5,
    username: 'SealedBoxPro',
    handle: '@sealedpro',
    profilePicture: '👤',
    rating: 5,
    review: "The historical price trends help me understand market cycles. I've been able to buy at the perfect times using this data.",
    date: '2 months ago'
  },
  {
    id: 6,
    username: 'BoxMaster',
    handle: '@boxmaster',
    profilePicture: '👤',
    rating: 5,
    review: "Incredible platform! The buyout detection saved me from missing a major opportunity. Worth every penny.",
    date: '3 days ago'
  },
  {
    id: 7,
    username: 'InvestorPro',
    handle: '@investpro',
    profilePicture: '👤',
    rating: 5,
    review: "The volume tracking feature is a game-changer. I can see market shifts before they happen.",
    date: '1 week ago'
  },
  {
    id: 8,
    username: 'OnePieceFan',
    handle: '@opfan',
    profilePicture: '👤',
    rating: 5,
    review: "Best investment tracking tool for One Piece boxes. The data is always accurate and up-to-date.",
    date: '5 days ago'
  },
  {
    id: 9,
    username: 'MarketInsight',
    handle: '@marketinsight',
    profilePicture: '👤',
    rating: 5,
    review: "Love the real-time updates. Makes trading so much easier with instant market data.",
    date: '2 weeks ago'
  },
  {
    id: 10,
    username: 'DataCollector',
    handle: '@datacollect',
    profilePicture: '👤',
    rating: 5,
    review: "The analytics are incredible. I've made smarter buying decisions using this platform.",
    date: '1 month ago'
  }
];

export function TestimonialsSection() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  
  // Detect mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Number of cards to show at once (1 on mobile, 2 on desktop)
  const cardsPerView = isMobile ? 1 : 2;
  
  // Calculate total pages
  const totalPages = Math.ceil(testimonials.length / cardsPerView);
  
  const goToNext = () => {
    setCurrentIndex((prev) => (prev + 1) % totalPages);
  };
  
  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev - 1 + totalPages) % totalPages);
  };
  
  const goToPage = (index: number) => {
    setCurrentIndex(index);
  };
  
  // Get visible testimonials for current page
  const getVisibleTestimonials = () => {
    const start = currentIndex * cardsPerView;
    return testimonials.slice(start, start + cardsPerView);
  };
  
  return (
    <section 
      id="testimonials"
      className="relative w-full pt-6 sm:pt-8 lg:pt-12 pb-6 sm:pb-8 lg:pb-12"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-12">
        {/* Header */}
        <div className="text-center mb-4 sm:mb-6 lg:mb-8">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-extrabold text-white mb-2 sm:mb-3 lg:mb-4 leading-tight">
            Reviews from the <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">Community</span>
          </h2>
          <p className="text-sm sm:text-base lg:text-lg text-white/80 font-medium">
            Trusted by Collectors Who Invest Consistently
          </p>
        </div>

        {/* Carousel Container */}
        <div className="relative mb-4 sm:mb-6 lg:mb-8">
          {/* Navigation Arrows */}
          <button
            onClick={goToPrevious}
            className="absolute left-0 sm:-left-4 lg:-left-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md flex items-center justify-center transition-all min-h-[44px] sm:min-h-[48px]"
            aria-label="Previous reviews"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <button
            onClick={goToNext}
            className="absolute right-0 sm:-right-4 lg:-right-8 top-1/2 -translate-y-1/2 z-10 w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md flex items-center justify-center transition-all min-h-[44px] sm:min-h-[48px]"
            aria-label="Next reviews"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Cards Container */}
          <div className={`flex gap-4 sm:gap-6 lg:gap-8 overflow-hidden ${isMobile ? 'px-2' : 'px-12 sm:px-16 lg:px-20'}`}>
            {getVisibleTestimonials().map((testimonial) => (
              <div
                key={testimonial.id}
                className={`${isMobile ? 'w-full' : 'flex-1'} min-w-0 bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm`}
                style={{
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                }}
              >
                {/* Profile Section */}
                <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 rounded-full bg-white/10 flex items-center justify-center text-xl sm:text-2xl flex-shrink-0">
                    {testimonial.profilePicture}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs sm:text-sm lg:text-base font-semibold text-white mb-0.5">
                      {testimonial.username}
                    </div>
                    <div className="text-[10px] sm:text-xs text-white/60 truncate">
                      {testimonial.handle}
                    </div>
                  </div>
                </div>

                {/* Star Rating */}
                <div className="flex gap-0.5 sm:gap-1 mb-2 sm:mb-3">
                  {Array.from({ length: testimonial.rating }).map((_, i) => (
                    <svg
                      key={i}
                      className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>

                {/* Review Text */}
                <p className="text-xs sm:text-sm lg:text-base text-white/80 leading-relaxed mb-2 sm:mb-3 line-clamp-4 sm:line-clamp-none">
                  "{testimonial.review}"
                </p>

                {/* Date */}
                <div className="text-[10px] sm:text-xs text-white/50">
                  {testimonial.date}
                </div>
              </div>
            ))}
          </div>

          {/* Join Now Button (replaces pagination dots) */}
          <div className="flex justify-center mt-3 sm:mt-4">
            <Link
              href="/signup"
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-yellow-400 hover:bg-yellow-300 text-white font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(234,179,8,0.35)] hover:shadow-[0_0_20px_rgba(234,179,8,0.8),0_0_40px_rgba(234,179,8,0.6),0_0_60px_rgba(234,179,8,0.4)]"
            >
              Join Now
            </Link>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center mt-4 sm:mt-6 mb-8 sm:mb-12 lg:mb-16">
          <p className="text-sm sm:text-base lg:text-lg text-white/80 mb-3 sm:mb-4">
            Join thousands of collectors making data-driven decisions.
          </p>
        </div>

        {/* Scrolling Reviews Section - Full Width */}
      </div>

      <div className="w-full overflow-hidden mb-8 sm:mb-12 lg:mb-16">
        {/* Top Row - Scrolling Right */}
        <div className="overflow-hidden mb-4 sm:mb-6 w-full">
          <div className="flex gap-4 sm:gap-6 scroll-right-animation">
            {[...testimonials, ...testimonials].map((testimonial, index) => (
                <div
                  key={`top-${testimonial.id}-${index}`}
                  className="flex-shrink-0 w-72 sm:w-80 lg:w-96 bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                  }}
                >
                  {/* Profile Section */}
                  <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/10 flex items-center justify-center text-xl sm:text-2xl flex-shrink-0">
                      {testimonial.profilePicture}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs sm:text-sm font-semibold text-white mb-0.5">
                        {testimonial.username}
                      </div>
                      <div className="text-[10px] sm:text-xs text-white/60 truncate">
                        {testimonial.handle}
                      </div>
                    </div>
                  </div>

                  {/* Star Rating */}
                  <div className="flex gap-0.5 sm:gap-1 mb-2 sm:mb-3">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <svg
                        key={i}
                        className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>

                  {/* Review Text */}
                  <p className="text-xs sm:text-sm text-white/80 leading-relaxed mb-2 sm:mb-3 line-clamp-4">
                    "{testimonial.review}"
                  </p>

                  {/* Date */}
                  <div className="text-[10px] sm:text-xs text-white/50">
                    {testimonial.date}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Row - Scrolling Left */}
          <div className="overflow-hidden w-full">
            <div className="flex gap-4 sm:gap-6 scroll-left-animation">
              {[...testimonials, ...testimonials].map((testimonial, index) => (
                <div
                  key={`bottom-${testimonial.id}-${index}`}
                  className="flex-shrink-0 w-72 sm:w-80 lg:w-96 bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-4 sm:p-5 lg:p-6 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                  }}
                >
                  {/* Profile Section */}
                  <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
                    <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/10 flex items-center justify-center text-xl sm:text-2xl flex-shrink-0">
                      {testimonial.profilePicture}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs sm:text-sm font-semibold text-white mb-0.5">
                        {testimonial.username}
                      </div>
                      <div className="text-[10px] sm:text-xs text-white/60 truncate">
                        {testimonial.handle}
                      </div>
                    </div>
                  </div>

                  {/* Star Rating */}
                  <div className="flex gap-0.5 sm:gap-1 mb-2 sm:mb-3">
                    {Array.from({ length: testimonial.rating }).map((_, i) => (
                      <svg
                        key={i}
                        className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>

                  {/* Review Text */}
                  <p className="text-xs sm:text-sm text-white/80 leading-relaxed mb-2 sm:mb-3 line-clamp-4">
                    "{testimonial.review}"
                  </p>

                  {/* Date */}
                  <div className="text-[10px] sm:text-xs text-white/50">
                    {testimonial.date}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
    </section>
  );
}


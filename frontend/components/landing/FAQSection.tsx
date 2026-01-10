/**
 * FAQ Section
 * Accordion-style FAQ with expandable questions
 * Mobile-first: Responsive layout with smooth transitions
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';

interface FAQItem {
  id: number;
  question: string;
  answer: string;
  category: string;
}

const faqItems: FAQItem[] = [
  // General Questions
  {
    id: 1,
    category: 'General',
    question: 'How often is the data updated?',
    answer: 'Our data is updated daily, with some metrics refreshed multiple times throughout the day. Floor prices and sales data are updated every 24 hours to ensure you have the most current market information.'
  },
  {
    id: 2,
    category: 'General',
    question: 'What marketplaces do you track?',
    answer: 'We currently track TCGplayer and eBay, the two largest marketplaces for One Piece sealed booster boxes. We\'re continuously expanding our marketplace coverage to provide comprehensive market data.'
  },
  {
    id: 3,
    category: 'General',
    question: 'Is the platform free to use?',
    answer: 'We offer a free tier with basic features including limited leaderboard access and historical data. Premium and Pro tiers unlock advanced features like full historical data, volume tracking, buyout alerts, and priority support.'
  },
  {
    id: 4,
    category: 'General',
    question: 'How do you calculate floor prices?',
    answer: 'Floor prices are calculated as the lowest available listing price across all tracked marketplaces. We update these prices daily and factor in listing conditions, shipping costs, and seller ratings to provide accurate market floor data.'
  },
  {
    id: 5,
    category: 'General',
    question: 'How accurate is the sales data?',
    answer: 'We track verified sales data from TCGplayer and eBay, ensuring high accuracy. Our system filters out canceled orders, returns, and invalid transactions to provide reliable sales velocity and volume metrics.'
  },
  // Chrome Extension Questions
  {
    id: 6,
    category: 'Chrome Extension',
    question: 'How do I install the Chrome extension?',
    answer: 'You can install the BoosterBoxPro Chrome extension from the Chrome Web Store. Simply search for "BoosterBoxPro" and click "Add to Chrome". The extension works automatically on TCGplayer and eBay product pages once installed.'
  },
  {
    id: 7,
    category: 'Chrome Extension',
    question: 'Which marketplaces does the extension work with?',
    answer: 'The Chrome extension currently works with TCGplayer and eBay product pages. When you browse listings on these marketplaces, you\'ll see real-time floor prices, sales velocity, and market insights directly on the page.'
  },
  {
    id: 8,
    category: 'Chrome Extension',
    question: 'Does the extension slow down my browser?',
    answer: 'No, our extension is lightweight and optimized for performance. It only activates on relevant product pages and uses minimal resources. You shouldn\'t notice any impact on your browser speed.'
  },
  {
    id: 9,
    category: 'Chrome Extension',
    question: 'What data does the extension show on product pages?',
    answer: 'The extension displays real-time floor price, 24-hour price changes, sales per day, volume metrics, and trend indicators directly on TCGplayer and eBay product pages. You can also click to view full analytics on our dashboard.'
  },
  // Data & Features Questions
  {
    id: 10,
    category: 'Data & Features',
    question: 'How does buyout detection work?',
    answer: 'Our system monitors listing disappearance rates and sales velocity spikes. When we detect unusually rapid listing removals or sales surges, we flag potential buyouts. This helps you identify when strong buyer interest or coordinated purchases are happening.'
  },
  {
    id: 11,
    category: 'Data & Features',
    question: 'What is volume movement tracking?',
    answer: 'Volume movement tracking shows when trading volume shifts from one box to another. We use 7-day exponential moving averages to identify trends, so you can see when volume moves from OP-01 to OP-03, or from Romance Dawn to Paramount War, indicating shifting market interest.'
  },
  {
    id: 12,
    category: 'Data & Features',
    question: 'Do you track all One Piece boxes?',
    answer: 'We track all major One Piece sealed booster boxes released in North America, including OP-01 through OP-13 and beyond. As new sets are released, we add them to our tracking system within 24-48 hours of launch.'
  },
  {
    id: 13,
    category: 'Data & Features',
    question: 'What makes BoosterBoxPro data unique?',
    answer: 'We provide faster market updates than any competitor, real-time buyout detection, volume movement tracking between boxes, and comprehensive analytics you can\'t get elsewhere. Our platform is built by collectors, for collectors, ensuring the data and features you actually need.'
  }
];

export function FAQSection() {
  const [openItems, setOpenItems] = useState<number[]>([]);

  const toggleItem = (id: number) => {
    setOpenItems((prev) =>
      prev.includes(id)
        ? prev.filter((itemId) => itemId !== id)
        : [...prev, id]
    );
  };

  return (
    <section 
      id="faq"
      className="relative w-full py-12 sm:py-16 lg:py-24 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight">
            Frequently Asked <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">Questions</span>
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-white/80 font-medium">
            Everything you need to know about BoosterBoxPro.
          </p>
        </div>

        {/* FAQ Items */}
        <div className="space-y-3 sm:space-y-4 mb-8 sm:mb-12 lg:mb-16">
          {faqItems.map((item) => {
            const isOpen = openItems.includes(item.id);
            return (
              <div
                key={item.id}
                className="bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl backdrop-blur-sm overflow-hidden transition-all"
                style={{
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
                }}
              >
                {/* Question Button */}
                <button
                  onClick={() => toggleItem(item.id)}
                  className="w-full px-4 sm:px-6 lg:px-8 py-4 sm:py-5 lg:py-6 flex items-center justify-between text-left gap-4 hover:bg-white/5 transition-all min-h-[44px]"
                  aria-expanded={isOpen}
                >
                  <span className="text-sm sm:text-base lg:text-lg font-semibold text-white flex-1">
                    {item.question}
                  </span>
                  <svg
                    className={`w-5 h-5 sm:w-6 sm:h-6 text-white/70 flex-shrink-0 transition-transform duration-200 ${
                      isOpen ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {/* Answer Content */}
                <div
                  className={`transition-all duration-300 ease-in-out overflow-hidden ${
                    isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
                  }`}
                >
                  <div className="px-4 sm:px-6 lg:px-8 pb-4 sm:pb-5 lg:pb-6 pt-0">
                    <p className="text-sm sm:text-base text-white/70 leading-relaxed">
                      {item.answer}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8">
            Still have questions? We're here to help.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link
              href="/support"
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] hover:opacity-90 text-[#1b1b1b] font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]"
            >
              Contact Support
            </Link>
            <Link
              href="#faq"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              Join Discord
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


/**
 * Unique Data Section
 * Showcases the unique data points that BoosterBoxPro tracks
 * Mobile-first: 1 column on mobile, 2 on tablet, 3 on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface DataPoint {
  id: number;
  icon: string;
  title: string;
  description: string;
  keyMetric: string;
}

const dataPoints: DataPoint[] = [
  {
    id: 1,
    icon: '⚡',
    title: 'Faster Market Updates Than Anything Else on the Market',
    description: 'Get market updates faster than any other platform. Our advanced tracking system ensures you see the latest data before anyone else.',
    keyMetric: 'Faster than competitors'
  },
  {
    id: 2,
    icon: '⚡',
    title: 'Sales Per Day',
    description: 'Know how fast boxes are selling with our 30-day average sales velocity. Spot hot boxes before they spike.',
    keyMetric: '30-day rolling average'
  },
  {
    id: 3,
    icon: '📊',
    title: 'Volume Movement',
    description: 'Track when volume shifts from one box to another. Identify emerging trends before they become mainstream.',
    keyMetric: '7-day EMA tracking'
  },
  {
    id: 4,
    icon: '⚡',
    title: 'Buyout Alerts',
    description: 'Know when buyouts are happening in real-time. See when listings disappear rapidly, indicating market interest.',
    keyMetric: 'Real-time monitoring'
  },
  {
    id: 5,
    icon: '📈',
    title: 'Price History & Patterns',
    description: '30-day, 90-day, and year-over-year price trends. Understand market cycles and patterns.',
    keyMetric: 'Complete historical data'
  },
  {
    id: 6,
    icon: '📦',
    title: 'Active Listings & Supply',
    description: 'Track how many boxes are currently listed, giving you insight into market supply and competition.',
    keyMetric: 'Live marketplace data'
  }
];

export function UniqueDataSection() {
  const { openSignup } = useAuthModals();
  
  return (
    <section 
      id="unique-data"
      className="relative w-full py-12 sm:py-16 lg:py-24 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight">
            What Unique Data Does <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">Booster Pro Track?</span>
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-white/80 font-medium">
            Metrics others don't see. Insights you can't get anywhere else.
          </p>
        </div>

        {/* Data Points Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 lg:gap-10 mb-8 sm:mb-12 lg:mb-16">
          {dataPoints.map((dataPoint) => (
            <div
              key={dataPoint.id}
              className="bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-6 sm:p-8 backdrop-blur-sm transition-all hover:bg-white/10 hover:border-white/20"
              style={{
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
              }}
            >
              {/* Icon */}
              <div className="text-4xl sm:text-5xl lg:text-6xl mb-4 sm:mb-6">
                {dataPoint.icon}
              </div>

              {/* Title */}
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-white mb-3 sm:mb-4">
                {dataPoint.title}
              </h3>

              {/* Description */}
              <p className="text-sm sm:text-base text-white/70 leading-relaxed mb-4 sm:mb-6">
                {dataPoint.description}
              </p>

              {/* Key Metric */}
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/20 border border-green-500/40">
                <span className="text-xs sm:text-sm font-medium text-green-400">
                  {dataPoint.keyMetric}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8">
            Get access to all these unique metrics and more.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] hover:opacity-90 text-[#1b1b1b] font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]"
            >
              View Dashboard
            </button>
            <Link
              href="#unique-data"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              See Sample Data
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

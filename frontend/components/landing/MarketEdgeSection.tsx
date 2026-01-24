

 * Explains how to gain an edge with buyout detection and volume tracking
 * Mobile-first: Stacked on mobile, split layout on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface FeatureSection {
  id: number;
  icon: string;
  title: string;
  description: string;
  features: string[];
}

const featureSections: FeatureSection[] = [
  {
    id: 1,
    icon: '⚡',
    title: 'Spot Buyouts as They Happen',
    description: "Don't miss the action. Our system detects when boxes are being bought out rapidly. See when listings disappear fast, indicating strong buyer interest or coordinated purchases.",
    features: [
      'Real-time listing disappearance tracking',
      'Velocity alerts when sales spike',
      'Historical buyout patterns',
      'Volume surge detection'
    ]
  },
  {
    id: 2,
    icon: '📊',
    title: 'Track Volume Shifts Between Boxes',
    description: "Understand market dynamics like never before. See when trading volume shifts from one box to another. When Romance Dawn volume drops and Paramount War volume spikes, you'll know immediately. This is where the smart money moves.",
    features: [
      'Volume comparison across all boxes',
      'Trend indicators showing volume flow',
      '7-day EMA tracking for smooth trends',
      'Historical volume patterns'
    ]
  },
  {
    id: 3,
    icon: '🧠',
    title: 'Understand Market Movements',
    description: "Volume shifts often precede price movements. When you see volume moving from OP-01 to OP-03, or from Romance Dawn to Paramount War, you're seeing early signals. Use this intelligence to position yourself ahead of the market.",
    features: [
      'Correlation analysis between boxes',
      'Early trend identification',
      'Market cycle patterns',
      'Portfolio optimization insights'
    ]
  }
];

export function MarketEdgeSection() {
  const { openSignup } = useAuthModals();
  
  return (
    <section 
      id="market-edge"
      className="relative w-full py-12 sm:py-16 lg:py-24 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight">
            Gain an Edge Over the <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">One Piece Market</span>
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-white/80 font-medium">
            Know when buyouts are happening, and volume is shifting from one box to another.
          </p>
        </div>

        {/* Feature Sections */}
        <div className="space-y-8 sm:space-y-12 lg:space-y-16 mb-8 sm:mb-12 lg:mb-16">
          {featureSections.map((section, index) => (
            <div
              key={section.id}
              className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-6 sm:gap-8 lg:gap-12`}
            >
              {/* Left/Right Side - Content */}
              <div className="w-full lg:w-1/2">
                <div className="flex items-start gap-4 sm:gap-6 mb-4 sm:mb-6">
                  <div className="text-4xl sm:text-5xl lg:text-6xl flex-shrink-0">
                    {section.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-3 sm:mb-4">
                      {section.title}
                    </h3>
                    <p className="text-sm sm:text-base lg:text-lg text-white/70 leading-relaxed mb-4 sm:mb-6">
                      {section.description}
                    </p>
                    
                    {/* Key Features */}
                    <div className="space-y-2 sm:space-y-3">
                      {section.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-start gap-2 sm:gap-3">
                          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-xs sm:text-sm lg:text-base text-white/80">
                            {feature}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right/Left Side - Visual Placeholder */}
              <div className="w-full lg:w-1/2">
                <div 
                  className="bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-6 sm:p-8 lg:p-12 backdrop-blur-sm h-full flex items-center justify-center"
                  style={{
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                    minHeight: '300px'
                  }}
                >
                  <div className="text-center">
                    <div className="text-4xl sm:text-5xl lg:text-6xl mb-4 text-white/20">
                      {section.icon}
                    </div>
                    <p className="text-sm sm:text-base text-white/40">
                      Visual representation coming soon
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8">
            Start tracking buyouts and volume shifts today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] hover:opacity-90 text-[#1b1b1b] font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]"
            >
              View Live Data
            </button>
            <Link
              href="#market-edge"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              See Examples
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


 * Explains how to gain an edge with buyout detection and volume tracking
 * Mobile-first: Stacked on mobile, split layout on desktop
 */

'use client';

import Link from 'next/link';
import { useAuthModals } from '@/components/auth/AuthModalsProvider';

interface FeatureSection {
  id: number;
  icon: string;
  title: string;
  description: string;
  features: string[];
}

const featureSections: FeatureSection[] = [
  {
    id: 1,
    icon: '⚡',
    title: 'Spot Buyouts as They Happen',
    description: "Don't miss the action. Our system detects when boxes are being bought out rapidly. See when listings disappear fast, indicating strong buyer interest or coordinated purchases.",
    features: [
      'Real-time listing disappearance tracking',
      'Velocity alerts when sales spike',
      'Historical buyout patterns',
      'Volume surge detection'
    ]
  },
  {
    id: 2,
    icon: '📊',
    title: 'Track Volume Shifts Between Boxes',
    description: "Understand market dynamics like never before. See when trading volume shifts from one box to another. When Romance Dawn volume drops and Paramount War volume spikes, you'll know immediately. This is where the smart money moves.",
    features: [
      'Volume comparison across all boxes',
      'Trend indicators showing volume flow',
      '7-day EMA tracking for smooth trends',
      'Historical volume patterns'
    ]
  },
  {
    id: 3,
    icon: '🧠',
    title: 'Understand Market Movements',
    description: "Volume shifts often precede price movements. When you see volume moving from OP-01 to OP-03, or from Romance Dawn to Paramount War, you're seeing early signals. Use this intelligence to position yourself ahead of the market.",
    features: [
      'Correlation analysis between boxes',
      'Early trend identification',
      'Market cycle patterns',
      'Portfolio optimization insights'
    ]
  }
];

export function MarketEdgeSection() {
  const { openSignup } = useAuthModals();
  
  return (
    <section 
      id="market-edge"
      className="relative w-full py-12 sm:py-16 lg:py-24 px-4 sm:px-6 lg:px-12"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 sm:mb-12 lg:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-white mb-4 lg:mb-6 leading-tight">
            Gain an Edge Over the <span className="text-transparent bg-clip-text bg-[linear-gradient(180deg,#22c55e,#16a34a)]">One Piece Market</span>
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-white/80 font-medium">
            Know when buyouts are happening, and volume is shifting from one box to another.
          </p>
        </div>

        {/* Feature Sections */}
        <div className="space-y-8 sm:space-y-12 lg:space-y-16 mb-8 sm:mb-12 lg:mb-16">
          {featureSections.map((section, index) => (
            <div
              key={section.id}
              className={`flex flex-col ${index % 2 === 0 ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-6 sm:gap-8 lg:gap-12`}
            >
              {/* Left/Right Side - Content */}
              <div className="w-full lg:w-1/2">
                <div className="flex items-start gap-4 sm:gap-6 mb-4 sm:mb-6">
                  <div className="text-4xl sm:text-5xl lg:text-6xl flex-shrink-0">
                    {section.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-3 sm:mb-4">
                      {section.title}
                    </h3>
                    <p className="text-sm sm:text-base lg:text-lg text-white/70 leading-relaxed mb-4 sm:mb-6">
                      {section.description}
                    </p>
                    
                    {/* Key Features */}
                    <div className="space-y-2 sm:space-y-3">
                      {section.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-start gap-2 sm:gap-3">
                          <svg className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                          <span className="text-xs sm:text-sm lg:text-base text-white/80">
                            {feature}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Right/Left Side - Visual Placeholder */}
              <div className="w-full lg:w-1/2">
                <div 
                  className="bg-white/5 border border-white/10 rounded-xl lg:rounded-2xl p-6 sm:p-8 lg:p-12 backdrop-blur-sm h-full flex items-center justify-center"
                  style={{
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                    minHeight: '300px'
                  }}
                >
                  <div className="text-center">
                    <div className="text-4xl sm:text-5xl lg:text-6xl mb-4 text-white/20">
                      {section.icon}
                    </div>
                    <p className="text-sm sm:text-base text-white/40">
                      Visual representation coming soon
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <p className="text-base sm:text-lg lg:text-xl text-white/80 mb-6 sm:mb-8">
            Start tracking buyouts and volume shifts today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <button
              onClick={openSignup}
              className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 rounded-full bg-[linear-gradient(180deg,var(--gold, #F6C35A),var(--gold-2, #F4B942))] hover:opacity-90 text-[#1b1b1b] font-semibold transition-all text-base sm:text-lg min-h-[44px] shadow-[0_10px_24px_rgba(246,195,90,0.35)] hover:shadow-[0_0_20px_rgba(246,195,90,0.8),0_0_40px_rgba(246,195,90,0.6),0_0_60px_rgba(246,195,90,0.4)]"
            >
              View Live Data
            </button>
            <Link
              href="#market-edge"
              className="text-sm sm:text-base text-white/80 hover:text-white underline transition-colors min-h-[44px] flex items-center"
            >
              See Examples
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}


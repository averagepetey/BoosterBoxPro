

 * Main marketing page for BoosterBoxPro
 */

'use client';

import { HeroSection } from '@/components/landing/HeroSection';
import { ChromeExtensionSection } from '@/components/landing/ChromeExtensionSection';
import { TestimonialsSection } from '@/components/landing/TestimonialsSection';
import { OurStorySection } from '@/components/landing/OurStorySection';
import { UniqueDataSection } from '@/components/landing/UniqueDataSection';
import { MarketEdgeSection } from '@/components/landing/MarketEdgeSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { FAQSection } from '@/components/landing/FAQSection';
import { Navigation } from '@/components/ui/Navigation';
import { AuthModalsProvider } from '@/components/auth/AuthModalsProvider';

export default function LandingPage() {
  return (
    <AuthModalsProvider>
      <div 
        className="min-h-screen relative"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
          backgroundColor: '#000000'
        }}
      >
        {/* Overlay to ensure content is readable */}
        <div className="absolute inset-0 bg-black/20 pointer-events-none" />
        
        {/* Navigation - NOT sticky */}
        <div className="relative z-10">
          <Navigation sticky={false} />
        </div>
      
      {/* Hero Section */}
      <div className="relative z-10">
        <HeroSection />
      </div>
      
      {/* Chrome Extension Section */}
      <div className="relative z-10">
        <ChromeExtensionSection />
      </div>
      
      {/* Testimonials Section */}
      <div className="relative z-10">
        <TestimonialsSection />
      </div>
      
      {/* Our Story Section */}
      <div className="relative z-10">
        <OurStorySection />
      </div>
      
      {/* Unique Data Section */}
      <div className="relative z-10">
        <UniqueDataSection />
      </div>
      
      {/* Market Edge Section */}
      <div className="relative z-10">
        <MarketEdgeSection />
      </div>
      
      {/* Pricing Section */}
      <div className="relative z-10">
        <PricingSection />
      </div>
      
      {/* FAQ Section */}
      <div className="relative z-10">
        <FAQSection />
      </div>
      </div>
    </AuthModalsProvider>
  );
}


 * Main marketing page for BoosterBoxPro
 */

'use client';

import { HeroSection } from '@/components/landing/HeroSection';
import { ChromeExtensionSection } from '@/components/landing/ChromeExtensionSection';
import { TestimonialsSection } from '@/components/landing/TestimonialsSection';
import { OurStorySection } from '@/components/landing/OurStorySection';
import { UniqueDataSection } from '@/components/landing/UniqueDataSection';
import { MarketEdgeSection } from '@/components/landing/MarketEdgeSection';
import { PricingSection } from '@/components/landing/PricingSection';
import { FAQSection } from '@/components/landing/FAQSection';
import { Navigation } from '@/components/ui/Navigation';
import { AuthModalsProvider } from '@/components/auth/AuthModalsProvider';

export default function LandingPage() {
  return (
    <AuthModalsProvider>
      <div 
        className="min-h-screen relative"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed',
          backgroundColor: '#000000'
        }}
      >
        {/* Overlay to ensure content is readable */}
        <div className="absolute inset-0 bg-black/20 pointer-events-none" />
        
        {/* Navigation - NOT sticky */}
        <div className="relative z-10">
          <Navigation sticky={false} />
        </div>
      
      {/* Hero Section */}
      <div className="relative z-10">
        <HeroSection />
      </div>
      
      {/* Chrome Extension Section */}
      <div className="relative z-10">
        <ChromeExtensionSection />
      </div>
      
      {/* Testimonials Section */}
      <div className="relative z-10">
        <TestimonialsSection />
      </div>
      
      {/* Our Story Section */}
      <div className="relative z-10">
        <OurStorySection />
      </div>
      
      {/* Unique Data Section */}
      <div className="relative z-10">
        <UniqueDataSection />
      </div>
      
      {/* Market Edge Section */}
      <div className="relative z-10">
        <MarketEdgeSection />
      </div>
      
      {/* Pricing Section */}
      <div className="relative z-10">
        <PricingSection />
      </div>
      
      {/* FAQ Section */}
      <div className="relative z-10">
        <FAQSection />
      </div>
      </div>
    </AuthModalsProvider>
  );
}


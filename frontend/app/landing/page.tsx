/**
 * Landing Page
 * Main marketing page for BoosterBoxPro (sign in / sign up only).
 * Signed-in users are redirected to the dashboard.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
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
import { getAuthToken } from '@/lib/api/client';

export default function LandingPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      router.replace('/dashboard');
      return;
    }
    setChecking(false);
  }, [router]);

  if (checking) {
    return (
      <div
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundColor: '#000000',
        }}
      >
        <div className="text-center relative z-10">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4" />
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

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

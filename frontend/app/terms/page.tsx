import { Navigation } from '@/components/ui/Navigation';
import Footer from '@/components/ui/Footer';

export const metadata = {
  title: 'Terms of Service | BoosterBoxPro',
  description: 'Terms of Service for the BoosterBoxPro platform.',
};

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navigation />

      <main className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <h1 className="text-3xl sm:text-4xl font-bold text-white/90 mb-2">
          Terms of Service
        </h1>
        <p className="text-sm text-white/40 mb-12">
          Last updated: January 31, 2026
        </p>

        <div className="space-y-10 text-white/60 text-sm leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              1. Acceptance of Terms
            </h2>
            <p>
              By accessing or using the BoosterBoxPro platform, website, Chrome
              extension, and related services (collectively, the
              &ldquo;Service&rdquo;), you agree to be bound by these Terms of
              Service (&ldquo;Terms&rdquo;). If you do not agree to these
              Terms, you may not use the Service.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              2. Description of Service
            </h2>
            <p>
              BoosterBoxPro provides market intelligence and analytics for
              sealed Trading Card Game (TCG) booster boxes, with a current
              focus on One Piece TCG products. The Service aggregates publicly
              available market data&mdash;including floor prices, sales volume,
              active listings, and historical trends&mdash;to help collectors
              and investors make informed decisions.
            </p>
            <p className="mt-3">
              The Service includes a web-based dashboard, API endpoints, and a
              Chrome browser extension that overlays market data on supported
              marketplace websites.
            </p>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              3. User Accounts
            </h2>
            <p>
              To access certain features of the Service, you must create an
              account by providing a valid email address and a secure password.
              You are responsible for maintaining the confidentiality of your
              account credentials and for all activity that occurs under your
              account.
            </p>
            <p className="mt-3">
              You agree to provide accurate and complete information during
              registration and to update your information as necessary. You must
              notify us immediately if you become aware of any unauthorized use
              of your account.
            </p>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              4. Subscription &amp; Billing
            </h2>
            <p>
              BoosterBoxPro offers a free trial period of seven (7) days. After
              the trial expires, continued access to premium features requires
              an active paid subscription. Subscription plans, pricing, and
              features are described on our Pricing page and may be updated from
              time to time.
            </p>
            <p className="mt-3">
              Payments are processed securely through Stripe. By subscribing,
              you authorize us to charge the payment method on file on a
              recurring basis until you cancel. You may cancel your subscription
              at any time from your Account page; cancellation takes effect at
              the end of the current billing period.
            </p>
            <p className="mt-3">
              We do not store your full credit card number. All payment
              information is handled directly by Stripe in accordance with PCI
              DSS standards.
            </p>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              5. Data Accuracy &amp; Disclaimer
            </h2>
            <p>
              The market data, analytics, projections, and metrics provided by
              the Service are for <strong className="text-white/80">informational purposes only</strong> and
              do not constitute financial, investment, or trading advice.
            </p>
            <p className="mt-3">
              While we strive to provide accurate and up-to-date information,
              we make no warranties or representations regarding the accuracy,
              completeness, or timeliness of the data. Market conditions change
              rapidly and past performance is not indicative of future results.
              You are solely responsible for your own purchasing and investment
              decisions.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              6. Intellectual Property
            </h2>
            <p>
              All content, features, and functionality of the Service&mdash;including
              but not limited to text, graphics, logos, icons, data compilations,
              software, and analytics methodologies&mdash;are the exclusive
              property of BoosterBoxPro and are protected by copyright,
              trademark, and other intellectual property laws.
            </p>
            <p className="mt-3">
              You may not reproduce, distribute, modify, create derivative works
              of, publicly display, or commercially exploit any part of the
              Service without our prior written consent.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              7. Acceptable Use
            </h2>
            <p>You agree not to:</p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/50">
              <li>Use the Service for any unlawful purpose</li>
              <li>Attempt to reverse-engineer, scrape, or extract data from the Service programmatically without authorization</li>
              <li>Interfere with or disrupt the Service or its infrastructure</li>
              <li>Share your account credentials with third parties</li>
              <li>Resell, redistribute, or commercially exploit data obtained from the Service</li>
            </ul>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              8. Limitation of Liability
            </h2>
            <p>
              To the fullest extent permitted by law, BoosterBoxPro and its
              officers, directors, employees, and agents shall not be liable for
              any indirect, incidental, special, consequential, or punitive
              damages arising out of or related to your use of the Service,
              including but not limited to loss of profits, data, or other
              intangible losses.
            </p>
            <p className="mt-3">
              Our total liability for any claim arising from the Service shall
              not exceed the amount you paid us in the twelve (12) months
              preceding the claim.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              9. Termination
            </h2>
            <p>
              We reserve the right to suspend or terminate your account at any
              time, with or without notice, for conduct that we determine
              violates these Terms or is harmful to other users, us, or third
              parties. Upon termination, your right to use the Service ceases
              immediately.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              10. Changes to These Terms
            </h2>
            <p>
              We may update these Terms from time to time. When we make material
              changes, we will notify you by updating the &ldquo;Last
              updated&rdquo; date at the top of this page and, where
              appropriate, by email. Your continued use of the Service after
              changes are posted constitutes your acceptance of the updated
              Terms.
            </p>
          </section>

          {/* 11 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              11. Governing Law
            </h2>
            <p>
              These Terms shall be governed by and construed in accordance with
              the laws of the United States. Any disputes arising from these
              Terms or the Service shall be resolved in the courts of
              competent jurisdiction.
            </p>
          </section>

          {/* 12 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              12. Contact
            </h2>
            <p>
              If you have questions about these Terms, please contact us at{' '}
              <a
                href="mailto:support@boosterboxpro.com"
                className="text-red-400 hover:text-red-300 underline underline-offset-2"
              >
                support@boosterboxpro.com
              </a>
              .
            </p>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}

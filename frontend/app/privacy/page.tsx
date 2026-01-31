import Navigation from '@/components/ui/Navigation';
import Footer from '@/components/ui/Footer';

export const metadata = {
  title: 'Privacy Policy | BoosterBoxPro',
  description: 'Privacy Policy for the BoosterBoxPro platform.',
};

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navigation />

      <main className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <h1 className="text-3xl sm:text-4xl font-bold text-white/90 mb-2">
          Privacy Policy
        </h1>
        <p className="text-sm text-white/40 mb-12">
          Last updated: January 31, 2026
        </p>

        <div className="space-y-10 text-white/60 text-sm leading-relaxed">
          {/* 1 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              1. Introduction
            </h2>
            <p>
              BoosterBoxPro (&ldquo;we,&rdquo; &ldquo;us,&rdquo; or
              &ldquo;our&rdquo;) is committed to protecting your privacy. This
              Privacy Policy explains how we collect, use, disclose, and
              safeguard your information when you use the BoosterBoxPro
              platform, website, Chrome extension, and related services
              (collectively, the &ldquo;Service&rdquo;).
            </p>
            <p className="mt-3">
              By using the Service, you consent to the data practices described
              in this policy. If you do not agree with this policy, please do
              not use the Service.
            </p>
          </section>

          {/* 2 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              2. Information We Collect
            </h2>
            <p className="font-medium text-white/80 mt-2">
              Account Information
            </p>
            <p className="mt-1">
              When you create an account, we collect your email address and a
              securely hashed version of your password. We do not store
              plaintext passwords.
            </p>

            <p className="font-medium text-white/80 mt-4">
              Billing Information
            </p>
            <p className="mt-1">
              If you subscribe to a paid plan, payment information (such as
              credit card details) is collected and processed directly by our
              payment processor, Stripe. We do not store your full credit card
              number. We may receive limited billing details from Stripe, such
              as the last four digits of your card, card brand, and billing
              address, to display on your account page.
            </p>

            <p className="font-medium text-white/80 mt-4">
              Usage Data
            </p>
            <p className="mt-1">
              We automatically collect certain information when you interact
              with the Service, including pages visited, features used, browser
              type, device information, and timestamps. This data helps us
              understand how the Service is used and improve performance.
            </p>

            <p className="font-medium text-white/80 mt-4">
              Chrome Extension Data
            </p>
            <p className="mt-1">
              The BoosterBoxPro Chrome extension reads product page URLs on
              supported marketplace websites (e.g., TCGplayer) to identify
              booster box listings and overlay market data. The extension does
              not collect, transmit, or store your browsing history, personal
              data, or activity on non-supported websites.
            </p>
          </section>

          {/* 3 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              3. How We Use Your Information
            </h2>
            <p>We use the information we collect to:</p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/50">
              <li>Provide, operate, and maintain the Service</li>
              <li>Process payments and manage subscriptions</li>
              <li>Authenticate your identity and secure your account</li>
              <li>Communicate with you about your account, updates, and support requests</li>
              <li>Analyze usage patterns to improve the Service</li>
              <li>Detect and prevent fraud or abuse</li>
            </ul>
          </section>

          {/* 4 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              4. Data Sharing &amp; Disclosure
            </h2>
            <p>
              We do not sell, rent, or trade your personal information to third
              parties. We may share information only in the following
              circumstances:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/50">
              <li>
                <strong className="text-white/70">Payment Processing:</strong>{' '}
                Billing information is shared with Stripe to process payments
                securely.
              </li>
              <li>
                <strong className="text-white/70">Legal Requirements:</strong>{' '}
                We may disclose information if required by law, regulation, or
                legal process.
              </li>
              <li>
                <strong className="text-white/70">Protection of Rights:</strong>{' '}
                We may share information to protect the rights, safety, or
                property of BoosterBoxPro, our users, or the public.
              </li>
            </ul>
          </section>

          {/* 5 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              5. Data Storage &amp; Security
            </h2>
            <p>
              Your data is stored securely using industry-standard practices.
              Passwords are hashed using bcrypt before storage. Authentication
              is handled via JSON Web Tokens (JWT) transmitted over HTTPS.
              Our database infrastructure is hosted on Supabase with
              row-level security policies and encrypted connections.
            </p>
            <p className="mt-3">
              While we implement reasonable security measures, no method of
              electronic storage or transmission is 100% secure. We cannot
              guarantee absolute security of your data.
            </p>
          </section>

          {/* 6 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              6. Cookies &amp; Local Storage
            </h2>
            <p>
              The BoosterBoxPro website uses cookies and local storage to
              maintain your authentication session and remember your
              preferences. The Chrome extension uses{' '}
              <code className="text-white/70 bg-white/5 px-1.5 py-0.5 rounded text-xs">
                chrome.storage
              </code>{' '}
              APIs to store your authentication token and extension settings
              locally on your device.
            </p>
            <p className="mt-3">
              We do not use third-party tracking cookies or advertising
              cookies.
            </p>
          </section>

          {/* 7 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              7. Third-Party Services
            </h2>
            <p>
              The Service integrates with the following third-party services:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/50">
              <li>
                <strong className="text-white/70">Stripe</strong> &mdash; for
                payment processing and subscription management
              </li>
              <li>
                <strong className="text-white/70">Supabase</strong> &mdash; for
                database hosting and authentication infrastructure
              </li>
              <li>
                <strong className="text-white/70">TCGplayer</strong> &mdash; as
                a source of publicly available market data for TCG products
              </li>
            </ul>
            <p className="mt-3">
              Each third-party service operates under its own privacy policy.
              We encourage you to review their respective policies.
            </p>
          </section>

          {/* 8 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              8. Your Rights
            </h2>
            <p>You have the right to:</p>
            <ul className="list-disc list-inside mt-2 space-y-1 text-white/50">
              <li>Access the personal information we hold about you</li>
              <li>Request correction of inaccurate information</li>
              <li>Request deletion of your account and associated data</li>
              <li>Export your data in a portable format</li>
              <li>Withdraw consent for data processing at any time</li>
            </ul>
            <p className="mt-3">
              To exercise any of these rights, please contact us at{' '}
              <a
                href="mailto:support@boosterboxpro.com"
                className="text-red-400 hover:text-red-300 underline underline-offset-2"
              >
                support@boosterboxpro.com
              </a>
              . We will respond to your request within 30 days.
            </p>
          </section>

          {/* 9 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              9. Children&rsquo;s Privacy
            </h2>
            <p>
              The Service is not intended for individuals under the age of 13.
              We do not knowingly collect personal information from children
              under 13. If we become aware that we have collected such
              information, we will take steps to delete it promptly.
            </p>
          </section>

          {/* 10 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              10. Data Retention
            </h2>
            <p>
              We retain your personal information for as long as your account
              is active or as needed to provide the Service. If you delete your
              account, we will remove your personal data within 30 days, except
              where retention is required by law or for legitimate business
              purposes (such as resolving disputes or enforcing agreements).
            </p>
          </section>

          {/* 11 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              11. Changes to This Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time. When we make
              material changes, we will notify you by updating the &ldquo;Last
              updated&rdquo; date at the top of this page and, where
              appropriate, by email. Your continued use of the Service after
              changes are posted constitutes your acceptance of the updated
              policy.
            </p>
          </section>

          {/* 12 */}
          <section>
            <h2 className="text-lg font-semibold text-white/90 mb-3">
              12. Contact
            </h2>
            <p>
              If you have questions about this Privacy Policy or our data
              practices, please contact us at{' '}
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

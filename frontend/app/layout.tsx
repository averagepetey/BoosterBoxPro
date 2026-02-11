import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { PostHogProvider } from "@/components/providers/PostHogProvider";
import { PostHogPageView } from "@/components/providers/PostHogPageView";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { AuthModalsProvider } from "@/components/auth/AuthModalsProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BoosterBox Pro",
  description: "Track the top performing TCG booster boxes",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <PostHogProvider>
          <PostHogPageView />
          <ErrorBoundary>
            <QueryProvider>
              <AuthModalsProvider>
                {children}
              </AuthModalsProvider>
            </QueryProvider>
          </ErrorBoundary>
        </PostHogProvider>
      </body>
    </html>
  );
}

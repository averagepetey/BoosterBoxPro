/**
 * Releases Listing Page
 * Shows all new release articles
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { NewReleaseArticle, NewReleases } from '@/components/leaderboard/NewReleases';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

const mockNewReleases: NewReleaseArticle[] = [
  {
    id: '1',
    title: 'Is OP-14 A GOOD or BAD Investment? | One Piece TCG: Market Deep Dive',
    set_name: 'One Piece TCG',
    set_code: 'OP-14',
    release_date: '2026-01-30',
    excerpt: 'Deep dive into OP-14 investment potential and market analysis.',
    youtube_url: 'https://www.youtube.com/watch?v=iduWQenG0sk',
    game_type: 'One Piece',
    author: 'Treasure Theory',
  },
  {
    id: '2',
    title: 'The One Piece Market Keeps Reaching New Highs',
    set_name: 'One Piece TCG',
    set_code: 'MARKET',
    release_date: '2026-01-28',
    excerpt: 'The One Piece TCG market continues its upward trend with record-breaking prices.',
    youtube_url: 'https://www.youtube.com/watch?v=V9IjBRhpen8',
    game_type: 'One Piece',
    author: 'Straw Hat Speculator',
  },
  {
    id: '3',
    title: 'Ok Now This Is Getting Insane, OP13 Is $700?!',
    set_name: 'One Piece TCG',
    set_code: 'OP-13',
    release_date: '2026-01-25',
    excerpt: 'OP-13 booster box prices have skyrocketed to $700 — breaking down why.',
    youtube_url: 'https://www.youtube.com/watch?v=GlDJKnF7GV8',
    game_type: 'One Piece',
    author: "Sam's Pirated Stocks",
  },
  {
    id: '4',
    title: 'EB-03 Is About To TEST One Piece Collectors | One Piece TCG Market Watch',
    set_name: 'One Piece TCG',
    set_code: 'EB-03',
    release_date: '2026-01-22',
    excerpt: 'EB-03 is coming and it could shake up the collector market significantly.',
    youtube_url: 'https://www.youtube.com/watch?v=8Br85Z6dBto',
    game_type: 'One Piece',
    author: 'Kaizoku Ice TCG',
  },
  {
    id: '5',
    title: 'Bandai, we need to talk. | Ep 16 | Buds Watch (One Piece TCG)',
    set_name: 'One Piece TCG',
    set_code: 'TALK',
    release_date: '2026-01-20',
    excerpt: "A candid discussion about Bandai's recent decisions and their impact on the TCG market.",
    youtube_url: 'https://www.youtube.com/watch?v=yaBXoTsIEoo',
    game_type: 'One Piece',
    author: 'TCG Buds',
  },
  {
    id: '6',
    title: "OP14 Prices Don't Make Sense! — Here's Why I'm Waiting | One Piece TCG",
    set_name: 'One Piece TCG',
    set_code: 'OP-14',
    release_date: '2026-01-18',
    excerpt: 'Breaking down why current OP-14 pricing may not be sustainable.',
    youtube_url: 'https://www.youtube.com/watch?v=pdpIrmOkBpI',
    game_type: 'One Piece',
    author: 'Daily Dose Of TCG',
  },
];

export default function ReleasesPage() {
  const [articles, setArticles] = useState<NewReleaseArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setArticles(mockNewReleases);
    setIsLoading(false);
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen lb-page">
        <div className="container mx-auto px-4 sm:px-6 py-6 sm:py-8" style={{ maxWidth: '1400px' }}>
          {/* Header */}
          <div className="mb-6 sm:mb-8">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-4 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Dashboard
            </Link>
            <h1 className="text-2xl sm:text-3xl font-bold text-white">New Releases</h1>
            <p className="text-white/70 mt-2">Stay updated on the latest TCG set releases and announcements</p>
          </div>

          {/* Articles Grid */}
          {isLoading ? (
            <div className="text-center text-white py-12">Loading articles...</div>
          ) : articles.length === 0 ? (
            <div className="text-center text-white/70 py-12">No articles available</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {articles.map((article) => (
                <Link
                  key={article.id}
                  href={`/releases/${article.id}`}
                  className="block group"
                >
                  <div
                    className="rounded-2xl overflow-hidden transition-all duration-300 h-full"
                    style={{
                      boxShadow: '0 0 20px rgba(255, 255, 255, 0.6), 0 0 40px rgba(255, 255, 255, 0.4), 0 0 60px rgba(255, 255, 255, 0.2), 0 30px 80px rgba(0,0,0,0.2)',
                      background: '#141414',
                      border: '1px solid rgba(255, 255, 255, 0.15)',
                    }}
                  >
                    {/* Article Preview - Same as NewReleases component */}
                    <div className="p-4 sm:p-6">
                      {/* Set Code Badge */}
                      <div className="mb-3">
                        <div className="inline-block px-2.5 py-1 rounded-full bg-gradient-to-r from-[#F4BC53] to-[#F4343F] border border-white/20 backdrop-blur-sm">
                          <span className="text-[#1b1b1b] text-xs font-bold">{article.set_code}</span>
                        </div>
                      </div>

                      {/* Title */}
                      <h3 className="text-lg sm:text-xl font-bold text-white mb-2 line-clamp-2 group-hover:text-white/90 transition-colors">
                        {article.title}
                      </h3>

                      {article.set_name && (
                        <p className="text-sm text-white/60 mb-3">
                          {article.set_name}
                        </p>
                      )}

                      {/* Excerpt */}
                      <p className="text-sm text-white/70 line-clamp-3 mb-4">
                        {article.excerpt}
                      </p>

                      {/* Meta Information */}
                      <div className="flex items-center justify-between pt-4 border-t border-white/10">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-white/60">Release:</span>
                            <span className="text-xs font-semibold text-white">
                              {new Date(article.release_date).toLocaleDateString('en-US', { 
                                month: 'short', 
                                day: 'numeric', 
                                year: 'numeric' 
                              })}
                            </span>
                          </div>
                          {article.author && (
                            <span className="text-xs text-white/50">
                              By {article.author}
                            </span>
                          )}
                        </div>
                        <div className="text-white/60 group-hover:text-white transition-colors">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}

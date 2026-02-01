/**
 * Article Detail Page
 * Full article view for New Releases
 */

'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { NewReleaseArticle } from '@/components/leaderboard/NewReleases';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

const mockArticles: Record<string, NewReleaseArticle> = {
  '1': {
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
  '2': {
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
  '3': {
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
  '4': {
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
  '5': {
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
  '6': {
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
};

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const articleId = params?.id as string;
  const [article, setArticle] = useState<NewReleaseArticle | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (articleId && mockArticles[articleId]) {
      setArticle(mockArticles[articleId]);
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  }, [articleId]);

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
      });
    } catch {
      return dateString;
    }
  };

  const getYouTubeThumbnail = (url: string | null | undefined): string | null => {
    if (!url) return null;
    try {
      const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)?.[1];
      if (videoId) {
        return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
      }
    } catch {
      // Invalid URL
    }
    return null;
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-white">Loading article...</div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!article) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white mb-4">Article Not Found</h1>
            <Link 
              href="/dashboard"
              className="text-white/70 hover:text-white underline"
            >
              Return to Dashboard
            </Link>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  const thumbnailUrl = getYouTubeThumbnail(article.youtube_url);

  return (
    <ProtectedRoute>
      <div className="min-h-screen lb-page">
        <div className="container mx-auto px-4 sm:px-6 py-6 sm:py-8" style={{ maxWidth: '900px' }}>
          {/* Back Button */}
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 text-white/80 hover:text-white mb-6 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </Link>

          {/* Article Container */}
          <div
            className="rounded-3xl overflow-hidden"
            style={{
              boxShadow: '0 0 20px rgba(255, 255, 255, 0.6), 0 0 40px rgba(255, 255, 255, 0.4), 0 0 60px rgba(255, 255, 255, 0.2), 0 30px 80px rgba(0,0,0,0.2)',
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
            }}
          >
            {/* Header Image */}
            {thumbnailUrl && (
              <div className="relative w-full h-64 sm:h-80">
                <img
                  src={thumbnailUrl}
                  alt={article.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/50 to-transparent" />
                
                {/* Set Code Badge */}
                <div className="absolute top-4 right-4 z-10">
                  <div className="px-3 py-1.5 rounded-full bg-gradient-to-r from-[#F4BC53] to-[#F4343F] border border-white/20 backdrop-blur-sm">
                    <span className="text-[#1b1b1b] text-sm font-bold">{article.set_code}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Article Content */}
            <div className="p-6 sm:p-8">
              {/* Title and Meta */}
              <div className="mb-6">
                <h1 className="text-2xl sm:text-3xl font-bold text-white mb-3">
                  {article.title}
                </h1>
                
                {article.set_name && (
                  <p className="text-lg text-white/70 mb-4">
                    {article.set_name}
                  </p>
                )}

                {/* Meta Information */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-white/60">
                  {article.author && (
                    <div className="flex items-center gap-2">
                      <span>By</span>
                      <span className="text-white/80 font-medium">{article.author}</span>
                    </div>
                  )}
                  {article.published_date && (
                    <div className="flex items-center gap-2">
                      <span>Published</span>
                      <span className="text-white/80">{formatDate(article.published_date)}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <span>Release Date</span>
                    <span className="text-white/80 font-medium">{formatDate(article.release_date)}</span>
                  </div>
                  {article.game_type && (
                    <div className="px-2 py-1 rounded bg-white/10 text-white/80 text-xs">
                      {article.game_type}
                    </div>
                  )}
                </div>
              </div>

              {/* YouTube Video Link */}
              {article.youtube_url && (
                <div className="mb-6">
                  <a
                    href={article.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-3 px-4 py-3 rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-600/30 transition-colors group"
                  >
                    <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                      <svg className="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-white font-semibold">Watch on YouTube</div>
                      <div className="text-white/70 text-sm">View the full video analysis</div>
                    </div>
                    <svg className="w-5 h-5 text-white/70 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              )}

              {/* Article Excerpt */}
              <div className="mb-6 p-4 rounded-lg bg-white/5 border border-white/10">
                <p className="text-white/90 text-lg leading-relaxed">
                  {article.excerpt}
                </p>
              </div>

              {/* Footer Actions */}
              <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row gap-4">
                <Link
                  href="/dashboard"
                  className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors text-center"
                >
                  Back to Dashboard
                </Link>
                {article.youtube_url && (
                  <a
                    href={article.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-600/30 text-white transition-colors text-center"
                  >
                    Watch Video
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

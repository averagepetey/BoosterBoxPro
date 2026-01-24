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

// Mock data - will be replaced with API call
const mockArticles: Record<string, NewReleaseArticle> = {
  '6': {
    id: '6',
    title: 'TCG Market Update',
    set_name: 'Market Analysis',
    set_code: 'UPDATE',
    release_date: '2026-01-04',
    excerpt: 'Latest market trends and insights for TCG collectors.',
    youtube_url: 'https://www.youtube.com/watch?v=f_2fgWeN8e4',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2026-01-04',
    image_url: null,
  },
  '5': {
    id: '5',
    title: 'Latest TCG Release Analysis',
    set_name: 'New Set Review',
    set_code: 'NEW',
    release_date: '2026-01-04',
    excerpt: 'In-depth analysis and review of the latest TCG release.',
    youtube_url: 'https://www.youtube.com/watch?v=QkS6Llq4Y6Y',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2026-01-04',
    image_url: null,
  },
  '1': {
    id: '1',
    title: 'OP-14: The Next Big Set',
    set_name: 'The Next Adventure',
    set_code: 'OP-14',
    release_date: '2025-02-15',
    excerpt: 'Get ready for the latest One Piece set featuring new characters and powerful cards.',
    youtube_url: 'https://www.youtube.com/watch?v=67ueP4okd9I&t=4414s',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2025-01-10',
    image_url: null,
  },
  '2': {
    id: '2',
    title: 'EB-02: Expansion Announcement',
    set_name: 'Eastern Blue Expansion',
    set_code: 'EB-02',
    release_date: '2025-03-01',
    excerpt: 'The Eastern Blue saga continues with this exciting new expansion set.',
    youtube_url: 'https://www.youtube.com/watch?v=example2',
    game_type: 'One Piece',
    author: 'Card Collector',
    published_date: '2025-01-08',
    image_url: null,
  },
  '3': {
    id: '3',
    title: 'PRB-02: Premium Release',
    set_name: 'Premium Booster',
    set_code: 'PRB-02',
    release_date: '2025-02-28',
    excerpt: 'Premium booster box with exclusive cards and special artwork.',
    youtube_url: 'https://www.youtube.com/watch?v=example3',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2025-01-05',
    image_url: null,
  },
  '4': {
    id: '4',
    title: 'Set Review: OP-13 Analysis',
    set_name: 'Carrying on His Will',
    set_code: 'OP-13',
    release_date: '2024-12-01',
    excerpt: 'Deep dive into the OP-13 set mechanics and meta implications.',
    youtube_url: 'https://www.youtube.com/watch?v=example4',
    game_type: 'One Piece',
    author: 'Meta Analyst',
    published_date: '2024-12-15',
    image_url: null,
  },
};

// Extended article content (full article text)
const mockArticleContent: Record<string, string> = {
  '1': `
    <h2>Introduction</h2>
    <p>The One Piece TCG community is buzzing with excitement as we approach the release of OP-14: The Next Adventure. This highly anticipated set promises to shake up the meta with new mechanics and powerful cards.</p>
    
    <h2>New Mechanics</h2>
    <p>OP-14 introduces several innovative mechanics that will change how players approach deck building. The new "Adventure" keyword allows players to explore different paths during gameplay, creating more strategic depth.</p>
    
    <h2>Key Cards</h2>
    <p>Several standout cards have been revealed, including powerful leaders and game-changing events. The set features new artwork from the latest One Piece arcs, making it a must-have for collectors.</p>
    
    <h2>Meta Implications</h2>
    <p>Early analysis suggests this set will significantly impact the competitive scene. Players should prepare for new strategies and counter-plays as the meta evolves.</p>
    
    <h2>Release Information</h2>
    <p>OP-14: The Next Adventure releases on February 15, 2025. Pre-orders are now available at participating retailers.</p>
  `,
  '2': `
    <h2>Eastern Blue Expansion</h2>
    <p>The Eastern Blue saga continues with EB-02, bringing new characters and story elements from this iconic arc.</p>
    
    <h2>What to Expect</h2>
    <p>This expansion focuses on the early adventures of the Straw Hat Pirates, featuring nostalgic cards and powerful new abilities.</p>
  `,
  '3': `
    <h2>Premium Booster Box</h2>
    <p>PRB-02 offers collectors and players exclusive cards with special artwork and enhanced rarity.</p>
    
    <h2>Exclusive Content</h2>
    <p>This premium release includes alternate art cards and special promotional materials not available in standard sets.</p>
  `,
  '4': `
    <h2>OP-13 Set Review</h2>
    <p>Now that OP-13 has been in circulation, we can provide a comprehensive analysis of its impact on the meta.</p>
    
    <h2>Performance Analysis</h2>
    <p>The set has proven to be highly competitive, with several cards becoming staples in top-tier decks.</p>
    
    <h2>Future Outlook</h2>
    <p>As we look ahead to future sets, OP-13's influence will continue to shape deck building strategies.</p>
  `,
};

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const articleId = params?.id as string;
  const [article, setArticle] = useState<NewReleaseArticle | null>(null);
  const [content, setContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with API call
    if (articleId && mockArticles[articleId]) {
      setArticle(mockArticles[articleId]);
      setContent(mockArticleContent[articleId] || '');
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

              {/* Full Article Content */}
              {content && (
                <div 
                  className="article-content"
                  style={{
                    color: 'rgba(255, 255, 255, 0.9)',
                    lineHeight: '1.8',
                  }}
                  dangerouslySetInnerHTML={{ __html: content }}
                />
              )}

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

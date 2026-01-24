

 * Shows all new release articles
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { NewReleaseArticle, NewReleases } from '@/components/leaderboard/NewReleases';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Mock data - will be replaced with API call
const mockNewReleases: NewReleaseArticle[] = [
  {
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
  {
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
  {
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
  {
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
  {
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
  {
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
];

export default function ReleasesPage() {
  const [articles, setArticles] = useState<NewReleaseArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with API call
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



 * Shows all new release articles
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { NewReleaseArticle, NewReleases } from '@/components/leaderboard/NewReleases';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Mock data - will be replaced with API call
const mockNewReleases: NewReleaseArticle[] = [
  {
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
  {
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
  {
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
  {
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
  {
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
  {
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
];

export default function ReleasesPage() {
  const [articles, setArticles] = useState<NewReleaseArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with API call
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



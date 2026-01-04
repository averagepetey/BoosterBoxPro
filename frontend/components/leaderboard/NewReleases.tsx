/**
 * New Releases Component
 * Horizontal scrolling container with articles and insights about new releases
 * Includes links to YouTube videos
 */

'use client';

import Link from 'next/link';
import { useState } from 'react';

export interface NewReleaseArticle {
  id: string;
  title: string;
  set_name: string;
  set_code: string; // e.g., "OP-14"
  release_date: string; // ISO date string
  image_url?: string | null;
  excerpt: string;
  youtube_url?: string | null;
  article_url?: string; // Link to full article if available
  game_type?: string;
  author?: string;
  published_date?: string;
}

interface NewReleasesProps {
  articles?: NewReleaseArticle[];
}

// Mock data for new releases - will be replaced with API data later
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
  },
];

export function NewReleases({ articles = mockNewReleases }: NewReleasesProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = date.getTime() - now.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays < 0) {
        return `Released ${Math.abs(diffDays)} days ago`;
      } else if (diffDays === 0) {
        return 'Releasing today!';
      } else if (diffDays === 1) {
        return 'Releasing tomorrow';
      } else if (diffDays <= 7) {
        return `Releasing in ${diffDays} days`;
      } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      }
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

  if (articles.length === 0) {
    return null;
  }

  return (
    <div className="mb-4 sm:mb-6">
      <div className="flex items-center justify-between mb-3 sm:mb-4">
        <h2 className="text-base sm:text-lg font-semibold text-white">New Releases</h2>
        <Link
          href="/releases"
          className="text-xs sm:text-sm text-white/85 hover:text-white transition-all hover:translate-x-1 flex items-center gap-1 min-h-[44px] px-2"
        >
          See all
          <span className="text-lg">→</span>
        </Link>
      </div>
      
      {/* Single Container with Horizontal Scroll */}
      <div 
        className="overflow-x-auto scrollbar-hide rounded-2xl"
        style={{
          boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)',
          background: '#141414',
          border: '1px solid rgba(255, 255, 255, 0.15)',
        }}
      >
        <div className="flex gap-4 p-4" style={{ width: 'max-content' }}>
          {articles.map((article, index) => {
            const thumbnailUrl = getYouTubeThumbnail(article.youtube_url);
            
            return (
              <div
                key={article.id}
                className="group flex-shrink-0 w-[320px] sm:w-[380px]"
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <Link
                  href={`/releases/${article.id}`}
                  className="block"
                >
                  <div
                    className={`relative transition-all duration-300 min-h-[280px] sm:min-h-[320px] ${
                      hoveredIndex === index
                        ? 'scale-[1.02]'
                        : ''
                    }`}
                  >
                    {/* Set Code Badge */}
                    <div className="absolute top-3 right-3 z-10">
                      <div className="px-2.5 py-1 rounded-full bg-gradient-to-r from-[#F4BC53] to-[#F4343F] border border-white/20 backdrop-blur-sm">
                        <span className="text-[#1b1b1b] text-xs font-bold">{article.set_code}</span>
                      </div>
                    </div>

                    {/* YouTube Thumbnail or Placeholder */}
                    <div className="mb-3 relative">
                      {thumbnailUrl ? (
                        <div className="relative">
                          <img
                            src={thumbnailUrl}
                            alt={article.title}
                            className="w-full h-40 sm:h-48 object-cover rounded-lg"
                            onError={(e) => {
                              // Fallback if thumbnail fails to load
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                          {/* YouTube Play Button Overlay */}
                          {article.youtube_url && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/30 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                              <div className="w-16 h-16 rounded-full bg-red-600/90 flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform">
                                <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M8 5v14l11-7z" />
                                </svg>
                              </div>
                            </div>
                          )}
                        </div>
                      ) : article.image_url ? (
                        <img
                          src={article.image_url}
                          alt={article.title}
                          className="w-full h-40 sm:h-48 object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-full h-40 sm:h-48 bg-gradient-to-br from-blue-600/20 to-purple-600/20 flex items-center justify-center rounded-lg border border-white/10">
                          <div className="text-center">
                            <div className="text-4xl mb-2">📦</div>
                            <div className="text-white/60 text-xs font-medium">{article.set_code}</div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Article Content */}
                    <div className="space-y-2">
                      <div>
                        <h3 className="text-sm sm:text-base font-bold text-white mb-1 line-clamp-2">
                          {article.title}
                        </h3>
                        {article.set_name && (
                          <p className="text-xs text-white/60 mb-2">
                            {article.set_name}
                          </p>
                        )}
                      </div>

                      <p className="text-xs sm:text-sm text-white/70 line-clamp-2 mb-3">
                        {article.excerpt}
                      </p>

                      {/* Meta Information */}
                      <div className="flex items-center justify-between pt-2 border-t border-white/10">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-white/60">Release:</span>
                            <span className="text-xs font-semibold text-white">
                              {formatDate(article.release_date)}
                            </span>
                          </div>
                          {article.author && (
                            <span className="text-xs text-white/50">
                              By {article.author}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Hover Indicator */}
                    {hoveredIndex === index && (
                      <div className="absolute bottom-3 right-3">
                        <div className="px-2 py-1 rounded bg-white/10 backdrop-blur-sm">
                          <span className="text-white text-xs font-medium">
                            Read More →
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </Link>
                
                {/* YouTube Link Button - Separate from card link */}
                {article.youtube_url && (
                  <a
                    href={article.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="mt-2 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-600/20 hover:bg-red-600/30 border border-red-600/30 transition-colors text-white text-sm font-medium"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                    </svg>
                    Watch Video
                  </a>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

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
    id: '7',
    title: 'TCG Market Analysis',
    set_name: 'Market Insights',
    set_code: 'ANALYSIS',
    release_date: '2026-01-05',
    excerpt: 'Comprehensive market analysis and trends for TCG collectors.',
    youtube_url: 'https://www.youtube.com/watch?v=rUu_WpCVGxQ',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2026-01-05',
  },
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
      <div className="flex items-center justify-between mb-1 sm:mb-2">
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
        className="overflow-x-auto scrollbar-hide rounded-2xl gradient-animated"
        style={{
          boxShadow: 'none',
          backgroundImage: 
            'radial-gradient(ellipse 400px 300px at 20% 30%, #73788D 0%, rgba(115, 120, 141, 0.6) 20%, rgba(115, 120, 141, 0.3) 40%, rgba(115, 120, 141, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 350px 400px at 80% 70%, #343839 0%, rgba(52, 56, 57, 0.6) 20%, rgba(52, 56, 57, 0.3) 40%, rgba(52, 56, 57, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 300px 350px at 50% 50%, #1a1a1a 0%, rgba(26, 26, 26, 0.7) 25%, rgba(26, 26, 26, 0.4) 50%, rgba(26, 26, 26, 0.2) 70%, transparent 90%),' +
            'radial-gradient(ellipse 450px 380px at 60% 25%, rgba(200, 40, 40, 0.9) 0%, rgba(200, 40, 40, 0.7) 15%, rgba(200, 40, 40, 0.5) 30%, rgba(200, 40, 40, 0.3) 45%, rgba(200, 40, 40, 0.15) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%),' +
            'radial-gradient(ellipse 320px 380px at 30% 80%, rgba(255, 165, 0, 0.5) 0%, rgba(255, 165, 0, 0.3) 25%, rgba(255, 165, 0, 0.15) 45%, rgba(255, 165, 0, 0.05) 65%, transparent 85%),' +
            'radial-gradient(ellipse 400px 350px at 85% 85%, rgba(200, 40, 40, 0.8) 0%, rgba(200, 40, 40, 0.6) 15%, rgba(200, 40, 40, 0.4) 30%, rgba(200, 40, 40, 0.2) 45%, rgba(200, 40, 40, 0.1) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%)',
          backgroundSize: '150% 150%, 120% 120%, 180% 180%, 140% 140%, 130% 130%, 145% 145%',
          backgroundPosition: '0% 0%, 100% 100%, 50% 50%, 60% 20%, 30% 80%, 85% 85%',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#2a2a2a',
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
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

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
    id: '7',
    title: 'TCG Market Analysis',
    set_name: 'Market Insights',
    set_code: 'ANALYSIS',
    release_date: '2026-01-05',
    excerpt: 'Comprehensive market analysis and trends for TCG collectors.',
    youtube_url: 'https://www.youtube.com/watch?v=rUu_WpCVGxQ',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2026-01-05',
  },
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
      <div className="flex items-center justify-between mb-1 sm:mb-2">
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
        className="overflow-x-auto scrollbar-hide rounded-2xl gradient-animated"
        style={{
          boxShadow: 'none',
          backgroundImage: 
            'radial-gradient(ellipse 400px 300px at 20% 30%, #73788D 0%, rgba(115, 120, 141, 0.6) 20%, rgba(115, 120, 141, 0.3) 40%, rgba(115, 120, 141, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 350px 400px at 80% 70%, #343839 0%, rgba(52, 56, 57, 0.6) 20%, rgba(52, 56, 57, 0.3) 40%, rgba(52, 56, 57, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 300px 350px at 50% 50%, #1a1a1a 0%, rgba(26, 26, 26, 0.7) 25%, rgba(26, 26, 26, 0.4) 50%, rgba(26, 26, 26, 0.2) 70%, transparent 90%),' +
            'radial-gradient(ellipse 450px 380px at 60% 25%, rgba(200, 40, 40, 0.9) 0%, rgba(200, 40, 40, 0.7) 15%, rgba(200, 40, 40, 0.5) 30%, rgba(200, 40, 40, 0.3) 45%, rgba(200, 40, 40, 0.15) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%),' +
            'radial-gradient(ellipse 320px 380px at 30% 80%, rgba(255, 165, 0, 0.5) 0%, rgba(255, 165, 0, 0.3) 25%, rgba(255, 165, 0, 0.15) 45%, rgba(255, 165, 0, 0.05) 65%, transparent 85%),' +
            'radial-gradient(ellipse 400px 350px at 85% 85%, rgba(200, 40, 40, 0.8) 0%, rgba(200, 40, 40, 0.6) 15%, rgba(200, 40, 40, 0.4) 30%, rgba(200, 40, 40, 0.2) 45%, rgba(200, 40, 40, 0.1) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%)',
          backgroundSize: '150% 150%, 120% 120%, 180% 180%, 140% 140%, 130% 130%, 145% 145%',
          backgroundPosition: '0% 0%, 100% 100%, 50% 50%, 60% 20%, 30% 80%, 85% 85%',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#2a2a2a',
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
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

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
    id: '7',
    title: 'TCG Market Analysis',
    set_name: 'Market Insights',
    set_code: 'ANALYSIS',
    release_date: '2026-01-05',
    excerpt: 'Comprehensive market analysis and trends for TCG collectors.',
    youtube_url: 'https://www.youtube.com/watch?v=rUu_WpCVGxQ',
    game_type: 'One Piece',
    author: 'TCG Insights',
    published_date: '2026-01-05',
  },
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
      <div className="flex items-center justify-between mb-1 sm:mb-2">
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
        className="overflow-x-auto scrollbar-hide rounded-2xl gradient-animated"
        style={{
          boxShadow: 'none',
          backgroundImage: 
            'radial-gradient(ellipse 400px 300px at 20% 30%, #73788D 0%, rgba(115, 120, 141, 0.6) 20%, rgba(115, 120, 141, 0.3) 40%, rgba(115, 120, 141, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 350px 400px at 80% 70%, #343839 0%, rgba(52, 56, 57, 0.6) 20%, rgba(52, 56, 57, 0.3) 40%, rgba(52, 56, 57, 0.1) 60%, transparent 80%),' +
            'radial-gradient(ellipse 300px 350px at 50% 50%, #1a1a1a 0%, rgba(26, 26, 26, 0.7) 25%, rgba(26, 26, 26, 0.4) 50%, rgba(26, 26, 26, 0.2) 70%, transparent 90%),' +
            'radial-gradient(ellipse 450px 380px at 60% 25%, rgba(200, 40, 40, 0.9) 0%, rgba(200, 40, 40, 0.7) 15%, rgba(200, 40, 40, 0.5) 30%, rgba(200, 40, 40, 0.3) 45%, rgba(200, 40, 40, 0.15) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%),' +
            'radial-gradient(ellipse 320px 380px at 30% 80%, rgba(255, 165, 0, 0.5) 0%, rgba(255, 165, 0, 0.3) 25%, rgba(255, 165, 0, 0.15) 45%, rgba(255, 165, 0, 0.05) 65%, transparent 85%),' +
            'radial-gradient(ellipse 400px 350px at 85% 85%, rgba(200, 40, 40, 0.8) 0%, rgba(200, 40, 40, 0.6) 15%, rgba(200, 40, 40, 0.4) 30%, rgba(200, 40, 40, 0.2) 45%, rgba(200, 40, 40, 0.1) 60%, rgba(200, 40, 40, 0.05) 75%, transparent 90%)',
          backgroundSize: '150% 150%, 120% 120%, 180% 180%, 140% 140%, 130% 130%, 145% 145%',
          backgroundPosition: '0% 0%, 100% 100%, 50% 50%, 60% 20%, 30% 80%, 85% 85%',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#2a2a2a',
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
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

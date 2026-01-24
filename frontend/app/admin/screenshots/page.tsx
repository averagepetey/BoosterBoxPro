/**
 * Admin Screenshots Page
 * Only accessible by admin users (john.petersen1818@gmail.com)
 * Provides screenshot upload and data entry tools
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Navigation } from '@/components/ui/Navigation';
import { getApiBaseUrl, getAuthToken } from '@/lib/api/client';

export default function AdminScreenshotsPage() {
  const router = useRouter();
  const { isAdmin, isLoading, user } = useAuth();
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.push('/dashboard');
    }
  }, [isAdmin, isLoading, router]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = getAuthToken();
      const apiBaseUrl = getApiBaseUrl();

      const response = await fetch(`${apiBaseUrl}/admin/screenshot/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✅ Upload successful! ${data.message || ''}`);
      } else {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        setUploadStatus(`❌ Error: ${error.detail || 'Upload failed'}`);
      }
    } catch (error: any) {
      setUploadStatus(`❌ Error: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div 
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#000000'
        }}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render for non-admin users
  if (!isAdmin) {
    return null;
  }

  return (
    <div 
      className="min-h-screen bg-black"
      style={{
        backgroundImage: 'url(/gradient2background.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundColor: '#000000'
      }}
    >
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 p-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <span className="text-4xl">📷</span>
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Tools</h1>
              <p className="text-white/60">Screenshot upload and data management</p>
            </div>
          </div>

          {/* Admin badge */}
          <div className="mb-8 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-sm">
              🔐 <strong>Admin Access:</strong> Logged in as {user?.email}
            </p>
          </div>

          {/* Screenshot Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Upload Screenshot</h2>
            <p className="text-white/60 mb-4">
              Upload screenshots from TCGplayer or eBay to extract market data.
            </p>
            
            <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-yellow-500/50 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
                id="screenshot-upload"
              />
              <label 
                htmlFor="screenshot-upload"
                className="cursor-pointer"
              >
                <div className="text-6xl mb-4">📤</div>
                <p className="text-white font-medium mb-2">
                  {isUploading ? 'Uploading...' : 'Click to upload a screenshot'}
                </p>
                <p className="text-white/50 text-sm">
                  Supports PNG, JPG, WEBP
                </p>
              </label>
            </div>

            {uploadStatus && (
              <div className={`mt-4 p-4 rounded-lg ${
                uploadStatus.includes('✅') 
                  ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                  : uploadStatus.includes('❌')
                  ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                  : 'bg-blue-500/10 border border-blue-500/30 text-blue-400'
              }`}>
                {uploadStatus}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">📊 Manual Data Entry</h3>
              <p className="text-white/60 text-sm mb-4">
                Manually enter market data for booster boxes
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
            
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">🔍 View Upload History</h3>
              <p className="text-white/60 text-sm mb-4">
                Review previously uploaded screenshots and data
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}


 * Admin Screenshots Page
 * Only accessible by admin users (john.petersen1818@gmail.com)
 * Provides screenshot upload and data entry tools
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Navigation } from '@/components/ui/Navigation';
import { getApiBaseUrl, getAuthToken } from '@/lib/api/client';

export default function AdminScreenshotsPage() {
  const router = useRouter();
  const { isAdmin, isLoading, user } = useAuth();
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.push('/dashboard');
    }
  }, [isAdmin, isLoading, router]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = getAuthToken();
      const apiBaseUrl = getApiBaseUrl();

      const response = await fetch(`${apiBaseUrl}/admin/screenshot/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✅ Upload successful! ${data.message || ''}`);
      } else {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        setUploadStatus(`❌ Error: ${error.detail || 'Upload failed'}`);
      }
    } catch (error: any) {
      setUploadStatus(`❌ Error: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div 
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#000000'
        }}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render for non-admin users
  if (!isAdmin) {
    return null;
  }

  return (
    <div 
      className="min-h-screen bg-black"
      style={{
        backgroundImage: 'url(/gradient2background.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundColor: '#000000'
      }}
    >
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 p-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <span className="text-4xl">📷</span>
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Tools</h1>
              <p className="text-white/60">Screenshot upload and data management</p>
            </div>
          </div>

          {/* Admin badge */}
          <div className="mb-8 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-sm">
              🔐 <strong>Admin Access:</strong> Logged in as {user?.email}
            </p>
          </div>

          {/* Screenshot Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Upload Screenshot</h2>
            <p className="text-white/60 mb-4">
              Upload screenshots from TCGplayer or eBay to extract market data.
            </p>
            
            <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-yellow-500/50 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
                id="screenshot-upload"
              />
              <label 
                htmlFor="screenshot-upload"
                className="cursor-pointer"
              >
                <div className="text-6xl mb-4">📤</div>
                <p className="text-white font-medium mb-2">
                  {isUploading ? 'Uploading...' : 'Click to upload a screenshot'}
                </p>
                <p className="text-white/50 text-sm">
                  Supports PNG, JPG, WEBP
                </p>
              </label>
            </div>

            {uploadStatus && (
              <div className={`mt-4 p-4 rounded-lg ${
                uploadStatus.includes('✅') 
                  ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                  : uploadStatus.includes('❌')
                  ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                  : 'bg-blue-500/10 border border-blue-500/30 text-blue-400'
              }`}>
                {uploadStatus}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">📊 Manual Data Entry</h3>
              <p className="text-white/60 text-sm mb-4">
                Manually enter market data for booster boxes
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
            
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">🔍 View Upload History</h3>
              <p className="text-white/60 text-sm mb-4">
                Review previously uploaded screenshots and data
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}


 * Admin Screenshots Page
 * Only accessible by admin users (john.petersen1818@gmail.com)
 * Provides screenshot upload and data entry tools
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Navigation } from '@/components/ui/Navigation';
import { getApiBaseUrl, getAuthToken } from '@/lib/api/client';

export default function AdminScreenshotsPage() {
  const router = useRouter();
  const { isAdmin, isLoading, user } = useAuth();
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && !isAdmin) {
      router.push('/dashboard');
    }
  }, [isAdmin, isLoading, router]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = getAuthToken();
      const apiBaseUrl = getApiBaseUrl();

      const response = await fetch(`${apiBaseUrl}/admin/screenshot/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus(`✅ Upload successful! ${data.message || ''}`);
      } else {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        setUploadStatus(`❌ Error: ${error.detail || 'Upload failed'}`);
      }
    } catch (error: any) {
      setUploadStatus(`❌ Error: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div 
        className="min-h-screen bg-black flex items-center justify-center"
        style={{
          backgroundImage: 'url(/gradient2background.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#000000'
        }}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400 mx-auto mb-4"></div>
          <p className="text-white/70">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render for non-admin users
  if (!isAdmin) {
    return null;
  }

  return (
    <div 
      className="min-h-screen bg-black"
      style={{
        backgroundImage: 'url(/gradient2background.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundColor: '#000000'
      }}
    >
      <Navigation />
      
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-black/50 backdrop-blur-md rounded-2xl border border-white/10 p-8">
          {/* Header */}
          <div className="flex items-center gap-4 mb-8">
            <span className="text-4xl">📷</span>
            <div>
              <h1 className="text-3xl font-bold text-white">Admin Tools</h1>
              <p className="text-white/60">Screenshot upload and data management</p>
            </div>
          </div>

          {/* Admin badge */}
          <div className="mb-8 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-yellow-400 text-sm">
              🔐 <strong>Admin Access:</strong> Logged in as {user?.email}
            </p>
          </div>

          {/* Screenshot Upload Section */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Upload Screenshot</h2>
            <p className="text-white/60 mb-4">
              Upload screenshots from TCGplayer or eBay to extract market data.
            </p>
            
            <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-yellow-500/50 transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
                id="screenshot-upload"
              />
              <label 
                htmlFor="screenshot-upload"
                className="cursor-pointer"
              >
                <div className="text-6xl mb-4">📤</div>
                <p className="text-white font-medium mb-2">
                  {isUploading ? 'Uploading...' : 'Click to upload a screenshot'}
                </p>
                <p className="text-white/50 text-sm">
                  Supports PNG, JPG, WEBP
                </p>
              </label>
            </div>

            {uploadStatus && (
              <div className={`mt-4 p-4 rounded-lg ${
                uploadStatus.includes('✅') 
                  ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                  : uploadStatus.includes('❌')
                  ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                  : 'bg-blue-500/10 border border-blue-500/30 text-blue-400'
              }`}>
                {uploadStatus}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">📊 Manual Data Entry</h3>
              <p className="text-white/60 text-sm mb-4">
                Manually enter market data for booster boxes
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
            
            <div className="p-6 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
              <h3 className="text-white font-semibold mb-2">🔍 View Upload History</h3>
              <p className="text-white/60 text-sm mb-4">
                Review previously uploaded screenshots and data
              </p>
              <button className="text-yellow-400 text-sm hover:text-yellow-300 transition-colors">
                Coming soon →
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}




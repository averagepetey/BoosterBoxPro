/**
 * API Route Proxy for booster-boxes
 * Proxies requests to the FastAPI backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

// Use NEXT_PUBLIC_ prefix for client-side access, or fallback to localhost
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://localhost:8000';

// Export route config to increase timeout (backend does heavy DB + historical batch)
export const maxDuration = 45; // 45 seconds max for this route

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/booster-boxes${queryString ? `?${queryString}` : ''}`;
    
    // Get authorization header from the incoming request
    const authHeader = request.headers.get('authorization');
    
    console.log('[API Proxy] Fetching from backend:', url);
    console.log('[API Proxy] BACKEND_URL:', BACKEND_URL);
    console.log('[API Proxy] Has auth header:', !!authHeader);
    
    // Add timeout to prevent hanging (45 seconds for slow backend with historical data)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.error('[API Proxy] Request timeout after 45 seconds');
      controller.abort();
    }, 45000); // 45 second timeout
    
    // Build headers for backend request
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers,
        // Don't cache - always fetch fresh data
        cache: 'no-store',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.error('[API Proxy] Backend error:', response.status, response.statusText);
        const errorText = await response.text();
        return NextResponse.json(
          { error: `Backend error: ${response.status}`, detail: errorText },
          { status: response.status }
        );
      }

      const data = await response.json();
      const duration = Date.now() - startTime;
      console.log(`[API Proxy] Got data in ${duration}ms, first box:`, data.data?.[0]?.product_name);
      
      return NextResponse.json(data);
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error('[API Proxy] Request timeout');
        return NextResponse.json(
          { error: 'Request timeout', detail: 'Backend took too long to respond' },
          { status: 504 }
        );
      }
      throw fetchError;
    }
  } catch (error: any) {
    console.error('[API Proxy] Fetch error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch from backend', 
        detail: error?.message || String(error),
        backend_url: BACKEND_URL
      },
      { status: 500 }
    );
  }
}

/**
 * API Route Proxy for box detail
 * Proxies requests to the FastAPI backend with extended timeout
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const url = `${BACKEND_URL}/booster-boxes/${id}`;
    const authHeader = request.headers.get('authorization');

    console.log('[API Proxy] Fetching box detail from backend:', url);
    
    // Use AbortController for 15 second timeout (backend can be slow)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (authHeader) headers['Authorization'] = authHeader;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
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
    console.log('[API Proxy] Got box detail for:', data.data?.product_name);
    
    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.error('[API Proxy] Request timeout for box detail');
      return NextResponse.json(
        { error: 'Request timeout', detail: 'Backend took too long to respond' },
        { status: 504 }
      );
    }
    console.error('[API Proxy] Fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: String(error) },
      { status: 500 }
    );
  }
}

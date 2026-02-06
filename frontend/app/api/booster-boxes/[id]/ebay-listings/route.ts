/**
 * API Route Proxy for eBay listings
 * Proxies requests to the FastAPI backend with auth header passthrough
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'https://boosterboxpro.onrender.com';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const searchParams = request.nextUrl.searchParams;
    const limit = searchParams.get('limit') || '25';
    const url = `${BACKEND_URL}/booster-boxes/${id}/ebay-listings?limit=${limit}`;
    const authHeader = request.headers.get('authorization');

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
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, detail: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Request timeout', detail: 'Backend took too long to respond' },
        { status: 504 }
      );
    }
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: String(error) },
      { status: 500 }
    );
  }
}

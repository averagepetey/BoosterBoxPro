/**
 * API Route Proxy for market-macro
 * Proxies requests to the FastAPI backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'https://boosterboxpro.onrender.com';

export const maxDuration = 45;

export async function GET(request: NextRequest) {
  try {
    const url = `${BACKEND_URL}/booster-boxes/market-macro`;
    const authHeader = request.headers.get('authorization');

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 45000);

    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (authHeader) headers['Authorization'] = authHeader;

    try {
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
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        return NextResponse.json(
          { error: 'Request timeout', detail: 'Backend took too long to respond' },
          { status: 504 }
        );
      }
      throw fetchError;
    }
  } catch (error: any) {
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: error?.message || String(error) },
      { status: 500 }
    );
  }
}

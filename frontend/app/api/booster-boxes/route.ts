/**
 * API Route Proxy for booster-boxes
 * Proxies requests to the FastAPI backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/booster-boxes${queryString ? `?${queryString}` : ''}`;
    
    console.log('[API Proxy] Fetching from backend:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't cache - always fetch fresh data
      cache: 'no-store',
    });

    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, detail: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[API Proxy] Got data, first box:', data.data?.[0]?.product_name);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: String(error) },
      { status: 500 }
    );
  }
}

 * API Route Proxy for booster-boxes
 * Proxies requests to the FastAPI backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/booster-boxes${queryString ? `?${queryString}` : ''}`;
    
    console.log('[API Proxy] Fetching from backend:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't cache - always fetch fresh data
      cache: 'no-store',
    });

    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, detail: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[API Proxy] Got data, first box:', data.data?.[0]?.product_name);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: String(error) },
      { status: 500 }
    );
  }
}

 * API Route Proxy for booster-boxes
 * Proxies requests to the FastAPI backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryString = searchParams.toString();
    const url = `${BACKEND_URL}/booster-boxes${queryString ? `?${queryString}` : ''}`;
    
    console.log('[API Proxy] Fetching from backend:', url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't cache - always fetch fresh data
      cache: 'no-store',
    });

    if (!response.ok) {
      console.error('[API Proxy] Backend error:', response.status, response.statusText);
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend error: ${response.status}`, detail: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('[API Proxy] Got data, first box:', data.data?.[0]?.product_name);
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('[API Proxy] Fetch error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch from backend', detail: String(error) },
      { status: 500 }
    );
  }
}



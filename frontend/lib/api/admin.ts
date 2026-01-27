/**
 * Admin API
 * Functions for admin operations (screenshot upload, data entry)
 */

import { getApiBaseUrl, getAuthToken } from '@/lib/api/client';

export interface ScreenshotProcessingResponse {
  success: boolean;
  extracted_data: Record<string, any>;
  confidence_scores: Record<string, number>;
  detected_box?: string;
  raw_text?: string;
  errors: string[];
}

export interface DuplicateCheckResponse {
  is_duplicate: boolean;
  existing_data?: Record<string, any>;
  differences: Record<string, any>;
  message: string;
}

export interface ManualExtractionSubmission {
  booster_box_id: string;
  metric_date: string; // ISO date string
  floor_price_usd?: number;
  active_listings_count?: number;
  boxes_sold_today?: number;
  daily_volume_usd?: number;
  visible_market_cap_usd?: number;
  boxes_added_today?: number;
  estimated_total_supply?: number;
  source?: string;
  notes?: string;
}

export interface SaveResponse {
  success: boolean;
  message: string;
  is_duplicate: boolean;
  action?: 'created' | 'updated';
}

export interface BoxOption {
  id: string;
  product_name: string;
  set_name?: string;
  game_type?: string;
}

/**
 * Get admin API key from localStorage or prompt
 */
function getAdminApiKey(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('admin_api_key');
}

/**
 * Set admin API key
 */
export function setAdminApiKey(key: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('admin_api_key', key);
  }
}

/**
 * Check if user has admin access
 */
export function hasAdminAccess(): boolean {
  return !!getAdminApiKey();
}

/**
 * Upload screenshot and extract data
 * @param file - Image file to upload
 * @param useAI - If true, use OpenAI Vision API (costs money). If false, return empty structure for manual entry.
 */
export async function uploadScreenshot(
  file: File,
  useAI: boolean = true
): Promise<ScreenshotProcessingResponse> {
  const adminKey = getAdminApiKey();
  if (!adminKey) {
    throw new Error('Admin API key not set. Please configure admin access.');
  }

  const formData = new FormData();
  formData.append('file', file);

  // Add use_ai as query parameter
  const url = new URL(`${getApiBaseUrl()}/api/v1/admin/upload-screenshot`);
  url.searchParams.append('use_ai', useAI.toString());

  const response = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      'X-Admin-API-Key': adminKey,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Screenshot upload failed');
  }

  return response.json();
}

/**
 * Check for duplicate data
 */
export async function checkDuplicate(
  submission: ManualExtractionSubmission
): Promise<DuplicateCheckResponse> {
  const adminKey = getAdminApiKey();
  if (!adminKey) {
    throw new Error('Admin API key not set.');
  }

  const response = await fetch(`${getApiBaseUrl()}/api/v1/admin/check-duplicate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-API-Key': adminKey,
    },
    body: JSON.stringify(submission),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Check failed' }));
    throw new Error(error.detail || 'Duplicate check failed');
  }

  return response.json();
}

/**
 * Save extracted data
 */
export async function saveExtractedData(
  submission: ManualExtractionSubmission
): Promise<SaveResponse> {
  const adminKey = getAdminApiKey();
  if (!adminKey) {
    throw new Error('Admin API key not set.');
  }

  const response = await fetch(`${getApiBaseUrl()}/api/v1/admin/save-extracted-data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-API-Key': adminKey,
    },
    body: JSON.stringify(submission),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Save failed' }));
    throw new Error(error.detail || 'Save failed');
  }

  return response.json();
}

/**
 * Get list of boxes for dropdown
 */
export async function getBoxesList(): Promise<BoxOption[]> {
  const adminKey = getAdminApiKey();
  if (!adminKey) {
    throw new Error('Admin API key not set.');
  }

  const response = await fetch(`${getApiBaseUrl()}/api/v1/admin/boxes`, {
    method: 'GET',
    headers: {
      'X-Admin-API-Key': adminKey,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to load boxes' }));
    throw new Error(error.detail || 'Failed to load boxes');
  }

  const data = await response.json();
  return data.data || [];
}


/**
 * BoosterBoxPro - Lightweight PostHog client for Chrome Extension
 * Uses PostHog's capture API directly (SDK doesn't work in content scripts due to CSP)
 */

const POSTHOG_API_KEY = 'phc_XhxvuetiJo2RY2SqT5p7rlX6T5YbIMQOrUxv1TCJr6j';
const POSTHOG_HOST = 'https://us.i.posthog.com';

/**
 * Get or create a persistent distinct_id for this extension install
 */
async function getDistinctId() {
  try {
    const { bbpPosthogDistinctId } = await chrome.storage.local.get('bbpPosthogDistinctId');
    if (bbpPosthogDistinctId) return bbpPosthogDistinctId;

    // Generate a UUID v4
    const id = crypto.randomUUID();
    await chrome.storage.local.set({ bbpPosthogDistinctId: id });
    return id;
  } catch (e) {
    // Fallback: generate a non-persistent ID
    return crypto.randomUUID();
  }
}

/**
 * Send an event to PostHog's capture endpoint
 */
async function captureEvent(eventName, properties = {}) {
  if (POSTHOG_API_KEY === '__POSTHOG_API_KEY__') return; // Not configured yet

  try {
    const distinctId = await getDistinctId();
    const payload = {
      api_key: POSTHOG_API_KEY,
      event: eventName,
      properties: {
        distinct_id: distinctId,
        $lib: 'boosterboxpro-extension',
        ...properties,
      },
      timestamp: new Date().toISOString(),
    };

    await fetch(`${POSTHOG_HOST}/capture/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    // Silently ignore analytics failures in production
  }
}

/**
 * Identify a user (link extension distinct_id to a known user)
 */
async function identifyUser(userId, properties = {}) {
  if (POSTHOG_API_KEY === '__POSTHOG_API_KEY__') return;

  try {
    const distinctId = await getDistinctId();
    const payload = {
      api_key: POSTHOG_API_KEY,
      event: '$identify',
      properties: {
        distinct_id: userId,
        $anon_distinct_id: distinctId,
        ...properties,
      },
      timestamp: new Date().toISOString(),
    };

    await fetch(`${POSTHOG_HOST}/capture/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    // Update stored distinct_id to the identified user
    await chrome.storage.local.set({ bbpPosthogDistinctId: userId });
  } catch (e) {
    // Silently ignore analytics failures in production
  }
}

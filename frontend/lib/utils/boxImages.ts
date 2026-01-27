/**
 * Box Image Utilities
 * Maps booster box product names to image file paths
 */

/**
 * Generate image URL for a booster box based on its product name
 * Converts product name to a safe filename format
 */
export function getBoxImageUrl(productName: string | null | undefined): string | null {
  if (!productName) return null;
  
  // Extract set identifier (e.g., OP-01, OP-02, EB-01, PRB-01)
  // Pattern: "One Piece - OP-XX ..." or "One Piece - EB-XX ..." or "One Piece - PRB-XX ..."
  const setMatch = productName.match(/(OP|EB|PRB)-\d+/i);
  if (!setMatch) return null;
  
  const setCode = setMatch[0].toUpperCase();
  
  // Generate filename: op-01blue.png, op-01white.png, op-02-blue.png, etc.
  let filename: string;
  if (productName.includes('(Blue)')) {
    if (setCode === 'OP-01') {
      // OP-01 Blue uses op-01blue.png
      filename = `${setCode.toLowerCase()}blue.png`;
    } else {
      filename = `${setCode.toLowerCase()}-blue.png`;
    }
  } else if (productName.includes('(White)')) {
    if (setCode === 'OP-01') {
      // OP-01 White uses op-01white.png
      filename = `${setCode.toLowerCase()}white.png`;
    } else {
      filename = `${setCode.toLowerCase()}-white.png`;
    }
  } else {
    // No variant - use base filename
    filename = `${setCode.toLowerCase()}.png`;
  }
  
  // Return path relative to public folder
  // Note: File names in public/images/boxes should be lowercase (e.g., op-02.png, not OP-02.png)
  return `/images/boxes/${filename}`;
}

/**
 * List of all box image mappings for reference
 */
export const BOX_IMAGE_MAPPINGS: Record<string, string> = {
  'OP-02': '/images/boxes/op-02.png',
  'OP-03': '/images/boxes/op-03.png',
  'OP-01 Blue': '/images/boxes/op-01-blue.png',
  'OP-04': '/images/boxes/op-04.png',
  'OP-05': '/images/boxes/op-05.png',
  'OP-01 White': '/images/boxes/op-01-white.png',
  'OP-06': '/images/boxes/op-06.png',
  'OP-07': '/images/boxes/op-07.png',
  'OP-08': '/images/boxes/op-08.png',
  'OP-09': '/images/boxes/op-09.png',
  'OP-10': '/images/boxes/op-10.png',
  'OP-11': '/images/boxes/op-11.png',
  'OP-12': '/images/boxes/op-12.png',
  'OP-13': '/images/boxes/op-13.png',
  'EB-01': '/images/boxes/eb-01.png',
  'EB-02': '/images/boxes/eb-02.png',
  'PRB-01': '/images/boxes/prb-01.png',
};


import { ai, IMAGE_GEN_MODEL } from './gemini-client';
import axios from 'axios';
import { ProductSKU } from './web-scraper';
import { CreativeStrategy } from './creative-strategist';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

export interface AdFormat {
  name: string;
  width: number;
  height: number;
  aspectRatio: string;
  category: 'social' | 'display' | 'video' | 'email';
  description: string;
  layoutGuidance: string;
}

export interface ResizedCreative {
  skuId: string;
  productName: string;
  format: string;
  width: number;
  height: number;
  aspectRatio: string;
  imagePath: string;
  prompt: string;
  masterCreativePath: string;
}

/**
 * Standard ad formats used across digital advertising
 * Based on IAB standard ad sizes and social media specs
 */
export const STANDARD_AD_FORMATS: AdFormat[] = [
  // Social Media Formats
  {
    name: 'instagram-square',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    category: 'social',
    description: 'Instagram Square Post',
    layoutGuidance: 'Centered composition. Product in middle. Equal padding all sides. Text in top or bottom third.',
  },
  {
    name: 'instagram-story',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    category: 'social',
    description: 'Instagram/Facebook Story',
    layoutGuidance: 'Vertical composition. Stack elements vertically. Logo/headline in top 20%. Product in middle 50%. CTA in bottom 20%. Avoid top 250px and bottom 250px for critical content.',
  },
  {
    name: 'facebook-feed',
    width: 1200,
    height: 628,
    aspectRatio: '1.91:1',
    category: 'social',
    description: 'Facebook Feed Ad',
    layoutGuidance: 'Landscape orientation. Product on left or right. Text on opposite side. Keep important elements centered.',
  },
  {
    name: 'twitter-post',
    width: 1200,
    height: 675,
    aspectRatio: '16:9',
    category: 'social',
    description: 'Twitter/X Post',
    layoutGuidance: 'Landscape 16:9. Product centered or rule-of-thirds. Minimal text overlay.',
  },
  {
    name: 'linkedin-post',
    width: 1200,
    height: 627,
    aspectRatio: '1.91:1',
    category: 'social',
    description: 'LinkedIn Post',
    layoutGuidance: 'Professional aesthetic. Product center-left or center-right. Clean background. Professional typography.',
  },

  // Display Banner Formats (IAB Standard)
  {
    name: 'leaderboard',
    width: 728,
    height: 90,
    aspectRatio: '8.09:1',
    category: 'display',
    description: 'Leaderboard Banner (728x90)',
    layoutGuidance: 'Extreme horizontal banner. Minimal text (3-5 words max). Product thumbnail on left or right. Strong visual contrast. CTA button if space allows.',
  },
  {
    name: 'billboard',
    width: 970,
    height: 250,
    aspectRatio: '3.88:1',
    category: 'display',
    description: 'Billboard Banner (970x250)',
    layoutGuidance: 'Wide horizontal format. Product on one side (left or right 40%). Text and CTA on opposite side. Clear visual hierarchy.',
  },
  {
    name: 'half-page',
    width: 300,
    height: 600,
    aspectRatio: '1:2',
    category: 'display',
    description: 'Half-Page Ad (300x600)',
    layoutGuidance: 'Tall vertical format. Stack elements: Logo/headline (top 15%), product (middle 60%), CTA (bottom 25%). Vertical visual flow.',
  },
  {
    name: 'medium-rectangle',
    width: 300,
    height: 250,
    aspectRatio: '1.2:1',
    category: 'display',
    description: 'Medium Rectangle (300x250)',
    layoutGuidance: 'Square-ish format. Product centered or top-center. Text below or overlaid. Compact layout.',
  },
  {
    name: 'large-rectangle',
    width: 336,
    height: 280,
    aspectRatio: '1.2:1',
    category: 'display',
    description: 'Large Rectangle (336x280)',
    layoutGuidance: 'Similar to medium rectangle. Product dominant. Minimal text. Clear CTA.',
  },
  {
    name: 'wide-skyscraper',
    width: 160,
    height: 600,
    aspectRatio: '4:15',
    category: 'display',
    description: 'Wide Skyscraper (160x600)',
    layoutGuidance: 'Very tall and narrow. Vertical stack: Logo (top), product (middle, may need to be cropped vertically), text (compact), CTA (bottom). Extreme vertical composition.',
  },
  {
    name: 'mobile-banner',
    width: 320,
    height: 50,
    aspectRatio: '6.4:1',
    category: 'display',
    description: 'Mobile Banner (320x50)',
    layoutGuidance: 'Extreme horizontal mobile banner. Product thumbnail tiny (40x40px). Brand name or 2-3 words max. High contrast.',
  },

  // Email Marketing Formats
  {
    name: 'email-header',
    width: 600,
    height: 200,
    aspectRatio: '3:1',
    category: 'email',
    description: 'Email Header Banner',
    layoutGuidance: 'Wide horizontal header. Brand-focused. Product secondary. Clean and professional.',
  },
  {
    name: 'email-hero',
    width: 600,
    height: 400,
    aspectRatio: '3:2',
    category: 'email',
    description: 'Email Hero Image',
    layoutGuidance: 'Standard email width. Product prominent. Text can be overlaid or separate. Email-safe colors.',
  },
];

const MAX_FILE_SIZE_BYTES: Record<AdFormat['category'], number> = {
  social: 8 * 1024 * 1024, // Instagram/Facebook recommended upper bound
  display: 2 * 1024 * 1024, // IAB recommendation for display banners
  video: 5 * 1024 * 1024, // Allow larger for video thumbnails
  email: 1.5 * 1024 * 1024, // Keep email assets lightweight for deliverability
};

/**
 * Fetch and cache product image
 */
async function fetchProductImageForResize(imageUrl?: string): Promise<{ data: string; mimeType: string } | undefined> {
  if (!imageUrl) return undefined;

  try {
    const response = await axios.get<ArrayBuffer>(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 15000,
    });

    const mimeType = response.headers['content-type'] || 'image/jpeg';
    const buffer = Buffer.from(response.data);
    return { data: buffer.toString('base64'), mimeType };
  } catch (error: any) {
    console.warn(`Unable to fetch product image ${imageUrl}: ${error.message}`);
    return undefined;
  }
}

/**
 * Build detailed prompt for AI-powered resizing
 */
function buildResizingPrompt(
  format: AdFormat,
  strategy: CreativeStrategy,
  product: ProductSKU
): string {
  const brandColors = strategy.elevatedBrandIdentity?.colorPalette?.join(', ') || 'brand colors';
  const visualStyle = strategy.elevatedBrandIdentity?.visualStyle || 'modern and clean';
  const mood = strategy.elevatedBrandIdentity?.mood?.join(', ') || 'sophisticated';

  return `You are an expert ad creative designer. Your task is to recreate the provided master ad creative for ${format.description} (${format.width}x${format.height}px, ${format.aspectRatio} aspect ratio).

CRITICAL REQUIREMENTS:
1. PRODUCT FIDELITY: The product from the first reference image MUST appear EXACTLY as shown. Do NOT alter colors, design, details, or appearance.

2. VISUAL CONSISTENCY: Use the second image (master creative) as your creative direction reference. Preserve these elements:
   - Color palette: ${brandColors}
   - Visual style: ${visualStyle}
   - Mood and atmosphere: ${mood}
   - Typography hierarchy and style
   - Lighting quality and direction
   - Overall design language and brand feel

3. LAYOUT ADAPTATION for ${format.aspectRatio} aspect ratio:
   ${format.layoutGuidance}

4. FORMAT-SPECIFIC CONSIDERATIONS:
   ${getFormatSpecificGuidance(format)}

5. QUALITY STANDARDS:
   - Professional commercial photography quality
   - High-resolution, crisp details
   - Proper color calibration
   - Consistent lighting with master creative
   - Clean composition without artifacts

PRODUCT: ${product.name}
${product.description ? `PRODUCT DESCRIPTION: ${product.description}` : ''}

OUTPUT: A professional ${format.description} ad that maintains brand consistency with the master creative while perfectly adapting to the ${format.width}x${format.height}px format.`;
}

/**
 * Get format-specific creative guidance
 */
function getFormatSpecificGuidance(format: AdFormat): string {
  switch (format.category) {
    case 'social':
      return `- Optimized for mobile viewing
   - Thumb-stopping visual impact
   - Clear focal point
   - Minimal text overlay (let caption handle copy)
   - Brand logo visible but not dominant`;

    case 'display':
      if (format.height > format.width * 2) {
        // Vertical banners
        return `- Vertical visual flow (top to bottom)
   - Compact, scannable text
   - Strong CTA placement
   - Product may need vertical crop/framing
   - High contrast for visibility`;
      } else if (format.width > format.height * 3) {
        // Horizontal banners
        return `- Horizontal layout priority
   - Extremely concise messaging (brand name + 1-2 words)
   - Product as icon/thumbnail
   - High contrast colors
   - Clickable area optimization`;
      } else {
        // Square-ish display
        return `- Balanced composition
   - Product prominent
   - Clear call-to-action
   - Readable at small sizes
   - Strong visual hierarchy`;
      }

    case 'email':
      return `- Email-safe color palette
   - Professional, trustworthy aesthetic
   - Desktop and mobile rendering
   - Clear product showcase
   - Supports email copy below/above`;

    case 'video':
      return `- Video thumbnail optimization
   - Eye-catching still frame
   - Play button space consideration
   - High intrigue/curiosity factor`;

    default:
      return '- Professional quality\n   - Brand consistency\n   - Clear messaging';
  }
}

/**
 * Resize a master creative to a specific format using AI
 */
export async function resizeCreativeToFormat(
  masterCreativePath: string,
  productImage: { data: string; mimeType: string } | undefined,
  strategy: CreativeStrategy,
  product: ProductSKU,
  format: AdFormat
): Promise<ResizedCreative> {
  console.info(`\n📐 Resizing to ${format.description} (${format.width}x${format.height})...`);

  // Load master creative
  const masterCreativeData = fs.readFileSync(masterCreativePath);
  const masterCreativeBase64 = masterCreativeData.toString('base64');
  const masterExt = path.extname(masterCreativePath).toLowerCase();
  const masterMimeType = masterExt === '.png' ? 'image/png' : masterExt === '.webp' ? 'image/webp' : 'image/jpeg';

  // Build multimodal prompt
  const parts: Array<{ text?: string; inlineData?: { mimeType: string; data: string } }> = [];

  // 1. Product reference image
  if (productImage) {
    parts.push({
      inlineData: {
        mimeType: productImage.mimeType,
        data: productImage.data,
      },
    });
  }

  // 2. Master creative as visual reference
  parts.push({
    inlineData: {
      mimeType: masterMimeType,
      data: masterCreativeBase64,
    },
  });

  // 3. Instruction prompt
  const prompt = buildResizingPrompt(format, strategy, product);
  parts.push({ text: prompt });

  try {
    // Generate resized creative
    const response = await ai.models.generateContent({
      model: IMAGE_GEN_MODEL,
      contents: [{ role: 'user', parts }],
      config: {
        responseModalities: ['TEXT', 'IMAGE'] as any,
      },
    });

    const candidates = response.candidates;
    if (!candidates || candidates.length === 0) {
      throw new Error('No image generated');
    }

    const content = candidates[0].content;
    if (!content || !content.parts) {
      throw new Error('No content in response');
    }

    // Extract and save generated image
    let imageData: Buffer | null = null;
    for (const part of content.parts) {
      if (part.inlineData && part.inlineData.data) {
        imageData = Buffer.from(part.inlineData.data, 'base64');
        break;
      }
    }

    if (!imageData) {
      throw new Error('No image data in response');
    }

    // Save resized creative
    const sanitizedSku = product.sku.replace(/[^a-zA-Z0-9]/g, '_');
    const baseDir = process.env.GENERATED_CREATIVES_DIR || 'generated-creatives';
    const timestamp = Date.now();
    const resizedPath = path.join(
      baseDir,
      `${sanitizedSku}_${format.name}_${format.width}x${format.height}_${timestamp}.png`
    );

    const dir = path.dirname(resizedPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(resizedPath, imageData);
    console.info(`✓ Saved ${format.description}: ${path.basename(resizedPath)}`);

    await enforcePlatformRequirements(resizedPath, format);

    return {
      skuId: product.sku,
      productName: product.name,
      format: format.name,
      width: format.width,
      height: format.height,
      aspectRatio: format.aspectRatio,
      imagePath: resizedPath,
      prompt,
      masterCreativePath,
    };
  } catch (error: any) {
    throw new Error(`Failed to resize creative to ${format.description}: ${error.message}`);
  }
}

/**
 * Resize master creative to all standard formats
 */
export async function resizeCreativeForAllFormats(
  masterCreativePath: string,
  productImageUrl: string | undefined,
  strategy: CreativeStrategy,
  product: ProductSKU,
  targetFormats: AdFormat[] = STANDARD_AD_FORMATS
): Promise<ResizedCreative[]> {
  console.info(`\n🎨 RESIZING MASTER CREATIVE FOR ALL FORMATS`);
  console.info(`Master: ${path.basename(masterCreativePath)}`);
  console.info(`Product: ${product.name} (${product.sku})`);
  console.info(`Target formats: ${targetFormats.length}`);

  // Fetch product image once
  const productImage = await fetchProductImageForResize(productImageUrl);

  if (!productImage) {
    console.warn('⚠️  No product image available - proceeding without product reference');
  }

  const resizedCreatives: ResizedCreative[] = [];

  for (const format of targetFormats) {
    try {
      const resized = await resizeCreativeToFormat(
        masterCreativePath,
        productImage,
        strategy,
        product,
        format
      );
      resizedCreatives.push(resized);
    } catch (error: any) {
      console.error(`❌ Failed to create ${format.description}: ${error.message}`);
      // Continue with other formats even if one fails
    }
  }

  console.info(`\n✅ Successfully created ${resizedCreatives.length}/${targetFormats.length} format variations`);

  return resizedCreatives;
}

/**
 * Get specific format presets by category
 */
export function getFormatsByCategory(category: 'social' | 'display' | 'email' | 'video'): AdFormat[] {
  return STANDARD_AD_FORMATS.filter(f => f.category === category);
}

/**
 * Get high-priority formats (most commonly used)
 */
export function getHighPriorityFormats(): AdFormat[] {
  const priorityNames = [
    'instagram-square',
    'instagram-story',
    'facebook-feed',
    'twitter-post',
    'linkedin-post',
    'leaderboard',
    'billboard',
    'medium-rectangle',
    'half-page',
    'mobile-banner',
    'email-hero',
    'email-header',
  ];
  return STANDARD_AD_FORMATS.filter(f => priorityNames.includes(f.name));
}

async function enforcePlatformRequirements(imagePath: string, format: AdFormat) {
  try {
    const metadata = await sharp(imagePath).metadata();
    const targetRatio = format.width / format.height;
    const actualRatio =
      metadata.width && metadata.height ? metadata.width / metadata.height : undefined;

    let fileUpdated = false;

    if (!metadata.width || !metadata.height) {
      console.warn(`⚠️  Dimension metadata missing for ${path.basename(imagePath)} - forcing resize`);
      await resizeToExactDimensions(imagePath, format);
      fileUpdated = true;
    } else {
      const needsDimensionFix =
        metadata.width !== format.width || metadata.height !== format.height;
      const ratioMismatch =
        actualRatio !== undefined && Math.abs(actualRatio - targetRatio) > 0.01;

      if (needsDimensionFix || ratioMismatch) {
        await resizeToExactDimensions(imagePath, format);
        fileUpdated = true;
      }
    }

    const fileSize = fs.statSync(imagePath).size;
    const maxSize = MAX_FILE_SIZE_BYTES[format.category] ?? 8 * 1024 * 1024;
    if (fileSize > maxSize) {
      await compressImage(imagePath, format);
      fileUpdated = true;
    }

    if (fileUpdated) {
      const postMeta = await sharp(imagePath).metadata();
      const postSize = fs.statSync(imagePath).size;
      console.info(
        `↻ Normalized ${path.basename(imagePath)} → ${postMeta.width}x${postMeta.height}px, ${(postSize / (1024 * 1024)).toFixed(2)}MB`
      );
    } else {
      console.info(
        `✓ ${path.basename(imagePath)} already meets ${format.description} specs`
      );
    }
  } catch (error: any) {
    console.warn(
      `⚠️  Failed to enforce platform requirements for ${path.basename(imagePath)}: ${error.message}`
    );
  }
}

async function resizeToExactDimensions(imagePath: string, format: AdFormat) {
  const tempPath = `${imagePath}.tmp`;
  await sharp(imagePath)
    .resize(format.width, format.height, {
      fit: 'cover',
      position: 'attention',
    })
    .png({
      compressionLevel: 8,
      adaptiveFiltering: true,
      palette: true,
    })
    .toFile(tempPath);
  fs.renameSync(tempPath, imagePath);
}

async function compressImage(imagePath: string, format: AdFormat) {
  const tempPath = `${imagePath}.compressed`;
  const metadata = await sharp(imagePath).metadata();

  let transformer = sharp(imagePath);
  const needsResize =
    !metadata.width ||
    !metadata.height ||
    metadata.width !== format.width ||
    metadata.height !== format.height;

  if (needsResize) {
    transformer = transformer.resize(format.width, format.height, {
      fit: 'cover',
      position: 'attention',
    });
  }

  await transformer
    .png({
      compressionLevel: 9,
      adaptiveFiltering: true,
      palette: true,
    })
    .toFile(tempPath);
  fs.renameSync(tempPath, imagePath);
}

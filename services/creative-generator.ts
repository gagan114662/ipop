import { ai, IMAGE_GEN_MODEL } from './gemini-client';
import axios from 'axios';
import { ProductSKU } from './web-scraper';
import { CreativeStrategy } from './creative-strategist';
import { ReferenceSceneTemplate } from './reference-curator';
import * as fs from 'fs';
import * as path from 'path';

export interface GeneratedCreative {
  skuId: string;
  productName: string;
  format: string;
  concept: string;
  imagePath: string;
  prompt: string;
}

type CachedImage = { data: string; mimeType: string };
const productImageCache = new Map<string, CachedImage>();

async function fetchProductImage(imageUrl?: string): Promise<CachedImage | undefined> {
  if (!imageUrl) {
    return undefined;
  }

  if (productImageCache.has(imageUrl)) {
    return productImageCache.get(imageUrl);
  }

  try {
    const response = await axios.get<ArrayBuffer>(imageUrl, {
      responseType: 'arraybuffer',
      timeout: 15000,
    });

    const mimeType = response.headers['content-type'] || 'image/jpeg';
    const buffer = Buffer.from(response.data);
    const cached = { data: buffer.toString('base64'), mimeType };
    productImageCache.set(imageUrl, cached);
    return cached;
  } catch (error: any) {
    console.warn(`Unable to fetch product image ${imageUrl}: ${error.message}`);
    return undefined;
  }
}

function buildSceneTemplateSection(template?: ReferenceSceneTemplate): string {
  if (!template) return '';
  return `Scene inspiration (from ${template.source.sourceName}): ${template.promptSummary || 'Award-winning composition.'}
Camera: ${template.sceneComposition.camera}
Lighting: ${template.sceneComposition.lighting}
Foreground: ${template.sceneComposition.foreground}
Midground: ${template.sceneComposition.midground}
Background: ${template.sceneComposition.background}
Props: ${template.sceneComposition.props}
Post-processing: ${template.sceneComposition.postProcessing}
Emotion: ${template.sceneComposition.emotion}

`;
}

export async function generateProductCreative(
  product: ProductSKU,
  strategy: CreativeStrategy,
  format: 'social-post' | 'product-ad' | 'lifestyle-shot' | 'packaging-mockup',
  variationIndex: number,
  sceneTemplates?: ReferenceSceneTemplate[]
): Promise<GeneratedCreative> {
  console.info(`\n=== GENERATING CREATIVE FOR ${product.name} ===`);
  if (!strategy.campaignConcepts || strategy.campaignConcepts.length === 0) {
    strategy.campaignConcepts = [{
      name: 'Elevated Brand Campaign',
      description: 'Modern, sophisticated brand elevation',
      targetAudience: 'Modern consumers',
      keyMessage: 'Premium quality and design',
      visualDirection: 'Clean, modern, aspirational'
    }];
  }

  const campaignConcept = strategy.campaignConcepts[variationIndex % strategy.campaignConcepts.length];
  const sceneTemplate = sceneTemplates && sceneTemplates.length > 0
    ? sceneTemplates[variationIndex % sceneTemplates.length]
    : undefined;

  if (sceneTemplate) {
    console.info(`Using reference: "${sceneTemplate.headline || 'Award-Winning Campaign'}"`);
    console.info(`Reference image: ${sceneTemplate.imageUrl}`);
  }

  const garmentIntegrityClause = `You are given a reference photo of the garment. Use the garment exactly as shown. Do NOT redesign, recolor, or change the silhouette, embellishments, trims, or construction details. Maintain full fidelity to the reference image and only adapt lighting, camera work, set design, and supporting elements.`;

  let prompt = `${garmentIntegrityClause}\n\n${buildSceneTemplateSection(sceneTemplate)}`;

  switch (format) {
    case 'social-post':
      prompt += `Create a stunning social media post showcasing the featured garment.
Style: ${strategy.elevatedBrandIdentity.visualStyle}.
Mood: ${strategy.campaignConcepts[0].visualDirection}.
Color palette: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Photography style: ${strategy.productCreativeDirection.photographyStyle}.
Ensure the garment from the reference photo remains unchanged and is framed with modern, aspirational styling.`;
      break;

    case 'product-ad':
      prompt += `Create a premium product advertisement for the featured garment.
Campaign: ${campaignConcept.name} - ${campaignConcept.description}.
Visual direction: ${campaignConcept.visualDirection}.
Style: ${strategy.elevatedBrandIdentity.visualStyle}.
Colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Photography: ${strategy.productCreativeDirection.photographyStyle}.
Deliver a high-end, magazine-quality visual while preserving every garment detail from the reference.`;
      break;

    case 'lifestyle-shot':
      prompt += `Create an aspirational lifestyle image featuring the garment in use.
Target audience: ${campaignConcept.targetAudience}.
Mood: ${strategy.elevatedBrandIdentity.mood.join(', ')}.
Visual style: ${strategy.elevatedBrandIdentity.visualStyle}.
Colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Keep the garment untouched and place it in an emotionally engaging, real-world context that respects the reference layout.`;
      break;

    case 'packaging-mockup':
      prompt += `Create a modern packaging design mockup aligned with the garment collection.
Brand colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Typography style: ${strategy.elevatedBrandIdentity.typography.primary} for headlines.
Design principles: ${strategy.elevatedBrandIdentity.designPrinciples.join(', ')}.
Visual style: ${strategy.elevatedBrandIdentity.visualStyle}.
Ensure any garment representation remains faithful to the reference image while presenting the packaging concept.`;
      break;
  }

  const timestamp = Date.now();
  const sanitizedSku = product.sku.replace(/[^a-zA-Z0-9]/g, '_');
  const baseDir = process.env.GENERATED_CREATIVES_DIR || 'generated-creatives';
  const imagePath = path.join(baseDir, `${sanitizedSku}_${format}_v${variationIndex}_${timestamp}.png`);

  const ensureOutputDir = () => {
    const dir = path.dirname(imagePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  };

  try {
    ensureOutputDir();

    const productImage = await fetchProductImage(product.imageUrl);

    const parts: Array<{ text?: string; inlineData?: { mimeType: string; data: string } }> = [];

    // Add product image as first reference
    if (productImage) {
      parts.push({
        inlineData: {
          mimeType: productImage.mimeType,
          data: productImage.data,
        },
      });
    }

    // CRITICAL FIX: Add reference image from scene template (if available)
    let referenceImageAdded = false;
    if (sceneTemplate && sceneTemplate.localImagePath && fs.existsSync(sceneTemplate.localImagePath)) {
      try {
        const referenceImageData = fs.readFileSync(sceneTemplate.localImagePath);
        const referenceBase64 = referenceImageData.toString('base64');

        // Determine MIME type from file extension
        const ext = path.extname(sceneTemplate.localImagePath).toLowerCase();
        const mimeType = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg';

        parts.push({
          inlineData: {
            mimeType,
            data: referenceBase64,
          },
        });

        referenceImageAdded = true;
        console.info(`✓ Added reference image to generation: ${path.basename(sceneTemplate.localImagePath)}`);
      } catch (error: any) {
        console.warn(`Failed to load reference image ${sceneTemplate.localImagePath}: ${error.message}`);
      }
    }

    // Update prompt to reference the images
    const imageInstructions = referenceImageAdded
      ? `You are provided with TWO reference images:
1. PRODUCT IMAGE: The actual product that MUST appear in the ad (maintain exact appearance)
2. CREATIVE REFERENCE: An award-winning campaign showing the visual style, composition, lighting, and mood to emulate

CRITICAL: The product from image #1 must appear exactly as shown. Use image #2 as your creative direction.

`
      : productImage
      ? `You are provided with the product image. Maintain exact product appearance in the creative.

`
      : '';

    parts.push({ text: imageInstructions + prompt });

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

    let imageSaved = false;
    for (const part of content.parts) {
      if (part.inlineData && part.inlineData.data) {
        const imageData = Buffer.from(part.inlineData.data, 'base64');
        fs.writeFileSync(imagePath, imageData);
        imageSaved = true;
        break;
      }
    }

    if (!imageSaved) {
      throw new Error('No image data in response');
    }

    // Save the product SKU image alongside the generated creative
    if (productImage) {
      const productImagePath = imagePath.replace('.png', '_product.jpg');
      const productImageData = Buffer.from(productImage.data, 'base64');
      fs.writeFileSync(productImagePath, productImageData);
      console.info(`✓ Saved product SKU image: ${path.basename(productImagePath)}`);
    }

    // Save the reference image used for inspiration
    if (sceneTemplate && sceneTemplate.localImagePath) {
      const referenceImagePath = imagePath.replace('.png', '_reference.jpg');
      try {
        fs.copyFileSync(sceneTemplate.localImagePath, referenceImagePath);
        console.info(`✓ Saved reference image: ${path.basename(referenceImagePath)}`);
      } catch (error: any) {
        console.warn(`Failed to copy reference image: ${error.message}`);
      }
    }

    console.info(`✓ Saved generated creative: ${path.basename(imagePath)}`);
    console.info(`\n📁 OUTPUT SUMMARY:`);
    console.info(`   Reference: ${sceneTemplate?.localImagePath ? path.basename(imagePath.replace('.png', '_reference.jpg')) : 'N/A'}`);
    console.info(`   Product:   ${productImage ? path.basename(imagePath.replace('.png', '_product.jpg')) : 'N/A'}`);
    console.info(`   Generated: ${path.basename(imagePath)}\n`);

    return {
      skuId: product.sku,
      productName: product.name,
      format,
      concept: campaignConcept.name,
      imagePath,
      prompt,
    };
  } catch (error: any) {
    throw new Error(`Creative generation failed for ${product.name}: ${error.message}`);
  }
}

export async function generateCreativesForAllProducts(
  products: ProductSKU[],
  strategy: CreativeStrategy,
  sceneTemplates: ReferenceSceneTemplate[] | undefined,
  formatsPerProduct: Array<'social-post' | 'product-ad' | 'lifestyle-shot' | 'packaging-mockup'> = ['product-ad'],
  variationsPerFormat: number = 1
): Promise<GeneratedCreative[]> {
  const allCreatives: GeneratedCreative[] = [];

  // Process only THE FIRST product (for testing/verification)
  const product = products[0];

  if (!product) {
    console.warn('No products available to generate creatives');
    return allCreatives;
  }

  console.info(`Processing single product: ${product.name} (SKU: ${product.sku})`);

  // Generate only 1 image (single format, single variation)
  const format = formatsPerProduct[0]; // Use first format only
  try {
    const creative = await generateProductCreative(product, strategy, format, 0, sceneTemplates);
    allCreatives.push(creative);
    console.info(`✓ Generated creative for ${product.name}`);
  } catch (error: any) {
    console.error(`Failed to generate creative for ${product.name}:`, error.message);
  }

  return allCreatives;
}

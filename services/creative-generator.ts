import { ai, IMAGE_GEN_MODEL } from './gemini-client';
import { ProductSKU } from './web-scraper';
import { CreativeStrategy } from './creative-strategist';
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

export async function generateProductCreative(
  product: ProductSKU,
  strategy: CreativeStrategy,
  format: 'social-post' | 'product-ad' | 'lifestyle-shot' | 'packaging-mockup',
  variationIndex: number
): Promise<GeneratedCreative> {
  const campaignConcept = strategy.campaignConcepts[variationIndex % strategy.campaignConcepts.length];
  
  let prompt = '';
  
  switch (format) {
    case 'social-post':
      prompt = `Create a stunning social media post for ${product.name}. 
Style: ${strategy.elevatedBrandIdentity.visualStyle}. 
Mood: ${strategy.campaignConcepts[0].visualDirection}.
Color palette: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Photography style: ${strategy.productCreativeDirection.photographyStyle}.
The image should feature the product prominently with modern, clean, aspirational styling.
Make it look premium, professional, and Instagram-worthy.`;
      break;
      
    case 'product-ad':
      prompt = `Create a premium product advertisement for ${product.name}.
Campaign: ${campaignConcept.name} - ${campaignConcept.description}.
Visual direction: ${campaignConcept.visualDirection}.
Style: ${strategy.elevatedBrandIdentity.visualStyle}.
Colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Photography: ${strategy.productCreativeDirection.photographyStyle}.
Create a high-end, magazine-quality product shot with sophisticated styling and lighting.`;
      break;
      
    case 'lifestyle-shot':
      prompt = `Create an aspirational lifestyle image featuring ${product.name} in use.
Target audience: ${campaignConcept.targetAudience}.
Mood: ${strategy.elevatedBrandIdentity.mood.join(', ')}.
Visual style: ${strategy.elevatedBrandIdentity.visualStyle}.
Colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Show the product in a beautiful, real-world context that resonates with the target audience.
Make it feel authentic, aspirational, and emotionally engaging.`;
      break;
      
    case 'packaging-mockup':
      prompt = `Create a modern packaging design mockup for ${product.name}.
Brand colors: ${strategy.elevatedBrandIdentity.colorPalette.join(', ')}.
Typography style: ${strategy.elevatedBrandIdentity.typography.primary} for headlines.
Design principles: ${strategy.elevatedBrandIdentity.designPrinciples.join(', ')}.
Visual style: ${strategy.elevatedBrandIdentity.visualStyle}.
Create clean, modern, premium packaging that stands out on shelves.`;
      break;
  }

  try {
    const timestamp = Date.now();
    const sanitizedSku = product.sku.replace(/[^a-zA-Z0-9]/g, '_');
    const imagePath = path.join('generated-creatives', `${sanitizedSku}_${format}_v${variationIndex}_${timestamp}.png`);
    
    // Ensure directory exists
    const dir = path.dirname(imagePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    const response = await ai.models.generateContent({
      model: IMAGE_GEN_MODEL,
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      config: {
        responseModalities: ["TEXT", "IMAGE"] as any,
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

    return {
      skuId: product.sku,
      productName: product.name,
      format,
      concept: campaignConcept.name,
      imagePath,
      prompt
    };
  } catch (error: any) {
    throw new Error(`Creative generation failed for ${product.name}: ${error.message}`);
  }
}

export async function generateCreativesForAllProducts(
  products: ProductSKU[],
  strategy: CreativeStrategy,
  formatsPerProduct: Array<'social-post' | 'product-ad' | 'lifestyle-shot' | 'packaging-mockup'> = ['social-post', 'product-ad'],
  variationsPerFormat: number = 2
): Promise<GeneratedCreative[]> {
  const allCreatives: GeneratedCreative[] = [];
  
  // Limit to first 5 products to avoid excessive API calls
  const productsToProcess = products.slice(0, 5);
  
  for (const product of productsToProcess) {
    for (const format of formatsPerProduct) {
      for (let i = 0; i < variationsPerFormat; i++) {
        try {
          const creative = await generateProductCreative(product, strategy, format, i);
          allCreatives.push(creative);
        } catch (error: any) {
          console.error(`Failed to generate ${format} for ${product.name}:`, error.message);
        }
      }
    }
  }
  
  return allCreatives;
}

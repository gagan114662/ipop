import { ProductSKU } from './web-scraper';
import { BrandAnalysis } from './brand-analyzer';
import { CreativeStrategy } from './creative-strategist';
import { ReferenceSceneTemplate } from './reference-curator';

export interface AssetInsight {
  productName: string;
  productUrl?: string;
  heroImage?: string;
  messagingHooks: string[];
  visualGuidance: string[];
  palette: string[];
  referenceId?: string;
  referenceSummary?: string;
}

interface BuildAssetInsightsParams {
  products: ProductSKU[];
  brandAnalysis?: BrandAnalysis;
  strategy?: CreativeStrategy;
  references?: ReferenceSceneTemplate[];
}

export function buildAssetInsights({
  products,
  brandAnalysis,
  strategy,
  references,
}: BuildAssetInsightsParams): Record<string, AssetInsight> {
  const insights: Record<string, AssetInsight> = {};
  if (!products || products.length === 0) {
    return insights;
  }

  const palette =
    strategy?.elevatedBrandIdentity?.colorPalette?.slice(0, 5) ||
    brandAnalysis?.designElements?.colorPalette?.slice(0, 5) ||
    [];

  const primaryConcept = strategy?.campaignConcepts?.[0];
  const visualStyle = strategy?.elevatedBrandIdentity?.visualStyle || brandAnalysis?.designElements?.visualStyle;
  const photographyStyle = strategy?.productCreativeDirection?.photographyStyle;
  const tone = brandAnalysis?.brandVoice?.tone || primaryConcept?.visualDirection;

  products.forEach((product, index) => {
    const reference = references && references.length > 0 ? references[index % references.length] : undefined;
    const hooks: string[] = [];
    const guidance: string[] = [];

    if (primaryConcept?.keyMessage) {
      hooks.push(primaryConcept.keyMessage);
    }
    if (brandAnalysis?.strengths && brandAnalysis.strengths.length > 0) {
      hooks.push(`Leverage brand strength: ${brandAnalysis.strengths[0]}`);
    }
    if (visualStyle) {
      guidance.push(`Honor the ${visualStyle.toLowerCase()} visual language.`);
    }
    if (photographyStyle) {
      guidance.push(`Photography style: ${photographyStyle}.`);
    }
    if (tone) {
      guidance.push(`Tone of voice: ${tone}.`);
    }
    if (reference) {
      guidance.push(`Pull composition cues from ${reference.source.sourceName}.`);
    }
    if (palette.length > 0) {
      guidance.push(`Core palette: ${palette.join(', ')}.`);
    }

    insights[product.sku] = {
      productName: product.name || product.sku,
      productUrl: product.url,
      heroImage: product.imageUrl,
      messagingHooks: hooks.length > 0 ? hooks : [`Spotlight ${product.name}`],
      visualGuidance: guidance.length > 0 ? guidance : ['Highlight craftsmanship and premium finish.'],
      palette,
      referenceId: reference?.id,
      referenceSummary: reference?.promptSummary || reference?.headline,
    };
  });

  return insights;
}

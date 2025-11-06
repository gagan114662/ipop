import { ProductSKU, BrandVisualData } from './web-scraper';
import { BrandAnalysis } from './brand-analyzer';
import { CompetitorAnalysis } from './competitor-researcher';
import { CreativeStrategy } from './creative-strategist';
import { GeneratedCreative } from './creative-generator';
import { ReferenceSceneTemplate } from './reference-curator';
import { AssetInsight } from './asset-insights';
import { ResizedCreative } from './creative-resizer';

export interface MarketingCampaign {
  id: string;
  websiteUrl: string;
  brandName: string;
  status: 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  
  // Extracted data
  products: ProductSKU[];
  visualData: BrandVisualData;
  
  // Analysis
  brandAnalysis?: BrandAnalysis;
  competitorAnalysis?: CompetitorAnalysis;
  
  // Strategy
  creativeStrategy?: CreativeStrategy;
  assetInsights?: Record<string, AssetInsight>;
  referenceLibrary?: ReferenceSceneTemplate[];
  
  // Generated assets
  generatedCreatives: GeneratedCreative[];
  resizedCreatives?: ResizedCreative[];

  error?: string;
}

import { openai, RESEARCH_MODEL } from './openai-client';
import { BrandAnalysis } from './brand-analyzer';
import { CompetitorAnalysis } from './competitor-researcher';
import { ProductSKU } from './web-scraper';

export interface CreativeStrategy {
  elevatedBrandIdentity: {
    colorPalette: string[];
    typography: {
      primary: string;
      secondary: string;
    };
    visualStyle: string;
    mood: string[];
    designPrinciples: string[];
  };
  campaignConcepts: Array<{
    name: string;
    description: string;
    targetAudience: string;
    keyMessage: string;
    visualDirection: string;
  }>;
  productCreativeDirection: {
    photographyStyle: string;
    layoutPrinciples: string[];
    colorTreatment: string;
    typographyUsage: string;
  };
  beforeAfterNarrative: string;
}

export async function developCreativeStrategy(
  brandAnalysis: BrandAnalysis,
  competitorAnalysis: CompetitorAnalysis,
  products: ProductSKU[]
): Promise<CreativeStrategy> {
  const prompt = `You are a Creative Director at a world-class agency. Based on the research below, develop an elevated creative strategy that transforms this brand.

CURRENT BRAND ANALYSIS:
- Quality Score: ${brandAnalysis.qualityScore}/100
- Needs Overhaul: ${brandAnalysis.needsOverhaul ? 'YES - Complete transformation needed' : 'NO - Refinement needed'}
- Industry: ${brandAnalysis.industry}
- Current Strengths: ${brandAnalysis.strengths.join(', ')}
- Weaknesses: ${brandAnalysis.weaknesses.join(', ')}
- Target Audience: ${brandAnalysis.targetAudience}

COMPETITOR INSIGHTS:
- Top Trends: ${competitorAnalysis.industryTrends.join(', ')}
- Market Gaps: ${competitorAnalysis.marketGaps.join(', ')}
- Differentiation Opportunities: ${competitorAnalysis.differentiationOpportunities.join(', ')}

PRODUCTS TO FEATURE:
${products.slice(0, 5).map(p => `- ${p.name} (${p.sku})`).join('\n')}

Develop a comprehensive creative strategy in JSON format:
{
  "elevatedBrandIdentity": {
    "colorPalette": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
    "typography": {
      "primary": "modern font family name",
      "secondary": "complementary font family"
    },
    "visualStyle": "detailed description of the elevated visual approach",
    "mood": ["sophisticated", "playful", etc.],
    "designPrinciples": ["principle 1", "principle 2", etc.]
  },
  "campaignConcepts": [
    {
      "name": "Campaign 1 Name",
      "description": "campaign description",
      "targetAudience": "specific audience segment",
      "keyMessage": "core message",
      "visualDirection": "how visuals should look and feel"
    }
  ],
  "productCreativeDirection": {
    "photographyStyle": "product photography approach",
    "layoutPrinciples": ["layout guideline 1", "layout guideline 2"],
    "colorTreatment": "how to use the color palette",
    "typographyUsage": "how to use typography effectively"
  },
  "beforeAfterNarrative": "compelling story of transformation"
}

Focus on creating a premium, modern brand identity that elevates the current state.`;

  try {
    const response = await openai.chat.completions.create({
      model: RESEARCH_MODEL,
      messages: [
        {
          role: "system",
          content: "You are a world-class Creative Director. Develop sophisticated, strategic creative direction. Output only valid JSON."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" }
    });

    const strategy = JSON.parse(response.choices[0].message.content || '{}');
    return strategy;
  } catch (error: any) {
    throw new Error(`Creative strategy development failed: ${error.message}`);
  }
}

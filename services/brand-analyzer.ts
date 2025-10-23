import { openai, RESEARCH_MODEL } from './openai-client';
import { BrandVisualData, ProductSKU } from './web-scraper';

export interface BrandAnalysis {
  qualityScore: number;
  strengths: string[];
  weaknesses: string[];
  designElements: {
    colorPalette: string[];
    typography: string[];
    visualStyle: string;
  };
  brandVoice: {
    tone: string;
    personality: string[];
    messagingThemes: string[];
  };
  industry: string;
  targetAudience: string;
  needsOverhaul: boolean;
  recommendations: string[];
}

export async function analyzeBrand(
  websiteUrl: string,
  visualData: BrandVisualData,
  rawContent: string,
  products: ProductSKU[]
): Promise<BrandAnalysis> {
  const prompt = `You are an expert brand strategist from a top creative agency. Analyze this brand's website and provide a comprehensive assessment.

WEBSITE URL: ${websiteUrl}

VISUAL DATA:
- Colors found: ${visualData.colors.join(', ')}
- Typography: ${visualData.typography.join(', ')}
- Number of images: ${visualData.imageUrls.length}
- Logo URL: ${visualData.logoUrl || 'Not found'}

WEBSITE CONTENT SAMPLE:
${rawContent.slice(0, 3000)}

PRODUCTS (${products.length} found):
${products.slice(0, 10).map(p => `- ${p.name} (SKU: ${p.sku})`).join('\n')}

Provide a detailed analysis in JSON format:
{
  "qualityScore": 1-100,
  "strengths": ["list of what works well"],
  "weaknesses": ["list of issues"],
  "designElements": {
    "colorPalette": ["dominant colors in hex"],
    "typography": ["font families detected"],
    "visualStyle": "description of current visual style"
  },
  "brandVoice": {
    "tone": "current tone description",
    "personality": ["brand personality traits"],
    "messagingThemes": ["key themes in messaging"]
  },
  "industry": "industry/category",
  "targetAudience": "target demographic description",
  "needsOverhaul": true/false (true if quality score < 60),
  "recommendations": ["specific improvement suggestions"]
}`;

  try {
    const response = await openai.chat.completions.create({
      model: RESEARCH_MODEL,
      messages: [
        {
          role: "system",
          content: "You are a world-class brand strategist. Provide honest, professional assessments. Output only valid JSON."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" }
    });

    const analysis = JSON.parse(response.choices[0].message.content || '{}');
    return analysis;
  } catch (error: any) {
    throw new Error(`Brand analysis failed: ${error.message}`);
  }
}

import { openai, RESEARCH_MODEL } from './openai-client';

export interface CompetitorInsight {
  name: string;
  website?: string;
  strengths: string[];
  visualStyle: string;
  positioning: string;
  uniqueFeatures: string[];
}

export interface CompetitorAnalysis {
  competitors: CompetitorInsight[];
  marketGaps: string[];
  differentiationOpportunities: string[];
  industryTrends: string[];
}

export async function researchCompetitors(
  brandName: string,
  industry: string,
  websiteUrl: string
): Promise<CompetitorAnalysis> {
  const prompt = `You are a market research expert. Research and analyze competitors for this brand:

BRAND: ${brandName}
INDUSTRY: ${industry}
WEBSITE: ${websiteUrl}

Tasks:
1. Identify 5-7 top competitors in this space
2. Analyze their visual branding strategies
3. Identify market gaps and differentiation opportunities
4. Note current industry design and marketing trends

Provide analysis in JSON format:
{
  "competitors": [
    {
      "name": "competitor name",
      "website": "url if known",
      "strengths": ["what they do well"],
      "visualStyle": "description of their design approach",
      "positioning": "their market positioning",
      "uniqueFeatures": ["what makes them stand out"]
    }
  ],
  "marketGaps": ["opportunities not being addressed"],
  "differentiationOpportunities": ["ways to stand out"],
  "industryTrends": ["current trends in this industry"]
}`;

  try {
    const response = await openai.chat.completions.create({
      model: RESEARCH_MODEL,
      messages: [
        {
          role: "system",
          content: "You are an expert market researcher. Provide comprehensive competitive analysis. Output only valid JSON."
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
    throw new Error(`Competitor research failed: ${error.message}`);
  }
}

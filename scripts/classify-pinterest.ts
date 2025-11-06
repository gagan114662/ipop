// Script to classify Pinterest images by industry using AI
import OpenAI from 'openai';
import * as fs from 'fs';
import * as path from 'path';

// Use free OpenRouter model for classification
const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY || 'sk-or-v1-f0824c7471797e4e49eebcc52b81a2a8e3571f04d5b9fd9715b7ea822826632bb',
  baseURL: 'https://openrouter.ai/api/v1',
  defaultHeaders: {
    'HTTP-Referer': 'https://motiacreative-development.local',
    'X-Title': 'Motia Creative - Pinterest Classification',
  },
});

interface ImageClassification {
  filename: string;
  filepath: string;
  industry: string;
  subCategory: string;
  designStyle: string[];
  confidence: number;
  reasoning: string;
}

interface ClassificationStats {
  totalImages: number;
  industries: {
    [industry: string]: {
      count: number;
      images: string[];
    };
  };
  underrepresented: string[];
  recommended: string[];
}

const INDUSTRIES = [
  'Fashion & Apparel',
  'Beauty & Cosmetics',
  'Food & Beverage',
  'Technology & Electronics',
  'Home & Interior Design',
  'Fitness & Wellness',
  'Automotive',
  'Travel & Hospitality',
  'Jewelry & Accessories',
  'Art & Crafts',
  'Sports & Recreation',
  'Luxury Goods',
  'Entertainment & Media',
  'Other',
];

const TARGET_IMAGES_PER_INDUSTRY = 50;
const INPUT_DIR = './reference-cache/images/pinterest/raw';
const OUTPUT_FILE = './reference-cache/pinterest-classifications.json';

async function classifyImage(imagePath: string): Promise<ImageClassification> {
  console.log(`\n🔍 Analyzing: ${path.basename(imagePath)}`);

  // Read image and convert to base64
  const imageBuffer = fs.readFileSync(imagePath);
  const base64Image = imageBuffer.toString('base64');
  const ext = path.extname(imagePath).toLowerCase();
  const mimeType = ext === '.png' ? 'image/png' : ext === '.webp' ? 'image/webp' : 'image/jpeg';

  try {
    const response = await openai.chat.completions.create({
      model: 'google/gemini-flash-1.5',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: `Analyze this creative/advertising image and classify it.

Determine:
1. PRIMARY INDUSTRY: Which industry? Choose from:
   ${INDUSTRIES.join(', ')}

2. SUB-CATEGORY: Specific category (e.g., "Women's Fashion", "Skincare", "Fine Dining")

3. DESIGN STYLE: Design aesthetic elements (e.g., ["minimalist", "bold typography", "vibrant colors"])

4. CONFIDENCE: Classification confidence (0-100)

5. REASONING: Brief explanation

Respond in JSON:
{
  "industry": "...",
  "subCategory": "...",
  "designStyle": ["...", "..."],
  "confidence": 95,
  "reasoning": "..."
}`,
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:${mimeType};base64,${base64Image}`,
              },
            },
          ],
        },
      ],
      max_tokens: 500,
    });

    const content = response.choices[0].message.content || '{}';

    // Extract JSON from response
    let jsonStr = content;
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/) || content.match(/```\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonStr = jsonMatch[1];
    }

    const classification = JSON.parse(jsonStr);

    console.log(`   Industry: ${classification.industry}`);
    console.log(`   Sub-category: ${classification.subCategory}`);
    console.log(`   Style: ${classification.designStyle.join(', ')}`);
    console.log(`   Confidence: ${classification.confidence}%`);

    return {
      filename: path.basename(imagePath),
      filepath: imagePath,
      industry: classification.industry,
      subCategory: classification.subCategory,
      designStyle: classification.designStyle,
      confidence: classification.confidence,
      reasoning: classification.reasoning,
    };
  } catch (error: any) {
    console.error(`   ❌ Error: ${error.message}`);

    return {
      filename: path.basename(imagePath),
      filepath: imagePath,
      industry: 'Other',
      subCategory: 'Unknown',
      designStyle: ['unknown'],
      confidence: 0,
      reasoning: `Error: ${error.message}`,
    };
  }
}

async function classifyAllImages() {
  console.log('='.repeat(80));
  console.log('PINTEREST IMAGE CLASSIFICATION');
  console.log('='.repeat(80));

  // Find all images
  const imageFiles = fs.readdirSync(INPUT_DIR)
    .filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ['.jpg', '.jpeg', '.png', '.webp'].includes(ext);
    })
    .map(file => path.join(INPUT_DIR, file));

  console.log(`\n📊 Found ${imageFiles.length} images to classify\n`);

  if (imageFiles.length === 0) {
    console.error('❌ No images found. Please run the Pinterest scraper first.');
    process.exit(1);
  }

  const classifications: ImageClassification[] = [];

  // Classify each image
  for (let i = 0; i < imageFiles.length; i++) {
    console.log(`\n[${i + 1}/${imageFiles.length}]`);

    const classification = await classifyImage(imageFiles[i]);
    classifications.push(classification);

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  // Generate statistics
  console.log('\n' + '='.repeat(80));
  console.log('GENERATING STATISTICS');
  console.log('='.repeat(80));

  const stats: ClassificationStats = {
    totalImages: classifications.length,
    industries: {},
    underrepresented: [],
    recommended: [],
  };

  // Count by industry
  classifications.forEach(c => {
    if (!stats.industries[c.industry]) {
      stats.industries[c.industry] = { count: 0, images: [] };
    }
    stats.industries[c.industry].count++;
    stats.industries[c.industry].images.push(c.filename);
  });

  // Identify underrepresented industries
  INDUSTRIES.forEach(industry => {
    const count = stats.industries[industry]?.count || 0;
    if (count < TARGET_IMAGES_PER_INDUSTRY) {
      stats.underrepresented.push(industry);
      const needed = TARGET_IMAGES_PER_INDUSTRY - count;
      stats.recommended.push(`${industry}: need ${needed} more images`);
    }
  });

  // Save results
  const output = {
    classifiedAt: new Date().toISOString(),
    totalImages: classifications.length,
    classifications,
    stats,
  };

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  console.log(`\n✅ Classifications saved to: ${OUTPUT_FILE}`);

  // Print report
  console.log('\n' + '='.repeat(80));
  console.log('CLASSIFICATION REPORT');
  console.log('='.repeat(80));

  console.log(`\n📊 INDUSTRY DISTRIBUTION:\n`);
  Object.entries(stats.industries)
    .sort((a, b) => b[1].count - a[1].count)
    .forEach(([industry, data]) => {
      const percentage = ((data.count / stats.totalImages) * 100).toFixed(1);
      const bar = '█'.repeat(Math.round(data.count / 2));
      console.log(`${industry.padEnd(30)} ${data.count.toString().padStart(3)} (${percentage.padStart(5)}%)  ${bar}`);
    });

  console.log(`\n🎯 GAP ANALYSIS:\n`);
  if (stats.underrepresented.length === 0) {
    console.log('✅ All industries well-represented!');
  } else {
    console.log(`⚠️  ${stats.underrepresented.length} industries need more images:\n`);
    stats.recommended.forEach(rec => console.log(`   • ${rec}`));
  }

  console.log(`\n✅ NEXT STEPS:\n`);
  console.log(`   1. Review classifications in: ${OUTPUT_FILE}`);
  console.log(`   2. Run targeted searches for underrepresented industries`);
  console.log(`   3. Organize images into industry-specific folders`);
  console.log(`   4. Prepare datasets for LoRA training\n`);

  return output;
}

// Run the classification
classifyAllImages()
  .then(() => {
    console.log('\n✅ Classification complete!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Classification failed:', error);
    process.exit(1);
  });

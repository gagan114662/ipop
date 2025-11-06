// Script to reorganize Behance images by industry instead of creative category
import * as fs from 'fs';
import * as path from 'path';
import { openai } from '../services/openai-client';

const METADATA_FILE = './reference-cache/behance-appreciated-metadata.json';
const SOURCE_DIR = './reference-cache/images/behance/appreciated';
const OUTPUT_DIR = './reference-cache/images/behance/by-industry';

// Industry categories for organizing creative work
const INDUSTRIES = [
  'fashion-apparel',
  'food-beverage',
  'automotive',
  'real-estate',
  'technology',
  'beauty-cosmetics',
  'finance-banking',
  'healthcare-pharma',
  'sports-fitness',
  'travel-hospitality',
  'retail-ecommerce',
  'entertainment-media',
  'luxury-goods',
  'consumer-electronics',
  'home-furniture',
  'abstract-conceptual', // For non-specific/artistic designs
];

interface BehanceProject {
  title: string;
  url: string;
  category: string;
  appreciations: number;
  views: number;
  owner: string;
  imageCount: number;
}

interface Metadata {
  scrapedAt: string;
  categories: string[];
  minAppreciations: number;
  projectsFound: number;
  totalImagesDownloaded: number;
  projects: BehanceProject[];
}

class IndustryOrganizer {
  private metadata: Metadata;

  constructor() {
    this.metadata = JSON.parse(fs.readFileSync(METADATA_FILE, 'utf-8'));
  }

  analyzeProjectIndustry(project: BehanceProject): string {
    const text = `${project.title} ${project.category} ${project.owner}`.toLowerCase();

    // Rule-based classification using keywords
    const rules = [
      {
        industry: 'fashion-apparel',
        keywords: ['fashion', 'apparel', 'clothing', 'shoe', 'sneaker', 'footwear', 'nike', 'adidas', 'vans', 'puma', 'outfit', 'garment', 'textile', 'wardrobe', 'style'],
      },
      {
        industry: 'food-beverage',
        keywords: ['food', 'beverage', 'restaurant', 'coffee', 'tea', 'drink', 'beer', 'wine', 'cafe', 'bakery', 'cuisine', 'pasta', 'coca-cola', 'pepsi', 'cider', 'smoothie', 'cocktail'],
      },
      {
        industry: 'automotive',
        keywords: ['car', 'auto', 'vehicle', 'ferrari', 'audi', 'bike', 'motorcycle', 'truck', 'automotive', 'tesla', 'bmw', 'mercedes', 'porsche'],
      },
      {
        industry: 'real-estate',
        keywords: ['real estate', 'property', 'housing', 'apartment', 'building', 'architecture', 'realty', 'home'],
      },
      {
        industry: 'technology',
        keywords: ['tech', 'technology', 'software', 'app', 'digital', 'ai ', 'data', 'cloud', 'apple', 'samsung', 'microsoft', 'google', 'airpods', 'iphone', 'dualsense', 'controller'],
      },
      {
        industry: 'beauty-cosmetics',
        keywords: ['beauty', 'cosmetic', 'makeup', 'skincare', 'perfume', 'fragrance', 'loreal', 'sephora', 'lipstick', 'mascara', 'serum', 'cream'],
      },
      {
        industry: 'finance-banking',
        keywords: ['bank', 'finance', 'investment', 'credit', 'loan', 'insurance', 'crypto', 'wallet', 'payment', 'itau', 'prudential'],
      },
      {
        industry: 'healthcare-pharma',
        keywords: ['health', 'medical', 'pharma', 'hospital', 'clinic', 'medicine', 'drug', 'therapy', 'wellness', 'vitamin'],
      },
      {
        industry: 'sports-fitness',
        keywords: ['sport', 'fitness', 'gym', 'workout', 'athlete', 'running', 'soccer', 'football', 'basketball', 'tennis', 'yoga'],
      },
      {
        industry: 'travel-hospitality',
        keywords: ['travel', 'hotel', 'tourism', 'vacation', 'airline', 'resort', 'hospitality', 'booking', 'trip', 'destination'],
      },
      {
        industry: 'retail-ecommerce',
        keywords: ['retail', 'ecommerce', 'shop', 'store', 'marketplace', 'shopping', 'amazon', 'ebay', 'tiki'],
      },
      {
        industry: 'entertainment-media',
        keywords: ['entertainment', 'media', 'movie', 'film', 'music', 'concert', 'festival', 'streaming', 'netflix', 'spotify', 'game', 'gaming', 'macbeth', 'bfi'],
      },
      {
        industry: 'luxury-goods',
        keywords: ['luxury', 'premium', 'exclusive', 'haute', 'rolex', 'gucci', 'louis vuitton', 'chanel', 'dior', 'cartier', 'jewelry', 'diamond'],
      },
      {
        industry: 'consumer-electronics',
        keywords: ['electronics', 'gadget', 'device', 'smart', 'wearable', 'iot', 'sensor'],
      },
      {
        industry: 'home-furniture',
        keywords: ['furniture', 'decor', 'interior', 'home', 'table', 'chair', 'sofa', 'lamp', 'ikea'],
      },
    ];

    // Score each industry based on keyword matches
    const scores: Record<string, number> = {};

    for (const rule of rules) {
      let score = 0;
      for (const keyword of rule.keywords) {
        if (text.includes(keyword)) {
          score += keyword.length; // Longer keywords get more weight
        }
      }
      if (score > 0) {
        scores[rule.industry] = score;
      }
    }

    // Return industry with highest score
    if (Object.keys(scores).length > 0) {
      const sortedIndustries = Object.entries(scores).sort((a, b) => b[1] - a[1]);
      return sortedIndustries[0][0];
    }

    // Default to abstract-conceptual for posters, designs without clear industry
    return 'abstract-conceptual';
  }

  async organizeByIndustry(): Promise<void> {
    console.log('='.repeat(80));
    console.log('ORGANIZING BEHANCE IMAGES BY INDUSTRY');
    console.log('='.repeat(80));
    console.log(`Total projects: ${this.metadata.projects.length}`);
    console.log(`Source: ${SOURCE_DIR}`);
    console.log(`Output: ${OUTPUT_DIR}\n`);

    // Create output directory
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Create industry subdirectories
    INDUSTRIES.forEach((industry) => {
      const industryDir = path.join(OUTPUT_DIR, industry);
      if (!fs.existsSync(industryDir)) {
        fs.mkdirSync(industryDir, { recursive: true });
      }
    });

    const industryMapping: Record<string, BehanceProject[]> = {};
    const uniqueProjects = this.getUniqueProjects();

    console.log(`Analyzing ${uniqueProjects.length} unique projects...\n`);

    let processed = 0;
    for (const project of uniqueProjects) {
      processed++;
      console.log(`[${processed}/${uniqueProjects.length}] Analyzing: ${project.title}`);

      const industry = this.analyzeProjectIndustry(project);
      console.log(`  ➜ Industry: ${industry}`);

      if (!industryMapping[industry]) {
        industryMapping[industry] = [];
      }
      industryMapping[industry].push(project);

      // Find and copy project images
      const projectImages = this.findProjectImages(project);
      if (projectImages.length > 0) {
        this.copyProjectImages(project, projectImages, industry);
        console.log(`  ✓ Copied ${projectImages.length} images\n`);
      } else {
        console.log(`  ✗ No images found\n`);
      }
    }

    // Save industry mapping metadata
    this.saveIndustryMetadata(industryMapping);

    // Print summary
    this.printSummary(industryMapping);
  }

  private getUniqueProjects(): BehanceProject[] {
    const uniqueMap = new Map<string, BehanceProject>();
    this.metadata.projects.forEach((project) => {
      if (!uniqueMap.has(project.url)) {
        uniqueMap.set(project.url, project);
      }
    });
    return Array.from(uniqueMap.values());
  }

  private findProjectImages(project: BehanceProject): string[] {
    const sanitizedTitle = project.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 50);
    const sanitizedCategory = project.category.replace(/[^a-z0-9]/gi, '-').toLowerCase();
    const projectDirName = `${sanitizedTitle}-${project.appreciations}app`;

    const possiblePaths = [
      path.join(SOURCE_DIR, sanitizedCategory, projectDirName),
      path.join(SOURCE_DIR, project.category.replace(/ /g, '-'), projectDirName),
    ];

    for (const dirPath of possiblePaths) {
      if (fs.existsSync(dirPath)) {
        const files = fs.readdirSync(dirPath);
        return files
          .filter((f) => f.match(/\.(jpg|jpeg|png|gif)$/i))
          .map((f) => path.join(dirPath, f));
      }
    }

    return [];
  }

  private copyProjectImages(project: BehanceProject, imagePaths: string[], industry: string): void {
    const sanitizedTitle = project.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 50);
    const projectDirName = `${sanitizedTitle}-${project.appreciations}app`;
    const targetDir = path.join(OUTPUT_DIR, industry, projectDirName);

    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    imagePaths.forEach((imagePath) => {
      const filename = path.basename(imagePath);
      const targetPath = path.join(targetDir, filename);
      fs.copyFileSync(imagePath, targetPath);
    });
  }

  private saveIndustryMetadata(industryMapping: Record<string, BehanceProject[]>): void {
    const metadata = {
      organizedAt: new Date().toISOString(),
      sourceDirectory: SOURCE_DIR,
      outputDirectory: OUTPUT_DIR,
      industries: INDUSTRIES,
      mapping: Object.entries(industryMapping).map(([industry, projects]) => ({
        industry,
        projectCount: projects.length,
        projects: projects.map((p) => ({
          title: p.title,
          url: p.url,
          appreciations: p.appreciations,
          views: p.views,
          owner: p.owner,
          originalCategory: p.category,
        })),
      })),
    };

    const metadataPath = path.join(OUTPUT_DIR, 'industry-mapping.json');
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    console.log(`\n✓ Metadata saved: ${metadataPath}`);
  }

  private printSummary(industryMapping: Record<string, BehanceProject[]>): void {
    console.log('\n' + '='.repeat(80));
    console.log('ORGANIZATION COMPLETE!');
    console.log('='.repeat(80));

    const sortedIndustries = Object.entries(industryMapping)
      .sort((a, b) => b[1].length - a[1].length)
      .filter(([_, projects]) => projects.length > 0);

    console.log('\n📊 PROJECTS BY INDUSTRY:\n');
    sortedIndustries.forEach(([industry, projects]) => {
      const totalImages = projects.reduce((sum, p) => sum + this.findProjectImages(p).length, 0);
      console.log(`  ${industry.padEnd(25)} ${projects.length.toString().padStart(3)} projects | ${totalImages.toString().padStart(4)} images`);
    });

    console.log('\n' + '─'.repeat(80));
    console.log(`Output directory: ${OUTPUT_DIR}`);
    console.log('─'.repeat(80) + '\n');
  }
}

async function main() {
  const organizer = new IndustryOrganizer();
  await organizer.organizeByIndustry();
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});

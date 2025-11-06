// Export all SKUs from a campaign to a folder
import * as fs from 'fs';
import * as path from 'path';

const campaignId = process.argv[2] || 'campaign_1762266359283_8yghi97pl';
const outputDir = './extracted-skus';

async function exportSKUs() {
  try {
    // Read campaign state from .local/kv/state/campaigns/
    const statePath = `./.local/kv/state/campaigns/${campaignId}.json`;

    if (!fs.existsSync(statePath)) {
      console.error(`Campaign not found: ${statePath}`);
      process.exit(1);
    }

    const campaignData = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
    const products = campaignData.products || [];

    console.log(`Found ${products.length} products in campaign ${campaignId}`);

    // Create output directory
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Export product list as JSON
    const productList = products.map((p: any, index: number) => ({
      index: index + 1,
      sku: p.sku,
      name: p.name,
      price: p.price,
      category: p.category,
      url: p.url,
      imageUrl: p.imageUrl,
      description: p.description?.substring(0, 200),
    }));

    fs.writeFileSync(
      path.join(outputDir, 'products.json'),
      JSON.stringify(productList, null, 2)
    );

    // Export as readable text file
    let textOutput = `EXTRACTED SKUS FROM: ${campaignData.brandName}\n`;
    textOutput += `Website: ${campaignData.websiteUrl}\n`;
    textOutput += `Total Products: ${products.length}\n`;
    textOutput += `\n${'='.repeat(80)}\n\n`;

    productList.forEach((p: any) => {
      textOutput += `${p.index}. ${p.name}\n`;
      textOutput += `   SKU: ${p.sku}\n`;
      textOutput += `   Price: ${p.price || 'N/A'}\n`;
      textOutput += `   Category: ${p.category || 'N/A'}\n`;
      textOutput += `   URL: ${p.url}\n`;
      if (p.imageUrl) {
        textOutput += `   Image: ${p.imageUrl}\n`;
      }
      textOutput += `\n`;
    });

    fs.writeFileSync(path.join(outputDir, 'products.txt'), textOutput);

    console.log(`\n✓ Exported ${products.length} SKUs to ${outputDir}/`);
    console.log(`  - products.json (structured data)`);
    console.log(`  - products.txt (human-readable)`);

    // Print first 5 products
    console.log(`\nFirst 5 products:`);
    productList.slice(0, 5).forEach((p: any) => {
      console.log(`  ${p.index}. ${p.name} (${p.sku}) - ${p.price || 'N/A'}`);
    });

  } catch (error: any) {
    console.error('Export failed:', error.message);
    process.exit(1);
  }
}

exportSKUs();

import { ApiRouteConfig, Handlers } from 'motia';
import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'ExportSKUs',
  description: 'Export all extracted SKUs from a campaign to a folder',
  flows: ['marketing-agency'],

  method: 'GET',
  path: '/api/export-skus/:campaignId',
  responseSchema: {
    200: z.object({
      message: z.string(),
      skuCount: z.number(),
      outputPath: z.string(),
    }),
    404: z.object({
      error: z.string(),
    }),
  },
  emits: [],
};

export const handler: Handlers['ExportSKUs'] = async (req: any, { logger, state }: any) => {
  const params = req?.params ?? req?.pathParams ?? {};
  const campaignId = params?.campaignId;

  if (!campaignId) {
    return {
      status: 404,
      body: {
        error: 'campaignId parameter is required',
      },
    };
  }

  logger.info('Exporting SKUs for campaign', { campaignId });

  const campaign = await state.get('campaigns', campaignId);

  if (!campaign) {
    return {
      status: 404,
      body: {
        error: `Campaign ${campaignId} not found`,
      },
    };
  }

  const products = campaign.products || [];
  const outputDir = './extracted-skus';

  // Create output directory
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Export as JSON
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
    path.join(outputDir, `${campaignId}_products.json`),
    JSON.stringify(productList, null, 2)
  );

  // Export as text
  let textOutput = `EXTRACTED SKUS FROM: ${campaign.brandName}\n`;
  textOutput += `Website: ${campaign.websiteUrl}\n`;
  textOutput += `Campaign ID: ${campaignId}\n`;
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

  fs.writeFileSync(path.join(outputDir, `${campaignId}_products.txt`), textOutput);

  logger.info('SKUs exported', { count: products.length, outputDir });

  return {
    status: 200,
    body: {
      message: `Exported ${products.length} SKUs`,
      skuCount: products.length,
      outputPath: outputDir,
    },
  };
};

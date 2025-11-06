# LoRA Training Plan for Industry-Specific Creative Generation

## 🎯 Objective

Train industry-specific LoRAs (Low-Rank Adaptations) using high-quality design references from Pinterest's "Winners Campaign" aesthetic to improve creative output across different industries.

## 📋 Implementation Plan

### Phase 1: Data Collection ✅ (In Progress)

**Goal:** Collect 700+ high-quality creative references

**Tasks:**
- ✅ Build Pinterest scraper with Playwright
- ✅ Implement Google authentication
- ✅ Add cookie persistence
- ✅ Create scraping script for board + "More ideas"
- ⏳ Scrape https://ca.pinterest.com/sangichandresh/winners-campaign/
  - Target: 200 pins from board
  - Target: 500 pins from "More ideas"
  - Quality filter: Minimum 50KB file size

**Current Status:** Scraping in progress (61/700 images downloaded)

**Scripts:**
```bash
npm run pinterest-login     # One-time manual login
npm run scrape-pinterest    # Run the scraper
```

---

### Phase 2: Industry Classification ✅ (Ready)

**Goal:** Categorize images by industry using AI

**Method:**
- Use GPT-4o Vision to analyze each image
- Classify into 14 industry categories
- Extract design style attributes
- Calculate confidence scores

**Industries:**
1. Fashion & Apparel
2. Beauty & Cosmetics
3. Food & Beverage
4. Technology & Electronics
5. Home & Interior Design
6. Fitness & Wellness
7. Automotive
8. Travel & Hospitality
9. Jewelry & Accessories
10. Art & Crafts
11. Sports & Recreation
12. Luxury Goods
13. Entertainment & Media
14. Other

**Output:**
- `reference-cache/pinterest-classifications.json`
- Industry distribution statistics
- Gap analysis report

**Scripts:**
```bash
npm run classify-pinterest
```

---

### Phase 3: Gap Analysis 🔜

**Goal:** Identify underrepresented industries

**Approach:**
- Target: 50+ images per industry
- Identify which industries need more samples
- Generate search queries for gap filling

**Expected Gaps:**
Based on "Winners Campaign" aesthetic, we expect gaps in:
- Technology & Electronics
- Automotive
- Travel & Hospitality
- Sports & Recreation

---

### Phase 4: Targeted Search & Gap Filling 🔜

**Goal:** Fill industry gaps with targeted Pinterest searches

**Method:**
1. For each underrepresented industry:
   - Generate industry-specific search queries
   - Use `scraper.searchPins(query, maxPins)`
   - Download images matching the aesthetic
2. Re-run classification
3. Iterate until all industries hit target

**Example Searches:**
- "modern tech product photography minimalist"
- "luxury automotive advertising campaign"
- "premium sports brand creative"

**Script to Create:**
```bash
npm run fill-gaps
```

---

### Phase 5: Dataset Organization 🔜

**Goal:** Organize images into industry-specific folders for training

**Structure:**
```
lora-training-data/
├── fashion-apparel/
│   ├── image001.jpg
│   ├── image002.jpg
│   └── metadata.json
├── beauty-cosmetics/
│   ├── image001.jpg
│   └── metadata.json
├── food-beverage/
│   └── ...
└── [other industries]/
```

**Metadata Format:**
```json
{
  "images": [
    {
      "filename": "image001.jpg",
      "originalUrl": "https://pinterest.com/pin/...",
      "subCategory": "Women's Fashion",
      "designStyle": ["minimalist", "bold typography", "vibrant colors"],
      "confidence": 95
    }
  ],
  "industry": "Fashion & Apparel",
  "totalImages": 87,
  "avgConfidence": 92.3
}
```

---

### Phase 6: LoRA Training Configuration 🔜

**Goal:** Define training parameters for each industry LoRA

**Recommended Tools:**
- **Kohya_ss** - Popular LoRA training GUI
- **AUTOMATIC1111 + Dreambooth** - Alternative approach
- **Replicate** - Cloud-based training (easiest)

**Training Parameters (Starting Point):**
```yaml
base_model: "stable-diffusion-xl-base-1.0" # or Flux
resolution: 1024x1024
training_steps: 1000-2000 per industry
batch_size: 1-4 (depending on VRAM)
learning_rate: 1e-4
network_dim: 32-64 (LoRA rank)
network_alpha: 16-32
optimizer: AdamW8bit
lr_scheduler: cosine_with_restarts
```

**Per-Industry Training:**
Each industry gets its own LoRA trained on:
- Minimum 50 curated images
- Consistent "Winners Campaign" aesthetic
- Industry-specific visual patterns

---

### Phase 7: Testing & Validation 🔜

**Goal:** Validate LoRA output quality

**Test Prompts (Per Industry):**
```
Fashion: "luxury fashion campaign, minimalist background, bold typography"
Beauty: "premium cosmetics product shot, clean aesthetic, soft lighting"
Food: "gourmet food photography, modern plating, vibrant colors"
Tech: "sleek tech product, futuristic design, minimalist composition"
```

**Quality Metrics:**
- ✅ Maintains "Winners Campaign" aesthetic
- ✅ Industry-appropriate imagery
- ✅ High visual quality
- ✅ Consistent brand feel
- ✅ Flexible enough for variations

---

### Phase 8: Integration 🔜

**Goal:** Integrate LoRAs into creative generation pipeline

**Implementation:**
1. Host LoRAs (Replicate, HuggingFace, or self-hosted)
2. Update `creative-generator.ts` to:
   - Detect industry from product SKU
   - Load appropriate LoRA
   - Generate with industry-specific prompt templates
3. A/B test against current Gemini output

**Expected Improvement:**
- Better industry-specific aesthetics
- More consistent "winners" look
- Higher conversion rates for creatives

---

## 📊 Success Metrics

### Data Quality
- [ ] 700+ images collected
- [ ] 50+ images per major industry
- [ ] Average confidence > 85%
- [ ] <5% "Other" category

### Training Quality
- [ ] LoRAs generate industry-appropriate images
- [ ] Maintains consistent aesthetic across industries
- [ ] Fast inference (<10s per image)
- [ ] Works with various prompts

### Business Impact
- [ ] Creatives match "Winners Campaign" quality
- [ ] Reduced manual curation time
- [ ] Higher client satisfaction
- [ ] Measurable conversion lift

---

## 🔧 Technical Stack

**Scraping:**
- Playwright (browser automation)
- TypeScript
- Pinterest API (unofficial)

**Classification:**
- OpenAI GPT-4o Vision
- Custom classification logic

**Training:**
- Kohya_ss / Replicate / AUTOMATIC1111
- Stable Diffusion XL or Flux
- LoRA technique

**Inference:**
- Integrated with existing Gemini pipeline
- OR replace with SDXL + LoRAs

---

## 📁 File Structure

```
motiacreative-development/
├── scripts/
│   ├── scrape-pinterest-at-scale.ts      ✅ Done
│   ├── pinterest-manual-login.ts         ✅ Done
│   ├── classify-pinterest.ts             ✅ Done
│   ├── fill-gaps.ts                      🔜 TODO
│   ├── organize-datasets.ts              🔜 TODO
│   └── test-loras.ts                     🔜 TODO
├── services/
│   ├── pinterest-scraper.ts              ✅ Done
│   └── creative-generator.ts             🔄 To update
├── reference-cache/
│   ├── images/pinterest/raw/             ✅ In progress
│   ├── pinterest-metadata.json           ⏳ Generated after scrape
│   └── pinterest-classifications.json    🔜 After classification
├── lora-training-data/                   🔜 To create
└── trained-loras/                        🔜 To create
```

---

## 📝 Next Steps

1. ⏳ **Wait for scraper to complete** (currently at 61/700)
2. 🔜 **Run classification:** `npm run classify-pinterest`
3. 🔜 **Analyze gaps** in the classification report
4. 🔜 **Build gap-filling script** for targeted searches
5. 🔜 **Organize datasets** by industry
6. 🔜 **Research LoRA training options** (Replicate vs local)
7. 🔜 **Train first LoRA** (start with best-represented industry)
8. 🔜 **Validate & iterate**

---

## 💡 Notes & Considerations

**Aesthetic Consistency:**
The "Winners Campaign" board has a specific aesthetic:
- High-end, premium feel
- Bold, modern design
- Clean composition
- Professional photography
- Aspirational quality

All training data must maintain this aesthetic to ensure LoRAs generate consistent quality.

**Industry Diversity:**
Some industries may naturally have fewer examples in the source board. Targeted searches will need to filter for both:
1. Industry relevance
2. Aesthetic match

**Training Time:**
- Local training: 1-4 hours per LoRA (with GPU)
- Replicate: $0.50-2.00 per LoRA training run
- Can parallelize training across industries

**Alternative Approach:**
Instead of 14 separate LoRAs, could train:
1. One "Winners Aesthetic" LoRA (all images)
2. Use industry-specific prompts
3. Simpler to maintain, may lose some industry specificity

---

**Last Updated:** 2025-11-04
**Status:** Phase 1 - Data Collection (In Progress)

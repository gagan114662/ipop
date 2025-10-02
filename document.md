Platform Compatibility Matrix:

Platform	Content Type	Dimensions	Max Duration	Format
TikTok Short	Video	1080×1920	60s	MP4
Instagram Reel	Both	1080×1920	90s	MP4/JPG
Instagram Feed	Image	1080×1080	-	JPG
Instagram Story	Both	1080×1920	15s	MP4/JPG
YouTube Short	Video	1080×1920	60s	MP4
Facebook Feed	Both	1200×630	240s	MP4/JPG
Twitter/X Post	Both	1200×675	140s	MP4/JPG
LinkedIn Post	Both	1200×627	600s	MP4/JPG


Example Processing Scenarios:

Scenario 1: Upload 4K Image (3840×2160)

Instagram Feed (1080×1080): Scales down to 1080×608, centers with padding
TikTok (1080×1920): Scales down to 607×1080, centers with padding
Facebook Feed (1200×630): Scales down to 1120×630, centers with padding
Scenario 2: Upload Landscape Video (1920×1080, 120s)

TikTok: Scales to 607×1080, adds padding, trims to 60s
Instagram Reel: Scales to 607×1080, adds padding, trims to 90s
YouTube Short: Scales to 607×1080, adds padding, trims to 60s
Scenario 3: Upload Portrait Video (1080×1920, 30s)

All vertical platforms: Direct resize to 1080×1920 (perfect fit)
Horizontal platforms: Scales to fit width, adds top/bottom padding
The worker intelligently handles both formats and ensures compatibility with each platform's requirements while maintaining quality and aspect ratios!
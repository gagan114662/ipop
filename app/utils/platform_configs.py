# # app/utils/platform_configs.py
# from dataclasses import dataclass
# from typing import Dict, List, Optional, Tuple
# from enum import Enum


# class ContentType(str, Enum):
#     IMAGE = "image"
#     VIDEO = "video"
#     BOTH = "both"


# @dataclass
# class PlatformSpec:
#     """Platform specification for content resizing"""
#     id: str
#     name: str
#     display_name: str
#     dimensions: Tuple[int, int]  # (width, height)
#     content_type: ContentType
#     max_duration: Optional[int] = None  # seconds for video
#     format_preference: List[str] = None  # preferred file formats
#     quality: int = 85  # compression quality
#     icon_url: Optional[str] = None

#     def __post_init__(self):
#         if self.format_preference is None:
#             if self.content_type == ContentType.VIDEO:
#                 self.format_preference = ["mp4"]
#             else:
#                 self.format_preference = ["jpg", "png"]


# # Platform configurations
# PLATFORM_CONFIGS: Dict[str, PlatformSpec] = {
#     "tiktok_short": PlatformSpec(
#         id="tiktok_short",
#         name="tiktok",
#         display_name="TikTok Short",
#         dimensions=(1080, 1920),
#         content_type=ContentType.VIDEO,
#         max_duration=60,
#         format_preference=["mp4"],
#         quality=90,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
#     ),
#     "instagram_reel": PlatformSpec(
#         id="instagram_reel",
#         name="instagram",
#         display_name="Instagram Reel",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=90,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_feed": PlatformSpec(
#         id="instagram_feed",
#         name="instagram",
#         display_name="Instagram Feed",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_story": PlatformSpec(
#         id="instagram_story",
#         name="instagram",
#         display_name="Instagram Story",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=15,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),

#         "instagram_feed_image": PlatformSpec(
#         id="instagram_feed_image",
#         name="instagram",
#         display_name="Instagram Feed (1:1)",
#         dimensions=(1440, 1440),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_profile_feed_image": PlatformSpec(
#         id="instagram_profile_feed_image",
#         name="instagram",
#         display_name="Instagram Profile Feed (1.91:1 → 4:5)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_story_image": PlatformSpec(
#         id="instagram_story_image",
#         name="instagram",
#         display_name="Instagram Story (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_reel_image": PlatformSpec(
#         id="instagram_reel_image",
#         name="instagram",
#         display_name="Instagram Reel Cover (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_carousel_feed_image": PlatformSpec(
#         id="instagram_carousel_feed_image",
#         name="instagram",
#         display_name="Instagram Carousel Feed (1:1)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_carousel_story_image": PlatformSpec(
#         id="instagram_carousel_story_image",
#         name="instagram",
#         display_name="Instagram Carousel Story (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=90,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_collection_feed_image": PlatformSpec(
#         id="instagram_collection_feed_image",
#         name="instagram",
#         display_name="Instagram Collection Feed (1:1)",
#         dimensions=(1080, 1080),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_collection_reel_image": PlatformSpec(
#         id="instagram_collection_reel_image",
#         name="instagram",
#         display_name="Instagram Collection Reel Cover (9:16)",
#         dimensions=(500, 888),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),
#     "instagram_explore_image": PlatformSpec(
#         id="instagram_explore_image",
#         name="instagram",
#         display_name="Instagram Explore (9:16)",
#         dimensions=(1080, 1920),
#         content_type=ContentType.IMAGE,
#         quality=88,
#         format_preference=["jpg"],
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
#     ),




#     "facebook_story": PlatformSpec(
#         id="facebook_story",
#         name="facebook",
#         display_name="Facebook Story",
#         dimensions=(1080, 1920),
#         content_type=ContentType.BOTH,
#         max_duration=20,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
#     ),
#     "facebook_feed": PlatformSpec(
#         id="facebook_feed",
#         name="facebook",
#         display_name="Facebook Feed",
#         dimensions=(1200, 630),
#         content_type=ContentType.BOTH,
#         max_duration=240,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
#     ),
#     "youtube_short": PlatformSpec(
#         id="youtube_short",
#         name="youtube",
#         display_name="YouTube Short",
#         dimensions=(1080, 1920),
#         content_type=ContentType.VIDEO,
#         max_duration=60,
#         format_preference=["mp4"],
#         quality=92,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
#     ),
#     "youtube_bumper": PlatformSpec(
#         id="youtube_bumper",
#         name="youtube",
#         display_name="YouTube Bumper",
#         dimensions=(1920, 1080),
#         content_type=ContentType.VIDEO,
#         max_duration=6,
#         format_preference=["mp4"],
#         quality=95,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
#     ),
#     "twitter_post": PlatformSpec(
#         id="twitter_post",
#         name="twitter",
#         display_name="Twitter/X Post",
#         dimensions=(1200, 675),
#         content_type=ContentType.BOTH,
#         max_duration=140,
#         format_preference=["mp4", "jpg"],
#         quality=85,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
#     ),
#     "linkedin_post": PlatformSpec(
#         id="linkedin_post",
#         name="linkedin",
#         display_name="LinkedIn Post",
#         dimensions=(1200, 627),
#         content_type=ContentType.BOTH,
#         max_duration=600,
#         format_preference=["mp4", "jpg"],
#         quality=88,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
#     ),
#     "google_display_medium": PlatformSpec(
#         id="google_display_medium",
#         name="google_ads",
#         display_name="Google Display (Medium Rectangle)",
#         dimensions=(300, 250),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg", "png"],
#         quality=80,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
#     ),
#     "google_display_banner": PlatformSpec(
#         id="google_display_banner",
#         name="google_ads",
#         display_name="Google Display (Banner)",
#         dimensions=(728, 90),
#         content_type=ContentType.IMAGE,
#         format_preference=["jpg", "png"],
#         quality=80,
#         icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
#     )
# }


# def get_compatible_platforms(content_type: str) -> List[PlatformSpec]:
#     """Get platforms compatible with content type"""
#     compatible = []
#     for platform in PLATFORM_CONFIGS.values():
#         if (platform.content_type == ContentType.BOTH or 
#             platform.content_type.value == content_type):
#             compatible.append(platform)
#     return compatible


# def get_platform_by_id(platform_id: str) -> Optional[PlatformSpec]:
#     """Get platform configuration by ID"""
#     return PLATFORM_CONFIGS.get(platform_id)




# def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
#     """Validate and filter platform IDs based on content type"""
#     from app.utils.platform_configs import PLATFORM_CONFIGS, ContentType

#     # 🔹 Auto-expand Instagram to all its image-based platform IDs
#     if "instagram" in platform_ids:
#         instagram_image_ids = [
#             pid for pid, p in PLATFORM_CONFIGS.items()
#             if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#         ]
#         platform_ids = instagram_image_ids

#     valid_platforms = []
#     compatible_platforms = get_compatible_platforms(content_type)
#     compatible_ids = {p.id for p in compatible_platforms}
#     for platform_id in platform_ids:
#         if platform_id in compatible_ids:
#             valid_platforms.append(platform_id)
#     return valid_platforms


# app/utils/platform_configs.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# =============================
# ENUM + DATA CLASS
# =============================

class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    BOTH = "both"


@dataclass
class PlatformSpec:
    """Platform specification for content resizing"""
    id: str
    name: str
    display_name: str
    dimensions: Tuple[int, int]  # (width, height)
    content_type: ContentType
    max_duration: Optional[int] = None  # seconds for video
    format_preference: List[str] = None  # preferred file formats
    quality: int = 85  # compression quality
    icon_url: Optional[str] = None

    def __post_init__(self):
        if self.format_preference is None:
            if self.content_type == ContentType.VIDEO:
                self.format_preference = ["mp4"]
            else:
                self.format_preference = ["jpg", "png"]


# =============================
# PLATFORM CONFIGURATIONS
# =============================

PLATFORM_CONFIGS: Dict[str, PlatformSpec] = {
    # --- Instagram Image Variants ---
    "instagram_feed_image": PlatformSpec(
        id="instagram_feed_image",
        name="instagram",
        display_name="Instagram Feed (1:1)",
        dimensions=(1440, 1440),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_profile_feed_image": PlatformSpec(
        id="instagram_profile_feed_image",
        name="instagram",
        display_name="Instagram Profile Feed (1.91:1 → 4:5)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_story_image": PlatformSpec(
        id="instagram_story_image",
        name="instagram",
        display_name="Instagram Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_reel_image": PlatformSpec(
        id="instagram_reel_image",
        name="instagram",
        display_name="Instagram Reel Cover (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_carousel_feed_image": PlatformSpec(
        id="instagram_carousel_feed_image",
        name="instagram",
        display_name="Instagram Carousel Feed (1:1)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_carousel_story_image": PlatformSpec(
        id="instagram_carousel_story_image",
        name="instagram",
        display_name="Instagram Carousel Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=90,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_collection_feed_image": PlatformSpec(
        id="instagram_collection_feed_image",
        name="instagram",
        display_name="Instagram Collection Feed (1:1)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_collection_reel_image": PlatformSpec(
        id="instagram_collection_reel_image",
        name="instagram",
        display_name="Instagram Collection Reel Cover (9:16)",
        dimensions=(500, 888),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
    "instagram_explore_image": PlatformSpec(
        id="instagram_explore_image",
        name="instagram",
        display_name="Instagram Explore (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        quality=88,
        format_preference=["jpg"],
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg"
    ),
        # --- Google Ads Display Image Variants ---
    "google_display_250x250": PlatformSpec(
        id="google_display_250x250",
        name="google_ads",
        display_name="Google Ads (250x250 – Square)",
        dimensions=(250, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_200x200": PlatformSpec(
        id="google_display_200x200",
        name="google_ads",
        display_name="Google Ads (200x200 – Small Square)",
        dimensions=(200, 200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_468x60": PlatformSpec(
        id="google_display_468x60",
        name="google_ads",
        display_name="Google Ads (468x60 – Banner)",
        dimensions=(468, 60),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_728x90": PlatformSpec(
        id="google_display_728x90",
        name="google_ads",
        display_name="Google Ads (728x90 – Leaderboard)",
        dimensions=(728, 90),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x250": PlatformSpec(
        id="google_display_300x250",
        name="google_ads",
        display_name="Google Ads (300x250 – Medium Rectangle)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_336x280": PlatformSpec(
        id="google_display_336x280",
        name="google_ads",
        display_name="Google Ads (336x280 – Large Rectangle)",
        dimensions=(336, 280),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_120x600": PlatformSpec(
        id="google_display_120x600",
        name="google_ads",
        display_name="Google Ads (120x600 – Skyscraper)",
        dimensions=(120, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_160x600": PlatformSpec(
        id="google_display_160x600",
        name="google_ads",
        display_name="Google Ads (160x600 – Wide Skyscraper)",
        dimensions=(160, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x600": PlatformSpec(
        id="google_display_300x600",
        name="google_ads",
        display_name="Google Ads (300x600 – Half Page)",
        dimensions=(300, 600),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_970x90": PlatformSpec(
        id="google_display_970x90",
        name="google_ads",
        display_name="Google Ads (970x90 – Large Leaderboard)",
        dimensions=(970, 90),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_300x50": PlatformSpec(
        id="google_display_300x50",
        name="google_ads",
        display_name="Google Ads (300x50 – Mobile Banner)",
        dimensions=(300, 50),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_320x50": PlatformSpec(
        id="google_display_320x50",
        name="google_ads",
        display_name="Google Ads (320x50 – Mobile Banner)",
        dimensions=(320, 50),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
        # --- Facebook Image Variants ---
    "facebook_feed_landscape": PlatformSpec(
        id="facebook_feed_landscape",
        name="facebook",
        display_name="Facebook Feed (Landscape)",
        dimensions=(1200, 630),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    "facebook_feed_square": PlatformSpec(
        id="facebook_feed_square",
        name="facebook",
        display_name="Facebook Feed (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    "facebook_story_image": PlatformSpec(
        id="facebook_story_image",
        name="facebook",
        display_name="Facebook Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    "facebook_right_column": PlatformSpec(
        id="facebook_right_column",
        name="facebook",
        display_name="Facebook Right Column (Desktop)",
        dimensions=(1200, 1200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
    "facebook_marketplace": PlatformSpec(
        id="facebook_marketplace",
        name="facebook",
        display_name="Facebook Marketplace (Listings)",
        dimensions=(1200, 1200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg"
    ),
        # --- LinkedIn Image Variants ---
    "linkedin_feed_landscape": PlatformSpec(
        id="linkedin_feed_landscape",
        name="linkedin",
        display_name="LinkedIn Feed (Sponsored Content)",
        dimensions=(1200, 627),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
    ),
    "linkedin_feed_square": PlatformSpec(
        id="linkedin_feed_square",
        name="linkedin",
        display_name="LinkedIn Feed (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
    ),
    "linkedin_story_image": PlatformSpec(
        id="linkedin_story_image",
        name="linkedin",
        display_name="LinkedIn Story (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
    ),
    "linkedin_message_ad_300x250": PlatformSpec(
        id="linkedin_message_ad_300x250",
        name="linkedin",
        display_name="LinkedIn Conversation Ad (Content Banner)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg"
    ),
        # --- Pinterest Image Variants ---
    "pinterest_standard_pin": PlatformSpec(
        id="pinterest_standard_pin",
        name="pinterest",
        display_name="Pinterest Standard Pin (2:3)",
        dimensions=(1000, 1500),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/pinterest.svg"
    ),
    "pinterest_square_pin": PlatformSpec(
        id="pinterest_square_pin",
        name="pinterest",
        display_name="Pinterest Square Pin",
        dimensions=(1000, 1000),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/pinterest.svg"
    ),
    "pinterest_story_pin": PlatformSpec(
        id="pinterest_story_pin",
        name="pinterest",
        display_name="Pinterest Story Pin (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/pinterest.svg"
    ),
        # --- Snapchat Image Variants ---
    "snapchat_single_image": PlatformSpec(
        id="snapchat_single_image",
        name="snapchat",
        display_name="Snapchat Single Image Ad (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/snapchat.svg"
    ),
    "snapchat_story_image": PlatformSpec(
        id="snapchat_story_image",
        name="snapchat",
        display_name="Snapchat Story Ad (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/snapchat.svg"
    ),
    "google_display_320x100": PlatformSpec(
        id="google_display_320x100",
        name="google_ads",
        display_name="Google Ads (320x100 – Large Mobile Banner)",
        dimensions=(320, 100),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),
    "google_display_330x200": PlatformSpec(
        id="google_display_330x200",
        name="google_ads",
        display_name="Google Ads (330x200 – Responsive Mobile)",
        dimensions=(330, 200),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=80,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/googleads.svg"
    ),

    # --- YouTube Image / Banner / Ad Sizes (IMAGE ONLY) ---

    "youtube_channel_banner": PlatformSpec(
        id="youtube_channel_banner",
        name="youtube",
        display_name="YouTube Channel Banner",
        dimensions=(2560, 1440),  # Recommended upload size
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_channel_banner_safe": PlatformSpec(
        id="youtube_channel_banner_safe",
        name="youtube",
        display_name="YouTube Channel Banner (Safe Area)",
        dimensions=(1546, 423),  # Safe zone visible on all devices
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_video_thumbnail": PlatformSpec(
        id="youtube_video_thumbnail",
        name="youtube",
        display_name="YouTube Video Thumbnail",
        dimensions=(1280, 720),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=92,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_video_thumbnail_min": PlatformSpec(
        id="youtube_video_thumbnail_min",
        name="youtube",
        display_name="YouTube Thumbnail (Minimum)",
        dimensions=(640, 360),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_300x250": PlatformSpec(
        id="youtube_display_ad_300x250",
        name="youtube",
        display_name="YouTube Display Ad (Medium Rectangle)",
        dimensions=(300, 250),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_300x60": PlatformSpec(
        id="youtube_display_ad_300x60",
        name="youtube",
        display_name="YouTube Display Ad (Banner)",
        dimensions=(300, 60),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1200x628": PlatformSpec(
        id="youtube_display_ad_1200x628",
        name="youtube",
        display_name="YouTube Discovery Ad (Landscape)",
        dimensions=(1200, 628),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1080x1080": PlatformSpec(
        id="youtube_display_ad_1080x1080",
        name="youtube",
        display_name="YouTube Square Ad",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),
    "youtube_display_ad_1080x1920": PlatformSpec(
        id="youtube_display_ad_1080x1920",
        name="youtube",
        display_name="YouTube Vertical Ad (Stories/Shorts-style)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg"
    ),

    # --- TikTok Image / Ad Sizes ---
    "tiktok_feed_ad_9_16": PlatformSpec(
        id="tiktok_feed_ad_9_16",
        name="tiktok",
        display_name="TikTok Feed Ad (9:16)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_feed_ad_1_1": PlatformSpec(
        id="tiktok_feed_ad_1_1",
        name="tiktok",
        display_name="TikTok Feed Ad (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_feed_ad_16_9": PlatformSpec(
        id="tiktok_feed_ad_16_9",
        name="tiktok",
        display_name="TikTok Feed Ad (16:9)",
        dimensions=(1920, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=90,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    "tiktok_profile_banner": PlatformSpec(
        id="tiktok_profile_banner",
        name="tiktok",
        display_name="TikTok Profile Banner (Cover)",
        dimensions=(1125, 633),  # Recommended by TikTok for profile header
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/tiktok.svg"
    ),
    # --- Twitter/X Image / Ad Sizes ---
    "twitter_feed_image_16_9": PlatformSpec(
        id="twitter_feed_image_16_9",
        name="twitter",
        display_name="Twitter Feed Image (Landscape)",
        dimensions=(1200, 675),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_feed_image_1_1": PlatformSpec(
        id="twitter_feed_image_1_1",
        name="twitter",
        display_name="Twitter Feed Image (Square)",
        dimensions=(1080, 1080),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_feed_image_9_16": PlatformSpec(
        id="twitter_feed_image_9_16",
        name="twitter",
        display_name="Twitter Feed Image (Portrait)",
        dimensions=(1080, 1920),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=85,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),
    "twitter_ad_image_1200x628": PlatformSpec(
        id="twitter_ad_image_1200x628",
        name="twitter",
        display_name="Twitter Website Card / Ad",
        dimensions=(1200, 628),
        content_type=ContentType.IMAGE,
        format_preference=["jpg", "png"],
        quality=88,
        icon_url="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/x.svg"
    ),


}


# =============================
# PLATFORM HELPERS
# =============================

def get_compatible_platforms(content_type: str) -> List[PlatformSpec]:
    """Get platforms compatible with content type"""
    compatible = []
    for platform in PLATFORM_CONFIGS.values():
        if (platform.content_type == ContentType.BOTH or
            platform.content_type.value == content_type):
            compatible.append(platform)
    return compatible


def get_platform_by_id(platform_id: str) -> Optional[PlatformSpec]:
    """Get platform configuration by ID"""
    return PLATFORM_CONFIGS.get(platform_id)


# def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
#     """Validate and filter platform IDs based on content type"""
#     expanded_ids = []

#     for pid in platform_ids:
#         if pid.lower() == "instagram":
#             expanded_ids.extend([
#                 key for key, p in PLATFORM_CONFIGS.items()
#                 if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#             ])
#         elif pid.lower() in ["google", "google_ads"]:
#             expanded_ids.extend([
#                 key for key, p in PLATFORM_CONFIGS.items()
#                 if p.name == "google_ads" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
#             ])
#         else:
#             expanded_ids.append(pid)

#     valid_platforms = []
#     compatible_platforms = get_compatible_platforms(content_type)
#     compatible_ids = {p.id for p in compatible_platforms}
#     for platform_id in expanded_ids:
#         if platform_id in compatible_ids:
#             valid_platforms.append(platform_id)

#     return valid_platforms


def validate_platform_ids(platform_ids: List[str], content_type: str) -> List[str]:
    """Validate and filter platform IDs based on content type"""
    expanded_ids = []

    for pid in platform_ids:
        if pid.lower() == "instagram":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "instagram" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() in ["google", "google_ads"]:
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "google_ads" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "youtube":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "youtube" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "tiktok":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "tiktok" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() in ["twitter", "x"]:
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "twitter" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "facebook":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "facebook" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "linkedin":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "linkedin" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "pinterest":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "pinterest" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        elif pid.lower() == "snapchat":
            expanded_ids.extend([
                key for key, p in PLATFORM_CONFIGS.items()
                if p.name == "snapchat" and p.content_type in (ContentType.IMAGE, ContentType.BOTH)
            ])
        else:
            expanded_ids.append(pid)

    valid_platforms = []
    compatible_platforms = get_compatible_platforms(content_type)
    compatible_ids = {p.id for p in compatible_platforms}
    seen = set()
    for platform_id in expanded_ids:
        if platform_id in compatible_ids and platform_id not in seen:
            valid_platforms.append(platform_id)
            seen.add(platform_id)

    return valid_platforms

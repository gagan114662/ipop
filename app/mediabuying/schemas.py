"""
Schemas for the Media Buying module.
"""
from pydantic import BaseModel

class MediaBuyingStatus(BaseModel):
    """
    Represents the status of the automated media buying process for a client.
    """
    client_id: str
    automated_campaigns_created: int
    automated_tests_running: int
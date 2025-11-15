"""Multimodal data ingestion pipeline."""

from .base import BaseIngester
from .text_ingester import TextIngester
from .image_ingester import ImageIngester
from .audio_ingester import AudioIngester
from .video_ingester import VideoIngester
from .pipeline import IngestionPipeline

__all__ = [
    "BaseIngester",
    "TextIngester",
    "ImageIngester",
    "AudioIngester",
    "VideoIngester",
    "IngestionPipeline",
]


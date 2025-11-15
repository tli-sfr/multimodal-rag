"""Image ingestion with OCR and captioning."""

from pathlib import Path
from typing import List, Optional
from uuid import uuid4
import base64
from io import BytesIO

from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from loguru import logger

from ..models import Document, Chunk, ModalityType, Metadata
from ..config import get_config
from .base import BaseIngester


class ImageIngester(BaseIngester):
    """Ingester for images with OCR and captioning."""
    
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    def __init__(
        self,
        enable_ocr: bool = True,
        enable_captioning: bool = True,
        max_dimension: int = 2048,
    ):
        """Initialize image ingester.
        
        Args:
            enable_ocr: Enable OCR text extraction
            enable_captioning: Enable image captioning
            max_dimension: Maximum image dimension
        """
        super().__init__(ModalityType.IMAGE)
        
        config = get_config()
        self.enable_ocr = enable_ocr
        self.enable_captioning = enable_captioning
        self.max_dimension = max_dimension
        
        # Initialize captioning model if enabled
        self.caption_processor = None
        self.caption_model = None
        
        if enable_captioning:
            try:
                model_name = config.get(
                    'ingestion.image.captioning_model',
                    'Salesforce/blip-image-captioning-base'
                )
                self.caption_processor = BlipProcessor.from_pretrained(model_name)
                self.caption_model = BlipForConditionalGeneration.from_pretrained(model_name)
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    self.caption_model = self.caption_model.cuda()
                
                logger.info(f"Loaded captioning model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load captioning model: {e}")
                self.enable_captioning = False
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate image file."""
        if not self._validate_file_exists(file_path):
            return False
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported image extension: {file_path.suffix}")
            return False
        
        if not self._validate_file_size(file_path):
            return False
        
        # Try to open image
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image file {file_path}: {e}")
            return False
    
    def ingest(self, file_path: Path, **kwargs) -> Document:
        """Ingest image file.
        
        Args:
            file_path: Path to image
            **kwargs: Additional parameters
            
        Returns:
            Document with image data
        """
        if not self.validate_file(file_path):
            raise ValueError(f"Invalid image file: {file_path}")
        
        logger.info(f"Ingesting image: {file_path}")
        
        # Load and process image
        image = Image.open(file_path)
        
        # Resize if needed
        image = self._resize_image(image)
        
        # Extract text via OCR
        ocr_text = ""
        if self.enable_ocr:
            ocr_text = self._extract_ocr_text(image)
        
        # Generate caption
        caption = ""
        if self.enable_captioning:
            caption = self._generate_caption(image)
        
        # Create metadata
        metadata = self.create_metadata(
            file_path,
            width=image.width,
            height=image.height,
            format=image.format,
            mode=image.mode,
        )
        
        # Combine text content
        content_parts = []
        if caption:
            content_parts.append(f"Caption: {caption}")
        if ocr_text:
            content_parts.append(f"OCR Text: {ocr_text}")
        
        content = "\n\n".join(content_parts) if content_parts else f"Image: {file_path.name}"
        
        # Create document
        doc_id = uuid4()
        document = Document(
            id=doc_id,
            title=file_path.stem,
            content=content,
            modality=ModalityType.IMAGE,
            metadata=metadata
        )
        
        # Create single chunk with all extracted information
        chunk = Chunk(
            content=content,
            modality=ModalityType.IMAGE,
            metadata=metadata,
            chunk_index=0,
            parent_id=doc_id
        )
        document.chunks = [chunk]
        
        logger.info(f"Processed image: {file_path}")
        
        return document
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image if it exceeds max dimension."""
        width, height = image.size
        
        if width <= self.max_dimension and height <= self.max_dimension:
            return image
        
        # Calculate new dimensions
        if width > height:
            new_width = self.max_dimension
            new_height = int(height * (self.max_dimension / width))
        else:
            new_height = self.max_dimension
            new_width = int(width * (self.max_dimension / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _extract_ocr_text(self, image: Image.Image) -> str:
        """Extract text from image using OCR."""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""
    
    def _generate_caption(self, image: Image.Image) -> str:
        """Generate caption for image."""
        if not self.caption_model or not self.caption_processor:
            return ""
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Process image
            inputs = self.caption_processor(image, return_tensors="pt")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate caption
            with torch.no_grad():
                output = self.caption_model.generate(**inputs, max_length=50)
            
            caption = self.caption_processor.decode(output[0], skip_special_tokens=True)
            return caption.strip()
        
        except Exception as e:
            logger.warning(f"Caption generation failed: {e}")
            return ""


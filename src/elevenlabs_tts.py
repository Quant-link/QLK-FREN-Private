import logging
import tempfile
import os
from typing import Optional
from elevenlabs.client import ElevenLabs
from src.app_config import app_settings

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    """ElevenLabs Text-to-Speech service wrapper."""
    
    def __init__(self):
        """Initialize the ElevenLabs TTS service."""
        self.client = None
        self.voice_id = None
        self.model_id = None
        self.voice_settings = None
        self.enabled = False
        
        if app_settings and hasattr(app_settings, 'elevenlabs_enabled'):
            self.enabled = app_settings.elevenlabs_enabled
            
            if self.enabled:
                self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize the ElevenLabs client with configuration."""
        try:
            if not app_settings or not hasattr(app_settings, 'elevenlabs_api_key'):
                logger.error("ElevenLabs API key not found in configuration")
                return False
                
            api_key = app_settings.elevenlabs_api_key
            if not api_key or api_key == "your_api_key_here":
                logger.error("ElevenLabs API key not configured properly")
                return False
            
            # Initialize ElevenLabs client
            self.client = ElevenLabs(api_key=api_key)
            
            # Set voice configuration
            self.voice_id = getattr(app_settings, 'elevenlabs_voice_id', '21m00Tcm4TlvDq8ikWAM')
            self.model_id = getattr(app_settings, 'elevenlabs_model_id', 'eleven_multilingual_v2')
            
            # Configure voice settings
            self.voice_settings = {
                "stability": getattr(app_settings, 'elevenlabs_stability', 0.5),
                "similarity_boost": getattr(app_settings, 'elevenlabs_similarity_boost', 0.8),
                "style": getattr(app_settings, 'elevenlabs_style', 0.0),
                "use_speaker_boost": getattr(app_settings, 'elevenlabs_use_speaker_boost', True)
            }
            
            logger.info("ElevenLabs TTS service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if ElevenLabs service is available and configured."""
        return self.enabled and self.client is not None
    
    def generate_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Generate speech from text using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            output_path: Optional path to save the audio file. If None, creates temp file.
            
        Returns:
            Path to the generated audio file, or None if generation failed
        """
        if not self.is_available():
            logger.error("ElevenLabs service not available")
            return None
            
        try:
            logger.debug(f"Generating speech for text: {text[:100]}...")
            
            # Generate speech using ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                voice_settings=self.voice_settings
            )
            
            # Determine output path
            if output_path is None:
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, "elevenlabs_audio.mp3")
            
            # Save audio data to file
            with open(output_path, "wb") as f:
                # Handle both generator and bytes types
                if hasattr(audio_generator, '__iter__') and not isinstance(audio_generator, (str, bytes)):
                    # It's a generator
                    for chunk in audio_generator:
                        if chunk:
                            f.write(chunk)
                else:
                    # It's bytes
                    f.write(audio_generator)
            
            logger.debug(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate speech with ElevenLabs: {e}")
            return None
    
    def get_available_voices(self) -> Optional[list]:
        """
        Get list of available voices from ElevenLabs.
        
        Returns:
            List of voice information or None if failed
        """
        if not self.is_available():
            return None
            
        try:
            voices = self.client.voices.search()
            return [{"id": voice.voice_id, "name": voice.name} for voice in voices.voices]
        except Exception as e:
            logger.error(f"Failed to get voices from ElevenLabs: {e}")
            return None


# Global instance
_elevenlabs_service = None


def get_elevenlabs_service() -> ElevenLabsTTS:
    """Get the global ElevenLabs TTS service instance."""
    global _elevenlabs_service
    if _elevenlabs_service is None:
        _elevenlabs_service = ElevenLabsTTS()
    return _elevenlabs_service


def is_elevenlabs_available() -> bool:
    """Check if ElevenLabs TTS service is available."""
    service = get_elevenlabs_service()
    return service.is_available()


def generate_elevenlabs_speech(text: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Generate speech using ElevenLabs service.
    
    Args:
        text: Text to convert to speech
        output_path: Optional path to save the audio file
        
    Returns:
        Path to generated audio file or None if failed
    """
    service = get_elevenlabs_service()
    return service.generate_speech(text, output_path) 
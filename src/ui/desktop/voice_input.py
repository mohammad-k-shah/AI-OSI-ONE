"""
OSI ONE AGENT - Voice Input Handler Component

This module provides the VoiceInputHandler for speech-to-text functionality
and voice input capabilities for the desktop application.
"""

import threading
from typing import Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QIcon

class VoiceInputHandler(QObject):
    """
    Voice input handler for the OSI ONE AGENT application.
    
    Provides speech-to-text functionality with microphone access
    and voice recognition capabilities.
    """
    
    # Signals
    voice_text_received = pyqtSignal(str)  # Emitted when voice text is received
    voice_error_occurred = pyqtSignal(str)  # Emitted when voice error occurs
    voice_listening_started = pyqtSignal()  # Emitted when listening starts
    voice_listening_stopped = pyqtSignal()  # Emitted when listening stops
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the voice input handler.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.parent_window = parent
        self.is_listening = False
        self.voice_thread = None
        self.recognition_engine = None
        
        self.setup_voice_recognition()
        self.setup_behavior()
    
    def setup_voice_recognition(self):
        """Set up the voice recognition engine."""
        try:
            # Try to import speech recognition
            import speech_recognition as sr
            
            self.recognition_engine = sr.Recognizer()
            self.recognition_engine.energy_threshold = 4000
            self.recognition_engine.dynamic_energy_threshold = True
            self.recognition_engine.pause_threshold = 0.8
            
            # Test microphone availability
            try:
                with sr.Microphone() as source:
                    self.recognition_engine.adjust_for_ambient_noise(source, duration=1)
                self.microphone_available = True
            except Exception as e:
                print(f"Microphone not available: {e}")
                self.microphone_available = False
                
        except ImportError:
            print("Speech recognition not available. Install with: pip install SpeechRecognition")
            self.recognition_engine = None
            self.microphone_available = False
    
    def setup_behavior(self):
        """Set up voice input behavior."""
        # You can add voice input preferences here
        pass
    
    def start_voice_recognition(self):
        """Start voice recognition in a separate thread."""
        if not self.microphone_available or not self.recognition_engine:
            self.voice_error_occurred.emit("Voice input not available. Please check microphone and install SpeechRecognition.")
            return
        
        if self.is_listening:
            return
        
        self.is_listening = True
        self.voice_listening_started.emit()
        
        # Start voice recognition in separate thread
        self.voice_thread = threading.Thread(target=self._listen_for_voice)
        self.voice_thread.daemon = True
        self.voice_thread.start()
    
    def stop_voice_recognition(self):
        """Stop voice recognition."""
        self.is_listening = False
        self.voice_listening_stopped.emit()
    
    def _listen_for_voice(self):
        """Listen for voice input in a separate thread."""
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognition_engine.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognition_engine.listen(source, timeout=5, phrase_time_limit=10)
                
                if self.is_listening:
                    # Recognize speech
                    text = self.recognition_engine.recognize_google(audio)
                    
                    if text:
                        # Emit the recognized text
                        self.voice_text_received.emit(text)
                    else:
                        self.voice_error_occurred.emit("No speech detected. Please try again.")
                else:
                    self.voice_error_occurred.emit("Voice recognition was cancelled.")
                    
        except sr.WaitTimeoutError:
            self.voice_error_occurred.emit("No speech detected within timeout period.")
        except sr.UnknownValueError:
            self.voice_error_occurred.emit("Could not understand the speech. Please try again.")
        except sr.RequestError as e:
            self.voice_error_occurred.emit(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            self.voice_error_occurred.emit(f"Voice recognition error: {str(e)}")
        finally:
            self.is_listening = False
            self.voice_listening_stopped.emit()
    
    def is_voice_available(self) -> bool:
        """
        Check if voice input is available.
        
        Returns:
            bool: True if voice input is available
        """
        return self.microphone_available and self.recognition_engine is not None
    
    def get_microphone_status(self) -> str:
        """
        Get the microphone status.
        
        Returns:
            str: Microphone status message
        """
        if not self.microphone_available:
            return "Microphone not available"
        elif not self.recognition_engine:
            return "Speech recognition not installed"
        else:
            return "Voice input ready"
    
    def test_microphone(self):
        """Test microphone functionality."""
        if not self.is_voice_available():
            self.voice_error_occurred.emit("Voice input not available for testing.")
            return
        
        # Start a test recognition
        self.start_voice_recognition()
    
    def set_energy_threshold(self, threshold: int):
        """
        Set the energy threshold for voice detection.
        
        Args:
            threshold: Energy threshold value
        """
        if self.recognition_engine:
            self.recognition_engine.energy_threshold = threshold
    
    def set_pause_threshold(self, threshold: float):
        """
        Set the pause threshold for voice detection.
        
        Args:
            threshold: Pause threshold value
        """
        if self.recognition_engine:
            self.recognition_engine.pause_threshold = threshold
    
    def get_voice_settings(self) -> dict:
        """
        Get current voice recognition settings.
        
        Returns:
            dict: Current voice settings
        """
        if self.recognition_engine:
            return {
                "energy_threshold": self.recognition_engine.energy_threshold,
                "pause_threshold": self.recognition_engine.pause_threshold,
                "dynamic_energy_threshold": self.recognition_engine.dynamic_energy_threshold
            }
        return {}
    
    def set_voice_settings(self, settings: dict):
        """
        Set voice recognition settings.
        
        Args:
            settings: Dictionary of voice settings
        """
        if not self.recognition_engine:
            return
        
        if "energy_threshold" in settings:
            self.recognition_engine.energy_threshold = settings["energy_threshold"]
        
        if "pause_threshold" in settings:
            self.recognition_engine.pause_threshold = settings["pause_threshold"]
        
        if "dynamic_energy_threshold" in settings:
            self.recognition_engine.dynamic_energy_threshold = settings["dynamic_energy_threshold"]
    
    def is_listening_active(self) -> bool:
        """
        Check if voice recognition is currently active.
        
        Returns:
            bool: True if listening is active
        """
        return self.is_listening
    
    def cancel_voice_recognition(self):
        """Cancel current voice recognition."""
        self.stop_voice_recognition()
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for voice recognition.
        
        Returns:
            list: List of supported language codes
        """
        # Google Speech Recognition supports many languages
        # You can implement language selection here
        return ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN"]
    
    def set_language(self, language_code: str):
        """
        Set the language for voice recognition.
        
        Args:
            language_code: Language code (e.g., "en-US")
        """
        # Store language preference
        self.current_language = language_code
    
    def get_current_language(self) -> str:
        """
        Get the current language setting.
        
        Returns:
            str: Current language code
        """
        return getattr(self, 'current_language', 'en-US')
    
    def process_voice_command(self, voice_text: str) -> str:
        """
        Process voice command and convert to text command.
        
        Args:
            voice_text: Raw voice text
            
        Returns:
            str: Processed command text
        """
        # Basic voice command processing
        # You can add more sophisticated processing here
        
        # Convert common voice patterns to text commands
        voice_patterns = {
            "show my tasks": "Show my tasks for this sprint",
            "get my tasks": "Show my tasks for this sprint",
            "update task": "Update TASK-",
            "fill timesheet": "Fill my timesheet based on last week's PRs",
            "show meetings": "Show my meetings today",
            "get meetings": "Show my meetings today",
            "update status": "Update TASK- Status -> Active",
            "clear chat": "Clear conversation",
            "export chat": "Export conversation"
        }
        
        voice_text_lower = voice_text.lower()
        
        # Check for pattern matches
        for pattern, command in voice_patterns.items():
            if pattern in voice_text_lower:
                return command
        
        # If no pattern match, return the original text
        return voice_text
    
    def handle_voice_text(self, voice_text: str):
        """
        Handle received voice text.
        
        Args:
            voice_text: Recognized voice text
        """
        # Process the voice command
        processed_text = self.process_voice_command(voice_text)
        
        # Emit the processed text
        self.voice_text_received.emit(processed_text)
    
    def cleanup(self):
        """Clean up voice recognition resources."""
        self.stop_voice_recognition()
        
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=1.0) 
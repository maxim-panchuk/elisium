import os
import configparser
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # API Keys
    eleven_labs_api_key: str
    eleven_labs_model_id: str
    
    # URLs
    url: str
    url_with_timestamps: str
    
    # Paths
    path_to_voice: str
    
    # Validation settings
    min_words_count: int
    min_voice_duration: int
    clip_duration: int

    # Transcription settings
    transcription_url: str
    transcription_model_id: str
    path_to_transcription: str
    @classmethod
    def load(cls) -> 'Config':
        """
        Загружает конфигурацию из config.ini файла
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)

        return cls(
            eleven_labs_api_key=config["API_KEYS"]["ELEVEN_LABS_API_KEY"],
            eleven_labs_model_id=config["API_KEYS"]["ELEVEN_LABS_MODEL_ID"],
            url=config["URLS"]["URL"],
            url_with_timestamps=config["URLS"]["URL_WITH_TIMESTAMPS"],
            path_to_voice=config["PATHS"]["PATH_TO_VOICE"],
            min_words_count=int(config.get("VALIDATION", "MIN_WORDS_COUNT", fallback=50)),
            min_voice_duration=int(config.get('VALIDTAION', 'MIN_VOICE_DURATION', fallback=10)),
            clip_duration=int(config.get('VALIDATION', 'CLIP_DURATION', fallback=5)),
            transcription_url=config["TRANSCRIPTION"]["TRANSCRIPTION_URL"],
            transcription_model_id=config["TRANSCRIPTION"]["TRANSCRIPTION_MODEL_ID"],
            path_to_transcription=config["TRANSCRIPTION"]["PATH_TO_TRANSCRIPTION"]
        )

# Создаем глобальный экземпляр конфигурации
config = Config.load() 
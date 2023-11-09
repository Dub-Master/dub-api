from enum import Enum
from pydantic import BaseModel


class JobStatus(str, Enum):
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"


class LanguageCode(str, Enum):
    en = "en"
    es = "es"
    fr = "fr"
    de = "de"


LANGUAGE_NAMES = {
    LanguageCode.en: "English",
    LanguageCode.es: "Spanish",
    LanguageCode.fr: "French",
    LanguageCode.de: "German",
}


class Job(BaseModel):
    id: str
    input_url: str
    output_url: str
    target_language: LanguageCode
    status: JobStatus

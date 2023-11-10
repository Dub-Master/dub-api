from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class JobStatus(str, Enum):
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"


def is_status_final(status: JobStatus) -> bool:
    return status in [JobStatus.completed, JobStatus.failed]


class LanguageCode(str, Enum):
    en = "en"
    es = "es"
    fr = "fr"
    de = "de"
    pl = "pl"
    it = "it"
    pt = "pt"
    hi = "hi"


LANGUAGE_NAMES = {
    LanguageCode.en: "English",
    LanguageCode.es: "Spanish",
    LanguageCode.fr: "French",
    LanguageCode.de: "German",
    LanguageCode.pl: "Polish",
    LanguageCode.it: "Italian",
    LanguageCode.pt: "Portuguese",
    LanguageCode.hi: "Hindi",
}


class Job(BaseModel):
    id: str = ""
    input_url: str = ""
    output_url: str = ""
    target_language: LanguageCode = LanguageCode.en
    status: JobStatus = ""
    created_at: datetime = datetime.now()


class JobIn(BaseModel):
    input_url: str
    target_language: LanguageCode

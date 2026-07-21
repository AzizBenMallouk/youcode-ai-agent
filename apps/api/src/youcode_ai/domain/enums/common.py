from enum import Enum


class Language(str, Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"
    DARIJA = "darija"


class ConsentPurpose(str, Enum):
    SUPPORT_REQUEST = "support_request"
    NEWSLETTER = "newsletter"
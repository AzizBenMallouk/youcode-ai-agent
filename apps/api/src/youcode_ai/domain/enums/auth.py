from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPPORT = "support"
    NEWSLETTER_MANAGER = "newsletter_manager"

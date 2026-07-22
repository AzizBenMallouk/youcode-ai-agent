import os
import sys
from youcode_ai.core.config import settings
from youcode_ai.infrastructure.database import database_session
from youcode_ai.infrastructure.database.tables.user import UserTable
from youcode_ai.domain.enums.auth import UserRole
from youcode_ai.infrastructure.security.password import hash_password

def main():
    email = os.getenv("ADMIN_INITIAL_EMAIL", settings.admin_initial_email)
    password = os.getenv("ADMIN_INITIAL_PASSWORD", settings.admin_initial_password)

    if not email:
        email = input("Admin email: ")
    if not password:
        import getpass
        password = getpass.getpass("Admin password: ")

    if not email or not password:
        print("Email and password are required")
        sys.exit(1)

    with database_session() as session:
        from youcode_ai.infrastructure.database.repositories.user import UserRepository
        user_repo = UserRepository(session=session)
        
        if user_repo.find_by_email(email):
            print(f"User {email} already exists")
            sys.exit(0)

        user = UserTable(
            email=email,
            password_hash=hash_password(password),
            full_name="Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"Successfully created admin user {email}")

if __name__ == "__main__":
    main()

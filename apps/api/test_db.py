from youcode_ai.infrastructure.database.initialize import initialize_database
try:
    initialize_database()
    print("DB INITIALIZED")
except Exception as e:
    print("ERROR:", e)

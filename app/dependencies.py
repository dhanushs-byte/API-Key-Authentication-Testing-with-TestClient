
from app.database import find_user


def get_user_by_hash(key_hash: str):
    return find_user(key_hash)


def get_llm():
    def generate(message: str):
        return f"AI response: {message}"

    return generate

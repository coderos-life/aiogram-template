from bot.database.models import User


TEST_USER_ID = 1
TEST_USERNAME = "username"


def make_test_user() -> User:
    return User(id=TEST_USER_ID, username=TEST_USERNAME)


def make_test_users(count: int = 100) -> list[User]:
    return [User(id=i, username=None if i % 3 == 0 else str(i)) for i in range(1_000, 1_000 + count)]

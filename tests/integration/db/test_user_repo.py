from bot.database import Repositories
from tests.integration.db.data import TEST_USER_ID, TEST_USERNAME


async def test_get_user_by_id(repo: Repositories):
    us = await repo.users.create(id=TEST_USER_ID, username=TEST_USERNAME)

    user = await repo.users.get(TEST_USER_ID)

    assert user is not None

    assert user.id == us.id
    assert user.username == us.username


async def test_get_user_by_username(repo: Repositories):
    await repo.users.create(id=TEST_USER_ID, username=TEST_USERNAME)

    users = await repo.users.get_users_by_username(TEST_USERNAME)

    assert TEST_USER_ID in [i.id for i in users]

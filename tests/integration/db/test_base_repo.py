from bot.database import Repositories
from bot.database.models import User
from tests.integration.db.data import TEST_USER_ID, TEST_USERNAME, make_test_user, make_test_users


async def test_create(repo: Repositories):
    test_user = make_test_user()
    us = await repo.users.create_from_model(test_user)

    assert us.id == TEST_USER_ID
    assert us.username == TEST_USERNAME


async def test_get(repo: Repositories):
    test_user = make_test_user()
    us = await repo.users.create_from_model(test_user)
    user = await repo.users.get(TEST_USER_ID)

    assert user is not None

    assert us.id == user.id
    assert us.username == user.username
    assert us.id == user.id


async def test_update(repo: Repositories):
    await repo.users.create_from_model(make_test_user())
    us: User = await repo.users.get(TEST_USER_ID)

    assert us is not None

    us.username = None
    await repo.users.update(us)

    us: User = await repo.users.get(TEST_USER_ID)

    assert us.username is None


async def test_delete(repo: Repositories):
    us = await repo.users.create_from_model(make_test_user())
    await repo.users.delete(us)

    us = await repo.users.get(TEST_USER_ID)
    assert us is None


async def test_get_all(repo: Repositories):
    test_users = make_test_users()
    await repo.users.create_from_model(*test_users)

    all_users = await repo.users.get_all()

    assert len(test_users) == len(all_users)

    await repo.users.delete(*all_users)


async def test_get_all_count(repo: Repositories):
    test_users = make_test_users()
    await repo.users.create_from_model(*test_users)

    users_count = await repo.users.get_all(count=True)

    assert users_count == len(test_users)

    await repo.users.delete(*(await repo.users.get_all()))

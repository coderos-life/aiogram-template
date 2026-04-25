# Middleware

## Подробнее про middleware

[Документация](https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html)

[Книга MasterGroosha](https://mastergroosha.github.io/aiogram-3-guide/filters-and-middlewares/)

## Список предустановленных middleware

1. `ThrottlingMiddleware` - middleware для защиты от частых повторных действий. Работает на `cachetools`.
2. `GetRepo` - создаёт SQLAlchemy session и передаёт её в handler.

Пример:

```python
from bot.database import Repositories
from aiogram import Router, types

router = Router()

@router.message(...)
async def example_handler(message: types.Message, repo: Repositories):
    user = repo.users.get_by_user_id(message.from_user.id)
    ...
```

3. `GetUser` - получает пользователя из БД и передаёт его в handler. По умолчанию каждый handler получает пользователя из базы данных.

```python
from bot.database.models import User

@router.message()
async def example_handler(message: types.Message, repo: Repositories, user: User):
    print(user)
    ...
```

Если user в handler не нужен, установите flag в `False`:

```python
@router.message(..., flags={'user': False})
async def example_handler(message: types.Message, repo: Repositories):
    ...
```

Если нужно загрузить relationships SQLAlchemy model, используйте flag `user_options` и передайте нужные relationships списком:

```python
from sqlalchemy.orm import relationship

class User(BaseModel):
    ...
    relationhip = relationship(...)

@router.message(..., flags={'user_options': [User.relationhip]})
async def example_handler(message: types.Message, repo: Repositories, user: User):
    ...
```

4. `GetChat` - работает аналогично `GetUser`, но по умолчанию handler не получает chat из базы данных.

Если в handler нужен chat из базы данных:

```python
from bot.database.models import Chat

@router.message(..., flags={'chat': True})
async def example_handler(message: types.Message, repo: Repositories, chat: Chat):
    print(chat)
```

# CRUD + JWT + PostgreSQL

Полноценное WEB-приложение с системой аутентификации и авторизации, CRUD-интерфейсом и журналом аудита. Реализована гибкая роль-ориентированная система доступа и логирование действий пользователей.

---

## Функциональность

- Аутентификация по логину и паролю (JWT)
- Авторизация с ролевой моделью
- CRUD-операции для всех таблиц
- PostgreSQL с `pgcrypto`, `SSL`, `row_to_json`
- Аудит действий пользователей через триггеры
- Управление доступом через `ACCESS_MATRIX`

---

## Структура проекта

```text
prog/
├── certs/
│   ├── cert.pem
│   └── key.pem
├── routes/
│   ├── auth.py
│   └── dashboard.py
├── services/
│   ├── access_control.py
│   └── auth_service.py
├── templates/
│   ├── errors/
│   │   └── *.html
│   └── *.html
├── utils/
│   ├── db.py
│   ├── decorators.py
│   └── security.py
└── __init__.py
query/
└── sql_query-v0.7.txt
requirements.txt
run.py
```

---

## Аутентификация и авторизация

- **Аутентификация** осуществляется через `/login`, возвращается JWT.
- **Авторизация** реализована через декораторы с проверкой роли на основе `ACCESS_MATRIX`.
- Пароли сравниваются через `pgcrypto` (`crypt()`).

---

## Система ролей

Права доступа управляются через таблицу `ACCESS_MATRIX`, где указано, какие роли могут выполнять действия (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) с какими таблицами.

Пример таблицы `ACCESS_MATRIX`:

| role     | table_name   | can_read | can_insert | can_update | can_delete |
|----------|--------------|----------|------------|------------|------------|
| admin    | employees    | ✅        | ✅          | ✅          | ✅          |
| manager  | reports      | ✅        | ✅          | ❌          | ❌          |
...

---

## Аудит действий

В базе есть триггер, который логирует действия:

```sql
INSERT INTO audit_log (username, role, operation, table_name, row_data)
VALUES (current_setting('app.current_user'), current_setting('app.current_role'), TG_OP, TG_TABLE_NAME, row_to_json(NEW/OLD));
```

> Значения `current_user` и `current_role` устанавливаются в начале запроса через `SET LOCAL`.

---

## Безопасность

- SSL-соединение с БД
- Хэширование паролей в PostgreSQL (`pgcrypto`)
- Использование JWT для API-доступа
- Разделение прав доступа по ролям

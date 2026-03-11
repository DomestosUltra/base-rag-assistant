# API для фронтенда

## Общие требования

Во все запросы передавать заголовки:
- `X-API-Key: <ключ>`
- `X-User-Id: <id пользователя>`

Базовый URL: `http://localhost:8000`

## 1) POST `/v1/query/text-image`

Назначение: текст или текст + картинка.

`multipart/form-data`:
- `text` (string, обязательный)
- `search_shared` (boolean, optional, default=true)
- `image` (file, optional)

Ответ:
```json
{
  "answer": "..."
}
```

## 2) POST `/v1/query/audio-image`

Назначение: аудио (.mp3) или аудио + картинка.

`multipart/form-data`:
- `audio` (file, обязательный)
- `search_shared` (boolean, optional, default=true)
- `image` (file, optional)

Ответ:
```json
{
  "answer": "..."
}
```

## 3) POST `/v1/query/memory/clear`

Очистка памяти диалога пользователя.

`application/json`:
```json
{
  "user_id": "user-123"
}
```

Ответ:
```json
{
  "cleared": true
}
```

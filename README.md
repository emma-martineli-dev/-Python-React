## Запуск

```bash
docker compose -f docker-compose.dev.yml up --build -d
docker exec -it backend alembic upgrade head
```

- Frontend: http://localhost:3000/test
- Backend: http://localhost:8000/docs

## Тесты

```bash
docker exec -it backend uv run pytest
```

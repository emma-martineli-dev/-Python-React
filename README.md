## Тестовое задание на позицию Fullstack разработчика (Python + React)

### Требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Запуск

```bash
docker compose -f docker-compose.dev.yml up --build -d
docker exec -it backend alembic upgrade head
```

### Ссылки

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:3000/test |
| Backend API docs | http://localhost:8000/docs |

### Тесты

```bash
docker exec -it backend uv run pytest
```

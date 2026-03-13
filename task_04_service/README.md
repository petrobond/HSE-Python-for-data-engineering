# Веб-сервис: мини-дашборд (FastAPI + Streamlit)

Backend на FastAPI хранит данные в CSV и отдаёт/изменяет их через API. Frontend на Streamlit показывает таблицу, графики и формы для добавления/удаления записей.

## Запуск локально

Нужны **два терминала**. Все команды выполняйте из директории `task_04_service`. Сначала поднимаете backend, затем frontend — иначе дашборд не сможет загрузить данные.

**Терминал 1 — окружение и backend**

Выполните по порядку (создание venv и установка зависимостей — один раз; при следующих запусках достаточно активировать venv и запустить uvicorn):

```bash
cd task_04_service
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Дождитесь сообщения вида `Uvicorn running on http://127.0.0.1:8000`. Backend будет доступен по этому адресу.  
Если порт 8000 занят, запустите вместо этого: `uvicorn backend.main:app --reload --port 8001` (тогда backend будет на http://127.0.0.1:8001).

**Терминал 2 — frontend**

Откройте второй терминал и выполните (обязательно активируйте тот же venv, чтобы был доступен `streamlit`):

```bash
cd task_04_service
source venv/bin/activate           # Windows: venv\Scripts\activate
streamlit run frontend/app.py
```

Откройте в браузере URL, который выведет Streamlit (обычно http://localhost:8501).

## Деплой

### Backend на Render

https://petrobond-task04-backend.onrender.com/

В backend настроен CORS (CORSMiddleware с явным origin для Streamlit), чтобы запросы с развёрнутого frontend проходили.

### Frontend на Streamlit Cloud

https://petrobond-task04-frontend.streamlit.app

Данные на Render хранятся в CSV на диске; при перезапуске сервиса файл может сброситься, если не используется persistent disk.

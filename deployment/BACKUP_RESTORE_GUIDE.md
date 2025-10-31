# 🏠 InBack.ru - Полный гайд по восстановлению в Replit

## 📋 Быстрое восстановление (5 минут)

### 1. Создание нового Repl
```bash
# 1. Создайте новый Repl на Python
# 2. Установите PostgreSQL через Replit Database
# 3. Скопируйте все файлы проекта
```

### 2. Установка зависимостей
```bash
# Основные пакеты Python
pip install flask flask-sqlalchemy gunicorn psycopg2-binary
pip install flask-login werkzeug requests pandas openpyxl
pip install openai python-telegram-bot sendgrid email-validator
pip install pyjwt flask-dance oauthlib telegram numpy sqlalchemy
```

### 3. Настройка базы данных
```bash
# Переменные окружения уже настроены через Replit Database:
# DATABASE_URL, PGDATABASE, PGHOST, PGPASSWORD, PGPORT, PGUSER
echo "База данных PostgreSQL подключается автоматически"
```

### 4. Настройка Workflow
```bash
# Команда для запуска сервера:
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --timeout 120 main:app

# Порт: 5000
# Тип: webview (для показа сайта)
```

### 5. Запуск и проверка
```bash
# После настройки workflow:
# 1. Сервер запустится автоматически на порту 5000
# 2. Откройте webview для просмотра сайта
# 3. Данные загрузятся из JSON файлов
```

## 🗂️ Структура проекта

### Критически важные файлы:
```
├── app.py                     # Основное Flask приложение (499KB)
├── main.py                    # Точка входа
├── models.py                  # Модели базы данных (1759 строк)
├── requirements.txt           # Зависимости Python
├── templates/                 # 67 HTML шаблонов
│   ├── base.html             # Базовый шаблон
│   ├── index.html            # Главная страница
│   ├── auth/dashboard.html   # Панель управления
│   └── residential_complexes.html
├── static/                   # CSS, JS, изображения
│   ├── data/                # JSON данные
│   │   ├── residential_complexes.json  # 11 ЖК
│   │   └── properties.json            # Квартиры
│   ├── css/style.css        # Основные стили
│   └── js/                  # JavaScript файлы
└── attached_assets/         # Excel файлы с данными
    ├── properties_krasnodar.xlsx
    └── residential_complexes.xlsx
```

## 🔧 Основные компоненты системы

### Flask приложение (app.py):
- **Порт**: 5000 (обязательно для Replit)
- **База данных**: PostgreSQL через DATABASE_URL
- **Аутентификация**: Flask-Login + хеширование паролей
- **Загрузка данных**: JSON файлы + Excel импорт

### Модели базы данных (models.py):
```python
# Основные таблицы:
- User                    # Пользователи (пароль: demo123)
- Manager                 # Менеджеры (пароль: demo123) 
- ExcelProperty          # Квартиры из Excel
- ResidentialComplex     # ЖК из базы
- UserFavoriteProperty   # Избранные квартиры
- ManagerFavoriteComplex # Избранные ЖК менеджеров
- CashbackApplication    # Заявки на кешбек
- UserActivity          # Активность пользователей
```

### JSON данные:
- `static/data/residential_complexes.json` - 11 ЖК для калькулятора
- `static/data/properties.json` - Квартиры для поиска

## 🚀 Особенности конфигурации

### Безопасность Flask:
```python
app.secret_key = os.environ.get("SESSION_SECRET")  # Replit устанавливает автоматически
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Для HTTPS
```

### Подключение к базе:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
```

### Создание таблиц:
```python
with app.app_context():
    import models  # Обязательно импортировать модели
    db.create_all()  # Создает все таблицы автоматически
```

## 📊 Данные по умолчанию

### Пользователи (пароль: demo123):
- user1@example.com → user10@example.com (10 пользователей)
- manager1@inback.ru → manager4@inback.ru (4 менеджера)

### Данные недвижимости:
- **354 квартиры** загружены из Excel в базу данных
- **11 ЖК** в JSON для калькулятора кешбека:
  - ЖК «Первое место»
  - ЖК Гранд Люкс  
  - ЖК Небесный
  - ЖК Триумфальная Арка
  - ЖК Солнечная Долина
  - И другие...

## 🔍 Устранение проблем

### Калькулятор кешбека показывает неправильные ЖК:
```python
# API исправлен - теперь берет данные из JSON:
/api/residential-complexes  # Загружает из static/data/residential_complexes.json
```

### Ошибки сети при подаче заявки:
```javascript
// CSRF токены добавлены в AJAX запросы:
'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
```

### База данных не создается:
```bash
# Проверьте переменные окружения:
echo $DATABASE_URL
echo $PGDATABASE

# Таблицы создаются автоматически при запуске app.py
```

## 🎯 Финальная проверка

### 1. Сервер запущен:
```bash
# Должно показать "Database tables created successfully!"
# Workflow "Start application" должен быть RUNNING
```

### 2. API работает:
```bash
curl http://localhost:5000/api/residential-complexes
# Должен вернуть 10+ ЖК из JSON
```

### 3. Калькулятор кешбека:
- Показывает реальные ЖК из каталога
- Расчет работает без ошибок сети
- Заявки сохраняются в базу данных

### 4. Интерфейс:
- Кнопки сравнения видны (серые иконки)
- Избранное работает для пользователей и менеджеров
- Дашборд показывает актуальную статистику

## 💾 Создание бекапа

### Экспорт базы данных:
```sql
-- Команды для создания бекапа:
pg_dump $DATABASE_URL > inback_backup.sql

-- Восстановление:
psql $DATABASE_URL < inback_backup.sql
```

### Архивирование файлов:
```bash
# Создать архив всего проекта:
tar -czf inback_full_backup.tar.gz \
  app.py main.py models.py requirements.txt \
  templates/ static/ attached_assets/ \
  *.md

# Распаковка в новом Repl:
tar -xzf inback_full_backup.tar.gz
```

## 🚨 Критически важно

1. **Порт 5000** - единственный незаблокированный порт в Replit
2. **DATABASE_URL** - Replit устанавливает автоматически при добавлении PostgreSQL
3. **Импорт моделей** - models.py должен импортироваться в app.py для создания таблиц
4. **JSON файлы** - калькулятор кешбека теперь работает с данными из JSON, не из базы
5. **CSRF токены** - обязательны для всех AJAX запросов

---

**✅ Система полностью восстановлена и готова к работе!**

Пароли для всех аккаунтов: **demo123**

Контакты: InBack.ru - Платформа недвижимости Краснодара с кешбеком
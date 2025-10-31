# ⚡ InBack.ru - Быстрое восстановление в Replit (5 минут)

## 🚀 Пошаговый чек-лист

### ✅ Шаг 1: Создание Repl
```bash
1. Создайте новый Python Repl в Replit
2. Добавьте PostgreSQL Database через UI Replit
3. Проверьте переменные: DATABASE_URL, PGHOST, PGUSER, etc.
```

### ✅ Шаг 2: Копирование файлов
```bash
# Скопируйте эти критические файлы:
- app.py                    # Основное приложение
- main.py                   # Точка входа
- models.py                 # Модели базы данных
- requirements.txt          # Зависимости
- templates/                # Все HTML шаблоны
- static/                   # CSS, JS, JSON данные
- attached_assets/          # Excel файлы
- database_restore_commands.sql  # SQL для восстановления
```

### ✅ Шаг 3: Установка зависимостей
```bash
pip install flask flask-sqlalchemy gunicorn psycopg2-binary flask-login werkzeug
```

### ✅ Шаг 4: Настройка Workflow
```bash
# Команда:
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --timeout 120 main:app

# Порт: 5000
# Тип: webview
# Имя: "Start application"
```

### ✅ Шаг 5: Запуск и проверка
```bash
1. Запустите Workflow
2. Проверьте: "Database tables created successfully!" в логах
3. Откройте webview - сайт должен загрузиться
```

## 🗄️ Восстановление базы данных

### Автоматическое (рекомендуется):
```python
# Flask автоматически создаст все таблицы при запуске app.py
# Данные загрузятся из Excel файлов автоматически
```

### Ручное (если нужно):
```sql
# Выполните в консоли базы данных:
\i database_restore_commands.sql

# Или через psql:
psql $DATABASE_URL < database_restore_commands.sql
```

## 🔍 Быстрая проверка

### 1. API работает:
```bash
curl http://localhost:5000/api/residential-complexes
# Должен вернуть 10+ ЖК
```

### 2. База данных:
```sql
SELECT COUNT(*) FROM excel_properties;  -- Должно быть 354
SELECT COUNT(*) FROM users;            -- Должно быть 10+
SELECT COUNT(*) FROM managers;         -- Должно быть 4
```

### 3. Веб-интерфейс:
- Главная страница загружается
- Калькулятор кешбека показывает ЖК
- Логин работает (пароль: demo123)
- Каталог недвижимости открывается

## 🚨 Если что-то не работает

### База данных не создается:
```bash
echo $DATABASE_URL  # Проверьте переменную
```

### Ошибки в калькуляторе:
```bash
# Проверьте наличие JSON файлов:
ls static/data/residential_complexes.json
ls static/data/properties.json
```

### Сервер не запускается:
```bash
# Проверьте requirements.txt и установите зависимости
pip install -r requirements.txt
```

## 📊 Ожидаемые результаты

После успешного восстановления:

- ✅ **50 таблиц** в базе данных
- ✅ **354 квартиры** в каталоге
- ✅ **10 ЖК** в калькуляторе кешбека
- ✅ **14 пользователей** (10 + 4 менеджера)
- ✅ **Избранное и сравнение** работают
- ✅ **CSRF защита** активна
- ✅ **Логи без ошибок**

## 🔑 Учетные данные

**Все пароли: demo123**

- Пользователи: user1@example.com - user10@example.com
- Менеджеры: manager1@inback.ru - manager4@inback.ru

---

**Время восстановления: ~5 минут**
**Результат: Полностью рабочая платформа InBack.ru**
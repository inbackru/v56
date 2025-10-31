# 🚀 Инструкция по установке и миграции проекта InBack

## 📋 Содержание
1. [Требования](#требования)
2. [Миграция на Replit](#миграция-на-replit)
3. [Локальная установка](#локальная-установка)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Переменные окружения](#переменные-окружения)
6. [Запуск приложения](#запуск-приложения)
7. [Экспорт и импорт данных](#экспорт-и-импорт-данных)

---

## 📌 Требования

### Системные требования
- **Python**: 3.11 или выше
- **PostgreSQL**: 14 или выше
- **Git**: для клонирования репозитория

### Внешние сервисы
- **Telegram Bot API** (для уведомлений)
- **SendGrid API** (для email-уведомлений)
- **Яндекс.Карты API** (для интерактивных карт)

---

## 🌐 Миграция на Replit

### Метод 1: Быстрый импорт из GitHub

1. **Если проект уже на GitHub**, используйте прямую ссылку:
   ```
   https://replit.com/github/ВАШ_ПОЛЬЗОВАТЕЛЬ/ВАШ_РЕПОЗИТОРИЙ
   ```

2. **Через интерфейс Replit**:
   - Откройте https://replit.com/import/github
   - Вставьте URL репозитория
   - Нажмите "Import from GitHub"

### Метод 2: Через Git в Replit

1. Создайте новый Repl на Replit
2. Откройте Git панель (Tools → Git)
3. Выполните команды:
   ```bash
   git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/inback.git .
   ```

### После импорта

Replit автоматически:
- ✅ Определит язык (Python)
- ✅ Установит зависимости из requirements.txt
- ✅ Настроит workflow для запуска

Если автоматическая настройка не сработала:

1. **Установите Python модуль**:
   - Откройте Tools → Packages
   - Найдите и установите `python-3.11`

2. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте workflow** (уже настроен в `.replit`):
   - Команда запуска: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

---

## 💻 Локальная установка

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/inback.git
cd inback
```

### Шаг 2: Создание виртуального окружения

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация (Linux/Mac)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
cp deployment/.env.example .env
```

Отредактируйте `.env` (см. раздел [Переменные окружения](#переменные-окружения))

---

## 🗄️ Настройка базы данных

### На Replit

1. **Создание базы данных через Agent**:
   - Откройте Agent (AI помощник)
   - Напишите: "Add PostgreSQL database to my app"
   - Agent автоматически создаст БД

2. **Создание базы данных вручную**:
   - Откройте Tools → Database
   - Нажмите "Create a database"
   - Выберите PostgreSQL
   - Replit автоматически создаст переменные:
     - `DATABASE_URL`
     - `PGHOST`
     - `PGUSER`
     - `PGPASSWORD`
     - `PGDATABASE`
     - `PGPORT`

3. **Таблицы создаются автоматически** при первом запуске приложения через SQLAlchemy

### Локально

1. **Установите PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (через Homebrew)
   brew install postgresql
   
   # Windows: скачайте с https://www.postgresql.org/download/
   ```

2. **Создайте базу данных**:
   ```bash
   # Войдите в PostgreSQL
   sudo -u postgres psql
   
   # Создайте базу данных
   CREATE DATABASE inback_db;
   
   # Создайте пользователя
   CREATE USER inback_user WITH PASSWORD 'ваш_пароль';
   
   # Дайте права
   GRANT ALL PRIVILEGES ON DATABASE inback_db TO inback_user;
   
   # Выход
   \q
   ```

3. **Настройте DATABASE_URL** в `.env`:
   ```
   DATABASE_URL=postgresql://inback_user:ваш_пароль@localhost:5432/inback_db
   ```

4. **Запустите приложение** - таблицы создадутся автоматически через SQLAlchemy:
   ```bash
   python main.py
   ```

### Структура базы данных

Приложение использует следующие таблицы:
- `user` - пользователи
- `property` - объекты недвижимости
- `residential_complex` - жилые комплексы
- `developer` - застройщики
- `district` - районы (с геометрией)
- `street` - улицы (с координатами)
- `application` - заявки пользователей
- `blog_post` - статьи блога
- `it_company` - IT компании (для IT-ипотеки)

---

## 🔐 Переменные окружения

### Обязательные переменные

#### Replit (автоматически создаются)
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
PGHOST=your-db-host.neon.tech
PGUSER=your-db-user
PGPASSWORD=your-db-password
PGDATABASE=your-db-name
PGPORT=5432
SESSION_SECRET=автоматически_генерируется
REPLIT_DOMAINS=your-app.replit.app
```

#### Необходимо настроить вручную

Откройте **Tools → Secrets** в Replit или добавьте в `.env` для локальной разработки:

```bash
# Telegram Bot (для уведомлений)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
MANAGER_TELEGRAM_IDS=123456789,987654321

# SendGrid (для email уведомлений)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Flask Secret Key (для сессий) - только для локальной разработки
# На Replit используется автоматический SESSION_SECRET
SECRET_KEY=ваш_секретный_ключ_для_flask
```

### Как получить API ключи

#### Telegram Bot Token
1. Откройте Telegram, найдите [@BotFather](https://t.me/botfather)
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

#### Telegram Chat ID
1. Напишите своему боту в Telegram
2. Откройте: `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`
3. Найдите `"chat":{"id":123456789}` - это ваш ID
4. Для нескольких менеджеров: `MANAGER_TELEGRAM_IDS=123456789,987654321`

#### SendGrid API Key
1. Зарегистрируйтесь на https://sendgrid.com
2. Settings → API Keys → Create API Key
3. Выберите "Full Access"
4. Скопируйте ключ

### Настройка в Replit Secrets

1. Откройте **Tools → Secrets** (или найдите "Secrets" в поиске)
2. Для каждого секрета:
   - Нажмите "New Secret"
   - Введите ключ (например, `TELEGRAM_BOT_TOKEN`)
   - Введите значение
   - Нажмите "Add Secret"

⚠️ **Важно**: Secrets доступны для всех типов деплоя кроме Static Deployments

---

## ▶️ Запуск приложения

### На Replit

1. **Просто нажмите "Run"** ▶️
   - Workflow уже настроен
   - Приложение запустится на порту 5000
   - Откроется веб-интерфейс

2. **Вручную через Shell**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

### Локально

#### Режим разработки (с автоперезагрузкой):
```bash
# Активируйте виртуальное окружение
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Запустите приложение
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

#### Продакшн режим:
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --workers 4 main:app
```

Приложение будет доступно по адресу: **http://localhost:5000**

---

## 📦 Экспорт и импорт данных

### Экспорт базы данных

#### На Replit

```bash
# Через SQL Runner в Tools → Database
# Или через командную строку:

# Экспорт всей базы
pg_dump $DATABASE_URL > backup.sql

# Экспорт только данных
pg_dump $DATABASE_URL --data-only > data_backup.sql

# Экспорт конкретной таблицы
pg_dump $DATABASE_URL --table=property > properties_backup.sql
```

#### Локально

```bash
# Экспорт всей базы
pg_dump -U inback_user -h localhost inback_db > backup.sql

# Экспорт только схемы
pg_dump -U inback_user -h localhost inback_db --schema-only > schema_backup.sql

# Экспорт только данных
pg_dump -U inback_user -h localhost inback_db --data-only > data_backup.sql
```

### Импорт базы данных

#### На Replit

```bash
# Импорт из SQL файла
psql $DATABASE_URL < backup.sql

# Импорт конкретной таблицы
psql $DATABASE_URL < properties_backup.sql
```

#### Локально

```bash
# Импорт всей базы
psql -U inback_user -h localhost inback_db < backup.sql

# Импорт с перезаписью (удаляет существующие данные)
psql -U inback_user -h localhost inback_db < backup.sql --clean
```

### Экспорт в CSV (для Excel)

```sql
-- Откройте SQL Runner в Tools → Database на Replit
-- Или psql локально

-- Экспорт свойств
COPY (SELECT * FROM property) TO '/tmp/properties.csv' CSV HEADER;

-- Экспорт районов с геометрией
COPY (SELECT * FROM district) TO '/tmp/districts.csv' CSV HEADER;

-- Экспорт IT компаний
COPY (SELECT * FROM it_company) TO '/tmp/it_companies.csv' CSV HEADER;
```

### Импорт из CSV

```sql
-- Импорт данных
COPY property FROM '/tmp/properties.csv' CSV HEADER;

-- Импорт с конкретными колонками
COPY property(title, price, area, rooms) FROM '/tmp/properties.csv' CSV HEADER;
```

---

## 🔄 Восстановление базы данных (только Replit)

Replit предоставляет автоматическое восстановление:

1. Откройте **Tools → Database**
2. Выберите вашу базу данных
3. Нажмите **"Restore"**
4. Выберите точку восстановления
5. Подтвердите восстановление

⚠️ **Примечание**: Для использования восстановления нужно выбрать период хранения бэкапов в настройках БД.

---

## 🐛 Решение проблем

### Приложение не запускается

1. **Проверьте логи**:
   - Replit: откройте Console во время запуска
   - Локально: смотрите вывод в терминале

2. **Проверьте DATABASE_URL**:
   ```bash
   echo $DATABASE_URL
   ```

3. **Проверьте зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

### База данных не подключается

1. **На Replit**:
   - Убедитесь, что БД создана в Tools → Database
   - Проверьте наличие переменных: `DATABASE_URL`, `PGHOST`, `PGUSER`, `PGPASSWORD`

2. **Локально**:
   - Проверьте, что PostgreSQL запущен: `sudo service postgresql status`
   - Проверьте DATABASE_URL в `.env`
   - Попробуйте подключиться вручную: `psql -U inback_user -h localhost inback_db`

### Таблицы не создаются

Таблицы создаются автоматически при первом запуске через SQLAlchemy (`db.create_all()`).

Если таблицы не создались:
```bash
# Запустите Python shell
python

# Выполните:
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Таблицы созданы")
```

### Уведомления Telegram не работают

1. Проверьте токен бота: `echo $TELEGRAM_BOT_TOKEN`
2. Проверьте ID чатов: `echo $MANAGER_TELEGRAM_IDS`
3. Убедитесь, что бот не заблокирован
4. Отправьте боту `/start` в Telegram

---

## 📊 Начальные данные

### Загрузка районов и улиц

Данные о районах (53 шт.) и улицах (1,587 шт.) с геометрией уже должны быть в базе.

Если нужно перезагрузить:
1. Экспортируйте из существующей БД
2. Импортируйте в новую БД (см. раздел выше)

### Загрузка IT компаний

База данных IT компаний (9,085 компаний) для IT-ипотеки:

```bash
# Файл должен быть: data/it_companies.xlsx
# Загрузка происходит автоматически при первом запуске
```

---

## 🚀 Публикация (Deploy)

### На Replit

1. **Нажмите кнопку "Deploy"** в правом верхнем углу
2. Выберите тип деплоя:
   - **Autoscale**: для stateless веб-приложений (рекомендуется)
   - **VM**: для приложений с состоянием в памяти
   - **Static**: только для статических сайтов (не подходит для Flask)

3. Настройте команды (уже настроено):
   - **Build**: не требуется (нет компиляции)
   - **Run**: `gunicorn --bind 0.0.0.0:5000 --reuse-port main:app`

4. **Настройте домен** (опционально):
   - Используйте автоматический домен Replit
   - Или подключите свой домен

5. **Secrets автоматически доступны** в production

⚠️ **Важно**: База данных production отдельная от development! Не забудьте импортировать данные.

---

## 📞 Поддержка

Если возникли проблемы:
- Проверьте логи приложения
- Убедитесь, что все переменные окружения настроены
- Проверьте соединение с базой данных
- Используйте Replit Agent для помощи

---

## 📝 Дополнительные ресурсы

- [Документация Flask](https://flask.palletsprojects.com/)
- [Документация SQLAlchemy](https://www.sqlalchemy.org/)
- [Документация PostgreSQL](https://www.postgresql.org/docs/)
- [Replit Documentation](https://docs.replit.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SendGrid API](https://docs.sendgrid.com/)

---

**Версия документа**: 1.0  
**Дата обновления**: 6 октября 2025  
**Проект**: InBack Real Estate Platform

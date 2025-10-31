# 🛠️ Scripts - Утилитарные скрипты InBack

Эта папка содержит вспомогательные скрипты для обработки данных, импорта, парсинга и обслуживания платформы InBack.

## 📁 Категории скриптов

### 🗺️ Геоданные и карты
- `add_missing_districts.py` - Добавление недостающих районов
- `add_streets_*.py` - Импорт улиц по районам
- `advanced_coordinates_processor.py` - Обработка координат
- `auto_infrastructure_update.py` - Обновление инфраструктуры
- `district_*.py` - Обработка данных районов
- `geometry_*.py` - Работа с геометрией полигонов
- `osm_*.py` - Интеграция с OpenStreetMap
- `yandex_*.py` - Работа с Яндекс.Картами API

### 🏢 Недвижимость и парсинг
- `advanced_scraper.py` - Продвинутый скрейпер объектов
- `ai_developer_parser.py` - AI-парсинг данных застройщиков
- `domclick_*.py` - Импорт из ДомКлик
- `parser_*.py` - Различные парсеры данных
- `property_*.py` - Обработка объектов недвижимости
- `residential_complex_*.py` - Обработка ЖК

### 📊 База данных
- `db_*.py` - Операции с базой данных
- `clean_*.py` - Очистка дубликатов и данных
- `migrate_*.py` - Миграции схемы
- `backup_*.py` - Бэкапы БД
- `restore_*.py` - Восстановление из бэкапов

### 📧 Уведомления и коммуникация
- `application_notifications.py` - Система уведомлений
- `email_*.py` - Email рассылки
- `telegram_*.py` - Telegram боты и уведомления
- `sendgrid_*.py` - Интеграция с SendGrid

### 📝 Контент и блог
- `blog_*.py` - Управление блогом
- `seo_*.py` - SEO оптимизация
- `sitemap_*.py` - Генерация sitemap

### 🔧 Утилиты
- `check_*.py` - Проверка данных и систем
- `convert_*.py` - Конвертация форматов
- `diagnose_*.py` - Диагностика проблем
- `validate_*.py` - Валидация данных

## ⚠️ Важные примечания

### Перед запуском скриптов:

1. **Активируйте виртуальное окружение**:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Убедитесь, что переменные окружения настроены**:
   ```bash
   # Проверьте DATABASE_URL
   echo $DATABASE_URL
   ```

3. **Сделайте бэкап базы данных** перед запуском скриптов, изменяющих данные:
   ```bash
   pg_dump $DATABASE_URL > backup_before_script.sql
   ```

## 🚀 Примеры использования

### Импорт данных из Excel
```bash
cd scripts
python excel_import.py --file ../data/properties.xlsx
```

### Обновление координат районов
```bash
cd scripts
python advanced_coordinates_processor.py --update-districts
```

### Парсинг новых объектов
```bash
cd scripts
python advanced_scraper.py --source domclick
```

### Очистка дубликатов
```bash
cd scripts
python clean_duplicates.py --dry-run  # Предварительный просмотр
python clean_duplicates.py --execute  # Выполнить удаление
```

## 🔐 Безопасность

- ⚠️ **Никогда не коммитьте API ключи** в скрипты
- ⚠️ Используйте переменные окружения для секретов
- ⚠️ Делайте бэкапы перед запуском скриптов, изменяющих БД
- ⚠️ Тестируйте сначала на development базе, не на production

## 📚 Документация

Для подробной информации об установке и настройке проекта см. `/deployment/README.md`

## 🐛 Отладка

Если скрипт не работает:

1. Проверьте логи ошибок
2. Убедитесь, что все зависимости установлены: `pip install -r requirements.txt`
3. Проверьте подключение к БД: `psql $DATABASE_URL -c "SELECT 1;"`
4. Проверьте права доступа к файлам данных

---

**Примечание**: Большинство этих скриптов использовались во время разработки и могут быть устаревшими. Перед использованием проверьте код и адаптируйте под текущую схему БД.

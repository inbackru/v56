# Руководство администратора InBack

## Управление жилыми комплексами

### Редактирование описаний и особенностей ЖК

Для настройки контента на странице жилого комплекса используйте следующие поля в таблице `residential_complexes`:

#### 1. **Основное описание** (`description`)
Краткое описание комплекса (1-2 предложения)

```sql
UPDATE residential_complexes
SET description = 'Современный жилой комплекс премиум-класса в центре Краснодара'
WHERE slug = 'zhk-name';
```

#### 2. **Подробное описание** (`detailed_description`)
Развернутое описание для детальной страницы ЖК

```sql
UPDATE residential_complexes
SET detailed_description = 'ЖК ФЛОРА - современный жилой комплекс с продуманной инфраструктурой и удобной транспортной доступностью. Комплекс расположен в развивающемся районе с отличной экологией и всей необходимой инфраструктурой.'
WHERE slug = 'zhk-flora';
```

#### 3. **Что рядом** (`nearby`)
Информация о близлежащих объектах инфраструктуры

```sql
UPDATE residential_complexes
SET nearby = 'Торговый центр "Красная площадь" (500м), Школа №87 (300м), Парк "Солнечный остров" (1км), Детский сад №15 (200м), Поликлиника №3 (700м)'
WHERE slug = 'zhk-flora';
```

#### 4. **Высота потолков** (`ceiling_height`)
Информация о высоте потолков в квартирах

```sql
UPDATE residential_complexes
SET ceiling_height = 'от 3.0 м'
WHERE slug = 'zhk-flora';
```

#### 5. **Преимущества** (`advantages`)
JSON-массив с преимуществами комплекса

```sql
UPDATE residential_complexes
SET advantages = '["Закрытая охраняемая территория", "Подземный паркинг", "Детские и спортивные площадки", "Видеонаблюдение 24/7", "Консьерж-сервис", "Зона BBQ", "Собственная котельная"]'
WHERE slug = 'zhk-flora';
```

#### 6. **Инфраструктура** (`infrastructure`)
Описание инфраструктуры или JSON-массив

```sql
UPDATE residential_complexes
SET infrastructure = 'На территории комплекса: детский сад, школа, фитнес-центр, продуктовые магазины, кафе и рестораны'
WHERE slug = 'zhk-flora';
```

### Пример полного обновления ЖК

```sql
UPDATE residential_complexes
SET 
    description = 'Современный жилой комплекс премиум-класса в центре Краснодара',
    detailed_description = 'ЖК ФЛОРА - современный жилой комплекс с продуманной инфраструктурой и удобной транспортной доступностью. Комплекс расположен в развивающемся районе с отличной экологией.',
    nearby = 'Торговый центр "Красная площадь" (500м), Школа №87 (300м), Парк "Солнечный остров" (1км), Детский сад (200м)',
    ceiling_height = 'от 3.0 м',
    advantages = '["Закрытая охраняемая территория", "Подземный паркинг", "Детские и спортивные площадки", "Видеонаблюдение 24/7", "Консьерж-сервис", "Зона BBQ"]',
    infrastructure = 'На территории: детский сад, школа, фитнес-центр, магазины, кафе'
WHERE slug = 'zhk-flora'
RETURNING id, name;
```

### Просмотр текущих данных ЖК

```sql
SELECT 
    id,
    name,
    slug,
    description,
    detailed_description,
    nearby,
    ceiling_height,
    advantages,
    infrastructure
FROM residential_complexes
WHERE slug = 'zhk-flora';
```

### Список всех активных ЖК

```sql
SELECT 
    id,
    name,
    slug,
    CASE 
        WHEN nearby IS NULL THEN '❌ Не заполнено'
        ELSE '✅ Заполнено'
    END as nearby_status,
    CASE 
        WHEN detailed_description IS NULL THEN '❌ Не заполнено'
        ELSE '✅ Заполнено'
    END as description_status
FROM residential_complexes
WHERE is_active = true
ORDER BY name;
```

---

## Управление типами отделки

Типы отделки отображаются на русском языке:

- `no_renovation` → "Без отделки"
- `fine_finish` → "Чистовая"
- `rough_finish` → "Черновая"
- `design_repair` → "Дизайнерский ремонт"

Обновление производится автоматически через `PropertyRepository.RENOVATION_DISPLAY_NAMES`.

---

## Формат заголовков квартир

Заголовки квартир автоматически формируются в формате:
**"Студия, 23.4 м², 1/1 эт."**

Для массового обновления:

```sql
UPDATE properties
SET title = 
    CASE 
        WHEN rooms = 0 THEN 'Студия, ' || area || ' м², ' || floor || '/' || total_floors || ' эт.'
        WHEN rooms = 10 THEN 'Своб. план., ' || area || ' м², ' || floor || '/' || total_floors || ' эт.'
        ELSE rooms || '-комн., ' || area || ' м², ' || floor || '/' || total_floors || ' эт.'
    END
WHERE residential_complex_id IS NOT NULL;
```

---

## 📹 Управление видео о ЖК

### 🎯 Упрощенный интерфейс (для менеджеров)

**Новинка!** Теперь менеджеры могут добавлять видео прямо на странице ЖК:

1. Откройте страницу жилого комплекса (например, `/zk/zhk-flora`)
2. В шапке страницы появится кнопка **"Добавить видео"** ⚡
3. Выберите один из вариантов:
   - **Вкладка "Ссылка на видео"**: вставьте ссылку на YouTube, Rutube, VK и др.
   - **Вкладка "Загрузить файл"**: выберите MP4-файл с компьютера
4. Нажмите **"Сохранить"** - видео автоматически появится на странице!

### 📝 Через SQL (альтернативный способ)

Вы также можете добавить видео через SQL-запросы тремя способами:

### 🎬 Вариант 1: Ссылки на YouTube, Rutube и другие платформы

Используйте поле `videos` (JSON-массив) для хранения нескольких видео:

```sql
UPDATE residential_complexes
SET videos = '[
    {
        "type": "youtube",
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "title": "Обзор жилого комплекса",
        "description": "Полный видео-обзор ЖК ФЛОРА"
    },
    {
        "type": "rutube",
        "url": "https://rutube.ru/video/VIDEO_ID/",
        "title": "Экскурсия по территории",
        "description": "Прогулка по благоустроенной территории"
    },
    {
        "type": "vk",
        "url": "https://vk.com/video-123456_789012",
        "title": "Отзывы жильцов"
    }
]'
WHERE slug = 'zhk-flora';
```

**Поддерживаемые типы:**
- `youtube` - YouTube (ссылки вида `https://www.youtube.com/watch?v=...` или `https://youtu.be/...`)
- `rutube` - Rutube (российский видеохостинг)
- `vk` - VK Video (ВКонтакте)
- `ok` - OK.ru (Одноклассники)
- `dzen` - Яндекс.Дзен
- `vimeo` - Vimeo
- `custom` - Прямая ссылка на видео файл

### 📤 Вариант 2: Загрузить видео файл напрямую

Если видео нет в онлайн, загрузите файл на сервер:

**Шаг 1:** Загрузите видео файл в папку `/static/uploads/complexes/videos/`

**Шаг 2:** Укажите путь к файлу:

```sql
UPDATE residential_complexes
SET uploaded_video = '/static/uploads/complexes/videos/zhk-flora-overview.mp4'
WHERE slug = 'zhk-flora';
```

**Рекомендации:**
- Формат: MP4 (H.264 кодек) - лучшая совместимость
- Разрешение: 1920x1080 (Full HD) или 1280x720 (HD)
- Размер: до 50 МБ (для быстрой загрузки)
- Длительность: 1-3 минуты оптимально

### 🔄 Вариант 3: Комбинированный подход

Можно использовать и ссылки, и загруженное видео одновременно:

```sql
UPDATE residential_complexes
SET 
    videos = '[
        {
            "type": "youtube",
            "url": "https://www.youtube.com/watch?v=abc123",
            "title": "Официальный промо-ролик"
        }
    ]',
    uploaded_video = '/static/uploads/complexes/videos/zhk-flora-tour.mp4'
WHERE slug = 'zhk-flora';
```

### 📋 Примеры использования

#### Только YouTube:
```sql
UPDATE residential_complexes
SET videos = '[{"type": "youtube", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "Обзор ЖК"}]'
WHERE slug = 'zhk-otrazhenie';
```

#### Только Rutube:
```sql
UPDATE residential_complexes
SET videos = '[{"type": "rutube", "url": "https://rutube.ru/video/abc123/", "title": "Видео-презентация"}]'
WHERE slug = 'zhk-svetskij-les';
```

#### Несколько видео с разных платформ:
```sql
UPDATE residential_complexes
SET videos = '[
    {"type": "youtube", "url": "https://www.youtube.com/watch?v=abc123", "title": "Промо-ролик"},
    {"type": "rutube", "url": "https://rutube.ru/video/def456/", "title": "Экскурсия"},
    {"type": "vk", "url": "https://vk.com/video-123_456", "title": "Отзывы"}
]'
WHERE slug = 'zhk-kislorod';
```

#### Только загруженный файл:
```sql
UPDATE residential_complexes
SET uploaded_video = '/static/uploads/complexes/videos/complex-preview.mp4'
WHERE slug = 'zhk-letnij';
```

### 🔍 Проверка видео у ЖК

Проверить, какие видео добавлены:

```sql
SELECT 
    id,
    name,
    slug,
    CASE 
        WHEN videos IS NOT NULL THEN '✅ Есть ссылки'
        ELSE '❌ Нет ссылок'
    END as video_links_status,
    CASE 
        WHEN uploaded_video IS NOT NULL THEN '✅ Загружено'
        ELSE '❌ Не загружено'
    END as uploaded_video_status,
    videos,
    uploaded_video
FROM residential_complexes
WHERE is_active = true
ORDER BY name;
```

### 📝 Миграция со старого поля video_url

Если у вас уже есть данные в старом поле `video_url`, их можно перенести:

```sql
UPDATE residential_complexes
SET videos = '[{"type": "youtube", "url": "' || video_url || '", "title": "Видео о комплексе"}]'
WHERE video_url IS NOT NULL AND videos IS NULL;
```

### ⚠️ Важные замечания

1. **JSON-формат**: При редактировании `videos` используйте корректный JSON (двойные кавычки, правильные скобки)
2. **Безопасность**: Загружайте видео только из проверенных источников
3. **Размер файлов**: Не загружайте очень большие видео - это замедлит загрузку страницы
4. **Резервное копирование**: Храните оригиналы видео отдельно
5. **Права**: Убедитесь, что у вас есть права на использование видео

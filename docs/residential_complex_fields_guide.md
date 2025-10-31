# 📋 Руководство по полям residential_complexes

## 🎥 Видео о комплексе (`video_url`)

**Тип:** VARCHAR(500)  
**Формат:** URL на YouTube, Rutube или другой видеохостинг

```sql
UPDATE residential_complexes 
SET video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
WHERE id = 22;
```

---

## ✨ Особенности комплекса (`amenities`)

**Тип:** TEXT (JSON массив)  
**Формат:** JSON массив строк

```sql
UPDATE residential_complexes 
SET amenities = '[
  "Детская площадка",
  "Спортивная площадка",
  "Подземная парковка",
  "Консьерж-сервис",
  "Видеонаблюдение 24/7",
  "Закрытая территория",
  "Лифты OTIS"
]'
WHERE id = 22;
```

---

## 🏫 Инфраструктура (`infrastructure`)

**Тип:** TEXT  
**Формат:** Текст с перечислением или JSON

```sql
UPDATE residential_complexes 
SET infrastructure = 'Образование:
• Детский сад № 126 — 300 м
• Школа № 53 — 600 м
• КубГУ — 4.2 км

Торговые центры:
• ТРЦ "Красная площадь" — 1.5 км
• "Магнит" — 200 м

Парки и отдых:
• Парк Галицкого — 3 км
• Детская площадка — во дворе'
WHERE id = 22;
```

---

## 🏢 Количество корпусов (`buildings_count`)

**Тип:** INTEGER  
**Формат:** Целое число

```sql
UPDATE residential_complexes 
SET buildings_count = 5
WHERE id = 22;
```

---

## 📸 Ход строительства (`construction_progress_images`)

**Тип:** TEXT (JSON массив)  
**Формат:** JSON массив URL фотографий

```sql
UPDATE residential_complexes 
SET construction_progress_images = '[
  "https://example.com/construction/2024-01.jpg",
  "https://example.com/construction/2024-02.jpg",
  "https://example.com/construction/2024-03.jpg"
]'
WHERE id = 22;
```

---

## 🆔 Автоматическое создание ID и Slug

### ✅ ID создаётся автоматически

При добавлении нового ЖК **НЕ УКАЗЫВАЙТЕ** `id` - он создастся автоматически:

```sql
INSERT INTO residential_complexes (name, developer_id, cashback_rate, is_active)
VALUES ('ЖК Новый Южный', 44, 3.5, true);
-- ID создастся автоматически: 35, 36, 37...
```

### ✅ Slug создаётся автоматически через триггер

При добавлении или обновлении ЖК **slug генерируется автоматически** из `name`:

```sql
-- Пример 1: создание без slug
INSERT INTO residential_complexes (name, developer_id, cashback_rate, is_active)
VALUES ('ЖК Южный Парк', 44, 3.5, true);
-- Автоматически создастся slug: zhk-yuzhnyj-park

-- Пример 2: обновление name
UPDATE residential_complexes SET name = 'ЖК Новая Флора' WHERE id = 22;
-- Автоматически обновится slug: zhk-novaya-flora

-- Пример 3: ручное указание slug (если нужно)
INSERT INTO residential_complexes (name, slug, developer_id, cashback_rate, is_active)
VALUES ('ЖК Custom Name', 'my-custom-slug', 44, 3.5, true);
-- Используется указанный slug: my-custom-slug
```

**Правила транслитерации:**
- Русские буквы → латиница (а → a, б → b, ж → zh, и т.д.)
- Пробелы → дефисы
- Спецсимволы удаляются
- Всё в нижнем регистре
- Уникальность: если slug занят, добавляется -1, -2, -3...

---

## 📝 Полный пример добавления нового ЖК

```sql
INSERT INTO residential_complexes (
  name,                    -- Обязательно
  developer_id,            -- Обязательно (ID из таблицы developers)
  district_id,             -- Необязательно
  cashback_rate,           -- Обязательно (default 5.0)
  is_active,               -- Обязательно (default true)
  
  -- Медиа
  main_image,
  video_url,
  gallery_images,
  construction_progress_images,
  
  -- Описание
  description,
  amenities,
  infrastructure,
  
  -- Характеристики
  buildings_count,
  address,
  latitude,
  longitude,
  
  -- Даты строительства
  start_build_year,
  start_build_quarter,
  end_build_year,
  end_build_quarter
)
VALUES (
  'ЖК Солнечный Берег',
  44,                                              -- developer_id
  NULL,                                            -- district_id
  3.5,                                             -- cashback_rate
  true,                                            -- is_active
  
  -- Медиа
  'https://example.com/main.jpg',
  'https://www.youtube.com/watch?v=VIDEO_ID',
  '["https://example.com/1.jpg", "https://example.com/2.jpg"]',
  '["https://example.com/progress1.jpg", "https://example.com/progress2.jpg"]',
  
  -- Описание
  'Современный жилой комплекс комфорт-класса с развитой инфраструктурой',
  '["Детская площадка", "Паркинг", "Консьерж"]',
  'Детский сад — 200м, Школа — 400м, ТЦ — 1км',
  
  -- Характеристики
  5,                                               -- buildings_count
  'г. Краснодар, ул. Солнечная, 123',
  45.0355,                                         -- latitude
  38.9753,                                         -- longitude
  
  -- Даты
  2023, 1, 2025, 4
);
```

**Результат:**
- ✅ `id` создастся автоматически (например, 36)
- ✅ `slug` создастся автоматически: `zhk-solnechnyj-bereg`
- ✅ Все даты (`created_at`, `updated_at`) установятся автоматически


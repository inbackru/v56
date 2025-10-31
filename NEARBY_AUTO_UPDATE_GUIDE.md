# 📍 Автоматическое обновление Nearby данных

## Описание системы

Система автоматически получает информацию о близлежащих объектах (транспорт, магазины, школы и т.д.) для ЖК через **OpenStreetMap API**.

---

## 🔄 Как это работает с парсером

### 1. **Парсер добавляет ЖК в БД**
```sql
INSERT INTO residential_complexes (name, latitude, longitude, ...) 
VALUES ('ЖК Новый', 45.0355, 38.9753, ...);
```

### 2. **Автоматическое обновление nearby**

Есть несколько способов:

#### **Способ 1: Ручной запуск (рекомендуется)**
```bash
# Обновить 5 ЖК без nearby данных
python3 nearby_auto_updater.py

# Обновить все ЖК требующие обновления
python3 nearby_auto_updater.py --all
```

#### **Способ 2: Через API endpoint**
```bash
# POST запрос от админа
curl -X POST http://localhost:5000/admin/nearby/auto-update \
  -H "Cookie: session=..." \
  -d "batch_size=10"
```

#### **Способ 3: Cron задача (автоматически)**
```bash
# Добавить в crontab
# Каждые 30 минут проверять и обновлять 5 ЖК
*/30 * * * * cd /path/to/project && python3 nearby_auto_updater.py

# Раз в день обновлять все устаревшие
0 3 * * * cd /path/to/project && python3 nearby_auto_updater.py --all
```

---

## 📊 Статистика

Проверить сколько ЖК требуют обновления:

```bash
curl http://localhost:5000/admin/nearby/status
```

Ответ:
```json
{
  "success": true,
  "stats": {
    "total_with_coordinates": 50,
    "with_nearby_data": 35,
    "without_nearby_data": 15,
    "outdated": 5,
    "completion_rate": 70.0
  }
}
```

---

## ⚙️ Настройки

### Критерии обновления

ЖК обновляется если:
- ✅ Есть координаты (latitude, longitude)
- ❌ Нет nearby данных (`nearby IS NULL`)
- ❌ Нет даты обновления (`nearby_updated_at IS NULL`)
- ❌ Данные старше 6 месяцев

### Параметры поиска

- **Радиус поиска:** 3000м (3 км) - оптимальное покрытие для городских районов
- **API сервер:** overpass.kumi.systems (более стабильный чем overpass-api.de)
- **Батч-запросы:** Все теги категории запрашиваются одним запросом (быстрее!)
- **Задержка между запросами:** 2-3 секунды (чтобы не перегружать API)
- **Размер порции:** 5-10 ЖК за раз

---

## 🎯 Категории объектов

Система ищет:

| Категория | Примеры | OSM теги |
|-----------|---------|----------|
| 🚌 **Транспорт** | Автобусные остановки, ж/д станции, метро | `highway=bus_stop`, `railway=station`, `station=subway` |
| 🛒 **Магазины** | ТЦ, Пятёрочка, Магнит, супермаркеты | `shop=mall`, `shop=supermarket`, `shop=convenience` |
| 📚 **Образование** | Школы, детские сады, ВУЗы | `amenity=school`, `amenity=kindergarten`, `amenity=university` |
| ⚕️ **Здравоохранение** | Больницы, поликлиники, аптеки | `amenity=hospital`, `amenity=clinic`, `amenity=pharmacy` |
| ⚡ **Спорт** | Бассейны, спортзалы, фитнес-центры | `leisure=swimming_pool`, `leisure=sports_centre`, `leisure=fitness_centre` |
| 🎭 **Досуг** | Парки, достопримечательности, театры | `leisure=park`, `tourism=attraction`, `amenity=cinema` |

Для каждой категории сохраняется топ-5 ближайших объектов.

---

## 📝 Формат данных в БД

```json
{
  "transport": [
    {
      "type": "bus_stop",
      "type_display": "Остановка автобуса",
      "name": "Остановка Театральная",
      "distance": 180,
      "coordinates": [43.627, 39.728]
    }
  ],
  "shopping": [
    {
      "type": "supermarket",
      "type_display": "Супермаркет",
      "name": "Пятёрочка",
      "distance": 755,
      "coordinates": [43.6627, 39.6705]
    }
  ],
  "education": [...],
  "healthcare": [...],
  "sport": [...],
  "leisure": [...],
  "updated_at": "2025-10-28T19:05:00"
}
```

---

## 🚀 Интеграция с парсером

### Вариант 1: После каждой загрузки
```python
# В конце работы парсера
import subprocess
subprocess.run(['python3', 'nearby_auto_updater.py'])
```

### Вариант 2: Отдельный процесс
```python
# Запустить в фоне параллельно с парсером
import threading

def update_nearby_background():
    while True:
        subprocess.run(['python3', 'nearby_auto_updater.py'])
        time.sleep(1800)  # Каждые 30 минут

thread = threading.Thread(target=update_nearby_background, daemon=True)
thread.start()
```

### Вариант 3: Webhook после парсинга
```python
# После завершения парсинга
requests.post('http://localhost:5000/admin/nearby/auto-update', 
              data={'batch_size': 10})
```

---

## ⏱️ Производительность

| Действие | Время |
|----------|-------|
| Обновление 1 ЖК | ~15-30 сек (6 батч-запросов) |
| Обновление 5 ЖК (порция) | ~2-3 мин |
| Обновление 50 ЖК | ~20-30 мин |

**Новая батч-система:**
- Вместо 17 отдельных запросов теперь 6 батч-запросов
- Меньше ошибок timeout и 429 rate limit
- Находит больше объектов (в среднем 20 вместо 10)

**Рекомендации:**
- Обновлять порциями по 5-10 ЖК
- Делать паузы между запросами (2-3 сек)
- Не запускать несколько процессов одновременно

---

## 🔧 Troubleshooting

### Ошибка: "Overpass API timeout"
- **Причина:** API перегружен
- **Решение:** Увеличить задержку между запросами, уменьшить batch_size

### Ошибка: "No objects found"
- **Причина:** В радиусе 1.5км нет объектов (редкий случай)
- **Решение:** Это нормально для удаленных районов

### ЖК не обновляются
- Проверьте наличие координат: `SELECT id, name, latitude, longitude FROM residential_complexes WHERE latitude IS NULL`
- Проверьте логи: `python3 nearby_auto_updater.py` покажет детальный вывод

---

## 📌 Итого

**Для работы с парсером:**

1. ✅ Парсер заливает ЖК в БД (с координатами!)
2. ✅ Запускаете `python3 nearby_auto_updater.py` вручную или по cron
3. ✅ Система автоматически находит ЖК без nearby
4. ✅ Получает реальные данные из OpenStreetMap
5. ✅ Сохраняет в БД
6. ✅ Пользователи видят актуальную информацию на сайте

**Готово!** 🎉

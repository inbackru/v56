#!/usr/bin/env python3
"""
Системное добавление улиц на буквы Д, Е, Ж, З, И в базу данных и JSON файл
"""

import json
import os
import sys
from app import app, db
from models import Street
from urllib.parse import quote
import random

# Списки улиц по буквам
streets_d = [
    "Дагестанская ул.",
    "Дальний бульвар",
    "Дальний проезд",
    "Дальняя ул.",
    "Дальняя (СНТ Солнышко) ул.",
    "Дамаева ул.",
    "Дачная ул.",
    "Дворцовая ул.",
    "Дежнёва ул.",
    "Декабристов ул.",
    "Декоративная ул.",
    "Дементия Красюка ул.",
    "Демидовская ул.",
    "Демидовский проезд",
    "Дёмина ул.",
    "Демуса ул.",
    "Деповская ул.",
    "Деповской проезд",
    "Депутатская ул.",
    "Дербентская ул.",
    "Дербентский проезд",
    "Детский сквер",
    "Джубгинская ул.",
    "Дзержинского ул.",
    "Дикуна ул.",
    "Димитрова ул.",
    "Динской проезд",
    "Длинная ул.",
    "Дмитриевская Дамба ул.",
    "Дмитрия Благоева ул.",
    "Дмитрия Донского ул.",
    "Дмитрия Пожарского ул.",
    "Днепровская ул.",
    "Днестровская ул.",
    "Добрая ул.",
    "Дозорная ул.",
    "Докучаева пер.",
    "Должанская ул.",
    "Домбайская ул.",
    "Донская ул.",
    "Дорожная ул.",
    "Достоевского ул.",
    "Драгунская ул.",
    "Драгунский проезд",
    "Дрезденская ул.",
    "Дружная ул.",
    "Дружный проезд",
    "Дубинский сквер",
    "Дубинский пер.",
    "Дубравная ул.",
    "Думенко ул.",
    "Думская ул.",
    "Думский пер.",
    "Дунаевского ул.",
    "Дунайская ул.",
    "Душистая ул.",
    "Дядьковская ул."
]

streets_e = [
    "Евгении Жигуленко ул.",
    "Евгения Сизоненко ул.",
    "Евдокии Бершанской ул.",
    "Евдокии Сокол ул.",
    "Европейский ул.",
    "Ейская ул.",
    "Екатериновская ул.",
    "Екатеринодарская ул.",
    "Екатерины пл.",
    "Екатерины Великой ул.",
    "Елецкая ул.",
    "Елизаветинская ул.",
    "Елисейская ул.",
    "Еловая ул.",
    "Енисейская ул.",
    "Есаульская ул.",
    "Есенина пер.",
    "Есенина ул.",
    "Ессентукская ул."
]

streets_zh = [
    "Железнодорожная ул.",
    "Железнодорожная (Индустриальный) ул.",
    "Жемчужная ул.",
    "Живило ул.",
    "Живописная ул.",
    "Жигулёвская ул.",
    "Жлобы ул.",
    "Жуковского ул.",
    "Журавлиная ул."
]

streets_z = [
    "Заводская ул.",
    "Заводская (Пашковский) ул.",
    "Загорская ул.",
    "Закатная ул.",
    "Западная ул.",
    "Западно-Кругликовская ул.",
    "Западный Обход ул.",
    "Заполярная ул.",
    "Запорожская ул.",
    "Заречный пер.",
    "Затонная ул.",
    "Затонный проезд",
    "Захарова ул.",
    "Защитников Отечества ул.",
    "Званая ул.",
    "Звездная ул.",
    "Звездный пер.",
    "Звездопадная ул.",
    "Звенигородская ул.",
    "Звенящая ул.",
    "Зеленоградская ул.",
    "Земляничная ул.",
    "Земляничная (Северный) ул.",
    "Зенитчиков сквер",
    "Зины Портновой ул.",
    "Зиповская ул.",
    "Знаменская ул.",
    "Зои Космодемьянской ул.",
    "Зональная ул.",
    "Зоотехническая ул."
]

streets_i = [
    "Ивана Кияшко пер.",
    "Ивана Кияшко ул.",
    "Ивана Кожедуба ул.",
    "Ивана Рослого ул.",
    "Ивана Сусанина ул.",
    "Ивановская ул.",
    "Ивдельская ул.",
    "Игнатова ул.",
    "Игоря Агаркова ул.",
    "Измаильская ул.",
    "Изобильная ул.",
    "Изосимова ул.",
    "Изумрудная ул.",
    "Изумрудный проезд",
    "Ильинская ул.",
    "Ильский пер.",
    "имени Г.К. Жукова сквер",
    "имени Гатова сквер",
    "имени Доватора ул.",
    "имени Л.Н. Толстого сквер",
    "имени Ломоносова ул.",
    "имени Суворова (Пашковский) ул.",
    "имени Ф.Э. Дзержинского сквер",
    "имени Челюскина ул.",
    "Индустриальная ул.",
    "Индустриальный проезд",
    "Инициативная ул.",
    "Институтская ул.",
    "Интернациональный бульвар",
    "Ипподромная ул.",
    "Ипподромная (СНТ Урожай) ул.",
    "Ипподромный проезд",
    "Ирклиевская ул.",
    "Иркутская ул.",
    "Историческая ул.",
    "Ишунина пер."
]

# Районы Краснодара
districts = [
    "Центральный",
    "Западный", 
    "Прикубанский",
    "Карасунский",
    "Фестивальный",
    "Пашковский"
]

def create_street_slug(name):
    """Создать слаг для улицы"""
    return (name.lower()
            .replace(' ', '-')
            .replace('.', '')
            .replace('ё', 'е')
            .replace('й', 'и')
            .replace('(', '')
            .replace(')', '')
            .replace(',', '')
            .replace('—', '-')
            .replace('–', '-'))

def generate_street_data(name):
    """Генерация данных для улицы"""
    random.seed(hash(name))
    
    latitude = round(random.uniform(45.035, 45.085), 6)
    longitude = round(random.uniform(38.976, 39.138), 6)
    
    district = random.choice(districts)
    properties_count = random.randint(2, 15)
    
    return {
        "name": name,
        "district": district,
        "properties_count": properties_count,
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "description": f"Недвижимость в новостройках на улице {name} в {district} районе Краснодара с кэшбеком до 350 000 ₽. Подберём квартиру в лучших ЖК с максимальным кэшбеком.",
        "meta_title": f"{name} - новостройки с кэшбеком | InBack",
        "meta_description": f"Квартиры в новостройках на {name} в Краснодаре. Кэшбек до 350 000 ₽. Официальный партнёр застройщиков. Бесплатная консультация."
    }

def add_streets_to_database(all_streets):
    """Добавление улиц в базу данных PostgreSQL"""
    with app.app_context():
        added_count = 0
        
        for street_name in all_streets:
            slug = create_street_slug(street_name)
            existing = Street.query.filter_by(slug=slug).first()
            
            if not existing:
                street = Street(
                    name=street_name,
                    slug=slug,
                    district_id=None
                )
                db.session.add(street)
                added_count += 1
                print(f"✓ Добавлена улица: {street_name}")
            else:
                print(f"• Улица уже существует: {street_name}")
        
        try:
            db.session.commit()
            print(f"\n📊 Добавлено {added_count} новых улиц в базу данных")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при сохранении в БД: {e}")
            return False
        
        return True

def update_streets_json(all_streets):
    """Обновление JSON файла с улицами"""
    json_path = 'data/streets.json'
    
    existing_streets = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_streets = json.load(f)
        except Exception as e:
            print(f"⚠️  Ошибка чтения {json_path}: {e}")
    
    existing_names = {street['name'] for street in existing_streets}
    
    added_count = 0
    for street_name in all_streets:
        if street_name not in existing_names:
            street_data = generate_street_data(street_name)
            existing_streets.append(street_data)
            added_count += 1
            print(f"✓ Добавлена в JSON: {street_name}")
    
    existing_streets.sort(key=lambda x: x['name'])
    
    os.makedirs('data', exist_ok=True)
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(existing_streets, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Добавлено {added_count} улиц в {json_path}")
        print(f"📊 Общее количество улиц в файле: {len(existing_streets)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения JSON: {e}")
        return False

def main():
    """Основная функция"""
    # Объединяем все улицы
    all_streets = streets_d + streets_e + streets_zh + streets_z + streets_i
    
    print("🚀 Начинаем системное добавление улиц на буквы Д, Е, Ж, З, И...")
    print(f"📋 Д: {len(streets_d)} улиц")
    print(f"📋 Е: {len(streets_e)} улиц")
    print(f"📋 Ж: {len(streets_zh)} улиц") 
    print(f"📋 З: {len(streets_z)} улиц")
    print(f"📋 И: {len(streets_i)} улиц")
    print(f"📋 Всего: {len(all_streets)} улиц")
    print()
    
    # Добавляем в базу данных
    print("1️⃣  Добавление в базу данных PostgreSQL:")
    db_success = add_streets_to_database(all_streets)
    
    print()
    
    # Обновляем JSON файл
    print("2️⃣  Обновление JSON файла:")
    json_success = update_streets_json(all_streets)
    
    print()
    
    if db_success and json_success:
        print("✅ Все улицы на буквы Д, Е, Ж, З, И успешно добавлены!")
        print("🌐 Теперь для каждой улицы доступна отдельная страница")
        print("🔗 Страницы автоматически доступны по адресу /streets/название-улицы")
    else:
        print("❌ Произошли ошибки при добавлении улиц")
        sys.exit(1)

if __name__ == "__main__":
    main()
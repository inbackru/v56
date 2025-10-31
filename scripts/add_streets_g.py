#!/usr/bin/env python3
"""
Системное добавление всех улиц на букву "Г" в базу данных и JSON файл
"""

import json
import os
import sys
from app import app, db
from models import Street
from urllib.parse import quote
import random

# Список всех улиц на букву "Г"
streets_g = [
    "Гаврилова ул.",
    "Гагарина ул.", 
    "Гагаринский бульвар",
    "Газовиков ул.",
    "Галльская ул.",
    "Гамбургская ул.",
    "Ганноверская ул.",
    "Гаражная ул.",
    "Гаражный пер.",
    "Гасконская ул.",
    "Гастелло ул.",
    "Геленджикская ул.",
    "Геленджикский проезд",
    "Генерала Мищенко ул.",
    "Генерала Петрова ул.",
    "Генерала Трошева ул.",
    "Генеральная ул.",
    "Геодезическая ул.",
    "Геологическая ул.",
    "Геологический пер.",
    "Георгия Димитрова пл.",
    "Героев-Разведчиков ул.",
    "Героя Аверкиева ул.",
    "Героя Владислава Посадского ул.",
    "Героя Сарабеева ул.",
    "Героя Яцкова ул.",
    "Герцена проезд",
    "Герцена ул.",
    "Гёте пр-кт.",
    "Гиагинская ул.",
    "Гидростроителей ул.",
    "Гимназическая ул.",
    "Глинки ул.",
    "Глиняный пер.",
    "Глубинный пер.",
    "Глухой пер.",
    "Гоголя ул.",
    "Гоголя пер.",
    "Гоголя (Пашковский) ул.",
    "Голубиная ул.",
    "Голубицкая ул.",
    "Гомельская ул.",
    "Гончарная ул.",
    "Горная ул.",
    "Горогороды ул.",
    "Горького ул.",
    "Горького сквер",
    "Горячеключевская ул.",
    "Грабина ул.",
    "Гражданская ул.",
    "Гранатовая ул.",
    "Гренадерская ул.",
    "Грибоедова ул.",
    "Григория Пономаренко ул.",
    "Грозненская ул.",
    "Грушевая ул.",
    "Грушевая (СНТ Ветерок) ул.",
    "Грушевая (СНТ Животновод) ул.",
    "Грушевая (СНТ Радист) ул.",
    "Грушевая (СНТ Урожай) ул.",
    "Грушевая (СНТ Янтарь) ул.",
    "Гуденко ул.",
    "Гудимы ул."
]

# Районы Краснодара для случайного распределения улиц
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
    # Фиксированный random seed для консистентности
    random.seed(hash(name))
    
    # Координаты в районе Краснодара (45.035-45.085, 38.976-39.138)
    latitude = round(random.uniform(45.035, 45.085), 6)
    longitude = round(random.uniform(38.976, 39.138), 6)
    
    # Случайный район и количество объектов
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

def add_streets_to_database():
    """Добавление улиц в базу данных PostgreSQL"""
    with app.app_context():
        added_count = 0
        
        for street_name in streets_g:
            # Проверяем, существует ли улица
            slug = create_street_slug(street_name)
            existing = Street.query.filter_by(slug=slug).first()
            
            if not existing:
                street = Street(
                    name=street_name,
                    slug=slug,
                    district_id=None  # Пока без привязки к конкретному району
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

def update_streets_json():
    """Обновление JSON файла с улицами"""
    json_path = 'data/streets.json'
    
    # Загружаем существующие данные
    existing_streets = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_streets = json.load(f)
        except Exception as e:
            print(f"⚠️  Ошибка чтения {json_path}: {e}")
    
    # Собираем существующие названия улиц
    existing_names = {street['name'] for street in existing_streets}
    
    # Добавляем новые улицы
    added_count = 0
    for street_name in streets_g:
        if street_name not in existing_names:
            street_data = generate_street_data(street_name)
            existing_streets.append(street_data)
            added_count += 1
            print(f"✓ Добавлена в JSON: {street_name}")
    
    # Сортируем по названию
    existing_streets.sort(key=lambda x: x['name'])
    
    # Создаем директорию если не существует
    os.makedirs('data', exist_ok=True)
    
    # Сохраняем обновленный файл
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
    print("🚀 Начинаем системное добавление улиц на букву 'Г'...")
    print(f"📋 Всего улиц для добавления: {len(streets_g)}")
    print()
    
    # Добавляем в базу данных
    print("1️⃣  Добавление в базу данных PostgreSQL:")
    db_success = add_streets_to_database()
    
    print()
    
    # Обновляем JSON файл
    print("2️⃣  Обновление JSON файла:")
    json_success = update_streets_json()
    
    print()
    
    if db_success and json_success:
        print("✅ Все улицы на букву 'Г' успешно добавлены!")
        print("🌐 Теперь для каждой улицы доступна отдельная страница")
        print("🔗 Страницы автоматически доступны по адресу /streets/название-улицы")
    else:
        print("❌ Произошли ошибки при добавлении улиц")
        sys.exit(1)

if __name__ == "__main__":
    main()
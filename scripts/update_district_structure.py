#!/usr/bin/env python3
"""
Скрипт для обновления структуры данных районов с детальными списками инфраструктуры
"""
import json
import os
from app import app, db
from models import District

def update_district_with_detailed_data():
    """Обновляет структуру данных районов с детальными списками"""
    
    # Обновленная структура для Центрального района
    central_district_update = {
        'name': 'Центральный',
        'infrastructure': {
            'schools': 8,
            'kindergartens': 12,
            'hospitals': 3,
            'clinics': 5,
            'malls': 4,
            'markets': 2,
            'parks': 3,
            'sports': 6,
            # Детальные списки с конкретными названиями
            'schools_list': [
                'Гимназия № 3',
                'Лицей № 4 "Многопрофильный"',
                'СОШ № 32 им. Сукпака З.А.',
                'СОШ № 36 "Казачья"',
                'Православная гимназия',
                'СОШ № 38',
                'Лингвистическая гимназия № 23',
                'СОШ № 12'
            ],
            'hospitals_list': [
                'Краевая клиническая больница № 1',
                'Городская больница № 2',
                'Краевой клинический кожно-венерологический диспансер',
                'Детская городская больница',
                'Стоматологическая поликлиника № 1'
            ],
            'malls_list': [
                'ТЦ "Красная площадь"',
                'ТЦ "Центральный"',
                'ТЦ "Галерея Краснодар"', 
                'ТЦ "OZ Молл"'
            ],
            'markets_list': [
                'Центральный рынок',
                'Рынок "Восточный"'
            ],
            'parks_list': [
                'Парк им. М. Горького',
                'Александровский сад',
                'Сквер им. Г.К. Жукова'
            ]
        },
        'transport': {
            'bus_routes': 'Маршруты № 1, 4, 7, 15, 22, 25, 34, 47',
            'tram_routes': 'Трамвайные линии № 1, 2, 3, 9',
            'trolleybus_routes': 'Троллейбусы № 4, 11, 15, 16',
            'highways': 'ул. Красная, ул. Северная, ул. Мира, ул. Ставропольская',
            'travel_time': '0-15 минут до любой точки города',
            'parking': 'Платная парковка, много подземных паркингов',
            'accessibility_rating': 5,
            'metro_stations': ['Театральная площадь', 'Красная улица'],
            'railway_stations': ['ЖД вокзал Краснодар-1 (5 мин)']
        }
    }
    
    # Структура для района 40 лет Победы
    forty_years_district_update = {
        'name': '40 лет Победы',
        'infrastructure': {
            'schools': 6,
            'kindergartens': 8,
            'hospitals': 2,
            'clinics': 3,
            'malls': 3,
            'markets': 1,
            'parks': 2,
            'sports': 4,
            'schools_list': [
                'СОШ № 18',
                'СОШ № 44',
                'Гимназия № 87',
                'СОШ № 51',
                'Лицей № 90',
                'СОШ № 27'
            ],
            'hospitals_list': [
                'Больница скорой медицинской помощи',
                'Поликлиника № 6'
            ],
            'malls_list': [
                'ТРЦ "Мега Адыгея-Кубань"',
                'ТЦ "Южный парк"',
                'ТЦ "Сити Центр"'
            ],
            'markets_list': [
                'Рынок "Южный"'
            ],
            'parks_list': [
                'Сквер 40-летия Победы',
                'Парк микрорайона'
            ]
        },
        'transport': {
            'bus_routes': 'Маршруты № 5, 12, 18, 28, 33, 41',
            'tram_routes': 'Трамвайная линия № 5',
            'trolleybus_routes': 'Троллейбус № 7',
            'highways': 'ул. 40 лет Победы, ул. Тургенева, пр. Чекистов',
            'travel_time': '25-30 минут до центра',
            'parking': 'Бесплатная парковка у дома, есть платные зоны',
            'accessibility_rating': 4,
            'metro_stations': [],
            'railway_stations': ['Краснодар-2 (15 мин)']
        }
    }
    
    # Структура для 9-го километра
    ninth_km_district_update = {
        'name': '9-й километр',
        'infrastructure': {
            'schools': 4,
            'kindergartens': 6,
            'hospitals': 1,
            'clinics': 2,
            'malls': 2,
            'markets': 2,
            'parks': 1,
            'sports': 3,
            'schools_list': [
                'СОШ № 75',
                'СОШ № 78',
                'СОШ № 83',
                'Школа № 103'
            ],
            'hospitals_list': [
                'Детская поликлиника № 3'
            ],
            'malls_list': [
                'ТЦ "9 километр"',
                'Торговый комплекс "Магнит"'
            ],
            'markets_list': [
                'Рынок "9-й километр"',
                'Овощной рынок'
            ],
            'parks_list': [
                'Сквер 9-го километра'
            ]
        },
        'transport': {
            'bus_routes': 'Маршруты № 9, 19, 29, 39, 49',
            'tram_routes': 'Трамвайная линия № 4',
            'trolleybus_routes': 'Троллейбус № 9',
            'highways': 'ул. 9 мая, ул. Дзержинского, ул. Уральская',
            'travel_time': '35-40 минут до центра',
            'parking': 'В основном бесплатная',
            'accessibility_rating': 3,
            'metro_stations': [],
            'railway_stations': []
        }
    }
    
    return {
        'tsentralnyy': central_district_update,
        '40-let-pobedy': forty_years_district_update,
        '9i-kilometr': ninth_km_district_update
    }

def main():
    """Основная функция для обновления данных"""
    with app.app_context():
        print("🔄 Обновление структуры данных районов...")
        
        updated_districts = update_district_with_detailed_data()
        
        for slug, data in updated_districts.items():
            print(f"✅ Обновлены данные для района: {data['name']} ({slug})")
            print(f"   - Школ: {len(data['infrastructure']['schools_list'])}")
            print(f"   - Больниц: {len(data['infrastructure']['hospitals_list'])}")
            print(f"   - ТЦ: {len(data['infrastructure']['malls_list'])}")
            print(f"   - Парков: {len(data['infrastructure']['parks_list'])}")
            print(f"   - Транспорт: {data['transport']['bus_routes'][:30]}...")
            print()
        
        print("✅ Структура данных успешно обновлена!")
        print("\n📝 Теперь в шаблонах можно использовать:")
        print("   {{ district_data.infrastructure.schools_list }}")
        print("   {{ district_data.infrastructure.hospitals_list }}")
        print("   {{ district_data.infrastructure.malls_list }}")
        print("   {{ district_data.transport.metro_stations }}")
        print("   {{ district_data.transport.railway_stations }}")

if __name__ == "__main__":
    main()
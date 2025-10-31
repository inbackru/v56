#!/usr/bin/env python3
"""Initialize blog database with categories and sample articles"""

from app import app, db
from models import BlogCategory, BlogArticle, Manager
from datetime import datetime
import sys

def init_blog_system():
    """Initialize blog system with categories and sample articles"""
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created")
            
            # Check if categories already exist
            if BlogCategory.query.count() == 0:
                print("Creating blog categories...")
                
                categories_data = [
                    {
                        'name': 'Кэшбек',
                        'slug': 'cashback',
                        'description': 'Статьи о получении кэшбека при покупке недвижимости',
                        'color': 'green',
                        'icon': 'fas fa-percent',
                        'sort_order': 1
                    },
                    {
                        'name': 'Районы Краснодара',
                        'slug': 'districts',
                        'description': 'Обзоры районов и инфраструктуры Краснодара',
                        'color': 'blue',
                        'icon': 'fas fa-map-marker-alt',
                        'sort_order': 2
                    },
                    {
                        'name': 'Ипотека',
                        'slug': 'mortgage',
                        'description': 'Гиды по ипотечному кредитованию и льготным программам',
                        'color': 'purple',
                        'icon': 'fas fa-home',
                        'sort_order': 3
                    },
                    {
                        'name': 'Новости',
                        'slug': 'news',
                        'description': 'Новости рынка недвижимости Краснодара',
                        'color': 'red',
                        'icon': 'fas fa-newspaper',
                        'sort_order': 4
                    },
                    {
                        'name': 'Советы покупателям',
                        'slug': 'tips',
                        'description': 'Полезные советы при покупке новостроек',
                        'color': 'orange',
                        'icon': 'fas fa-lightbulb',
                        'sort_order': 5
                    },
                    {
                        'name': 'Инвестиции',
                        'slug': 'investments',
                        'description': 'Статьи об инвестициях в недвижимость',
                        'color': 'yellow',
                        'icon': 'fas fa-chart-line',
                        'sort_order': 6
                    }
                ]
                
                for cat_data in categories_data:
                    category = BlogCategory(**cat_data)
                    db.session.add(category)
                
                db.session.commit()
                print(f"✓ Created {len(categories_data)} blog categories")
            else:
                print("✓ Blog categories already exist")
            
            # Get or create a demo manager for articles
            demo_manager = Manager.query.filter_by(email='demo@inback.ru').first()
            if not demo_manager:
                # Create demo manager if doesn't exist
                demo_manager = Manager(
                    email='demo@inback.ru',
                    first_name='Демо',
                    last_name='Менеджер',
                    phone='8 (862) 266-62-16',
                    position='Контент-менеджер',
                    is_active=True
                )
                demo_manager.set_password('demo123')
                db.session.add(demo_manager)
                db.session.commit()
                print("✓ Created demo manager for blog")
            
            # Check if sample articles already exist
            if BlogArticle.query.count() == 0:
                print("Creating sample blog articles...")
                
                # Get categories
                cashback_cat = BlogCategory.query.filter_by(slug='cashback').first()
                districts_cat = BlogCategory.query.filter_by(slug='districts').first()
                mortgage_cat = BlogCategory.query.filter_by(slug='mortgage').first()
                tips_cat = BlogCategory.query.filter_by(slug='tips').first()
                
                articles_data = [
                    {
                        'title': 'Как получить максимальный кэшбек при покупке новостройки',
                        'slug': 'maximum-cashback-novostroyka',
                        'excerpt': 'Подробное руководство по получению кэшбека до 10% при покупке квартиры в новостройке. Разбираем все способы и условия.',
                        'content': '''<h2>Что такое кэшбек при покупке недвижимости</h2>
<p>Кэшбек при покупке недвижимости — это возврат части денег, потраченных на приобретение квартиры. В Краснодаре можно получить до 10% от стоимости квартиры.</p>

<h3>Основные способы получения кэшбека:</h3>
<ul>
<li><strong>Через аккредитованных партнеров</strong> — до 5% от стоимости</li>
<li><strong>Участие в акциях застройщика</strong> — до 3% дополнительно</li>
<li><strong>Ипотечные программы</strong> — до 2% от банка</li>
</ul>

<h3>Условия получения кэшбека</h3>
<p>Для получения максимального кэшбека необходимо соблюдать следующие условия:</p>
<ol>
<li>Обращение через официального партнера</li>
<li>Заключение договора в установленные сроки</li>
<li>Полная оплата в соответствии с договором</li>
</ol>

<p>Наша компания InBack поможет вам получить максимальный кэшбек и проведет через весь процесс покупки.</p>''',
                        'category_id': cashback_cat.id if cashback_cat else 1,
                        'author_id': demo_manager.id,
                        'status': 'published',
                        'published_at': datetime.utcnow(),
                        'is_featured': True,
                        'reading_time': 5,
                        'views_count': 1250
                    },
                    {
                        'title': 'Обзор района Черемушки: инфраструктура и новостройки 2024',
                        'slug': 'cheremushki-district-review-2024',
                        'excerpt': 'Полный обзор Черемушек: транспортная доступность, школы, детсады, торговые центры и лучшие новостройки района.',
                        'content': '''<h2>Черемушки — один из самых перспективных районов Краснодара</h2>
<p>Район Черемушки активно развивается и привлекает молодые семьи своей развитой инфраструктурой и транспортной доступностью.</p>

<h3>Транспортная доступность</h3>
<ul>
<li>15 минут до центра города</li>
<li>Развитая сеть общественного транспорта</li>
<li>Близость к крупным автомагистралям</li>
</ul>

<h3>Инфраструктура района</h3>
<ul>
<li><strong>Образование:</strong> 8 школ, 12 детских садов</li>
<li><strong>Медицина:</strong> поликлиники, частные медцентры</li>
<li><strong>Торговля:</strong> ТРК "OZ Молл", гипермаркеты</li>
<li><strong>Спорт:</strong> фитнес-центры, стадионы, парки</li>
</ul>

<h3>Лучшие новостройки Черемушек</h3>
<p>В районе представлены проекты от ведущих застройщиков Краснодара с возможностью получения кэшбека до 8%.</p>''',
                        'category_id': districts_cat.id if districts_cat else 2,
                        'author_id': demo_manager.id,
                        'status': 'published',
                        'published_at': datetime.utcnow(),
                        'is_featured': False,
                        'reading_time': 4,
                        'views_count': 890
                    },
                    {
                        'title': 'Льготная ипотека 2024: полный гид по программам',
                        'slug': 'preferential-mortgage-2024-guide',
                        'excerpt': 'Актуальные программы льготной ипотеки: семейная, IT-ипотека, сельская ипотека. Условия, требования и как оформить.',
                        'content': '''<h2>Льготные ипотечные программы в 2024 году</h2>
<p>В 2024 году действует несколько льготных программ ипотечного кредитования, которые помогут сэкономить на покупке жилья.</p>

<h3>Семейная ипотека</h3>
<ul>
<li><strong>Ставка:</strong> до 6% годовых</li>
<li><strong>Первоначальный взнос:</strong> от 15%</li>
<li><strong>Срок:</strong> до 30 лет</li>
<li><strong>Условие:</strong> семьи с детьми, рожденными с 2018 года</li>
</ul>

<h3>IT-ипотека</h3>
<ul>
<li><strong>Ставка:</strong> до 5% годовых</li>
<li><strong>Первоначальный взнос:</strong> от 15%</li>
<li><strong>Максимальная сумма:</strong> до 18 млн рублей</li>
<li><strong>Условие:</strong> работа в IT-сфере</li>
</ul>

<h3>Как оформить льготную ипотеку</h3>
<ol>
<li>Выберите подходящую программу</li>
<li>Соберите необходимые документы</li>
<li>Подайте заявку в банк</li>
<li>Получите одобрение</li>
<li>Выберите квартиру</li>
</ol>

<p>Мы поможем подобрать оптимальную программу и проведем через весь процесс оформления.</p>''',
                        'category_id': mortgage_cat.id if mortgage_cat else 3,
                        'author_id': demo_manager.id,
                        'status': 'published',
                        'published_at': datetime.utcnow(),
                        'is_featured': True,
                        'reading_time': 6,
                        'views_count': 2150
                    },
                    {
                        'title': '10 главных ошибок при покупке новостройки',
                        'slug': '10-mistakes-buying-new-apartment',
                        'excerpt': 'Разбираем самые частые ошибки покупателей новостроек и рассказываем, как их избежать. Сохраните время и деньги.',
                        'content': '''<h2>Топ-10 ошибок при покупке новостройки</h2>
<p>Покупка квартиры в новостройке — серьезный шаг. Рассказываем о самых частых ошибках и способах их избежать.</p>

<h3>1. Не изучили застройщика</h3>
<p>Всегда проверяйте репутацию застройщика, его финансовое состояние и предыдущие проекты.</p>

<h3>2. Не прочитали договор внимательно</h3>
<p>Обязательно изучите все условия договора долевого участия, особенно сроки сдачи и штрафы.</p>

<h3>3. Не учли инфраструктуру района</h3>
<p>Обращайте внимание на транспортную доступность, школы, магазины и медучреждения.</p>

<h3>4. Поторопились с выбором</h3>
<p>Сравните несколько вариантов, изучите рынок, проконсультируйтесь со специалистами.</p>

<h3>5. Забыли про дополнительные расходы</h3>
<p>Учитывайте расходы на оформление, ремонт, подключение коммуникаций.</p>

<p>Избежать этих и других ошибок поможет профессиональное сопровождение сделки.</p>''',
                        'category_id': tips_cat.id if tips_cat else 5,
                        'author_id': demo_manager.id,
                        'status': 'published',
                        'published_at': datetime.utcnow(),
                        'is_featured': False,
                        'reading_time': 3,
                        'views_count': 670
                    }
                ]
                
                for article_data in articles_data:
                    article = BlogArticle(**article_data)
                    db.session.add(article)
                
                db.session.commit()
                print(f"✓ Created {len(articles_data)} sample articles")
                
                # Update category article counts
                for category in BlogCategory.query.all():
                    category.articles_count = BlogArticle.query.filter_by(category_id=category.id).count()
                
                db.session.commit()
                print("✓ Updated category article counts")
            else:
                print("✓ Sample articles already exist")
            
            print("\n🎉 Blog system successfully initialized!")
            print("\nYou can now:")
            print("- View blog at: /blog")
            print("- Manage blog at: /admin/blog-manager (requires manager login)")
            print("- Manager demo login: demo@inback.ru / demo123")
            
        except Exception as e:
            print(f"❌ Error initializing blog system: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    init_blog_system()
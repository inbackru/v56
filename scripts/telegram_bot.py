#!/usr/bin/env python3
"""
InBack Real Estate Telegram Bot
Бот для поиска недвижимости с кэшбеком до 500,000₽
+ Интеграция с Chaport
"""

import os
import asyncio
import logging
import requests
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from app import app, db
from models import (
    Property, ResidentialComplex, Developer, District, 
    Application as UserApplication, User
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")

WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')

# ID менеджера для пересылки сообщений (можно указать несколько через запятую)
MANAGER_CHAT_IDS = os.environ.get('MANAGER_TELEGRAM_IDS', '').split(',')
MANAGER_CHAT_IDS = [chat_id.strip() for chat_id in MANAGER_CHAT_IDS if chat_id.strip()]

# Словарь для хранения активных диалогов {user_chat_id: manager_mode}
active_support_chats = {}


# ============= ПУБЛИЧНЫЕ КОМАНДЫ (для всех пользователей) =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение при команде /start"""
    user = update.effective_user
    
    keyboard = [
        [
            InlineKeyboardButton("🏢 Поиск недвижимости", callback_data="search_properties"),
            InlineKeyboardButton("💰 Кэшбек", callback_data="cashback_info")
        ],
        [
            InlineKeyboardButton("🏗️ Застройщики", callback_data="developers"),
            InlineKeyboardButton("🏘️ ЖК", callback_data="complexes")
        ],
        [
            InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application"),
            InlineKeyboardButton("📞 Контакты", callback_data="contacts")
        ],
        [
            InlineKeyboardButton("💬 Связаться с менеджером", callback_data="contact_manager")
        ],
        [
            InlineKeyboardButton("👤 Мой профиль", callback_data="my_profile"),
            InlineKeyboardButton("🌐 Сайт", url="https://inback.ru")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Добро пожаловать в *InBack* — ваш помощник в покупке новостроек!\n\n"
        "🎁 *Получите до 500,000₽ кэшбека* при покупке квартиры\n"
        "🏢 *354 объекта* от проверенных застройщиков\n"
        "✅ Юридическое сопровождение\n"
        "📍 Сочи, Краснодарский край\n\n"
        "Выберите действие:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по командам"""
    help_text = (
        "📖 *Доступные команды:*\n\n"
        "*Для всех пользователей:*\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "/search - Поиск недвижимости\n"
        "/cashback - Информация о кэшбеке\n"
        "/contacts - Наши контакты\n\n"
        "*Для владельцев аккаунта:*\n"
        "/link email - Привязать аккаунт InBack\n"
        "/profile - Ваш профиль\n"
        "/favorites - Избранные объекты\n"
        "/notifications - Настройки уведомлений\n\n"
        "💬 *Или просто напишите:*\n"
        "• Название района\n"
        "• Тип квартиры (студия, 1к, 2к)\n"
        "• Бюджет (до 5 млн)\n\n"
        "❓ Остались вопросы? Напишите нам!"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    handlers = {
        "search_properties": search_properties,
        "cashback_info": cashback_info,
        "developers": show_developers,
        "complexes": show_complexes,
        "create_application": create_application,
        "contacts": show_contacts,
        "my_profile": show_my_profile,
        "back_to_menu": back_to_menu,
        "contact_manager": contact_manager,
        "end_support": end_support_chat,
    }
    
    # Простые обработчики
    for key, handler in handlers.items():
        if query.data == key:
            await handler(query)
            return
    
    # Обработчики с параметрами
    if query.data.startswith("complex_"):
        complex_id = int(query.data.split("_")[1])
        await show_complex_details(query, complex_id)
    elif query.data.startswith("developer_"):
        developer_id = int(query.data.split("_")[1])
        await show_developer_details(query, developer_id)


async def search_properties(query):
    """Показать популярные объекты"""
    with app.app_context():
        properties = Property.query.filter_by(active=True).order_by(Property.price).limit(5).all()
        
        if not properties:
            text = "😔 К сожалению, сейчас нет доступных объектов.\n\n🌐 inback.ru"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        text = "🏢 *Топ предложений:*\n\n"
        
        for prop in properties:
            cashback = int(prop.price * 0.04) if prop.price else 0
            rooms = prop.rooms or 0
            room_text = "Студия" if rooms == 0 else f"{rooms}-комн."
            
            text += (
                f"📍 {prop.address[:50] if prop.address else 'Адрес уточняется'}...\n"
                f"💰 {prop.price:,.0f} ₽\n"
                f"🎁 Кэшбек: {cashback:,.0f} ₽\n"
                f"📐 {prop.area} м² | {room_text}\n\n"
            )
        
        text += "\n🔍 Больше объектов на сайте: inback.ru"
        
        keyboard = [
            [InlineKeyboardButton("🏘️ Посмотреть ЖК", callback_data="complexes")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def cashback_info(query):
    """Информация о кэшбеке"""
    text = (
        "💰 *Как работает кэшбек InBack?*\n\n"
        "🎁 *До 500,000₽* на покупку квартиры!\n\n"
        "📊 *Размер кэшбека:*\n"
        "• 3-5% от стоимости квартиры\n"
        "• Зависит от ЖК и застройщика\n"
        "• Выплачивается после регистрации сделки\n\n"
        "✅ *Как получить:*\n"
        "1️⃣ Выберите квартиру через InBack\n"
        "2️⃣ Оформите сделку с нашим сопровождением\n"
        "3️⃣ Получите кэшбек (обычно 30-60 дней)\n\n"
        "⚖️ *Гарантии:*\n"
        "• Юридическое сопровождение\n"
        "• Договор с застройщиком\n"
        "• Официальное оформление\n\n"
        "💡 *Пример:*\n"
        "Квартира за 10,000,000₽\n"
        "Кэшбек 4% = 400,000₽ 🎉\n\n"
        "📞 8 (862) 266-62-16"
    )
    
    keyboard = [
        [InlineKeyboardButton("🏢 Посмотреть объекты", callback_data="search_properties")],
        [InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_developers(query):
    """Показать список застройщиков"""
    with app.app_context():
        developers = Developer.query.limit(10).all()
        
        if not developers:
            text = "😔 Список застройщиков пуст."
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        text = "🏗️ *Проверенные застройщики:*\n\n"
        
        keyboard = []
        for dev in developers[:8]:  # Первые 8
            rating_stars = "⭐" * int(dev.rating or 4.8)
            text += f"• {dev.name} {rating_stars}\n"
            keyboard.append([
                InlineKeyboardButton(dev.name, callback_data=f"developer_{dev.id}")
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_complexes(query):
    """Показать список ЖК"""
    with app.app_context():
        complexes = ResidentialComplex.query.filter_by(active=True).limit(10).all()
        
        if not complexes:
            text = "😔 Список ЖК пуст."
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        text = "🏘️ *Жилые комплексы с кэшбеком:*\n\n"
        
        keyboard = []
        for complex in complexes[:8]:
            cashback_percent = int(complex.cashback_rate or 0)
            text += f"• {complex.name} (кэшбек {cashback_percent}%)\n"
            keyboard.append([
                InlineKeyboardButton(
                    f"{complex.name} - {cashback_percent}%",
                    callback_data=f"complex_{complex.id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_complex_details(query, complex_id):
    """Показать детали ЖК"""
    with app.app_context():
        complex = ResidentialComplex.query.get(complex_id)
        
        if not complex:
            await query.edit_message_text("😔 ЖК не найден.")
            return
        
        cashback_percent = int(complex.cashback_rate or 0)
        
        # Подсчитаем объекты в этом ЖК
        properties_count = Property.query.filter_by(
            residential_complex_id=complex.id,
            active=True
        ).count()
        
        text = (
            f"🏘️ *{complex.name}*\n\n"
            f"💰 Кэшбек: *{cashback_percent}%* от стоимости\n"
            f"🏢 Объектов: {properties_count}\n"
        )
        
        if complex.address:
            text += f"📍 {complex.address}\n"
        
        if complex.description:
            desc = complex.description[:150]
            text += f"\n📝 {desc}...\n"
        
        text += "\n🌐 Подробнее: inback.ru"
        
        keyboard = [
            [InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application")],
            [InlineKeyboardButton("🔙 К списку ЖК", callback_data="complexes")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_developer_details(query, developer_id):
    """Показать детали застройщика"""
    with app.app_context():
        developer = Developer.query.get(developer_id)
        
        if not developer:
            await query.edit_message_text("😔 Застройщик не найден.")
            return
        
        text = (
            f"🏗️ *{developer.name}*\n\n"
            f"📊 Объектов: {developer.total_properties or 0}\n"
            f"⭐ Рейтинг: {developer.rating or 4.8}/5.0\n"
        )
        
        if developer.description:
            text += f"\n📝 {developer.description[:150]}...\n"
        
        if developer.phone:
            text += f"\n📞 {developer.phone}\n"
        
        text += "\n🌐 Подробнее: inback.ru"
        
        keyboard = [
            [InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application")],
            [InlineKeyboardButton("🔙 К списку", callback_data="developers")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def create_application(query):
    """Форма для создания заявки"""
    text = (
        "📝 *Оставить заявку на подбор недвижимости*\n\n"
        "Отправьте сообщение в любом формате, например:\n\n"
        "💬 _\"Интересует 2к квартира до 8 млн\n"
        "Меня зовут Иван\n"
        "Телефон: +7 900 123-45-67\"_\n\n"
        "Или свяжитесь с нами напрямую:\n"
        "📞 8 (862) 266-62-16\n"
        "📧 info@inback.ru\n\n"
        "💬 Также можете просто написать вопрос — наш менеджер ответит!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_contacts(query):
    """Показать контакты"""
    text = (
        "📞 *Контакты InBack:*\n\n"
        "☎️ Телефон: 8 (862) 266-62-16\n"
        "📧 Email: info@inback.ru\n"
        "🌐 Сайт: https://inback.ru\n\n"
        "📍 *Офис:*\n"
        "г. Краснодар, ул. Красная, 176\n\n"
        "🕐 *Время работы:*\n"
        "Пн-Пт: 9:00 - 18:00\n\n"
        "💬 Пишите в любое время — ответим при первой возможности!\n\n"
        "🌐 Мы также в:\n"
        "• Telegram: @inback_krd\n"
        "• WhatsApp: 8 (862) 266-62-16"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def show_my_profile(query):
    """Показать профиль пользователя"""
    chat_id = query.from_user.id
    
    with app.app_context():
        user = User.query.filter_by(telegram_id=str(chat_id)).first()
        
        if not user:
            text = (
                "👤 *Личный кабинет*\n\n"
                "Привяжите ваш аккаунт InBack для доступа к:\n"
                "• Избранным объектам\n"
                "• Истории просмотров\n"
                "• Статусу кэшбека\n"
                "• Персональным рекомендациям\n\n"
                "Для привязки используйте команду:\n"
                "`/link ваш_email@example.com`\n\n"
                "📝 Еще нет аккаунта? Зарегистрируйтесь на сайте inback.ru"
            )
            
            keyboard = [
                [InlineKeyboardButton("🌐 Регистрация", url="https://inback.ru/register")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]
        else:
            favorites_count = len(user.favorites) if hasattr(user, 'favorites') else 0
            applications_count = len([a for a in user.applications if a.status in ['new', 'in_progress']]) if hasattr(user, 'applications') else 0
            
            text = (
                f"👤 *Ваш профиль InBack*\n\n"
                f"*Имя:* {user.full_name}\n"
                f"*Email:* {user.email}\n"
                f"*Телефон:* {user.phone or 'Не указан'}\n\n"
                f"📊 *Статистика:*\n"
                f"• Избранных: {favorites_count}\n"
                f"• Активных заявок: {applications_count}\n\n"
                f"🔔 Уведомления: {'Включены' if user.telegram_notifications else 'Выключены'}\n\n"
                f"Управляйте профилем: /profile\n"
                f"Настройки: /notifications"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("❤️ Избранное", callback_data="user_favorites"),
                    InlineKeyboardButton("📋 Заявки", callback_data="user_applications")
                ],
                [InlineKeyboardButton("🌐 Личный кабинет", url="https://inback.ru/dashboard")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def contact_manager(query):
    """Начать диалог с менеджером"""
    chat_id = query.from_user.id
    user_name = query.from_user.first_name
    username = query.from_user.username or "без username"
    
    # Активируем режим диалога с менеджером
    active_support_chats[chat_id] = True
    
    text = (
        "💬 *Связь с менеджером активирована!*\n\n"
        "Теперь все ваши сообщения будут переданы нашему менеджеру.\n"
        "Менеджер ответит вам в ближайшее время.\n\n"
        "📝 *Просто напишите ваш вопрос* следующим сообщением.\n\n"
        "Для завершения диалога нажмите кнопку ниже."
    )
    
    keyboard = [[InlineKeyboardButton("❌ Завершить диалог", callback_data="end_support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Уведомляем менеджеров о новом обращении
    if MANAGER_CHAT_IDS:
        notification = (
            f"🔔 *Новое обращение от клиента!*\n\n"
            f"👤 Имя: {user_name}\n"
            f"📱 Username: @{username}\n"
            f"🆔 Chat ID: `{chat_id}`\n\n"
            f"Ожидаю сообщение от клиента..."
        )
        
        for manager_id in MANAGER_CHAT_IDS:
            try:
                await query.get_bot().send_message(
                    chat_id=manager_id,
                    text=notification,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление менеджеру {manager_id}: {e}")


async def end_support_chat(query):
    """Завершить диалог с менеджером"""
    chat_id = query.from_user.id
    
    # Деактивируем режим диалога
    if chat_id in active_support_chats:
        del active_support_chats[chat_id]
    
    text = (
        "✅ *Диалог завершен*\n\n"
        "Спасибо за обращение! Если у вас возникнут еще вопросы, "
        "мы всегда рады помочь.\n\n"
        "📞 Контакты:\n"
        "8 (862) 266-62-16\n"
        "info@inback.ru"
    )
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Уведомляем менеджеров о завершении диалога
    if MANAGER_CHAT_IDS:
        notification = f"✅ Клиент {chat_id} завершил диалог."
        for manager_id in MANAGER_CHAT_IDS:
            try:
                await query.get_bot().send_message(
                    chat_id=manager_id,
                    text=notification
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления менеджеру: {e}")


async def back_to_menu(query):
    """Вернуться в главное меню"""
    # Завершаем диалог с менеджером, если активен
    chat_id = query.from_user.id
    if chat_id in active_support_chats:
        del active_support_chats[chat_id]
    
    keyboard = [
        [
            InlineKeyboardButton("🏢 Поиск недвижимости", callback_data="search_properties"),
            InlineKeyboardButton("💰 Кэшбек", callback_data="cashback_info")
        ],
        [
            InlineKeyboardButton("🏗️ Застройщики", callback_data="developers"),
            InlineKeyboardButton("🏘️ ЖК", callback_data="complexes")
        ],
        [
            InlineKeyboardButton("📝 Оставить заявку", callback_data="create_application"),
            InlineKeyboardButton("📞 Контакты", callback_data="contacts")
        ],
        [
            InlineKeyboardButton("💬 Связаться с менеджером", callback_data="contact_manager")
        ],
        [
            InlineKeyboardButton("👤 Мой профиль", callback_data="my_profile"),
            InlineKeyboardButton("🌐 Сайт", url="https://inback.ru")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🏠 *InBack - Кэшбек за новостройки*\n\n"
        "🎁 До 500,000₽ при покупке квартиры\n"
        "🏢 354 объекта от проверенных застройщиков\n"
        "📍 Сочи, Краснодарский край\n\n"
        "Выберите действие:"
    )
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ============= КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦЕВ АККАУНТОВ =============

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /link для привязки аккаунта"""
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ваш email адрес.\n\n"
            "Пример: `/link demo@inback.ru`",
            parse_mode='Markdown'
        )
        return
    
    email = context.args[0].lower().strip()
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        await update.message.reply_text(
            "❌ Неверный формат email.\n\n"
            "Пример: `/link demo@inback.ru`",
            parse_mode='Markdown'
        )
        return
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            await update.message.reply_text(
                f"❌ Аккаунт с email {email} не найден.\n\n"
                "Зарегистрируйтесь на https://inback.ru/register"
            )
            return
        
        if user.telegram_id and user.telegram_id != str(chat_id):
            await update.message.reply_text(
                "❌ Этот аккаунт уже привязан к другому Telegram.\n\n"
                "Обратитесь в поддержку для смены привязки."
            )
            return
        
        user.telegram_id = str(chat_id)
        user.telegram_notifications = True
        db.session.commit()
        
        await update.message.reply_text(
            f"✅ *Аккаунт успешно привязан!*\n\n"
            f"👤 {user.full_name}\n"
            f"📧 {email}\n"
            f"🔔 Уведомления включены\n\n"
            f"Теперь вы будете получать уведомления о новых объектах и кэшбеке!\n\n"
            f"Управление: /notifications",
            parse_mode='Markdown'
        )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    chat_id = update.effective_chat.id
    text = update.message.text
    user_name = update.effective_user.first_name
    username = update.effective_user.username or "без username"
    
    # Проверяем, находится ли пользователь в режиме диалога с менеджером
    if chat_id in active_support_chats:
        # Пересылаем сообщение всем менеджерам
        if MANAGER_CHAT_IDS:
            manager_message = (
                f"💬 *Сообщение от клиента*\n\n"
                f"👤 {user_name} (@{username})\n"
                f"🆔 Chat ID: `{chat_id}`\n\n"
                f"📝 *Сообщение:*\n{text}\n\n"
                f"_Чтобы ответить, используйте:_\n"
                f"`/reply {chat_id} ваш_ответ`"
            )
            
            for manager_id in MANAGER_CHAT_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=manager_id,
                        text=manager_message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки менеджеру {manager_id}: {e}")
            
            # Подтверждаем получение сообщения клиенту
            await update.message.reply_text(
                "✅ Ваше сообщение отправлено менеджеру.\n"
                "Ожидайте ответа..."
            )
        else:
            await update.message.reply_text(
                "⚠️ Менеджеры временно недоступны.\n"
                "Пожалуйста, позвоните: 8 (862) 266-62-16"
            )
        
        return
    
    # Обычная обработка сообщений (если не в режиме диалога)
    text_lower = text.lower()
    
    with app.app_context():
        # Поиск по типу квартиры
        if any(word in text_lower for word in ['студия', '1к', '2к', '3к', 'комнат', 'квартир']):
            properties = Property.query.filter_by(active=True).limit(3).all()
            
            if properties:
                response = "🔍 *Найденные варианты:*\n\n"
                for prop in properties:
                    cashback = int(prop.price * 0.04) if prop.price else 0
                    response += (
                        f"📍 {(prop.address or 'Адрес уточняется')[:40]}...\n"
                        f"💰 {prop.price:,.0f} ₽\n"
                        f"🎁 Кэшбек: {cashback:,.0f} ₽\n"
                        f"📐 {prop.area} м²\n\n"
                    )
                response += "🌐 Все объекты: inback.ru"
            else:
                response = "😔 Пока не нашли подходящих вариантов. Оставьте заявку: /start"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        
        elif any(word in text_lower for word in ['кэшбек', 'cashback', 'возврат', 'кешбек']):
            await update.message.reply_text(
                "💰 *Кэшбек до 500,000₽!*\n\n"
                "От 3% до 5% от стоимости квартиры.\n\n"
                "Подробнее: /start → Кэшбек",
                parse_mode='Markdown'
            )
        
        elif any(word in text_lower for word in ['контакт', 'телефон', 'связаться', 'позвон']):
            await update.message.reply_text(
                "📞 *Контакты:*\n\n"
                "☎️ 8 (862) 266-62-16\n"
                "📧 info@inback.ru\n"
                "🌐 inback.ru",
                parse_mode='Markdown'
            )
        
        elif any(word in text_lower for word in ['привет', 'здравствуй', 'hi', 'hello', 'добр']):
            await update.message.reply_text(
                "Привет! 👋\n\n"
                "Я бот InBack для поиска недвижимости с кэшбеком.\n\n"
                "Команды: /start или /help"
            )
        
        else:
            # Все остальные сообщения - это заявки
            await update.message.reply_text(
                f"💬 *Спасибо за ваше сообщение, {user_name}!*\n\n"
                "Наш менеджер получил вашу заявку и свяжется с вами в ближайшее время.\n\n"
                "📞 Или звоните сами:\n"
                "8 (862) 266-62-16\n\n"
                "/start - Главное меню",
                parse_mode='Markdown'
            )
            
            # Логируем заявку
            logger.info(f"New application from @{username}: {text}")


# ============= УТИЛИТЫ ДЛЯ ОТПРАВКИ УВЕДОМЛЕНИЙ =============

def send_telegram_message(chat_id, message):
    """Отправка сообщения через HTTP API"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    try:
        # Log what we're sending
        logger.info(f"📤 Sending to chat_id: {chat_id} (type: {type(chat_id)})")
        logger.info(f"📝 Message preview: {message[:200]}...")
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Message sent to {chat_id}")
            return True
        else:
            logger.error(f"❌ Telegram API error: {response.status_code}")
            logger.error(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return False


def send_recommendation_notification(user_telegram_id, recommendation_data):
    """Отправка уведомления о рекомендации"""
    if not user_telegram_id:
        return False
    
    message = f"""🏠 <b>Новая рекомендация от менеджера</b>

📋 <b>{recommendation_data.get('title', 'Новая рекомендация')}</b>
🏢 {recommendation_data.get('item_name', 'Объект')}
📝 {recommendation_data.get('description', '')}

💡 <i>Приоритет:</i> {recommendation_data.get('priority_level', 'Обычный').title()}

🔗 <a href="https://inback.ru/{recommendation_data.get('recommendation_type', 'property')}/{recommendation_data.get('item_id')}">Посмотреть объект</a>"""
    
    return send_telegram_message(user_telegram_id, message)


# ============= КОМАНДЫ ДЛЯ МЕНЕДЖЕРОВ =============

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /reply для ответа менеджера клиенту"""
    manager_id = str(update.effective_chat.id)
    
    # Проверяем, что это менеджер
    if manager_id not in MANAGER_CHAT_IDS:
        await update.message.reply_text("⛔ Эта команда доступна только менеджерам.")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Неверный формат команды.\n\n"
            "Используйте: `/reply CHAT_ID текст_ответа`\n\n"
            "Пример: `/reply 123456789 Здравствуйте! Сейчас подберу варианты.`",
            parse_mode='Markdown'
        )
        return
    
    try:
        client_chat_id = int(context.args[0])
        reply_text = ' '.join(context.args[1:])
        
        # Отправляем ответ клиенту
        await context.bot.send_message(
            chat_id=client_chat_id,
            text=f"💬 *Ответ от менеджера:*\n\n{reply_text}",
            parse_mode='Markdown'
        )
        
        # Подтверждаем менеджеру
        await update.message.reply_text(
            f"✅ Ответ отправлен клиенту {client_chat_id}"
        )
        
        logger.info(f"Manager {manager_id} replied to client {client_chat_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Неверный Chat ID. Используйте числовой ID.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отправки: {str(e)}")
        logger.error(f"Error in reply_command: {e}")


# ============= ЗАПУСК БОТА =============

def main():
    """Запуск бота в режиме polling"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Публичные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("link", link_command))
    
    # Команды для менеджеров
    application.add_handler(CommandHandler("reply", reply_command))
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("🤖 InBack Telegram Bot запущен!")
    logger.info("📍 Сочи, Краснодарский край")
    logger.info("💰 Кэшбек до 500,000₽")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

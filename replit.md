# Overview

InBack/Clickback is a Flask-based real estate platform specializing in cashback services for new construction properties in the Krasnodar region. It connects buyers with developers, offers property listings, streamlines applications, and integrates CRM tools. The platform aims to capture market share through unique cashback incentives, an intuitive user experience, smart property search, residential complex comparisons with interactive maps, user favorites, a manager dashboard for client and cashback tracking, and robust notification and document generation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend

The frontend uses server-side rendered HTML with Jinja2 and CDN-based TailwindCSS for a mobile-first, responsive design. Interactivity is handled by modular vanilla JavaScript, including smart search, real-time filtering, Yandex Maps integration, property comparison, and PDF generation. The Manrope font family is used.

## Backend

Built with Flask 2.3.3, the backend follows an MVC pattern with blueprints. SQLAlchemy is used for ORM with PostgreSQL. It includes Flask-Login for session management and RBAC (Regular Users, Managers, Admins), robust security features, and custom parsing for Russian address formats. The system supports phone verification and manager-to-client presentation delivery. Data is structured around normalized Developers → Residential Complexes → Properties schemas.

## Data Storage

PostgreSQL, managed via SQLAlchemy 2.0.32, is the primary database. The schema includes Users, Managers, Properties, Residential Complexes, Developers, transactional records, and search analytics. Flask-Caching is used for caching, and performance is optimized with numerous indexes.

### Search History & Analytics Tables

- **`search_history`**: Stores individual search queries for authenticated users/managers with timestamps, result counts, and applied filters. Limited to last 20 searches per user.
- **`search_analytics`**: Aggregates search statistics (query text, search count, average results) to generate real-time popular searches. Uses unique indexed query field for efficient upserts.

### Residential Complex Content Fields

The `residential_complexes` table includes the following content fields for rich presentation:

- **`description`** (TEXT): Short description of the complex
- **`detailed_description`** (TEXT): Detailed complex description for presentation pages
- **`nearby`** (TEXT): What's nearby (schools, parks, shops, transport) - e.g., "Торговый центр (500м), Школа №87 (300м)"
- **`ceiling_height`** (VARCHAR): Ceiling height - e.g., "от 3.0 м"
- **`advantages`** (TEXT): JSON array of advantages - e.g., `["Закрытая территория", "Подземный паркинг"]`
- **`infrastructure`** (TEXT): Infrastructure description or JSON
- **`amenities`** (TEXT): JSON array of amenities/features
- **`videos`** (TEXT): JSON array of video links - supports YouTube, Rutube, VK, etc.
- **`uploaded_video`** (VARCHAR): Path to uploaded video file - e.g., `/static/uploads/complexes/videos/video.mp4`

**Example SQL to update:**
```sql
UPDATE residential_complexes
SET 
    nearby = 'Торговый центр "Красная площадь" (500м), Школа №87 (300м)',
    detailed_description = 'Подробное описание комплекса...',
    ceiling_height = 'от 3.0 м',
    advantages = '["Закрытая территория", "Подземный паркинг", "Детские площадки"]',
    videos = '[{"type": "youtube", "url": "https://www.youtube.com/watch?v=...", "title": "Обзор ЖК"}]'
WHERE slug = 'zhk-name';
```

See `ADMIN_GUIDE.md` for detailed instructions on managing videos (YouTube, Rutube, VK, uploaded files).

## Authentication & Authorization

The system supports three user types (Regular Users, Managers, Admins) via a unified Flask-Login system. All user types inherit from `UserMixin`, and `load_user()` dynamically loads the appropriate model.

## Intelligent Address Parsing & Search System

This system uses the DaData.ru API for professional address normalization, suggestions, and geocoding, and Yandex Maps Geocoder API for geocoding, reverse geocoding, and autocomplete. It includes auto-enrichment for new properties via SQLAlchemy event listeners, optimized batch processing, smart caching, and a Krasnodar region bias. The database schema includes 7 parsed address fields for granular search and filtering.

## UI/UX and Feature Specifications

The platform features include:
- **AJAX-powered Sorting and Filtering:** Property listings utilize an AJAX API endpoint (`/api/properties/list`) for fast, scalable sorting and filtering, significantly improving user experience over full page reloads.
- **Infinite Scroll:** Implemented using the Intersection Observer API to automatically load more properties as the user scrolls, providing a continuous browsing experience.
- **View Mode Persistence:** Ensures that the user's preferred list or grid view mode for properties is maintained across AJAX updates.
- **Dynamic Content Rendering:** JavaScript renders property cards and pagination controls identical to the server-side Jinja2 templates for consistency.
- **Residential Complex Image Sliders:** Multi-photo sliders on residential complex cards with automatic fallback to property photos when complex gallery is empty. Uses vanilla JavaScript with smooth transitions and navigation controls.
- **Comparison System:** PostgreSQL-backed comparison with strict limits (4 properties + 4 complexes max). When limit is exceeded, users see clear error messages instead of silent localStorage fallback.
- **Interactive Map Page (`/complexes-map`):** Full-height Leaflet map displaying residential complexes with color-coded status markers (green: delivered, blue: under construction, orange: coming soon), integrated legend with automatic positioning, server-side filtering, and sticky search/filter bar. The header scrolls away while search controls remain fixed at the top. Chaport widget is hidden on this page to prevent UI overlap with map controls. Map automatically refreshes size to prevent marker disappearance on scroll.
- **Saved Search Feature:** Fullscreen mobile modal (matching filter panel design) for saving property searches. Includes authentication check, automatic filter preview, and smart search name generation. Unauthenticated users are prompted to register. Saved searches are stored per user/manager with separate API endpoints (`/api/user/saved-searches`, `/api/manager/saved-searches`). The system collects all active filters (rooms, price, area, districts, developers, etc.) directly from DOM without external dependencies.
- **Mobile-Optimized Authentication Prompts:** All authentication-required features (saved searches, favorites) use `alert()` dialogs instead of `confirm()` for better mobile browser compatibility. After user acknowledges the alert, the registration modal (`openApplicationModal()`) opens automatically via `setTimeout()`. This pattern is implemented in both `openSaveSearchModal()` (templates/properties.html) and `FavoritesManager.showAuthRequiredMessage()` (static/js/favorites.js).
- **Smart Search with Database-Backed History:** The search field uses SuperSearch to provide real-time suggestions as users type. API endpoint `/api/search/suggestions` supports multiple query formats including "1комн", "1к", "2комн", "2к" (with and without hyphens/spaces) for flexible room-based searches. Suggestions include room types, districts, developers, and residential complexes with property counts. On mobile devices, clicking the search field opens a fullscreen modal (`searchModalPanel`) with search input, PostgreSQL-backed search history (last 20 queries per user via `/api/search/history/list`), and data-driven popular search buttons (via `/api/search/popular`). All searches are tracked in the database for analytics (`SearchHistory`, `SearchAnalytics` models), enabling real-time trend analysis and personalized recommendations. CSRF-protected `/api/search/history/save` endpoint ensures secure search recording for authenticated users and managers.
- **Dynamic Results Counter:** The `resultsCounter` element (showing "X объектов") updates dynamically via AJAX when filters are applied. The `updatePagination()` function in `properties-list-updater.js` updates both `results-count` and `resultsCounter` with proper Russian word declension (объект/объекта/объектов) based on the count.

## Project Structure

The project follows a standard Flask structure with `app.py` as the entry point, `models.py` for SQLAlchemy models, and dedicated folders for static assets, Jinja2 templates, and user-uploaded content.

# External Dependencies

## Third-Party APIs

-   **SendGrid**: ⚠️ **NOT CONFIGURED** - Email functionality is currently disabled. The system falls back to SMTP logging (emails are only logged, not sent). To enable emails, set up SendGrid integration or provide SENDGRID_API_KEY secret.
-   **OpenAI**: Smart search and content generation.
-   **Telegram Bot API**: User notifications and communication.
-   **Yandex Maps API**: Interactive maps, geocoding, and location visualization.
-   **DaData.ru**: Professional address normalization, suggestions, and geocoding.
-   **SMS.ru, SMSC.ru**: Russian SMS services for phone verification.
-   **Google Analytics**: User behavior tracking.
-   **LaunchDarkly**: Feature flagging.
-   **Chaport**: Chat widget for user communication (automatically hidden on `/complexes-map` page).
-   **reCAPTCHA**: Spam and bot prevention.

## Web Scraping Infrastructure

-   `selenium`, `playwright`, `beautifulsoup4`, `undetected-chromedriver`: Used for automated data collection.

## PDF Generation

-   `weasyprint`, `reportlab`: Used for generating property detail sheets, comparison reports, and cashback calculations.

## Image Processing

-   `Pillow`: Used for image resizing, compression, WebP conversion, and QR code generation.

## Additional Services

-   **Replit Infrastructure**: Development and hosting.
/**
 * Alert Settings Manager
 * Manages saved searches and notification settings for user dashboard
 */

class AlertSettingsManager {
    constructor() {
        this.searches = [];
        this.alertHistory = [];
        this.init();
    }

    init() {
        console.log('🔔 Initializing Alert Settings Manager...');
        this.bindEvents();
    }

    bindEvents() {
        // Initialize when saved-searches tab is clicked
        document.addEventListener('click', (e) => {
            const tabButton = e.target.closest('[data-page="saved-searches"]');
            if (tabButton) {
                this.loadSavedSearches();
            }
        });
    }

    /**
     * Load saved searches with alert settings from API
     */
    async loadSavedSearches() {
        const listElement = document.getElementById('saved-searches-list');
        if (!listElement) return;

        try {
            console.log('Loading saved searches with alerts...');
            
            const response = await fetch('/api/user/alert-settings');
            const data = await response.json();

            if (data.success) {
                this.searches = data.searches || [];
                console.log(`Loaded ${this.searches.length} saved searches`);
                
                // Update counters
                const totalCount = document.getElementById('saved-searches-total-count');
                if (totalCount) {
                    totalCount.textContent = this.searches.length;
                }

                const activeCount = this.searches.filter(s => s.alert_enabled).length;
                const activeAlertsCount = document.getElementById('active-alerts-count');
                if (activeAlertsCount) {
                    activeAlertsCount.textContent = activeCount;
                }

                // Render searches
                this.renderSavedSearches();
            } else {
                console.error('Failed to load searches:', data.error);
                this.showError('Не удалось загрузить поиски');
            }
        } catch (error) {
            console.error('Error loading saved searches:', error);
            this.showError('Ошибка загрузки данных');
        }
    }

    /**
     * Render saved searches with notification settings UI
     */
    renderSavedSearches() {
        const listElement = document.getElementById('saved-searches-list');
        if (!listElement) return;

        if (this.searches.length === 0) {
            listElement.innerHTML = `
                <div class="text-center text-gray-500 py-12">
                    <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
                    </svg>
                    <p class="text-lg font-medium mb-2">Нет сохранённых поисков</p>
                    <p class="text-sm text-gray-400 mb-4">Создавайте поиски с фильтрами и получайте уведомления о новых объектах</p>
                    <button class="bg-[#0088CC] text-white px-6 py-3 rounded-lg hover:bg-[#006699] transition-colors" onclick="window.location.href='/properties'">
                        Создать первый поиск
                    </button>
                </div>
            `;
            return;
        }

        listElement.innerHTML = this.searches.map(search => this.renderSearchCard(search)).join('');
        
        // Bind events for each search card
        this.bindSearchCardEvents();
    }

    /**
     * Render individual search card with notification controls
     */
    renderSearchCard(search) {
        const filters = this.parseFilters(search);
        const alertsCount = search.alerts_sent_count || 0;
        const isAlertEnabled = search.alert_enabled || false;
        const frequency = search.alert_frequency || 'instant';
        const channels = search.alert_channels || ['email'];

        return `
            <div class="border border-gray-200 rounded-xl p-5 hover:shadow-md transition-all" data-search-id="${search.id}">
                <!-- Search Header -->
                <div class="flex items-start justify-between mb-4">
                    <div class="flex-1">
                        <h4 class="text-lg font-semibold text-gray-900 mb-1">${search.name || 'Сохранённый поиск'}</h4>
                        <p class="text-sm text-gray-600">${filters}</p>
                    </div>
                    ${alertsCount > 0 ? `
                        <span class="bg-purple-100 text-purple-800 text-xs font-medium px-3 py-1 rounded-full">
                            ${alertsCount} ${this.getDeclension(alertsCount, ['уведомление', 'уведомления', 'уведомлений'])}
                        </span>
                    ` : ''}
                </div>

                <!-- Notification Toggle -->
                <div class="flex items-center justify-between py-3 border-t border-gray-100">
                    <div class="flex items-center space-x-2">
                        <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
                        </svg>
                        <span class="text-sm font-medium text-gray-700">Уведомления</span>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" class="sr-only peer alert-toggle" data-search-id="${search.id}" ${isAlertEnabled ? 'checked' : ''}>
                        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#0088CC]"></div>
                    </label>
                </div>

                <!-- Notification Settings (shown when enabled) -->
                <div class="notification-settings ${isAlertEnabled ? '' : 'hidden'}" data-search-id="${search.id}">
                    <!-- Frequency Selector -->
                    <div class="py-3 border-t border-gray-100">
                        <label class="text-sm font-medium text-gray-700 block mb-2">Частота уведомлений</label>
                        <select class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#0088CC] focus:border-transparent frequency-select" data-search-id="${search.id}">
                            <option value="instant" ${frequency === 'instant' ? 'selected' : ''}>⚡ Мгновенно</option>
                            <option value="daily" ${frequency === 'daily' ? 'selected' : ''}>📅 Раз в день</option>
                            <option value="weekly" ${frequency === 'weekly' ? 'selected' : ''}>📆 Раз в неделю</option>
                        </select>
                    </div>

                    <!-- Channel Checkboxes -->
                    <div class="py-3 border-t border-gray-100">
                        <label class="text-sm font-medium text-gray-700 block mb-3">Способы уведомления</label>
                        <div class="space-y-2">
                            <label class="flex items-center space-x-3 cursor-pointer">
                                <input type="checkbox" class="w-4 h-4 text-[#0088CC] border-gray-300 rounded focus:ring-[#0088CC] channel-checkbox" data-search-id="${search.id}" data-channel="email" ${channels.includes('email') ? 'checked' : ''}>
                                <span class="text-sm text-gray-700">✉️ Email</span>
                            </label>
                            <label class="flex items-center space-x-3 cursor-pointer">
                                <input type="checkbox" class="w-4 h-4 text-[#0088CC] border-gray-300 rounded focus:ring-[#0088CC] channel-checkbox" data-search-id="${search.id}" data-channel="telegram" ${channels.includes('telegram') ? 'checked' : ''}>
                                <span class="text-sm text-gray-700">📱 Telegram</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center space-x-2 pt-4 border-t border-gray-100 mt-4">
                    <button class="flex-1 bg-[#0088CC] text-white px-4 py-2 rounded-lg hover:bg-[#006699] transition-colors text-sm font-medium apply-search-btn" data-search-id="${search.id}">
                        Применить поиск
                    </button>
                    <button class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium delete-search-btn" data-search-id="${search.id}">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Parse search filters into human-readable string
     */
    parseFilters(search) {
        const filters = [];
        const data = search.additional_filters || {};

        if (data.rooms) filters.push(`${data.rooms}-комн.`);
        if (data.priceFrom || data.priceTo) {
            const from = data.priceFrom ? `от ${(data.priceFrom / 1000000).toFixed(1)} млн` : '';
            const to = data.priceTo ? `до ${(data.priceTo / 1000000).toFixed(1)} млн` : '';
            filters.push([from, to].filter(Boolean).join(' '));
        }
        if (data.district) filters.push(data.district);
        if (data.complex_name) filters.push(`ЖК "${data.complex_name}"`);

        return filters.length > 0 ? filters.join(' • ') : 'Все параметры';
    }

    /**
     * Bind events for search card controls
     */
    bindSearchCardEvents() {
        // Toggle switches
        document.querySelectorAll('.alert-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const searchId = e.target.dataset.searchId;
                const enabled = e.target.checked;
                
                // Show/hide notification settings
                const settingsDiv = document.querySelector(`.notification-settings[data-search-id="${searchId}"]`);
                if (settingsDiv) {
                    if (enabled) {
                        settingsDiv.classList.remove('hidden');
                    } else {
                        settingsDiv.classList.add('hidden');
                    }
                }
                
                this.updateAlertSettings(searchId, { alert_enabled: enabled });
            });
        });

        // Frequency selectors
        document.querySelectorAll('.frequency-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const searchId = e.target.dataset.searchId;
                const frequency = e.target.value;
                this.updateAlertSettings(searchId, { alert_frequency: frequency });
            });
        });

        // Channel checkboxes
        document.querySelectorAll('.channel-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const searchId = e.target.dataset.searchId;
                const channel = e.target.dataset.channel;
                
                // Collect all checked channels for this search
                const checkboxes = document.querySelectorAll(`.channel-checkbox[data-search-id="${searchId}"]`);
                const channels = Array.from(checkboxes)
                    .filter(cb => cb.checked)
                    .map(cb => cb.dataset.channel);
                
                this.updateAlertSettings(searchId, { alert_channels: channels });
            });
        });

        // Apply search buttons
        document.querySelectorAll('.apply-search-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const searchId = e.currentTarget.dataset.searchId;
                this.applySearch(searchId);
            });
        });

        // Delete search buttons
        document.querySelectorAll('.delete-search-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const searchId = e.currentTarget.dataset.searchId;
                this.deleteSavedSearch(searchId);
            });
        });
    }

    /**
     * Update alert settings for a specific search
     */
    async updateAlertSettings(searchId, settings) {
        try {
            console.log(`Updating alert settings for search ${searchId}:`, settings);

            const response = await fetch('/api/user/alert-settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ search_id: parseInt(searchId), ...settings })
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Alert settings updated successfully');
                this.showSuccess('Настройки обновлены');
                
                // Update local data
                const search = this.searches.find(s => s.id === parseInt(searchId));
                if (search) {
                    Object.assign(search, settings);
                    
                    // Update active alerts counter
                    const activeCount = this.searches.filter(s => s.alert_enabled).length;
                    const activeAlertsCount = document.getElementById('active-alerts-count');
                    if (activeAlertsCount) {
                        activeAlertsCount.textContent = activeCount;
                    }
                }
            } else {
                console.error('Failed to update settings:', data.error);
                this.showError('Не удалось обновить настройки');
            }
        } catch (error) {
            console.error('Error updating alert settings:', error);
            this.showError('Ошибка обновления настроек');
        }
    }

    /**
     * Delete a saved search
     */
    async deleteSavedSearch(searchId) {
        if (!confirm('Удалить этот поиск и все связанные уведомления?')) {
            return;
        }

        try {
            console.log(`Deleting search ${searchId}...`);

            const response = await fetch(`/api/user/saved-search/${searchId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                console.log('✅ Search deleted successfully');
                this.showSuccess('Поиск удалён');
                
                // Remove from local array
                this.searches = this.searches.filter(s => s.id !== parseInt(searchId));
                
                // Re-render
                this.renderSavedSearches();
            } else {
                console.error('Failed to delete search:', data.error);
                this.showError('Не удалось удалить поиск');
            }
        } catch (error) {
            console.error('Error deleting search:', error);
            this.showError('Ошибка удаления поиска');
        }
    }

    /**
     * Apply a saved search (redirect to properties with filters)
     */
    applySearch(searchId) {
        const search = this.searches.find(s => s.id === parseInt(searchId));
        if (!search) {
            console.error('Search not found:', searchId);
            return;
        }

        const filters = search.additional_filters || {};
        const params = new URLSearchParams();

        // Build query parameters from filters
        if (filters.complex_name) params.append('complex', filters.complex_name);
        if (filters.rooms) params.append('rooms', filters.rooms);
        if (filters.priceFrom) params.append('price_min', filters.priceFrom);
        if (filters.priceTo) params.append('price_max', filters.priceTo);
        if (filters.areaFrom) params.append('area_min', filters.areaFrom);
        if (filters.areaTo) params.append('area_max', filters.areaTo);
        if (filters.district) params.append('district', filters.district);

        const queryString = params.toString();
        const url = queryString ? `/properties?${queryString}` : '/properties';
        
        console.log('Applying search, redirecting to:', url);
        window.location.href = url;
    }

    /**
     * Load alert history from API
     */
    async loadAlertHistory() {
        try {
            console.log('Loading alert history...');
            
            const response = await fetch('/api/user/alert-history?limit=20');
            const data = await response.json();

            if (data.success) {
                this.alertHistory = data.alerts || [];
                console.log(`Loaded ${this.alertHistory.length} alerts`);
                this.renderAlertHistory();
            } else {
                console.error('Failed to load alert history:', data.error);
                this.showError('Не удалось загрузить историю уведомлений');
            }
        } catch (error) {
            console.error('Error loading alert history:', error);
            this.showError('Ошибка загрузки истории');
        }
    }

    /**
     * Render alert history list
     */
    renderAlertHistory() {
        const listElement = document.getElementById('alert-history-list');
        const noHistoryMsg = document.getElementById('no-history-message');
        
        if (!listElement) return;

        if (this.alertHistory.length === 0) {
            listElement.innerHTML = '';
            if (noHistoryMsg) {
                noHistoryMsg.classList.remove('hidden');
            }
            return;
        }

        if (noHistoryMsg) {
            noHistoryMsg.classList.add('hidden');
        }

        listElement.innerHTML = this.alertHistory.map(alert => `
            <div class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer" onclick="window.location.href='/object/${alert.property_id}'">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <h5 class="font-medium text-gray-900 text-sm mb-1">${alert.property_name || 'Новый объект'}</h5>
                        <p class="text-xs text-gray-600 mb-2">${this.formatPrice(alert.property_price)}</p>
                        <div class="flex items-center space-x-3 text-xs text-gray-500">
                            <span>📅 ${this.formatDate(alert.sent_at)}</span>
                            ${alert.delivery_status === 'sent' ? 
                                '<span class="text-green-600">✓ Отправлено</span>' : 
                                '<span class="text-yellow-600">⏳ В очереди</span>'
                            }
                        </div>
                    </div>
                    <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                    </svg>
                </div>
            </div>
        `).join('');
    }

    /**
     * Helper: Format price
     */
    formatPrice(price) {
        if (!price) return 'Цена не указана';
        return `${(price / 1000000).toFixed(2)} млн ₽`;
    }

    /**
     * Helper: Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'Недавно';
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Helper: Get word declension
     */
    getDeclension(number, forms) {
        const n = Math.abs(number) % 100;
        const n1 = n % 10;
        
        if (n > 10 && n < 20) return forms[2];
        if (n1 > 1 && n1 < 5) return forms[1];
        if (n1 === 1) return forms[0];
        
        return forms[2];
    }

    /**
     * Helper: Get CSRF token
     */
    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    /**
     * Helper: Show success message
     */
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    /**
     * Helper: Show error message
     */
    showError(message) {
        this.showNotification(message, 'error');
    }

    /**
     * Helper: Show notification
     */
    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500'
        };

        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => notification.classList.remove('translate-x-full'), 100);
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

/**
 * Toggle alert history accordion
 */
window.toggleAlertHistory = function() {
    const content = document.getElementById('alert-history-content');
    const chevron = document.getElementById('history-chevron');
    
    if (content && chevron) {
        const isHidden = content.classList.contains('hidden');
        
        if (isHidden) {
            content.classList.remove('hidden');
            chevron.style.transform = 'rotate(180deg)';
            
            // Load history when opening for the first time
            if (window.alertSettingsManager && window.alertSettingsManager.alertHistory.length === 0) {
                window.alertSettingsManager.loadAlertHistory();
            }
        } else {
            content.classList.add('hidden');
            chevron.style.transform = 'rotate(0deg)';
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.alertSettingsManager = new AlertSettingsManager();
    });
} else {
    window.alertSettingsManager = new AlertSettingsManager();
}

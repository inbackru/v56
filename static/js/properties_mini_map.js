// Properties Mini Map (Yandex Maps - Avito-style)
console.log('🗺️ properties_mini_map.js загружен');
let miniPropertiesMapInstance = null;

function clusterCoordinates(coordinates, radius) {
    const clusters = [];
    const used = new Set();
    
    coordinates.forEach((coord, i) => {
        if (used.has(i)) return;
        
        const cluster = {
            lat: coord.lat,
            lng: coord.lng,
            count: 1
        };
        
        coordinates.forEach((other, j) => {
            if (i !== j && !used.has(j)) {
                const distance = Math.sqrt(
                    Math.pow(coord.lat - other.lat, 2) + 
                    Math.pow(coord.lng - other.lng, 2)
                );
                
                if (distance < radius) {
                    cluster.count++;
                    used.add(j);
                }
            }
        });
        
        used.add(i);
        clusters.push(cluster);
    });
    
    return clusters;
}

function initMiniPropertiesMap() {
    const mapElement = document.getElementById('miniPropertiesMap');
    if (!mapElement || miniPropertiesMapInstance) return;
    
    if (typeof ymaps === 'undefined') {
        console.warn('ymaps not loaded yet, retrying in 500ms');
        setTimeout(initMiniPropertiesMap, 500);
        return;
    }
    
    ymaps.ready(function() {
        try {
            // Начальный центр (Краснодарский край) - будет пересчитан после загрузки объектов
            miniPropertiesMapInstance = new ymaps.Map('miniPropertiesMap', {
                center: [45.0355, 38.9753],
                zoom: 11,
                controls: []
            }, {
                suppressMapOpenBlock: true,
                yandexMapDisablePoiInteractivity: true
            });
            
            miniPropertiesMapInstance.behaviors.disable(['drag', 'scrollZoom', 'dblClickZoom', 'multiTouch']);
            
            fetch('/api/mini-map/properties')
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.coordinates && data.coordinates.length > 0) {
                        console.log(`✅ Loaded ${data.count} property coordinates`);
                        
                        const clusters = clusterCoordinates(data.coordinates, 0.01);
                        
                        // Создаем метки на карте
                        clusters.forEach(cluster => {
                            const placemark = new ymaps.Placemark([cluster.lat, cluster.lng], {
                                iconContent: cluster.count
                            }, {
                                preset: 'islands#blueCircleIcon',
                                iconColor: '#0088CC'
                            });
                            
                            placemark.events.add('click', function() {
                                window.location.href = '/map';
                            });
                            
                            miniPropertiesMapInstance.geoObjects.add(placemark);
                        });
                        
                        console.log(`✅ Created ${clusters.length} clusters on Yandex mini map`);
                        
                        // 🎯 АВТОМАТИЧЕСКОЕ ЦЕНТРИРОВАНИЕ ПО ОБЪЕКТАМ
                        // Вычисляем границы по всем координатам
                        const bounds = data.coordinates.reduce((acc, coord) => {
                            if (!acc.minLat || coord.lat < acc.minLat) acc.minLat = coord.lat;
                            if (!acc.maxLat || coord.lat > acc.maxLat) acc.maxLat = coord.lat;
                            if (!acc.minLng || coord.lng < acc.minLng) acc.minLng = coord.lng;
                            if (!acc.maxLng || coord.lng > acc.maxLng) acc.maxLng = coord.lng;
                            return acc;
                        }, {});
                        
                        // Устанавливаем карту по границам объектов с небольшим отступом
                        miniPropertiesMapInstance.setBounds([
                            [bounds.minLat, bounds.minLng],
                            [bounds.maxLat, bounds.maxLng]
                        ], {
                            checkZoomRange: true,
                            zoomMargin: 20  // Отступ от краев в пикселях
                        });
                        
                        console.log(`🎯 Auto-centered map: [${bounds.minLat.toFixed(4)}, ${bounds.minLng.toFixed(4)}] - [${bounds.maxLat.toFixed(4)}, ${bounds.maxLng.toFixed(4)}]`);
                    }
                })
                .catch(error => {
                    console.error('❌ Error loading property coordinates:', error);
                });
            
            console.log('✅ Yandex mini map initialized for properties');
        } catch (error) {
            console.error('❌ Error initializing Yandex mini map:', error);
        }
    });
}

// Initialize mini map on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🗺️ Properties mini map - DOMContentLoaded');
        setTimeout(initMiniPropertiesMap, 500);
    });
} else {
    console.log('🗺️ Properties mini map - DOM already loaded');
    setTimeout(initMiniPropertiesMap, 500);
}

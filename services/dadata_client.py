"""
DaData.ru API Client for Professional Address Normalization
Provides hybrid search combining DaData suggestions with database results
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from dadata import Dadata

logger = logging.getLogger(__name__)


class DaDataCache:
    """Simple in-memory cache with configurable TTL per key type"""
    
    def __init__(self):
        self.cache = {}
        # Default TTLs in seconds
        self.ttls = {
            'city': 12 * 3600,      # 12 hours for cities/regions
            'district': 12 * 3600,  # 12 hours for districts
            'street': 1 * 3600,     # 1 hour for streets
            'default': 1 * 3600     # 1 hour default
        }
    
    def _get_ttl(self, key_type: str) -> int:
        """Get TTL for specific key type"""
        return self.ttls.get(key_type, self.ttls['default'])
    
    def get(self, key: str, key_type: str = 'default') -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp, cached_type = self.cache[key]
            ttl = self._get_ttl(cached_type)
            if time.time() - timestamp < ttl:
                logger.debug(f"Cache HIT for '{key}' (type: {cached_type})")
                return value
            else:
                logger.debug(f"Cache EXPIRED for '{key}' (type: {cached_type})")
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, key_type: str = 'default'):
        """Set value in cache with current timestamp and type"""
        self.cache[key] = (value, time.time(), key_type)
        logger.debug(f"Cache SET for '{key}' (type: {key_type}, TTL: {self._get_ttl(key_type)}s)")
    
    def clear(self):
        """Clear all cached values"""
        self.cache.clear()
        logger.info("DaData cache cleared")


class DaDataClient:
    """
    DaData API Client with caching and error handling
    Provides address suggestions for cities, streets, districts
    """
    
    def __init__(self):
        self.api_key = os.environ.get('DADATA_API_KEY')
        self.secret_key = os.environ.get('DADATA_SECRET_KEY')
        
        if not self.api_key:
            logger.warning("DADATA_API_KEY not found - DaData suggestions disabled")
            self.client = None
        else:
            try:
                self.client = Dadata(self.api_key, self.secret_key)
                logger.info("✅ DaData client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DaData client: {e}")
                self.client = None
        
        self.cache = DaDataCache()
        
        # Краснодарский край FIAS ID для фильтрации
        self.krasnodar_region_fias = "d00e1013-16bd-4c09-b3d5-3cb09fc54bd8"
    
    def is_available(self) -> bool:
        """Check if DaData client is available"""
        return self.client is not None
    
    def suggest_address(
        self, 
        query: str, 
        count: int = 5,
        locations: Optional[List[Dict]] = None,
        from_bound: Optional[Dict] = None,
        to_bound: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Get address suggestions from DaData API
        
        Args:
            query: Search query
            count: Number of suggestions to return (max 20)
            locations: Filter by location (e.g., Krasnodar region)
            from_bound: Lower bound for address level (e.g., {"value": "city"})
            to_bound: Upper bound for address level (e.g., {"value": "settlement"})
        
        Returns:
            List of suggestions with structured address data
        """
        if not self.is_available():
            logger.debug("DaData client not available")
            return []
        
        if not query or len(query) < 2:
            return []
        
        # Normalize query for cache key
        cache_key = f"address:{query.lower()}:{count}"
        
        # Check cache
        cached = self.cache.get(cache_key, 'street')
        if cached is not None:
            return cached
        
        try:
            # Default to Krasnodar region filter
            if locations is None:
                locations = [{"region_fias_id": self.krasnodar_region_fias}]
            
            # Safety check (already checked in is_available, but for type checker)
            if self.client is None:
                return []
            
            # Call DaData API
            logger.debug(f"🌐 DaData API call for query: '{query}'")
            result = self.client.suggest(
                name="address",
                query=query,
                count=count,
                locations=locations,
                from_bound=from_bound,
                to_bound=to_bound
            )
            
            # Parse and normalize results
            suggestions = []
            for item in result:
                try:
                    data = item.get('data', {})
                    value = item.get('value', '')
                    
                    # Determine address type
                    addr_type = self._determine_type(data)
                    
                    # Build suggestion object
                    suggestion = {
                        'text': value,
                        'type': addr_type,
                        'source': 'dadata',
                        'data': {
                            'city': data.get('city'),
                            'city_with_type': data.get('city_with_type'),
                            'settlement': data.get('settlement'),
                            'settlement_with_type': data.get('settlement_with_type'),
                            'street': data.get('street'),
                            'street_with_type': data.get('street_with_type'),
                            'area': data.get('area'),
                            'area_with_type': data.get('area_with_type'),
                            'region': data.get('region'),
                            'region_with_type': data.get('region_with_type'),
                            'geo_lat': data.get('geo_lat'),
                            'geo_lon': data.get('geo_lon'),
                            'postal_code': data.get('postal_code'),
                            'fias_id': data.get('fias_id'),
                            'kladr_id': data.get('kladr_id'),
                            # Детальные адресные компоненты
                            'house': data.get('house'),
                            'house_type': data.get('house_type'),
                            'block': data.get('block'),
                            'block_type': data.get('block_type'),
                            'flat': data.get('flat'),
                            'flat_type': data.get('flat_type')
                        }
                    }
                    
                    suggestions.append(suggestion)
                except Exception as e:
                    logger.warning(f"Failed to parse DaData suggestion: {e}")
                    continue
            
            # Cache results (determine type from first suggestion)
            cache_type = suggestions[0]['type'] if suggestions else 'default'
            self.cache.set(cache_key, suggestions, cache_type)
            
            logger.info(f"✅ DaData returned {len(suggestions)} suggestions for '{query}'")
            return suggestions
            
        except Exception as e:
            logger.error(f"DaData API error for query '{query}': {e}")
            return []
    
    def _determine_type(self, data: Dict) -> str:
        """
        Determine address type from DaData response
        Priority: street > district > settlement > city > region
        """
        if data.get('street'):
            return 'street'
        elif data.get('area'):  # район
            return 'district'
        elif data.get('settlement'):  # населенный пункт
            return 'settlement'
        elif data.get('city'):
            return 'city'
        elif data.get('region'):
            return 'region'
        else:
            return 'address'
    
    def suggest_cities(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get city suggestions only"""
        return self.suggest_address(
            query=query,
            count=count,
            from_bound={"value": "city"},
            to_bound={"value": "settlement"}
        )
    
    def suggest_streets(self, query: str, city: Optional[str] = None, count: int = 5) -> List[Dict[str, Any]]:
        """Get street suggestions, optionally filtered by city"""
        locations = None
        if city:
            locations = [{"city": city}]
        
        return self.suggest_address(
            query=query,
            count=count,
            locations=locations,
            from_bound={"value": "street"},
            to_bound={"value": "street"}
        )
    
    def suggest_districts(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Get district/area suggestions"""
        return self.suggest_address(
            query=query,
            count=count,
            from_bound={"value": "area"},
            to_bound={"value": "area"}
        )
    
    def enrich_property_address(self, address_text: str) -> Optional[Dict]:
        """
        Обогащение адреса недвижимости через DaData API
        Возвращает детализированную разбивку адреса для заполнения полей Property
        
        Args:
            address_text: Полный адрес для обогащения
            
        Returns:
            Dict с детализированными компонентами адреса или None
        """
        try:
            # Используем suggest_address для получения полных данных
            suggestions = self.suggest_address(query=address_text, count=1)
            
            if not suggestions:
                logger.warning(f"DaData не нашел адрес: {address_text}")
                return None
            
            # Берём первое (наиболее релевантное) предложение
            suggestion = suggestions[0]
            data = suggestion.get('data', {})
            
            # Извлекаем детализированные компоненты
            result = {
                'parsed_city': data.get('city') or '',
                'parsed_area': data.get('area') or '',                # Административный район
                'parsed_settlement': data.get('settlement') or '',     # Микрорайон/населенный пункт
                'parsed_street': data.get('street') or '',
                'parsed_house': data.get('house') or '',              # Номер дома
                'parsed_block': data.get('block') or '',              # Корпус/блок
                'parsed_district': '',  # Legacy поле - заполним комбинацией
                'latitude': data.get('geo_lat'),
                'longitude': data.get('geo_lon'),
                'full_address': suggestion.get('text', '')
            }
            
            # Заполняем legacy поле parsed_district комбинацией area + settlement
            district_parts = []
            if result['parsed_area']:
                district_parts.append(result['parsed_area'])
            if result['parsed_settlement']:
                district_parts.append(result['parsed_settlement'])
            result['parsed_district'] = ', '.join(district_parts) if district_parts else ''
            
            logger.info(f"✅ DaData обогатил адрес: {address_text[:50]} → {result['parsed_city']}, {result['parsed_street']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка обогащения через DaData: {e}")
            return None
    
    @staticmethod
    def normalize_address_for_search(address_text: str) -> List[str]:
        """
        Extract searchable tokens from DaData address string.
        Removes prefixes and creates search variants that match database format.
        
        Example:
            Input: "Краснодарский край, г Сочи, р-н Адлерский, ул Искры"
            Output: ["Сочи", "Адлерский", "Искры", "ул Искры"]
        
        This helps match DaData format with database addresses like:
        "Россия, Краснодарский край, Сочи, Кудепста м-н, Искры, 88 лит7"
        """
        if not address_text:
            return []
        
        tokens = []
        parts = [p.strip() for p in address_text.split(',')]
        
        for part in parts:
            # Skip region and country
            if any(skip in part for skip in ['Россия', 'Краснодарский край']):
                continue
            
            # Extract clean names without prefixes
            clean = part
            
            # Remove common prefixes
            prefixes = ['г ', 'р-н ', 'ул ', 'д ', 'мкр ', 'пер ', 'пр-кт ', 'наб ']
            for prefix in prefixes:
                if clean.startswith(prefix):
                    clean_without_prefix = clean[len(prefix):]
                    tokens.append(clean_without_prefix)  # Add version without prefix
                    # For streets, also keep "ул Название" format
                    if prefix == 'ул ':
                        tokens.append(clean)  # Keep "ул Искры" format
                    break
            else:
                # No prefix found, add as is
                if clean and clean not in ['Краснодарский край', 'Россия']:
                    tokens.append(clean)
        
        return tokens


# Global instance
_dadata_client = None


def get_dadata_client() -> DaDataClient:
    """Get or create global DaData client instance"""
    global _dadata_client
    if _dadata_client is None:
        _dadata_client = DaDataClient()
    return _dadata_client

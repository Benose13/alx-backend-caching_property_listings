from django.core.cache import cache
from django_redis import get_redis_connection
import logging
from .models import Property

logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Get all properties from cache if available, otherwise fetch from database
    and cache for 1 hour (3600 seconds)
    """
    # Try to get properties from cache
    properties = cache.get('all_properties')
    
    if properties is None:
        # If not in cache, fetch from database
        properties = Property.objects.all()
        
        # Store in cache for 1 hour (3600 seconds)
        cache.set('all_properties', properties, 3600)
        logger.info("Properties fetched from database and cached")
    else:
        logger.info("Properties fetched from cache")
    
    return properties

def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics
    
    Returns:
        dict: Dictionary containing cache hits, misses, and hit ratio
    """
    try:
        # Connect to Redis via django_redis
        redis_conn = get_redis_connection("default")
        
        # Get Redis INFO command output
        info = redis_conn.info()
        
        # Extract keyspace hits and misses from stats section
        hits = info.get('stats', {}).get('keyspace_hits', 0)
        misses = info.get('stats', {}).get('keyspace_misses', 0)
        
        # Calculate hit ratio using the exact required syntax
        total_requests = hits + misses
        hit_ratio = hits / total_requests if total_requests > 0 else 0
        
        # Create metrics dictionary
        metrics = {
            'hits': hits,
            'misses': misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
            'hit_ratio_percentage': round(hit_ratio * 100, 2)
        }
        
        # Log the metrics
        logger.info(
            f"Redis Cache Metrics - "
            f"Hits: {hits}, Misses: {misses}, "
            f"Hit Ratio: {metrics['hit_ratio_percentage']}%"
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {str(e)}")
        # Return default metrics in case of error
        return {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'hit_ratio': 0,
            'hit_ratio_percentage': 0,
            'error': str(e)
        }
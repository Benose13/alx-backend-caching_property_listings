from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property
from .utils import get_all_properties

# Cache the view for 15 minutes (60 * 15 seconds)
@cache_page(60 * 15)
def property_list(request):
    """Return all properties as JSON, cached for 15 minutes."""
    properties = Property.objects.all().values(
        "id", "title", "description", "price", "location", "created_at"
    )
    data = {
        "data": list(properties)
    }
    return JsonResponse(data)
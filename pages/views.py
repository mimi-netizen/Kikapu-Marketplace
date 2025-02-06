from django.shortcuts import render, get_object_or_404
from ads.models import Ads, County, City, Category, AdsImages, AdsTopBanner, AdsRightBanner, AdsBottomBanner
from django.http import JsonResponse
from django.db.models import Q  # Import Q for complex queries

def home(request):
    # Fetch recent ads (limit to 10)
    recent_ads = Ads.objects.order_by('-date_created')[:10]
    
    # Fetch featured ads (limit to 10)
    featured_ads = Ads.objects.filter(is_featured=True)[:10]
    
    # Browse Ads by Category
    category_listing = Category.objects.all()

    # Browse Ads by County
    county_listing = County.objects.all()

    # Fetch Ads Banner
    sidebar_banners = AdsRightBanner.objects.all()
    top_banner = AdsTopBanner.objects.all()
    bottom_banner = AdsBottomBanner.objects.all()

    # Fetch search location & category 
    # Use county_name instead of name
    county_search = County.objects.values_list('county_name', flat=True).distinct().order_by("county_name")
    category_search = Category.objects.values_list('category', flat=True).distinct().order_by("category")
    
    # Contexts
    context = {
        'recent_ads' : recent_ads,
        'featured_ads' : featured_ads,
        'county_search' : county_search,
        'category_search' : category_search,
        'category_listing' : category_listing,
        'county_listing' : county_listing,
        'sidebar_banners' : sidebar_banners,
        'top_banner' : top_banner,
        'bottom_banner' : bottom_banner,
    }

    return render(request, 'pages/index.html', context)

# Search Ads View
def ads_search(request):
    query = request.GET.get('query', '').strip()  # Get the search query from the request
    ads = Ads.objects.all()  # Default to all ads if no query is provided

    if query:
        # Use Q objects to filter ads by title or description
        ads = Ads.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # Context for the search results
    context = {
        'ads': ads,
        'query': query,
    }

    return render(request, 'ads/search_results.html', context)

# Faq view
def faq(request):
    return render(request, 'pages/faq.html')

# Terms of service view
def terms_of_service(request):
    return render(request, 'pages/terms-of-service.html')

# Contact view
def contact(request):
    return render(request, 'pages/contact.html')
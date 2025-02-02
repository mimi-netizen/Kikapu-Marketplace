from django.shortcuts import render, get_object_or_404
from ads.models import Ads, County, City, Category, AdsImages, AdsTopBanner, AdsRightBanner, AdsBottomBanner
from django.http import JsonResponse

def home(request):
    # Fetch recent ads 
    recent_ads = Ads.objects.order_by('-date_created')[:3]
    
    # Fetch featured Ads 
    featured_ads = Ads.objects.filter(is_featured=True)
    
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


# Faq view
def faq(request):
    return render(request, 'pages/faq.html')

# Terms of service view
def terms_of_service(request):
    return render(request, 'pages/terms-of-service.html')

# Contact view
def contact(request):
    return render(request, 'pages/contact.html')
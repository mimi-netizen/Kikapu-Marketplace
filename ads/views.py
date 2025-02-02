from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from ads.forms import PostAdsForm
from ads.models import Ads, Author, AdsImages, County, City, Category, AdsTopBanner, AdsRightBanner, AdsBottomBanner
from datetime import datetime, timedelta
from .models import Message
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.text import slugify
import unicodedata
import logging
from django.db import transaction

def ads_listing(request):
    ads = Ads.objects.all().order_by('-date_created')
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads': ads,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-listing.html', context)



# Configure logging
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def post_ads(request):
    if request.method == 'POST':
        form = PostAdsForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Start a database transaction to ensure atomic operations
                with transaction.atomic():
                    # Save the ad with the current user's author
                    ads = form.save(commit=False)
                    ads.author = request.user.author

                    # Process location and category
                    county_name = request.POST.get('county', '').strip()
                    city_name = request.POST.get('city', '').strip()
                    category_name = request.POST.get('category', '').strip()

                    # Normalize and create slugs
                    def normalize_slug(name):
                        return slugify(
                            unicodedata.normalize('NFKD', name)
                            .encode('ascii', 'ignore')
                            .decode('ascii')
                        )

                    # Get or create related objects with proper error checking
                    try:
                        county_slug = normalize_slug(county_name)
                        county, _ = County.objects.get_or_create(
                            slug=county_slug, 
                            defaults={'county_name': county_name}
                        )

                        city_slug = normalize_slug(city_name)
                        city, _ = City.objects.get_or_create(
                            slug=city_slug, 
                            county=county, 
                            defaults={'city_name': city_name}
                        )

                        category_slug = normalize_slug(category_name)
                        category, _ = Category.objects.get_or_create(
                            slug=category_slug, 
                            defaults={'main_category': category_name}
                        )

                        # Assign related objects to the ad
                        ads.county = county
                        ads.city = city
                        ads.category = category
                        
                        # Save the ad
                        ads.save()

                    except Exception as location_error:
                        logger.error(f"Error processing location/category: {location_error}")
                        messages.error(request, 'Error processing location or category.')
                        return render(request, 'ads/post-ads.html', {'form': form})

                    # Process ad images
                    try:
                        image_count = int(request.POST.get('length', 0))
                        for file_num in range(image_count):
                            image_file = request.FILES.get(f'images{file_num}')
                            if image_file:
                                AdsImages.objects.create(
                                    ad=ads,
                                    image=image_file
                                )
                    except Exception as image_error:
                        logger.error(f"Error processing images: {image_error}")
                        messages.warning(request, 'Ad saved, but some images could not be uploaded.')

                    # Send notification email
                    try:
                        send_mail(
                            subject="New Ads Submitted",
                            message=f"Dear Admin, you received a new ads request from {request.user.email}",
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[settings.EMAIL_HOST_USER],
                            fail_silently=False,
                        )
                    except Exception as email_error:
                        logger.error(f"Email notification failed: {email_error}")
                        # Non-critical, so we don't stop the process

                # Success message and redirect
                messages.success(request, 'Your ad has been posted successfully!')
                return redirect('ads_listing')

            except Exception as e:
                # Catch any unexpected errors
                logger.error(f"Unexpected error in post_ads: {e}", exc_info=True)
                messages.error(request, f'An unexpected error occurred: {str(e)}')
                return render(request, 'ads/post-ads.html', {'form': form})
        else:
            # Form validation failed
            logger.warning(f"Form validation failed: {form.errors}")
            messages.error(request, 'Please correct the errors in the form.')
            return render(request, 'ads/post-ads.html', {'form': form})
    
    # GET request handling (unchanged)
    else:
        form = PostAdsForm()
        categories = Category.objects.all()
        counties = County.objects.all()
        cities = City.objects.all()
        active_time = datetime.now() - timedelta(days=30)
        top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
        right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
        bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

        context = {
            'form': form,
            'categories': categories,
            'counties': counties,
            'cities': cities,
            'top_banners': top_banners,
            'right_banners': right_banners,
            'bottom_banners': bottom_banners,
        }

        return render(request, 'ads/post-ads.html', context)
    

# message views
@login_required
def send_message(request, ad_id):
    if request.method == 'POST':
        content = request.POST.get('message')
        ad = Ads.objects.get(id=ad_id)
        
        Message.objects.create(
            sender=request.user,
            receiver=ad.author.user,
            ad=ad,
            content=content
        )
        return redirect('ads-detail', ad_id)

@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'ads/inbox.html', context)

def ads_search(request):
    county_slug = request.GET.get('county_slug')
    category_slug = request.GET.get('category_slug')

    county = None
    category = None

    if county_slug:
        county = get_object_or_404(County, slug=county_slug)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)

    if county and category:
        ads_search_result = Ads.objects.filter(county=county, category=category)
    elif county:
        ads_search_result = Ads.objects.filter(county=county)
    elif category:
        ads_search_result = Ads.objects.filter(category=category)
    else:
        ads_search_result = Ads.objects.all()
    
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads_search_result': ads_search_result,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-search.html', context)

def ads_detail(request, pk):
    ads_detail = Ads.objects.get(pk=pk)
    ads_images = AdsImages.objects.filter(ad=ads_detail)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads_detail': ads_detail,
        'ads_images': ads_images,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-detail.html', context)

def ads_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    ads = Ads.objects.filter(category=category)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads': ads,
        'category': category,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-by-category.html', context)

def ads_by_county(request, county_slug):
    county = get_object_or_404(County, slug=county_slug)
    ads = Ads.objects.filter(county=county)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads': ads,
        'county': county,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-by-county.html', context)

def ads_by_city(request, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    ads = Ads.objects.filter(city=city)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads': ads,
        'city': city,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/ads-by-city.html', context)

def get_cities(request, county_id):
    cities = City.objects.filter(county_id=county_id).values('id', 'city_name')
    return JsonResponse({'cities': list(cities)})

def ads_author_archive(request, pk):
    author = get_object_or_404(Author, pk=pk)
    ads_by_author = Ads.objects.filter(author=author)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'author' : author,
        'ads_by_author' : ads_by_author,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/author-archive.html', context)

@login_required(login_url='login')
def delete_ad(request, pk):
    try:
        ad = get_object_or_404(Ads, pk=pk)
        if request.method == 'POST':
            ad.delete()
            messages.success(request, 'The ad has been deleted successfully.')
            return redirect('ads_listing')
    except Exception as e:
        messages.error(request, 'An error occurred while deleting the ad. Please try again.')
        return redirect('delete_ad', pk=pk)

    return render(request, 'ads/ads-delete.html', {'ad': ad})
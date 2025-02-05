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
from .models import Conversation, Message
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.http import require_POST
import unicodedata
import logging
from django.db import transaction

def ads_listing(request):
    ads_listing = Ads.objects.all().order_by('-date_created')
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)
    category_listing = Category.objects.all()
    county_listing = County.objects.all()

    context = {
        'ads_listing': ads_listing,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
        'category_listing': category_listing,  
        'county_listing': county_listing,      
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
                            defaults={'category': category_name}
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
                return redirect('ads-listing')

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
    if request.method != 'POST':
        return redirect('ads-detail', ad_id)

    ad = get_object_or_404(Ads, id=ad_id)
    content = request.POST.get('message')
    receiver = ad.author.user

    conversation = Conversation.get_or_create_conversation(request.user, receiver, ad)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        receiver=receiver,
        ad=ad,
        content=content
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'sender_username': message.sender.username
            }
        })

    messages.success(request, 'Message sent successfully!')
    return redirect('ads-detail', ad_id)

@login_required
def inbox(request):
    conversations = Conversation.get_user_conversations(request.user)
    
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        latest_message = conv.latest_message
        
        conversation_data.append({
            'id': conv.id,
            'other_user': other_user,
            'ad': conv.ad,
            'latest_message': latest_message,
            'unread_count': conv.unread_messages,
        })

    unread_total = sum(conv.unread_messages for conv in conversations)

    return render(request, 'ads/inbox.html', {
        'conversations': conversation_data,
        'unread_messages_count': unread_total,
    })

@login_required
def conversation_detail(request, conversation_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        conversation = get_object_or_404(
            Conversation.objects.prefetch_related('messages'),
            id=conversation_id,
            participants=request.user
        )
        
        return JsonResponse({
            'id': conversation.id,
            'ad': {
                'id': conversation.ad.id,
                'title': conversation.ad.title,
            },
            'other_user': {
                'username': conversation.get_other_participant(request.user).username,
            },
            'messages': [{
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'is_sender': msg.sender == request.user,
            } for msg in conversation.messages.all().order_by('created_at')]
        })
    
    # Regular template response for non-AJAX requests
    return render(request, 'ads/conversation_detail.html', {...})

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )
    conversation.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, 'Conversation deleted successfully.')
    return redirect('inbox')



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

    # Verify image existence
    for image in ads_images:
        if image.image:
            try:
                image.image.file  # This will check if file exists
            except:
                image.image = None  # Clear invalid image reference

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
    ads_by_category = Ads.objects.filter(category=category) 
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads_by_category': ads_by_category,  
        'category': category,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/category-archive.html', context)

def ads_by_county(request, county_slug):
    county = get_object_or_404(County, slug=county_slug)
    ads_by_county = Ads.objects.filter(county=county)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads_by_county': ads_by_county,
        'county': county,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/county-archive.html', context)

def ads_by_city(request, city_slug):
    city = get_object_or_404(City, slug=city_slug)
    ads_by_city = Ads.objects.filter(city=city)
    active_time = datetime.now() - timedelta(days=30)
    top_banners = AdsTopBanner.objects.filter(created_at__gte=active_time)
    right_banners = AdsRightBanner.objects.filter(created_at__gte=active_time)
    bottom_banners = AdsBottomBanner.objects.filter(created_at__gte=active_time)

    context = {
        'ads_by_city': ads_by_city,
        'city': city,
        'top_banners': top_banners,
        'right_banners': right_banners,
        'bottom_banners': bottom_banners,
    }

    return render(request, 'ads/city-archive.html', context)

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
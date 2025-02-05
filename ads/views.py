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
from django.db.models import Max, Count, Q
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
        form = PostAdsForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the ad
                    ads = form.save()

                    # Handle multiple images
                    images = request.FILES.getlist('images')
                    for image in images:
                        AdsImages.objects.create(
                            ad=ads,
                            image=image
                        )

                    # Send notification email
                    try:
                        send_mail(
                            subject="New Ad Submitted",
                            message=f"New ad submitted by {request.user.email}",
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[settings.EMAIL_HOST_USER],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Email sending failed: {e}")

                    messages.success(request, 'Your ad has been posted successfully!')
                    return redirect('ads-listing')

            except Exception as e:
                logger.error(f"Error saving ad: {e}")
                messages.error(request, 'An error occurred while posting your ad.')
                return render(request, 'ads/post-ads.html', {'form': form})
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostAdsForm(user=request.user)

    context = {
        'form': form,
        'categories': Category.objects.all(),
        'counties': County.objects.all(),
        'cities': City.objects.all(),
        'top_banners': AdsTopBanner.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ),
        'right_banners': AdsRightBanner.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ),
        'bottom_banners': AdsBottomBanner.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=30)
        ),
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
        content=content,
        is_read=False  # Changed from read to is_read
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
    conversations = (
        Conversation.objects.filter(participants=request.user)
        .select_related('ad', 'ad__author')
        .prefetch_related('messages')
        .annotate(
            latest_message=Max('messages__created_at')
        )
        .order_by('-latest_message')
    )
    
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        latest_message = conv.messages.order_by('-created_at').first()
        
        conversation_data.append({
            'id': conv.id,
            'other_user': other_user,
            'ad': conv.ad,
            'latest_message': latest_message,
            'unread_count': conv.unread_count,  # Using the model field
        })

    unread_total = sum(conv['unread_count'] for conv in conversation_data)

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
        
        # Use the model method to mark messages as read and update unread count
        conversation.mark_messages_read(request.user)
        
        # Update the unread count
        conversation.update_unread_count(request.user)
        
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
            } for msg in conversation.messages.all().order_by('created_at')],
            'unread_count': conversation.unread_count  # Add this to update frontend counter
        })
    
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('messages'),
        id=conversation_id,
        participants=request.user
    )
    
    # Mark messages as read for non-AJAX requests too
    conversation.mark_messages_read(request.user)
    conversation.update_unread_count(request.user)
    
    return render(request, 'ads/conversation_detail.html', {
        'conversation': conversation,
        'other_user': conversation.get_other_participant(request.user),
    })

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
        return redirect('ads-delete', pk=pk)

    return render(request, 'ads/ads-delete.html', {'ad': ad})
from django.urls import path
from . import views

urlpatterns = [
    path('post-ads/', views.post_ads, name='post-ads'),
    path('ads-listing/', views.ads_listing, name='ads-listing'),
    path('ads/<int:pk>/', views.ads_detail, name='ads-detail'),
    path('ads/<int:pk>/delete/', views.delete_ad, name='ads-delete'),
    path('category/', views.Category, name='category'), 
    path('category/<slug:category_slug>/', views.ads_by_category, name='category-archive'),
    path('county/<slug:county_slug>/', views.ads_by_county, name='county-archive'),
    path('city/<slug:city_slug>/', views.ads_by_city, name='city-archive'),
    path('author/<int:pk>/', views.ads_author_archive, name='author-archive'),
    path('ads-search/', views.ads_search, name='ads-search'),
    path('get-cities/<int:county_id>/', views.get_cities, name='get_cities'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('send-message/<int:ad_id>/', views.send_message, name='send-message')
]
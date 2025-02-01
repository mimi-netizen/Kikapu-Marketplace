from django.urls import path
from . import views

urlpatterns = [
    path('post-ads/', views.post_ads, name='post-ads'),
    path('ads-listing/', views.ads_listing, name='ads-listing'),
    path('ads/<int:pk>/', views.ads_detail, name='ads-detail'),
    path('ads/<int:pk>/delete/', views.delete_ad, name='ads-delete'),
    path('category/<slug:category_slug>/', views.ads_by_category, name='category-archive'),
    path('county/<slug:county_slug>/', views.ads_by_county, name='county-archive'),
    path('city/<slug:city_slug>/', views.ads_by_city, name='city-archive'),
    path('author/<int:pk>/', views.ads_author_archive, name='author-archive'),
    path('ads-search/', views.ads_search, name='ads-search'),
]
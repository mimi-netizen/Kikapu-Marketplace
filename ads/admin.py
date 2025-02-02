from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Author, Ads, County, City, Category, 
    AdsImages, AdsTopBanner, AdsRightBanner, AdsBottomBanner
)

class AdsImagesInline(admin.StackedInline):
    model = AdsImages
    extra = 1  # Adds one empty upload slot by default
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;" />'.format(obj.image.url))
        return 'No image'

class AdsAdmin(admin.ModelAdmin):
    list_display = (
        'ad_id',
        'title', 
        'price', 
        'author', 
        'category', 
        'county', 
        'city', 
        'date_created', 
        'is_featured'
    )
    
    list_display_links = ('ad_id', 'title')
    list_editable = ['is_featured']
    search_fields = ('title', 'price', 'county__county_name', 'city__city_name', 'category')
    search_help_text = 'Search by title, price, county, city, or category'
    list_filter = ('price', 'date_created', 'county', 'city', 'is_featured', 'category')
    list_per_page = 20

    inlines = [AdsImagesInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category', 'county', 'city')

class AdsImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'image_preview', 'is_primary')
    search_help_text = 'Search by associated ad'
    search_fields = ('ad__title',)
    list_per_page = 20
    list_editable = ['is_primary']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;" />'.format(obj.image.url))
        return 'No image'

class CountyAdmin(admin.ModelAdmin):
    list_display = ('county_name', 'slug')
    prepopulated_fields = {'slug': ('county_name',)}
    search_fields = ('county_name', 'slug')
    search_help_text = 'Search by county name or slug'
    list_per_page = 20

class CityAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'county', 'slug')
    list_filter = ('county',)
    prepopulated_fields = {'slug': ('city_name',)}
    search_fields = ('city_name', 'slug', 'county__county_name')
    search_help_text = 'Search by city name, slug, or county'
    list_per_page = 20

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'slug')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('category',)}
    search_fields = ('category', 'slug')
    search_help_text = 'Search by category name or slug'
    list_per_page = 20

class BannerBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    search_help_text = 'Search banners by title'
    list_per_page = 20
    readonly_fields = ('created_at', 'updated_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="100" style="object-fit:cover;" />'.format(obj.image.url))
        return 'No image'
    
    readonly_fields = ['image_preview']

class AdsTopBannerAdmin(BannerBaseAdmin):
    pass

class AdsRightBannerAdmin(BannerBaseAdmin):
    pass

class AdsBottomBannerAdmin(BannerBaseAdmin):
    pass

# Register models
admin.site.register(Ads, AdsAdmin)
admin.site.register(AdsImages, AdsImagesAdmin)
admin.site.register(Author)
admin.site.register(County, CountyAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AdsTopBanner, AdsTopBannerAdmin)
admin.site.register(AdsRightBanner, AdsRightBannerAdmin)
admin.site.register(AdsBottomBanner, AdsBottomBannerAdmin)
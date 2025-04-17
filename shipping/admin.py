from django.contrib import admin
from .models import Country, City, District, Ward, ShippingFee, ShippingInfo

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'code', 'country')
    search_fields = ('name', 'name_with_type')
    list_filter = ('type', 'country')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'code', 'city')
    search_fields = ('name', 'name_with_type')
    list_filter = ('type', 'city')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'code', 'district')
    search_fields = ('name', 'name_with_type')
    list_filter = ('type', 'district')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ShippingFee)
class ShippingFeeAdmin(admin.ModelAdmin):
    list_display = ('get_location', 'fee')
    search_fields = ('city__name', 'district__name')
    list_filter = ('city',)

    def get_location(self, obj):
        if obj.district:
            return f"{obj.district.name_with_type}"
        return f"{obj.city.name_with_type}"
    get_location.short_description = "Location"

@admin.register(ShippingInfo)
class ShippingInfoAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'address', 'city', 'district', 'ward', 'created_at')
    list_filter = ('city', 'district', 'ward', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
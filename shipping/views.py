from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import City, District, Ward, ShippingFee

def get_cities(request):
    cities = City.objects.all().values('id', 'name', 'name_with_type')
    return JsonResponse(list(cities), safe=False)

def get_districts(request, city_id):
    districts = District.objects.filter(city_id=city_id).values('id', 'name', 'name_with_type')
    return JsonResponse(list(districts), safe=False)

def get_wards(request, district_id):
    wards = Ward.objects.filter(district_id=district_id).values('id', 'name', 'name_with_type')
    return JsonResponse(list(wards), safe=False)

def get_shipping_fee(request, city_id, district_id=None, ward_id=None):
    if ward_id:
        shipping_fee = ShippingFee.objects.filter(ward_id=ward_id).first()
        if shipping_fee:
            return JsonResponse({'fee': shipping_fee.fee})
    
    if district_id:
        shipping_fee = ShippingFee.objects.filter(district_id=district_id).first()
        if shipping_fee:
            return JsonResponse({'fee': shipping_fee.fee})
    
    shipping_fee = ShippingFee.objects.filter(city_id=city_id).first()
    if shipping_fee:
        return JsonResponse({'fee': shipping_fee.fee})
    
    return JsonResponse({'fee': 0})

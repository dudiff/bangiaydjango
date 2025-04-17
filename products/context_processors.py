from .models import UsePurpose, ShoeType, Material
from .models import LABEL_CHOICES
from .models import Brand
from django.db.models import Count

def menu_context(request):
    purposes_men = UsePurpose.objects.filter(
        purpose_types__regex=r'(^1$|^1,|,1$|,1,)'
    ).exclude(
        purpose_types__regex=r'[0-9][0-9]'
    ).distinct()
    
    purposes_women = UsePurpose.objects.filter(
        purpose_types__regex=r'(^2$|^2,|,2$|,2,)'
    ).exclude(
        purpose_types__regex=r'[0-9][0-9]'
    ).distinct()
    
    purposes_kids = UsePurpose.objects.filter(
        purpose_types__regex=r'(^3$|^3,|,3$|,3,)'
    ).exclude(
        purpose_types__regex=r'[0-9][0-9]'
    ).distinct()

    # Add brand queries for each category
    brands_men = Brand.objects.filter(
        brand_types__regex=r'(^1$|^1,|,1$|,1,)'
    ).exclude(
        brand_types__regex=r'[0-9][0-9]'
    ).distinct()
    
    brands_women = Brand.objects.filter(
        brand_types__regex=r'(^2$|^2,|,2$|,2,)'
    ).exclude(
        brand_types__regex=r'[0-9][0-9]'
    ).distinct()
    
    brands_kids = Brand.objects.filter(
        brand_types__regex=r'(^3$|^3,|,3$|,3,)'
    ).exclude(
        brand_types__regex=r'[0-9][0-9]'
    ).distinct()

    return {
        'menu_purposes_men': purposes_men,
        'menu_purposes_women': purposes_women,
        'menu_purposes_kids': purposes_kids,
        'menu_brands_men': brands_men,
        'menu_brands_women': brands_women,
        'menu_brands_kids': brands_kids,
        'shoe_types': ShoeType.objects.all(),
        'materials': Material.objects.all(),
        'labels': LABEL_CHOICES,
    }


def global_brands(request):
    # Get 8 random brands
    random_brands = Brand.objects.annotate(
        product_count=Count('product')
    ).order_by('?')[:8]
    
    return {
        'global_brands': random_brands
    }
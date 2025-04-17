from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings
from shipping.models import Country, City, District, Ward, ShippingFee
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import location data from JSON files'

    def handle(self, *args, **options):
        # Create default country
        vietnam, created = Country.objects.get_or_create(name="Việt Nam")
        
        # Import cities
        cities_file = os.path.join(settings.BASE_DIR, 'templates', 'location', 'cities.json')
        with open(cities_file, 'r', encoding='utf-8') as f:
            cities_data = json.load(f)
            
        for city_data in cities_data:
            city, created = City.objects.update_or_create(
                code=city_data['code'],
                defaults={
                    'name': city_data['name'],
                    'slug': city_data['slug'],
                    'type': city_data['type'],
                    'name_with_type': city_data['name_with_type'],
                    'country': vietnam
                }
            )
            
            # Create default shipping fee
            ShippingFee.objects.get_or_create(
                city=city,
                defaults={'fee': Decimal('30000')}
            )

        # Import districts
        districts_file = os.path.join(settings.BASE_DIR, 'templates', 'location', 'districts.json')
        if os.path.exists(districts_file):
            with open(districts_file, 'r', encoding='utf-8') as f:
                districts_data = json.load(f)
                
            for district_data in districts_data:
                city = City.objects.get(code=district_data['parent_code'])
                district, created = District.objects.update_or_create(
                    code=district_data['code'],
                    defaults={
                        'name': district_data['name'],
                        'slug': district_data['slug'],
                        'type': district_data['type'],
                        'name_with_type': district_data['name_with_type'],
                        'path': district_data['path'],
                        'path_with_type': district_data['path_with_type'],
                        'parent_code': district_data['parent_code'],
                        'city': city
                    }
                )
                
                # Create default district shipping fee
                ShippingFee.objects.get_or_create(
                    city=city,
                    district=district,
                    defaults={'fee': Decimal('30000')}
                )

        # Import wards
        wards_file = os.path.join(settings.BASE_DIR, 'templates', 'location', 'wards.json')
        if os.path.exists(wards_file):
            with open(wards_file, 'r', encoding='utf-8') as f:
                wards_data = json.load(f)
                
            for ward_data in wards_data:
                try:
                    district = District.objects.get(code=ward_data['parent_code'])
                    ward, created = Ward.objects.update_or_create(
                        code=ward_data['code'],
                        defaults={
                            'name': ward_data['name'],
                            'slug': ward_data['slug'],
                            'type': ward_data['type'],
                            'name_with_type': ward_data['name_with_type'],
                            'path': ward_data['path'],
                            'path_with_type': ward_data['path_with_type'],
                            'parent_code': ward_data['parent_code'],
                            'district': district
                        }
                    )
                    
                    # Create default ward shipping fee
                    ShippingFee.objects.get_or_create(
                        city=district.city,
                        district=district,
                        ward=ward,
                        defaults={'fee': Decimal('30000')}
                    )
                except District.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'District with code {ward_data["parent_code"]} not found for ward {ward_data["name"]}')
                    )
                
        self.stdout.write(
            self.style.SUCCESS('Successfully imported location data')
        )
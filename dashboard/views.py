from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from orders.models import Order
from imports.models import ImportOrder, Supplier  # Changed this line to import Supplier from imports
from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear
import json
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from products.models import Product
from collections import defaultdict
# Removed the incorrect import: from suppliers.models import Supplier

@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_products = Product.objects.all()
        total_products_count = total_products.count()
        total_stock = sum(product.stock for product in total_products)

        date_filter = self.request.GET.get('date', '').strip() or None

        completed_orders = Order.objects.filter(status='delivered', payment_status='paid')
        cancelled_orders = Order.objects.filter(status='cancelled')
        completed_orders_count = completed_orders.count()
        cancelled_orders_count = cancelled_orders.count()
        total_orders_count = Order.objects.count()

        # Get suppliers data
        suppliers = Supplier.objects.all()
        suppliers_count = suppliers.count()

        # Get import orders data
        import_orders = ImportOrder.objects.all().order_by('-created_at')
        import_orders_count = import_orders.count()

        all_orders = Order.objects.all().select_related('user').order_by('-created_at')

        chart_data_raw = self.get_dashboard_data(date_filter)
        daily_data_raw = self.get_daily_data(date_filter)

        financial_data = {
            'labels': ['Revenue', 'Import Cost'],
            'data': [chart_data_raw['total_revenue'], chart_data_raw['total_import_cost']]
        }

        chart_data = {
            'labels': chart_data_raw['labels'],
            'completed': chart_data_raw['completed'],
            'cancelled': chart_data_raw['cancelled'],
            'total': chart_data_raw['total'],
        }

        context.update({
            'completed_orders': completed_orders_count,
            'cancelled_orders': cancelled_orders_count,
            'total_orders': total_orders_count,
            'total_revenue': chart_data_raw['total_revenue'],
            'total_import_cost': chart_data_raw['total_import_cost'],
            'chart_data': chart_data,
            'financial_data': financial_data,
            'daily_data': daily_data_raw,
            'completed_orders_list': completed_orders.select_related('user').order_by('-created_at'),
            'cancelled_orders_list': cancelled_orders.select_related('user').order_by('-created_at'),
            'all_orders_list': all_orders,
            'total_products': total_products_count,
            'total_stock': total_stock,
            'products_list': total_products.select_related('category', 'brand'),
            # Add new context data
            'suppliers_count': suppliers_count,
            'suppliers_list': suppliers,
            'import_orders_count': import_orders_count,
            'import_orders_list': import_orders.select_related('supplier', 'created_by'),
        })
        return context

    def get_dashboard_data(self, date_filter=None):
        vn_timezone = timezone.get_current_timezone()
        all_orders = list(Order.objects.all())

        if date_filter:
            try:
                naive_date = datetime.strptime(date_filter, '%Y-%m-%d')
                filter_date = timezone.make_aware(naive_date, vn_timezone)
                filtered_orders = [
                    order for order in all_orders
                    if timezone.localtime(order.created_at, vn_timezone).year == filter_date.year and
                       timezone.localtime(order.created_at, vn_timezone).month == filter_date.month
                ]
            except ValueError:
                filtered_orders = all_orders
                filter_date = None
        else:
            filtered_orders = all_orders
            filter_date = None

        completed = sum(1 for o in filtered_orders if o.status == 'delivered' and o.payment_status == 'paid')
        cancelled = sum(1 for o in filtered_orders if o.status == 'cancelled')
        total = len(filtered_orders)

        if filter_date:
            labels = [filter_date.strftime('%B %Y')]
        else:
            now = timezone.localtime()
            labels = [now.strftime('%B %Y')]

        total_revenue = sum(o.total_amount for o in filtered_orders if o.status == 'delivered' and o.payment_status == 'paid')
        total_import_cost = ImportOrder.objects.aggregate(total=Sum('total_amount'))['total'] or 0

        return {
            'labels': labels,
            'completed': [completed],
            'cancelled': [cancelled],
            'total': [total],
            'total_revenue': float(total_revenue),
            'total_import_cost': float(total_import_cost)
        }

    def get_daily_data(self, date_filter=None):
        vn_timezone = timezone.get_current_timezone()
        if not date_filter:
            return {
                'completed': 0,
                'cancelled': 0,
                'total': 0,
                'revenue': 0
            }
        try:
            naive_date = datetime.strptime(date_filter, '%Y-%m-%d')
            filter_date = timezone.make_aware(naive_date, vn_timezone)
            start = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = filter_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return {
                'completed': 0,
                'cancelled': 0,
                'total': 0,
                'revenue': 0
            }

        filtered = Order.objects.filter(created_at__range=(start, end))
        return {
            'completed': filtered.filter(status='delivered', payment_status='paid').count(),
            'cancelled': filtered.filter(status='cancelled').count(),
            'total': filtered.count(),
            'revenue': filtered.filter(status='delivered', payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
        }

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            date_filter = request.GET.get('date', '').strip() or None
            return JsonResponse({
                **self.get_dashboard_data(date_filter),
                'daily': self.get_daily_data(date_filter)
            })
        return super().get(request, *args, **kwargs)

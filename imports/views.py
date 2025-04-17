from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import ImportOrder, ImportOrderItem
from products.models import Product, Size, Supplier
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
import xlwt
from django.template.loader import render_to_string
# Remove the WeasyPrint import
# from weasyprint import HTML
import tempfile

@staff_member_required
def get_supplier_products(request):
    supplier_id = request.GET.get('supplier_id')
    
    if supplier_id:
        try:
            # Get products associated with this supplier
            products = Product.objects.filter(supplier_id=supplier_id)
            
            # Return product data including price
            product_list = list(products.values('id', 'name', 'price'))
            
            return JsonResponse(product_list, safe=False)
        except Exception as e:
            print(f"Debug: Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # Return empty list if no supplier_id provided
    return JsonResponse([], safe=False)

@staff_member_required
def get_product_sizes(request):
    product_id = request.GET.get('product_id')
    print(f"Debug: API called with product_id: {product_id}")
    
    if product_id:
        try:
            # Get the product
            product = Product.objects.get(id=product_id)
            
            # Get sizes associated with this product
            sizes = product.sizes.all()
            
            # If no sizes found, get all available sizes
            if not sizes.exists():
                sizes = Size.objects.all()
                print(f"Debug: No sizes found for product {product_id}, returning all sizes")
            
            size_list = list(sizes.values('id', 'name'))
            
            print(f"Debug: Found sizes for product {product_id}: {size_list}")
            return JsonResponse(size_list, safe=False)
        except Product.DoesNotExist:
            print(f"Debug: Product with ID {product_id} not found")
            # Return all sizes if product not found
            sizes = Size.objects.all()
            size_list = list(sizes.values('id', 'name'))
            return JsonResponse(size_list, safe=False)
        except Exception as e:
            print(f"Debug: Error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # Return all sizes if no product_id provided
    sizes = Size.objects.all()
    size_list = list(sizes.values('id', 'name'))
    return JsonResponse(size_list, safe=False)


@staff_member_required
def import_order_create(request):
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        notes = request.POST.get('notes')
        
        # Create import order
        import_order = ImportOrder.objects.create(
            supplier_id=supplier_id,
            notes=notes,
            created_by=request.user
        )
        
        # Process items
        product_ids = request.POST.getlist('product[]')
        size_ids = request.POST.getlist('size[]')
        quantities = request.POST.getlist('quantity[]')
        purchase_prices = request.POST.getlist('purchase_price[]')
        
        warning_messages = []
        
        for i in range(len(product_ids)):
            if product_ids[i] and size_ids[i] and int(quantities[i]) > 0:
                # Convert string values to appropriate types
                quantity = int(quantities[i])
                purchase_price = float(purchase_prices[i]) if purchase_prices[i] else 0
                
                # Get the product to check its selling price
                product = Product.objects.get(id=product_ids[i])
                
                # Check if purchase price is higher than selling price
                if purchase_price > product.price:
                    warning_messages.append(f"Cảnh báo: Giá nhập của sản phẩm '{product.name}' ({purchase_price:,.0f} VNĐ) cao hơn giá bán ({product.price:,.0f} VNĐ)!")
                
                ImportOrderItem.objects.create(
                    import_order=import_order,
                    product_id=product_ids[i],
                    size_id=size_ids[i],
                    quantity=quantity,
                    purchase_price=purchase_price
                )
        
        # Display warnings if any
        for warning in warning_messages:
            messages.warning(request, warning)
        
        messages.success(request, f'Đơn nhập hàng #{import_order.id} đã được tạo thành công!')
        return redirect('imports:import_order_list')
    
    context = {
        'suppliers': suppliers,
        'products': products,
    }
    return render(request, 'imports/import_order_create.html', context)

@staff_member_required
def import_order_list(request):
    # Get all suppliers for the filter dropdown
    suppliers = Supplier.objects.all()
    
    # Get filter parameters
    supplier_id = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all orders
    import_orders = ImportOrder.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    if supplier_id:
        import_orders = import_orders.filter(supplier_id=supplier_id)
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__gte=date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__lte=date_to_obj.replace(hour=23, minute=59, second=59))
    
    # Calculate total amount before pagination
    total_orders_count = import_orders.count()
    total_amount = sum(order.total_amount for order in import_orders)
    
    # Pagination
    paginator = Paginator(import_orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'import_orders': page_obj,
        'suppliers': suppliers,
        'total_orders_count': total_orders_count,
        'total_amount': total_amount,
    }
    return render(request, 'imports/import_order_list.html', context)

@staff_member_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="import_orders.xls"'
    
    # Get filter parameters
    supplier_id = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all orders
    import_orders = ImportOrder.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    if supplier_id:
        import_orders = import_orders.filter(supplier_id=supplier_id)
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__gte=date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__lte=date_to_obj.replace(hour=23, minute=59, second=59))
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Đơn nhập hàng')
    
    # Sheet header, first row
    row_num = 0
    
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['Mã đơn', 'Nhà cung cấp', 'Người tạo', 'Ngày tạo', 'Tổng tiền (VNĐ)']
    
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    for i, order in enumerate(import_orders):
        row_num += 1
        
        row = [
            i + 1,  # Start from 1 instead of order.id
            order.supplier.name,
            order.created_by.username,
            order.created_at.strftime('%d/%m/%Y %H:%M'),
            str(order.total_amount),
        ]
        
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    
    wb.save(response)
    return response

@staff_member_required
def print_order(request, order_id):
    import_order = get_object_or_404(ImportOrder, id=order_id)
    
    context = {
        'import_order': import_order,
        'print_mode': True,
    }
    
    return render(request, 'imports/import_order_print.html', context)

@staff_member_required
def print_order_list(request):
    # Get filter parameters
    supplier_id = request.GET.get('supplier')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all orders
    import_orders = ImportOrder.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    if supplier_id:
        import_orders = import_orders.filter(supplier_id=supplier_id)
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__gte=date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        import_orders = import_orders.filter(created_at__lte=date_to_obj.replace(hour=23, minute=59, second=59))
    
    # Calculate total amount
    total_amount = sum(order.total_amount for order in import_orders)
    
    context = {
        'import_orders': import_orders,
        'total_amount': total_amount,
    }
    
    return render(request, 'imports/import_order_list_print.html', context)

@staff_member_required
def import_order_detail(request, order_id):
    import_order = get_object_or_404(ImportOrder, id=order_id)
    context = {
        'import_order': import_order
    }
    return render(request, 'imports/import_order_detail.html', context)


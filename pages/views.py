from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AboutUs, ShoeGuide, Contact

def about_view(request):
    about_list = AboutUs.objects.all().order_by('order', '-updated_at')
    paginator = Paginator(about_list, 5)
    page = request.GET.get('page')
    abouts = paginator.get_page(page)
    return render(request, 'partials/pages/about.html', {'abouts': abouts})

def shoe_guide_view(request):
    guide_list = ShoeGuide.objects.all().order_by('order', '-updated_at')
    paginator = Paginator(guide_list, 5)
    page = request.GET.get('page')
    guides = paginator.get_page(page)
    return render(request, 'partials/pages/shoe_guide.html', {'guides': guides})

def contact_view(request):
    if request.method == 'POST':
        # Check for honeypot field
        if request.POST.get('_gotcha'):
            return redirect('pages:contact')
            
        contact = Contact(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        contact.save()
        messages.success(request, 'Cảm ơn bạn đã liên hệ. Chúng tôi sẽ phản hồi sớm nhất có thể!')
        return redirect('pages:contact')
        
    return render(request, 'partials/pages/contact.html')
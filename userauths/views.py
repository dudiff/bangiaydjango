from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm, UserLoginForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  # Add urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str  # Import từ django.utils.encoding
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from django.urls import reverse
from userauths.models import User, Profile
from shipping.models import City, District, Ward
from django.contrib.auth import get_user_model
from django.http import JsonResponse 
from products.models import Product

User = get_user_model()

def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk)) 
    token = default_token_generator.make_token(user)
    # Create activation link
    activation_link = request.build_absolute_uri(
        reverse('userauths:activate', kwargs={'uidb64': uid, 'token': token})
    )
    # Email content
    subject = 'Kích hoạt tài khoản DStore của bạn'
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]
    # Create email content
    context = {
        'user': user,
        'activation_link': activation_link,
        'domain': request.get_host(),  # Add domain to context
        'uid': uid,  # Add uid to context
        'token': token,  # Add token to context
    }
    # Render email templates
    html_content = render_to_string('userauths/activation_email.html', context)
    text_content = strip_tags(html_content)
    # Create and send email
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    # Debug print
    print(f"Activation email sent to {user.email}")
    print(f"Activation link: {activation_link}")
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"{username} đã đến với trang web của DStore, vui lòng kiểm tra email để xác thực tài khoản.")

            # Send verification email
            send_activation_email(new_user, request)

            # Redirect to existing activation email view
            return redirect("userauths:activation_email")  # Changed from activation_email_sent
        else:
            messages.error(request, "Đăng ký không thành công.")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)
# View xử lý xác thực tài khoản
def activate_account(request, uidb64, token):
    try:
        # Fix: Use urlsafe_base64_decode directly on uidb64
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Tài khoản đã được kích hoạt thành công! Bạn có thể đăng nhập ngay.")
        return redirect('userauths:sign-in')
    else:
        messages.error(request, "Liên kết kích hoạt không hợp lệ hoặc đã hết hạn.")
        return redirect('userauths:sign-in')
def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:index")
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Xác thực user bằng backend mới
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Bạn đã đăng nhập thành công!")
                return redirect("core:index")
            else:
                messages.error(request, "Tên đăng nhập/email hoặc mật khẩu không đúng.")
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin đăng nhập.")
    else:
        form = UserLoginForm()
    context = {'form': form}
    return render(request, "userauths/sign-in.html", context)
def logout_view(request):
    # Check if user is admin/staff before logging out
    is_admin = request.user.is_staff or request.user.is_superuser
    # Perform logout
    logout(request)
    
    if is_admin:
        messages.success(request, "Bạn đã đăng xuất thành công")
        return redirect('/admin/login/?next=/admin/')
    else:
        messages.success(request, "Bạn đã đăng xuất thành công")
        return redirect("userauths:sign-in")
def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Create reset link using reverse URL
            reset_url = request.build_absolute_uri(
                reverse('userauths:password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token,
                })
            )
            
            # Send email
            email_subject = "Đặt lại mật khẩu"
            html_content = render_to_string('userauths/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(email_subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            messages.success(request, "Email hướng dẫn đặt lại mật khẩu đã được gửi.")
            return redirect('userauths:password_reset_done')
        except User.DoesNotExist:
            messages.error(request, "Không tìm thấy tài khoản với email này.")
    
    return render(request, 'userauths/password_reset.html')
def password_reset_done_view(request):
    return render(request, 'userauths/password_reset_done.html')
def password_reset_confirm_view(request, uidb64, token):
    try:
        # Fix: Changed from encode to decode
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, "Mật khẩu đã được đặt lại thành công. Bạn có thể đăng nhập ngay bây giờ.")
                return redirect('userauths:sign-in')
            else:
                messages.error(request, "Mật khẩu không khớp.")
        return render(request, 'userauths/password_reset_confirm.html')
    else:
        messages.error(request, "Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.")
        return redirect('userauths:password_reset')
# View thông báo gửi email xác thực
def activation_email_view(request):
    return render(request, "userauths/activation_email.html")
@login_required
def profile_view(request):
    return render(request, 'userauths/profile.html', {'user': request.user})
@login_required
def edit_profile_view(request):
    user = request.user
    
    # Try to get or create profile
    try:
        profile = user.profile
    except:
        # If profile doesn't exist, create one
        from userauths.models import Profile
        profile = Profile.objects.create(user=user)
    
    if request.method == 'POST':
        # Update user info
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.bio = request.POST.get('bio')
        user.save()
        
        # Update profile info
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.city_id = request.POST.get('city')
        profile.district_id = request.POST.get('district')
        profile.ward_id = request.POST.get('ward')
        profile.save()
        
        messages.success(request, "Thông tin đã được cập nhật thành công!")
        return redirect('userauths:profile')
    
    # Get current districts and wards for the user
    districts = []
    wards = []
    if profile.city_id:
        districts = District.objects.filter(city_id=profile.city_id).order_by('name_with_type')
        if profile.district_id:
            wards = Ward.objects.filter(district_id=profile.district_id).order_by('name_with_type')
    
    context = {
        'cities': City.objects.all().order_by('name_with_type'),
        'districts': districts,
        'wards': wards,
        'user': user,
        'profile': profile,
    }
    return render(request, 'userauths/edit_profile.html', context)

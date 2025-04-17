from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

class AboutUs(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    content = CKEditor5Field('Content', config_name='default')
    image = models.ImageField(upload_to='about/', verbose_name="Hình ảnh")
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        verbose_name = "Về chúng tôi"
        verbose_name_plural = "Về chúng tôi"
        ordering = ['order']

    def __str__(self):
        return self.title

class ShoeGuide(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tiêu đề")
    content = CKEditor5Field('Content', config_name='default')
    image = models.ImageField(upload_to='guides/', verbose_name="Hình ảnh")
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        verbose_name = "Cách chọn giày"
        verbose_name_plural = "Cách chọn giày"
        ordering = ['order']

    def __str__(self):
        return self.title

class Contact(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Họ", default="")
    last_name = models.CharField(max_length=100, verbose_name="Tên", default="")
    email = models.EmailField(verbose_name="Email", default="")
    subject = models.CharField(max_length=200, verbose_name="Chủ đề", blank=True)
    message = models.TextField(verbose_name="Nội dung", default="")
    created_at = models.DateTimeField(verbose_name="Ngày gửi", default=timezone.now)
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")

    class Meta:
        verbose_name = "Liên hệ"
        verbose_name_plural = "Liên hệ"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

from django.db import models

class HomeSlide(models.Model):
    subtitle = models.CharField(max_length=200, verbose_name="Tiêu đề phụ")
    title_start = models.CharField(max_length=100, verbose_name="Phần đầu tiêu đề", blank=True)
    title_highlighted = models.CharField(max_length=100, verbose_name="Phần tiêu đề nổi bật", blank=True)
    title_end = models.CharField(max_length=100, verbose_name="Phần cuối tiêu đề", blank=True)
    button_text = models.CharField(max_length=50, verbose_name="Nút bấm")
    button_link = models.CharField(max_length=200, verbose_name="Đường dẫn")
    image = models.ImageField(upload_to='slides/', verbose_name="Hình ảnh")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    show_year = models.BooleanField(default=False, verbose_name="Hiển thị năm")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Slide Trang Chủ"
        verbose_name_plural = "Slides Trang Chủ"

    def __str__(self):
        return f"{self.title_start} {self.title_highlighted} {self.title_end}"
class InstagramPost(models.Model):
    image = models.ImageField(upload_to='instagram/', verbose_name="Hình ảnh")
    title = models.CharField(max_length=200, verbose_name="Tiêu đề ảnh", blank=True)
    alt_text = models.CharField(max_length=200, verbose_name="Mô tả ảnh", blank=True)
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Ảnh Instagram"
        verbose_name_plural = "Ảnh Instagram"

    def __str__(self):
        return self.title or f"Instagram Post {self.id}"
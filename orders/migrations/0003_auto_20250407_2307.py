from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('orders', '0002_alter_orderitem_price_alter_orderitem_promotions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='size',
            field=models.ForeignKey('products.Size', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='order_items_size'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='color',
            field=models.ForeignKey('products.ColorType', on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='order_items_color'),
        ),
    ]

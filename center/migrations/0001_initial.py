# Generated by Django 3.2.5 on 2023-05-11 03:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind_id', models.IntegerField(verbose_name='kind_id')),
                ('kind', models.CharField(max_length=128, verbose_name='kind_title')),
                ('title', models.CharField(max_length=128, verbose_name='room_title')),
                ('floor', models.IntegerField(verbose_name='floor')),
                ('details', models.TextField(verbose_name='room_details')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='room_photo')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='price')),
                ('avg_rating', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='avg_rating')),
            ],
            options={
                'db_table': 'view_room',
                'ordering': ['kind', 'title'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datec', models.DateTimeField(auto_now_add=True, verbose_name='datec_claim')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('finish', models.DateTimeField(verbose_name='finish')),
                ('details', models.TextField(verbose_name='claim_details')),
                ('result', models.TextField(blank=True, null=True, verbose_name='claim_result')),
            ],
            options={
                'db_table': 'claim',
                'ordering': ['datec'],
            },
        ),
        migrations.CreateModel(
            name='Kind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, verbose_name='kind_title')),
            ],
            options={
                'db_table': 'kind',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daten', models.DateTimeField(verbose_name='daten')),
                ('title', models.CharField(max_length=256, verbose_name='title_news')),
                ('details', models.TextField(verbose_name='details_news')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='photo_news')),
            ],
            options={
                'db_table': 'news',
                'ordering': ['daten'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=16, verbose_name='room_title')),
                ('floor', models.IntegerField(verbose_name='floor')),
                ('details', models.TextField(verbose_name='room_details')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='images/', verbose_name='room_photo')),
                ('price', models.DecimalField(decimal_places=2, max_digits=9, verbose_name='price')),
                ('kind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_kind', to='center.kind')),
            ],
            options={
                'db_table': 'room',
                'ordering': ['kind', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dater', models.DateTimeField(auto_now_add=True, verbose_name='dater_reviews')),
                ('rating', models.IntegerField(blank=True, null=True, verbose_name='rating')),
                ('details', models.TextField(verbose_name='details_reviews')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_room', to='center.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reviews',
                'ordering': ['dater'],
            },
        ),
        migrations.AddIndex(
            model_name='news',
            index=models.Index(fields=['daten'], name='news_daten_a29edb_idx'),
        ),
        migrations.AddIndex(
            model_name='kind',
            index=models.Index(fields=['title'], name='kind_title_e37f47_idx'),
        ),
        migrations.AddField(
            model_name='claim',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claim_room', to='center.room'),
        ),
        migrations.AddField(
            model_name='claim',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='claim_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['kind', 'title'], name='room_kind_id_04609d_idx'),
        ),
        migrations.AddIndex(
            model_name='reviews',
            index=models.Index(fields=['dater'], name='reviews_dater_c1460a_idx'),
        ),
        migrations.AddIndex(
            model_name='claim',
            index=models.Index(fields=['datec', 'user'], name='claim_datec_7b225b_idx'),
        ),
    ]
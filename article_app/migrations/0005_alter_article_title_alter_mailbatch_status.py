# Generated by Django 5.1.4 on 2025-02-11 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article_app', '0004_rename_sent_mail_count_usercategory_last_mailed_article_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='mailbatch',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('PENDING', 'Pending'), ('SENT', 'Sent'), ('FAILED', 'Failed')], default='CREATED', max_length=100),
        ),
    ]

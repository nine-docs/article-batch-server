# Generated by Django 5.1.4 on 2025-01-15 01:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article_app', '0003_usercategory_user_id_userschedule_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercategory',
            old_name='sent_mail_count',
            new_name='last_mailed_article_id',
        ),
    ]

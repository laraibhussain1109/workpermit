from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0002_workpermitrequest_request_id_governmentid_visitor_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='governmentid',
            name='id_photo',
            field=models.FileField(upload_to='government_ids/'),
        ),
        migrations.AlterField(
            model_name='governmentid',
            name='visitor_photo',
            field=models.ImageField(blank=True, null=True, upload_to='visitor_photos/'),
        ),
    ]

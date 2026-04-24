import uuid

from django.db import migrations, models


def generate_request_ids(apps, schema_editor):
    WorkPermitRequest = apps.get_model('permits', 'WorkPermitRequest')
    for permit in WorkPermitRequest.objects.filter(request_id__isnull=True):
        permit.request_id = f'WPR-{uuid.uuid4().hex[:8].upper()}'
        permit.save(update_fields=['request_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='governmentid',
            name='visitor_photo',
            field=models.ImageField(default='', upload_to='visitor_photos/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workpermitrequest',
            name='request_id',
            field=models.CharField(editable=False, max_length=20, null=True),
        ),
        migrations.RunPython(generate_request_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='workpermitrequest',
            name='request_id',
            field=models.CharField(editable=False, max_length=20, unique=True),
        ),
    ]

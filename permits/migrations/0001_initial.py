from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkPermitRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('location', models.CharField(max_length=255)),
                ('work_types', models.CharField(blank=True, max_length=500)),
                ('hazards', models.TextField()),
                ('precautions', models.TextField()),
                ('legal_requirements', models.TextField(blank=True)),
                ('persons_to_notify', models.CharField(blank=True, max_length=255)),
                ('contractor_name', models.CharField(max_length=255)),
                ('contact_person', models.CharField(max_length=255)),
                ('country_code', models.CharField(choices=[('+91', '🇮🇳 India (+91)'), ('+1', '🇺🇸 United States (+1)'), ('+44', '🇬🇧 United Kingdom (+44)'), ('+971', '🇦🇪 UAE (+971)'), ('+966', '🇸🇦 Saudi Arabia (+966)'), ('+65', '🇸🇬 Singapore (+65)')], default='+91', max_length=8)),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^\\d{7,15}$', 'Enter a valid phone number (7-15 digits).')])),
                ('department', models.CharField(max_length=255)),
                ('shift_start', models.DateTimeField()),
                ('shift_end', models.DateTimeField()),
                ('exact_location', models.CharField(max_length=255)),
                ('ppe_items', models.CharField(blank=True, max_length=500)),
                ('other_requirement', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_permits', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_permits', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='GovernmentID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_type', models.CharField(choices=[('Adhaar Card', 'Adhaar Card'), ('Voter ID Card', 'Voter ID Card'), ("Driver's License", "Driver's License"), ('Passport', 'Passport'), ('Ration Card', 'Ration Card')], max_length=30)),
                ('id_number', models.CharField(max_length=100)),
                ('id_photo', models.ImageField(upload_to='government_ids/')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('permit_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='government_id', to='permits.workpermitrequest')),
            ],
        ),
    ]

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class WorkPermitRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    WORK_TYPE_CHOICES = [
        ('Hot Work', 'Hot Work'),
        ('Excavation/Civil Work', 'Excavation/Civil Work'),
        ('Pipeline Work', 'Pipeline Work'),
        ('Confined Space Entry', 'Confined Space Entry'),
        ('Height Work (1.8m+)', 'Height Work (1.8m+)'),
        ('Electrical', 'Electrical'),
        ('Emergency Machinery', 'Emergency Machinery'),
        ('Others', 'Others'),
    ]

    PPE_CHOICES = [
        ('Full Body Harness', 'Full Body Harness'),
        ('Ear Plug', 'Ear Plug'),
        ('Goggle / Face Shield', 'Goggle / Face Shield'),
        ('Dust Mask', 'Dust Mask'),
        ('Hand Gloves', 'Hand Gloves'),
        ('Apron & Leg Guard', 'Apron & Leg Guard'),
        ('Heat Resistant Suit', 'Heat Resistant Suit'),
        ('Fitness Certificate', 'Fitness Certificate'),
    ]

    COUNTRY_CHOICES = [
        ('+91', '🇮🇳 India (+91)'),
        ('+1', '🇺🇸 United States (+1)'),
        ('+44', '🇬🇧 United Kingdom (+44)'),
        ('+971', '🇦🇪 UAE (+971)'),
        ('+966', '🇸🇦 Saudi Arabia (+966)'),
        ('+65', '🇸🇬 Singapore (+65)'),
    ]

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_permits')
    valid_from = models.DateField()
    valid_to = models.DateField()
    location = models.CharField(max_length=255)

    work_types = models.CharField(max_length=500, blank=True)
    hazards = models.TextField()
    precautions = models.TextField()
    legal_requirements = models.TextField(blank=True)
    persons_to_notify = models.CharField(max_length=255, blank=True)

    contractor_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    country_code = models.CharField(max_length=8, choices=COUNTRY_CHOICES, default='+91')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{7,15}$', 'Enter a valid phone number (7-15 digits).')],
    )
    department = models.CharField(max_length=255)
    shift_start = models.DateTimeField()
    shift_end = models.DateTimeField()
    exact_location = models.CharField(max_length=255)

    ppe_items = models.CharField(max_length=500, blank=True)
    other_requirement = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_permits')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.location} ({self.get_status_display()})'

    def work_types_list(self):
        return [v for v in self.work_types.split('|') if v]

    def ppe_items_list(self):
        return [v for v in self.ppe_items.split('|') if v]


class GovernmentID(models.Model):
    class IdType(models.TextChoices):
        ADHAAR = 'Adhaar Card', 'Adhaar Card'
        VOTER = 'Voter ID Card', 'Voter ID Card'
        DRIVING = "Driver's License", "Driver's License"
        PASSPORT = 'Passport', 'Passport'
        RATION = 'Ration Card', 'Ration Card'

    permit_request = models.OneToOneField(WorkPermitRequest, on_delete=models.CASCADE, related_name='government_id')
    id_type = models.CharField(max_length=30, choices=IdType.choices)
    id_number = models.CharField(max_length=100)
    id_photo = models.ImageField(upload_to='government_ids/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id_type} - {self.id_number}'

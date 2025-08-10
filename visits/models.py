from django.db import models
import uuid

class VisitRequest(models.Model):
    RELATION_CHOICES = [
        ('mother', 'الأم'),
        ('father', 'الأب'),
        ('spouse', 'الزوج/الزوجة'),
        ('son', 'الابن/الابنة'),
        ('other', 'أخرى'),
    ]

    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    full_name = models.CharField(max_length=150)
    national_id = models.CharField(max_length=20)
    inmate_id = models.CharField(max_length=20)  # هوية النزيل الجديدة
    phone = models.CharField(max_length=20)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES)
    documents = models.FileField(upload_to='documents/')
    terms_accepted = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_notes = models.TextField(blank=True)

    appointment_datetime = models.DateTimeField(null=True, blank=True)
    appointment_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"طلب {self.full_name} ({self.get_status_display()})"

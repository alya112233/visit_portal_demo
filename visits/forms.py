from django import forms
from .models import VisitRequest

ALLOWED_EXTS = {'.pdf', '.jpg', '.jpeg', '.png'}
MAX_FILE_MB = 5

class VisitRequestForm(forms.ModelForm):
    # نجعل الإقرار إلزامي مع رسالة خطأ واضحة
    terms_accepted = forms.BooleanField(
        label='أُقرّ بالموافقة على الشروط والأحكام',
        required=True,
        error_messages={'required': 'يلزم الإقرار بالموافقة على الشروط والأحكام قبل الإرسال.'}
    )

    class Meta:
        model = VisitRequest
        fields = ['full_name', 'national_id','inmate_id', 'phone', 'relation', 'documents', 'terms_accepted']
        labels = {
            'full_name': 'الاسم الثلاثي',
            'national_id': 'رقم الهوية الوطنية',
            'inmate_id': 'رقم الهوية الوطنية',
            'phone': 'رقم الجوال',
            'relation': 'صلة القرابة',
            'documents': 'المستندات المطلوبة (PDF/صورة)',
        }

    def clean_national_id(self):
        nid = self.cleaned_data['national_id']
        if not nid.isdigit() or not (8 <= len(nid) <= 20):
            raise forms.ValidationError('رقم الهوية غير صحيح.')
        return nid

    def clean_phone(self):
        ph = self.cleaned_data['phone']
        if not ph.replace('+', '').replace('-', '').isdigit():
            raise forms.ValidationError('رقم الجوال غير صحيح.')
        return ph

    def clean_documents(self):
        f = self.cleaned_data['documents']
        ext = (f.name.rsplit('.', 1)[-1] if '.' in f.name else '').lower()
        ext = '.' + ext if ext else ''
        if ext not in ALLOWED_EXTS:
            raise forms.ValidationError('الامتدادات المسموحة: PDF, JPG, JPEG, PNG')
        if f.size > MAX_FILE_MB * 1024 * 1024:
            raise forms.ValidationError(f'حجم الملف يجب ألا يتجاوز {MAX_FILE_MB}MB')
        return f

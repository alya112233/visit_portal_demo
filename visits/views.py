from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import Http404
from io import BytesIO
import base64
import qrcode

from .models import VisitRequest
from .forms import VisitRequestForm


# الصفحة الرئيسية (نوجهها لقائمة المراجعة للموظف)
def home(request):
    return redirect('visits:review_list')


# نموذج تقديم الطلب (واجهة عامة)
def request_form(request):
    if request.method == 'POST':
        form = VisitRequestForm(request.POST, request.FILES)
        if form.is_valid():
            visit = form.save()
            # نقدر نرسل رابط الكرت لاحقاً عند القبول
            return redirect('visits:request_success')
    else:
        form = VisitRequestForm()
    return render(request, 'visits/request_form.html', {'form': form})


def request_success(request):
    return render(request, 'visits/request_success.html')


# لوحة الموظف: قائمة الطلبات
def review_list(request):
    visits = VisitRequest.objects.order_by('-created_at')
    return render(request, 'visits/review_list.html', {'requests': visits})


# لوحة الموظف: تفاصيل الطلب + اعتماد/رفض
def review_detail(request, pk):
    visit = get_object_or_404(VisitRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')  # approve / reject
        notes = request.POST.get('review_notes', '').strip()
        appt_str = request.POST.get('appointment_datetime', '').strip()

        visit.review_notes = notes

        if action == 'approve':
            visit.status = 'approved'
        elif action == 'reject':
            visit.status = 'rejected'

        if appt_str:
            from datetime import datetime
            try:
                dt = datetime.strptime(appt_str, "%Y-%m-%dT%H:%M")
                visit.appointment_datetime = timezone.make_aware(
                    dt, timezone.get_current_timezone()
                )
            except Exception:
                pass

        visit.save()

        # عند القبول نفتح صفحة الكرت مباشرة
        if visit.status == 'approved' and visit.appointment_datetime:
            return redirect('visits:appointment_card', token=visit.appointment_token)

        # غير ذلك نرجع للقائمة
        return redirect('visits:review_list')

    return render(request, 'visits/review_detail.html', {'obj': visit})


# زر/مسار اعتماد منفصل (لوحة الموظف) — يضبط الحالة ويذهب للكرت
def approve_request(request, pk):
    visit = get_object_or_404(VisitRequest, pk=pk)
    visit.status = 'approved'
    if not visit.appointment_datetime:
        # لو ما حدد موعد في التفاصيل، نحط موعد افتراضي الآن + 3 أيام مثلاً
        visit.appointment_datetime = timezone.now() + timezone.timedelta(days=3)
    visit.save()
    return redirect('visits:appointment_card', token=visit.appointment_token)


# كرت الموعد القابل للطباعة
def appointment_card(request, token):
    visit = get_object_or_404(VisitRequest, appointment_token=token)

    # نسمح بعرض الكرت فقط للطلبات المقبولة التي لها موعد
    if visit.status != 'approved' or not visit.appointment_datetime:
        raise Http404("الكرت غير متاح حالياً.")

    # QR يحوي رابط التحقق (نفس رابط الصفحة)
    verify_url = request.build_absolute_uri(request.path)
    qr_img = qrcode.make(verify_url)
    buf = BytesIO()
    qr_img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    context = {
        'o': visit,
        'ticket_link': verify_url,
        'qr_uri': f"data:image/png;base64,{qr_b64}",
    }
    return render(request, 'visits/appointment_card.html', context)


# اسم بديل للمسار /ticket/<uuid:token>/
def ticket_view(request, token):
    return appointment_card(request, token)

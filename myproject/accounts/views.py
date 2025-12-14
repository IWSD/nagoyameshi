from django.shortcuts import render

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm
from .models import CustomUser
from mysite.models import Reservation

class UserRegisterView(CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')  # 登録後にログインページへ

# def mypage(request):
#     reservations = Reservation.objects.filter(user=request.user).order_by('-reserve_datetime')

#     return render(request, "mysite/mypage.html", {
#         "reservations": reservations,
#     })

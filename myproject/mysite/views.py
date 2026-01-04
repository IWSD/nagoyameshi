from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from .models import Shop, Review, Reservation, Category
from .forms import ReviewForm, ReservationForm, ShopForm
from accounts.models import CustomUser
import stripe
from django.conf import settings
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.core.mail import send_mail
from django.conf import settings


from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
class TopView(ListView):
  model = Shop
  template_name = "top.html"
  context_object_name = "shops"

  def get_queryset(self):
      queryset = Shop.objects.all()
      # GETで検索条件取得
      name = self.request.GET.get("name")
      station = self.request.GET.get("station")
      category_id = self.request.GET.get("category")
      price = self.request.GET.get("price")
      sort = self.request.GET.get("sort")

      # 店舗名検索（部分一致）
      if name:
          queryset = queryset.filter(name__icontains=name)
      # 最寄駅検索（部分一致）
      if station:
          queryset = queryset.filter(near_station__icontains=station) 
      
       # 料理種別検索
      if category_id:
            queryset = queryset.filter(shop_category_id=category_id)

      # 価格帯検索
      if price:
            queryset = queryset.filter(price_range__lte=price)

  
      # --- 評価平均を計算 ---
      queryset = queryset.annotate(
         avg_rating=Avg("reviews__rating")).annotate(sort_rating=Coalesce("avg_rating", 0.0))

      # --- 並び替え ---
      if sort == "rating":
        queryset = queryset.order_by("-sort_rating")
      else:
      # デフォルトは新着順
        queryset = queryset.order_by("-id")

      return queryset   
  
  # 検索ヒット数
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["result_count"] = self.get_queryset().count()
      context["current_sort"] = self.request.GET.get("sort", "")
       # カテゴリ一覧（プルダウン用）
      context["categories"] = Category.objects.all()
      return context

class LoginView(LoginView):
  form_class = AuthenticationForm
  template_name = 'login.html'

class LogoutView(LoginRequiredMixin, LogoutView):
  template_name = 'top.html'
  
class ShopDetailView(DetailView):
    model = Shop
    template_name = "shop_detail.html"
    context_object_name = "shop"

    def get_context_data(self, **kwargs):
        context = super(ShopDetailView, self).get_context_data(**kwargs)
        shop = context["shop"]
        context["reviews"] = shop.reviews.all().order_by("-created_at")
        return context

# #店舗情報編集
# @login_required
# def edit_shop(request, shop_id):
#     shop = get_object_or_404(Shop, id=shop_id)

#     # 権限チェック
#     if not request.user.is_editor() or shop.editor != request.user:
#         return HttpResponseForbidden("この店舗を編集する権限がありません。")

#     if request.method == "POST":
#         form = ShopForm(request.POST, request.FILES, instance=shop)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "店舗情報を更新しました。")
#             return redirect("edit_shop", shop_id=shop.id)
#     else:
#         form = ShopForm(instance=shop)

#     return render(request, "shops/edit_shop.html", {"form": form, "shop": shop})

class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = "shops/shop_edit.html"

    def test_func(self):
        shop = self.get_object()
        return self.request.user == shop.editor or self.request.user.is_admin()
    
    def get_success_url(self):
        return reverse_lazy("shop_detail", kwargs={"pk": self.object.pk})
    
class MyShopListView(LoginRequiredMixin, ListView):
    model = Shop
    template_name = "shops/my_shop_list.html"

    def get_queryset(self):
        return Shop.objects.filter(editor=self.request.user)

# class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#   model = Shop
#   fields = ['name', 'shop_explanation', 'near_station', 'walk_minutes', 'price_range', 'business_hour_start', 'business_hour_end', 'address', 'img']
#   template_name = 'shop_edit.html'

#   def test_func(self):
#     user = self.request.user
#     return user.is_admin() or user.is_editor()
  
#   def handle_no_permission(self):
#     from django.shortcuts import redirect
#     return redirect('top')
  
#   def get_success_url(self):
#     return reverse_lazy('shop_detail', kwargs={'pk': self.object.pk})

class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
  model = Review
  form_class = ReviewForm
  template_name = "review_form.html"

  def test_func(self):
     # 有料ユーザーだけレビュー投稿可
     return self.request.user.is_paid() or self.request.user.is_admin()
  
  def form_valid(self, form):
    form.instance.user = self.request.user
    form.instance.shop_id = self.kwargs['pk'] # URLから店舗IDを取得
    return super().form_valid(form)
  
  def get_success_url(self):
    return reverse_lazy('shop_detail', kwargs={'pk': self.kwargs['pk']})
  
#予約実施画面
class ReservationInitialView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = "reservation_form.html"

    def test_func(self):
        # 有料ユーザーまたは管理者のみ予約可能
        return self.request.user.is_paid() or self.request.user.is_admin()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 店舗オブジェクトをテンプレートに渡す
        context['shop'] = Shop.objects.get(pk=self.kwargs['pk'])
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        shop = Shop.objects.get(pk=self.kwargs['pk'])
        # インスタンスにshopをセットすることでバリデーション時点で参照できるようにする
        kwargs['instance'] = Reservation(shop=shop, user=self.request.user)
        return kwargs
  
    def form_valid(self, form):
        form.instance.user = self.request.user
        shop = Shop.objects.get(pk=self.kwargs['pk'])
        form.instance.shop = Shop.objects.get(pk=self.kwargs['pk'])
        # form.instance.shop = shop

        try:
            form.instance.clean()  # 上限チェック
        except ValidationError as e:
            form.add_error(None, e.message)
            return self.form_invalid(form)
        # return super().form_valid(form)
   
        # ===== ① 予約を保存 =====
        response = super().form_valid(form)
        # ===== ② 保存された予約を取得 =====
        reservation = self.object
        user = self.request.user
        # ===== ③ メール送信 =====
        send_mail(
          subject="【予約完了】ご予約ありがとうございます",
          message=(
              f"{user.username} 様\n\n"
              f"以下の内容で予約を受け付けました。\n\n"
              f"店舗名：{shop.name}\n"
              f"予約日：{reservation.date}\n"
              f"予約時間：{reservation.time}\n"
              f"人数：{reservation.num_people} 名\n\n"
              f"ご来店をお待ちしております。"
          ),
          from_email=settings.DEFAULT_FROM_EMAIL,
          recipient_list=[user.email],
          fail_silently=False,
        )
       # ===== ④ 成功画面へ =====
        return response
  

    def get_success_url(self):
        return reverse_lazy('reservation_success', kwargs={'reservation_id': self.object.id})
    
# 予約の成功画面
class ReservationSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "reservation_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation_id = self.kwargs['reservation_id']
        reservation = get_object_or_404(Reservation, id=reservation_id)
        context['reservation'] = reservation
        context['shop'] = reservation.shop
        return context

def test_mail(request):
    send_mail(
        subject="【テスト】メール送信確認",
        message="これはDjangoの開発用メール送信テストです。",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["test@example.com"],
        fail_silently=False,
    )
    return HttpResponse("メール送信テスト完了（コンソールを確認してください）")


#会員情報一覧
class MyPageView(LoginRequiredMixin, TemplateView):
    template_name = "mypage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
    # ユーザーの予約一覧（予約日時の降順）
        reservations = Reservation.objects.filter(
        user = user).order_by('-time')

        context["reservations"] = reservations
        return context

#stripeのサブスクリプション
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        YOUR_PRICE_ID = "price_1SX0XqDVo3BBFnDCBkJHGtYG"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            # customer_creation="always",
            client_reference_id=request.user.id,
            line_items=[
                {
                    "price": YOUR_PRICE_ID,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=request.build_absolute_uri(reverse("payment_success")),
            cancel_url=request.build_absolute_uri(reverse("payment_cancel")),
            
        )
        print("通過0")
        return redirect(checkout_session.url)
    
def payment_success(request):
    return render(request, "payment_success.html")

def payment_cancel(request):
    return render(request, "payment_cancel.html")

#stripeのwebhook処理
@csrf_exempt
def stripe_webhook(request):
    print("🔥 WEBHOOK 到達")
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    # except stripe.error.SignatureVerificationError:
    #     return HttpResponse(status=400)
    except Exception as e:
      print("❌ Webhook エラー:", e)
      return HttpResponse(status=400)
    
    print("通過1")

   # ① checkout 完了時
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        user_id = session.get("client_reference_id")

        # Subscription ID を精確に取得
        subscription_id = session.get("subscription")

        if user_id:
            user = CustomUser.objects.get(id=user_id)
            user.user_type = user.USER_TYPE_PAID
            user.stripe_subscription_id = subscription_id
            user.save()
            print("通過2")

        return HttpResponse(status=200)
    
    # ② サブスク解約(client から cancelしたとき含む)
    if event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]

        # DB から該当ユーザーを特定
        try:
            user = CustomUser.objects.get(stripe_subscription_id=subscription_id)
            user.user_type = user.USER_TYPE_FREE
            user.stripe_subscription_id = None
            user.save()
            print("通過5")
        except CustomUser.DoesNotExist:
            pass

        return HttpResponse(status=200)

    return HttpResponse(status=200)

@login_required
def cancel_subscription(request):
    user = request.user

    if not user.stripe_subscription_id:
        # サブスクリプションがない場合は処理せずトップへ
        print("通過3")
        return redirect('mypage')

    try:
        # Stripe上でサブスクリプションをキャンセル
        stripe.Subscription.delete(user.stripe_subscription_id)

        # ユーザーのステータスを無料に変更
        user.user_type = user.USER_TYPE_FREE
        user.stripe_subscription_id = None
        user.save()
        print("通過4")

    except stripe.error.StripeError as e:
        # エラー処理（ログ出力やメッセージ表示）
        print("Stripe error:", e)

    return redirect('mypage')  # 任意のリダイレクト先
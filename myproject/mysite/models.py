from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.models import CustomUser


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
       return self.name

class Shop(models.Model):
  name = models.CharField(max_length=200, verbose_name="店名")
  shop_explanation = models.CharField(max_length=200, verbose_name="店舗紹介")
  near_station = models.CharField(max_length=200, verbose_name="最寄駅")
  walk_minutes = models.PositiveIntegerField(verbose_name="徒歩時間")
  shop_category_id = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="カテゴリ")
  price_range = models.PositiveIntegerField(verbose_name="価格帯")
  business_hour_start = models.TimeField(verbose_name="営業時間（開始）")
  business_hour_end = models.TimeField(verbose_name="営業時間（終了）")
  address = models.CharField(max_length=300, verbose_name="住所")
  latitude = models.FloatField(null=True, blank=True, verbose_name="緯度")   # 緯度（任意）
  longitude = models.FloatField(null=True, blank=True, verbose_name="経度")  # 経度（任意）
    # あとで予約可能数を修正
  max_reserve_num = models.PositiveIntegerField(verbose_name="予約可能人数")
  img = models.ImageField(blank=True, default='noImage.png', verbose_name="店舗画像")

 # どのユーザーが編集できるかを紐づける
  editor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="editable_shops", )

  def __str__(self):
    return self.name
  
class Review (models.Model):
   shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   title = models.CharField(max_length=200)
   rating = models.PositiveSmallIntegerField(choices=[(i, f"{i}点") for i in range(1, 6)])
   content = models.TextField()
   created_at = models.DateTimeField(default=timezone.now)

   def __str__(self):
    return f"{self.title} ({self.shop.name})" 
   


class Reservation(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(verbose_name="予約日")
    time = models.TimeField(verbose_name="予約時間")
    num_people = models.PositiveIntegerField(verbose_name="予約人数")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        shop_name = self.shop.name if self.shop_id else "未設定の店舗"
        username = self.user.username if self.user_id else "未設定のユーザー"
        return f"{shop_name} ({self.date} {self.time}) - {username}"
    
    def clean(self):
        #"""予約上限を超えていないかチェック"""
        # 同じ店舗・同じ日付の既存予約を合計
        existing_total = Reservation.objects.filter(shop=self.shop, date=self.date).aggregate(
            total=models.Sum('num_people')
        )['total'] or 0

        # すでにある予約 + 今回の予約 > 店舗の上限 ならエラー
        if existing_total + self.num_people > self.shop.max_reserve_num:
            raise ValidationError(f"この日の予約可能人数を超えています。（残り {self.shop.max_reserve_num - existing_total} 名まで）")
        

    class Meta:
        ordering = ['-date', '-time']


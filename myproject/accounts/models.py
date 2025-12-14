from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    # --- 定数を定義（ハードコードの排除） ---
    USER_TYPE_ADMIN = 'admin'
    USER_TYPE_EDITOR = 'shop_editor'
    USER_TYPE_FREE = 'free'
    USER_TYPE_PAID = 'paid'

    USER_TYPE_CHOICE = (
        (USER_TYPE_ADMIN, 'サイト管理者'),
        (USER_TYPE_EDITOR, '店舗編集ユーザー'),
        (USER_TYPE_FREE, '一般無料ユーザー'),
        (USER_TYPE_PAID, '一般有料ユーザー'),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICE,
        default=USER_TYPE_FREE,
    )

    # --- 判定メソッド ---
    def is_admin(self):
        return self.user_type == self.USER_TYPE_ADMIN

    def is_editor(self):
        return self.user_type == self.USER_TYPE_EDITOR

    def is_paid(self):
        return self.user_type == self.USER_TYPE_PAID
    # #stripeのID
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

# class CustomUser(AbstractUser):
#   USER_TYPE_CHOICE = (
#     ('admin', 'サイト管理者'),
#     ('shop_editor', '店舗編集ユーザー'),
#     ('free', '一般無料ユーザー'),
#     ('paid', '一般有料ユーザー'),
#   )

#   user_type = models.CharField(
#     max_length = 20,
#     choices=USER_TYPE_CHOICE,
#     default='free'
#   )

#   def is_admin(self):
#     return self.user_type == 'admin'

#   def is_editor(self):
#     return self.user_type == 'shop_editor'

#   def is_paid(self):
#     return self.user_type == 'paid'

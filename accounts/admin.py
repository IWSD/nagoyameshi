from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    CustomUser 用の管理画面設定
    """

    # 🔹 一覧画面に表示する項目
    list_display = (
        "username",
        "email",
        "user_type",
        "stripe_customer_id",
        "stripe_subscription_id",
        "is_staff",
        "is_active",
    )

    # 🔹 右側のフィルター
    list_filter = (
        "user_type",
        "is_staff",
        "is_active",
    )

    # 🔹 検索できる項目
    search_fields = (
        "username",
        "email",
        "stripe_customer_id",
        "stripe_subscription_id",
    )

    # 🔹 編集画面の項目構成
    fieldsets = UserAdmin.fieldsets + (
        (
            "Stripe 情報",
            {
                "fields": (
                    "user_type",
                    "stripe_customer_id",
                    "stripe_subscription_id",
                )
            },
        ),
    )


# class CustomUserAdmin(UserAdmin):
#   fieldsets = UserAdmin.fieldsets + (
#     (None, {'fields': ('user_type',)}),
#   )

#   list_display = ('username', 'email', 'user_type', 'is_staff', 'is_active','stripe_customer_id')

# admin.site.register(CustomUser, CustomUserAdmin)
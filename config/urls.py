from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views

from products.views import ProductViewSet
from suppliers.views import SupplierViewSet
from users.views import UserViewSet


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]


router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
urlpatterns += router.urls

from django.urls import path
from . import views
from .views import signup_view, login_view, logout_view, profile_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('profile/', profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    path('my-orders/', views.order_history_dashboard, name='order_history_dashboard'),
    path('my-orders/<str:order_type>/', views.order_history, name='order_history'),
   
    path('order-detail/product/<int:order_id>/', views.product_order_detail, name='product_order_detail'),
    path('order-detail/framing/<int:order_id>/', views.framing_order_detail, name='framing_order_detail'),
    path('order-detail/marbles/<int:order_id>/', views.marbles_order_detail, name='marbles_order_detail'),
]   
"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # <-- เพิ่ม include
from django.conf import settings # <-- เพิ่ม settings สำหรับ media files
from django.conf.urls.static import static # <-- เพิ่ม static สำหรับ media files

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),     # <-- เพิ่มบรรทัดนี้เพื่อเปิดใช้งาน django-browser-reload

    path('', include('core.urls')),                                 # <-- URL หลักของเว็บไซต์จะถูกจัดการโดยแอป core
    path('accounts/', include('accounts.urls')),                    # <-- URL ของ accounts จะเป็นหน้าจัดการสำหรับผู้ใช้
    path('stores/', include('stores.urls')),                        # <-- URL ของ stores จะเป็นหน้าจัดการสินค้า และร้านค้า
    path('framings/', include('framings.urls')),                    # <-- URL ของ framings จะเป็นหน้าสั่งเข้ากรอบรูป
    path('marbles/', include('marbles.urls')),                      # <-- URL ของ marbles จะเป็นหน้าสั่งทำป้ายแกะสลักหินอ่อน
    path('cart/', include('cart.urls')),                            # <-- URL ของ cart จะเป็นหน้าตะกร้าสินค้า
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # <-- เพิ่มบรรทัดนี้เพื่อให้ Django เสิร์ฟ media files ในโหมด DEBUG
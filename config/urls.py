from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

handler404 = 'main.views.error_404_view'
handler500 = 'main.views.error_500_view'
handler403 = 'main.views.error_403_view'
handler400 = 'main.views.error_400_view'

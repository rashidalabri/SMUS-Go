from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('spiritdashboard.urls'))
]

from django.conf import settings
from django.conf.urls.static import static

# This is discouraged, but we're using it for the sake of simplicity
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

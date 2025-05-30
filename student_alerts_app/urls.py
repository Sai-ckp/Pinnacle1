from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from master.views import dashboard_view


urlpatterns = [
    path('', dashboard_view, name='home'),
    path('admin/', admin.site.urls),
    path('master/', include('master.urls')),         # Previously '', now 'master/'
    path('admission/', include('admission.urls')),   # Previously '', now 'admission/'
    path('attendence/', include('attendence.urls')), # Previously '', now 'attendence/'
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

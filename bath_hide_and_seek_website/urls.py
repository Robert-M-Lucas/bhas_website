from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import backend.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('login.urls')),
    path('setup/', include('backend.urls'))
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path('', include('public.urls'))
]
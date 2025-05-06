#from django.contrib import admin
from django.urls import path, include
from attendance import views

urlpatterns = [
    #path('admin/', admin.site.urls),  
    path('', include('attendance.urls')),
    path('admin/', views.redirect_from_admin),  # instead of admin.site.urls

]

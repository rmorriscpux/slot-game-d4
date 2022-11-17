from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('game/', views.game_page),
    path('game/spin/', views.game_spin),
    path('user/', views.user_info),
    path('user/history/', views.show_history),
    path('user/add_credit/', views.add_credit),
    path('user/confirm_delete/', views.confirm_delete),
    path('user/destroy/', views.destroy_user),
    path('jackpots/', views.jackpot_list),
    path('jackpots/kudos/<int:jackpot_id>/', views.kudos),
    path('jackpots/undo_kudos/<int:jackpot_id>/', views.undo_kudos),
]

if settings.DEBUG:
    urlpatterns.append(path('test/', views.test_page))
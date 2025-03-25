# productivity_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('productivity_habits.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# productivity_habits/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productivity-questions/', views.productivity_questions, name='productivity_questions'),

    # Quarterly Quests
    path('quarterly-quests/', views.quarterly_quest_list, name='quarterly_quest_list'),
    path('quarterly-quests/create/', views.quarterly_quest_create, name='quarterly_quest_create'),
    path('quarterly-quests/<int:pk>/', views.quarterly_quest_detail, name='quarterly_quest_detail'),
    path('quarterly-quests/<int:pk>/update/', views.quarterly_quest_update, name='quarterly_quest_update'),
    path('quarterly-quests/<int:pk>/delete/', views.quarterly_quest_delete, name='quarterly_quest_delete'),

    # Weekly Reset
    path('weekly-reset/', views.weekly_reset_current, name='weekly_reset_current'),
    path('weekly-reset/history/', views.weekly_reset_history, name='weekly_reset_history'),

    # Morning Manifesto
    path('morning-manifesto/', views.morning_manifesto_today, name='morning_manifesto_today'),
    path('morning-manifesto/history/', views.morning_manifesto_history, name='morning_manifesto_history'),

    # Focus Sessions
    path('focus/start/', views.focus_session_start, name='focus_session_start'),
    path('focus/active/', views.focus_session_active, name='focus_session_active'),
    path('focus/manual/', views.focus_session_manual, name='focus_session_manual'),
    path('focus/history/', views.focus_session_history, name='focus_session_history'),

    # Social Events
    path('social-events/', views.social_event_list, name='social_event_list'),
    path('social-events/create/', views.social_event_create, name='social_event_create'),
    path('social-events/<int:pk>/', views.social_event_detail, name='social_event_detail'),
    path('social-events/<int:pk>/update/', views.social_event_update, name='social_event_update'),
    path('social-events/<int:pk>/toggle/', views.social_event_toggle, name='social_event_toggle'),
    path('social-events/<int:pk>/delete/', views.social_event_delete, name='social_event_delete'),
    path('invitees/<int:pk>/delete/', views.invitee_delete, name='invitee_delete'),

    # Voice Notes
    path('voice-notes/', views.voice_note_list, name='voice_note_list'),
    path('voice-notes/create/', views.voice_note_create, name='voice_note_create'),
    path('voice-notes/<int:pk>/', views.voice_note_detail, name='voice_note_detail'),
    path('voice-notes/<int:pk>/delete/', views.voice_note_delete, name='voice_note_delete'),
]
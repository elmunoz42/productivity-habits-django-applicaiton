# productivity_habits/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

class QuarterlyQuest(models.Model):
    """
    Model for tracking 90-day goals (Quarterly Quests)
    """
    CATEGORY_CHOICES = [
        ('work', _('Work')),
        ('life', _('Life')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('abandoned', _('Abandoned')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quarterly_quests')
    title = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    category = models.CharField(_("Category"), max_length=10, choices=CATEGORY_CHOICES, default='work')
    start_date = models.DateField(_("Start Date"), default=timezone.now)
    end_date = models.DateField(_("End Date"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default='active')
    progress = models.IntegerField(_("Progress (%)"), default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.end_date:
            # Set end date to 90 days from start date if not provided
            self.end_date = self.start_date + datetime.timedelta(days=90)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()}) - {self.get_status_display()}"

    def days_remaining(self):
        today = timezone.now().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = _("Quarterly Quest")
        verbose_name_plural = _("Quarterly Quests")


class WeeklyReset(models.Model):
    """
    Model for tracking weekly reviews/resets
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_resets')
    date = models.DateField(_("Date"), default=timezone.now)
    wins = models.TextField(_("Wins from Previous Week"), blank=True, 
                          help_text=_("List your wins from the previous week"))
    quest_notes = models.TextField(_("Quarterly Quest Check-in"), blank=True, 
                                help_text=_("Review progress on your quarterly quests"))
    priority_1 = models.CharField(_("Priority 1"), max_length=200, blank=True)
    priority_2 = models.CharField(_("Priority 2"), max_length=200, blank=True)
    priority_3 = models.CharField(_("Priority 3"), max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Weekly Reset - {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = _("Weekly Reset")
        verbose_name_plural = _("Weekly Resets")
        unique_together = ['user', 'date']


class MorningManifesto(models.Model):
    """
    Model for tracking daily morning manifestos
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='morning_manifestos')
    date = models.DateField(_("Date"), default=timezone.now)
    weekly_priorities_reviewed = models.BooleanField(_("Weekly Priorities Reviewed"), default=False)
    priority_notes = models.TextField(_("Weekly Priorities Notes"), blank=True)
    todays_adventure = models.CharField(_("Today's Adventure"), max_length=200, 
                                     help_text=_("What is the most important thing to accomplish today?"))
    notes = models.TextField(_("Additional Notes"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Morning Manifesto - {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = _("Morning Manifesto")
        verbose_name_plural = _("Morning Manifestos")
        unique_together = ['user', 'date']


class FocusSession(models.Model):
    """
    Model for tracking focused work sessions
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='focus_sessions')
    date = models.DateField(_("Date"), default=timezone.now)
    start_time = models.DateTimeField(_("Start Time"), default=timezone.now)
    end_time = models.DateTimeField(_("End Time"), null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(_("Duration (minutes)"), default=0)
    project = models.ForeignKey(QuarterlyQuest, on_delete=models.SET_NULL, 
                              related_name='focus_sessions', null=True, blank=True)
    description = models.CharField(_("Description"), max_length=200, blank=True)
    is_completed = models.BooleanField(_("Completed"), default=False)
    notes = models.TextField(_("Notes"), blank=True)
    
    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            # Calculate duration in minutes
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Focus Session - {self.date} ({self.duration_minutes} min)"
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = _("Focus Session")
        verbose_name_plural = _("Focus Sessions")


class SocialEvent(models.Model):
    """
    Model for tracking standing order social events
    """
    FREQUENCY_CHOICES = [
        ('weekly', _('Weekly')),
        ('biweekly', _('Biweekly')),
        ('monthly', _('Monthly')),
    ]
    
    DAY_CHOICES = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_events')
    title = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    location = models.CharField(_("Location"), max_length=200, blank=True)
    day_of_week = models.IntegerField(_("Day of Week"), choices=DAY_CHOICES)
    time = models.TimeField(_("Time"))
    frequency = models.CharField(_("Frequency"), max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    start_date = models.DateField(_("Start Date"), default=timezone.now)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_day_of_week_display()} at {self.time}"
    
    class Meta:
        ordering = ['day_of_week', 'time']
        verbose_name = _("Social Event")
        verbose_name_plural = _("Social Events")


class Invitee(models.Model):
    """
    Model for tracking invitees to social events
    """
    social_event = models.ForeignKey(SocialEvent, on_delete=models.CASCADE, related_name='invitees')
    name = models.CharField(_("Name"), max_length=100)
    email = models.EmailField(_("Email"), blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                           related_name='event_invitations', null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.social_event.title}"
    
    class Meta:
        unique_together = ['social_event', 'email']
        verbose_name = _("Invitee")
        verbose_name_plural = _("Invitees")


class VoiceNote(models.Model):
    """
    Model for voice notes (multimodality multitasking)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_notes')
    title = models.CharField(_("Title"), max_length=100, blank=True)
    date = models.DateField(_("Date"), default=timezone.now)
    audio_file = models.FileField(_("Audio File"), upload_to='voice_notes/%Y/%m/%d/')
    transcript = models.TextField(_("Transcript"), blank=True)
    related_quest = models.ForeignKey(QuarterlyQuest, on_delete=models.SET_NULL, 
                                    related_name='voice_notes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Voice Note - {self.date} - {self.title or 'Untitled'}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Voice Note")
        verbose_name_plural = _("Voice Notes")


# productivity_habits/admin.py
from django.contrib import admin
from .models import (
    QuarterlyQuest, 
    WeeklyReset, 
    MorningManifesto, 
    FocusSession, 
    SocialEvent, 
    Invitee, 
    VoiceNote
)

@admin.register(QuarterlyQuest)
class QuarterlyQuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'start_date', 'end_date', 'status', 'progress')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(WeeklyReset)
class WeeklyResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'priority_1')
    list_filter = ('date',)
    search_fields = ('priority_1', 'priority_2', 'priority_3', 'wins')
    date_hierarchy = 'date'

@admin.register(MorningManifesto)
class MorningManifestoAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'todays_adventure', 'weekly_priorities_reviewed')
    list_filter = ('date', 'weekly_priorities_reviewed')
    search_fields = ('todays_adventure', 'notes')
    date_hierarchy = 'date'

@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'duration_minutes', 'is_completed')
    list_filter = ('date', 'is_completed')
    search_fields = ('description', 'notes')
    date_hierarchy = 'date'

@admin.register(SocialEvent)
class SocialEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'day_of_week', 'time', 'frequency', 'is_active')
    list_filter = ('day_of_week', 'frequency', 'is_active')
    search_fields = ('title', 'description', 'location')

class InviteeInline(admin.TabularInline):
    model = Invitee
    extra = 1

@admin.register(Invitee)
class InviteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'social_event')
    list_filter = ('social_event',)
    search_fields = ('name', 'email')

@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'date', 'related_quest')
    list_filter = ('date',)
    search_fields = ('title', 'transcript')
    date_hierarchy = 'date'


# productivity_habits/apps.py
from django.apps import AppConfig

class ProductivityHabitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productivity_habits'
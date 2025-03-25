# productivity_habits/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    QuarterlyQuest,
    WeeklyReset,
    MorningManifesto,
    FocusSession,
    SocialEvent,
    Invitee,
    VoiceNote
)

class QuarterlyQuestForm(forms.ModelForm):
    """Form for creating and updating quarterly quests."""
    class Meta:
        model = QuarterlyQuest
        fields = ['title', 'description', 'category', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class QuarterlyQuestUpdateForm(forms.ModelForm):
    """Form for updating quarterly quest progress."""
    class Meta:
        model = QuarterlyQuest
        fields = ['progress', 'status']
        widgets = {
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

class WeeklyResetForm(forms.ModelForm):
    """Form for creating weekly resets."""
    class Meta:
        model = WeeklyReset
        fields = ['wins', 'quest_notes', 'priority_1', 'priority_2', 'priority_3']
        widgets = {
            'wins': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What went well this week?'}),
            'quest_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How are your quarterly quests progressing?'}),
            'priority_1': forms.TextInput(attrs={'placeholder': 'Your top priority for next week'}),
            'priority_2': forms.TextInput(attrs={'placeholder': 'Your second priority for next week'}),
            'priority_3': forms.TextInput(attrs={'placeholder': 'Your third priority for next week'}),
        }

class MorningManifestoForm(forms.ModelForm):
    """Form for creating daily morning manifestos."""
    class Meta:
        model = MorningManifesto
        fields = ['weekly_priorities_reviewed', 'priority_notes', 'todays_adventure', 'notes']
        widgets = {
            'priority_notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Notes about your weekly priorities'}),
            'todays_adventure': forms.TextInput(attrs={'placeholder': 'What is the MOST important thing to get done today?'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional thoughts for the day'}),
        }

class FocusSessionStartForm(forms.ModelForm):
    """Form for starting a focus session."""
    class Meta:
        model = FocusSession
        fields = ['project', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'What are you focusing on?'}),
        }

class FocusSessionEndForm(forms.ModelForm):
    """Form for ending a focus session."""
    class Meta:
        model = FocusSession
        fields = ['notes', 'is_completed']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any notes about this focus session?'}),
        }

class ManualFocusEntryForm(forms.ModelForm):
    """Form for manually entering a completed focus session."""
    duration = forms.IntegerField(min_value=1, label=_("Duration (minutes)"))
    
    class Meta:
        model = FocusSession
        fields = ['date', 'project', 'description', 'duration', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set start_time and end_time based on date and duration
        date = self.cleaned_data['date']
        duration = self.cleaned_data['duration']
        
        # Use noon as default time
        start_datetime = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time()) + timezone.timedelta(hours=12)
        )
        
        instance.start_time = start_datetime
        instance.end_time = start_datetime + timezone.timedelta(minutes=duration)
        instance.duration_minutes = duration
        instance.is_completed = True
        
        if commit:
            instance.save()
        return instance

class SocialEventForm(forms.ModelForm):
    """Form for creating and updating social events."""
    class Meta:
        model = SocialEvent
        fields = ['title', 'description', 'location', 'day_of_week', 'time', 'frequency', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InviteeForm(forms.ModelForm):
    """Form for adding invitees to a social event."""
    class Meta:
        model = Invitee
        fields = ['name', 'email']

class VoiceNoteForm(forms.ModelForm):
    """Form for uploading voice notes."""
    class Meta:
        model = VoiceNote
        fields = ['title', 'audio_file', 'related_quest']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Optional title for this voice note'}),
        }
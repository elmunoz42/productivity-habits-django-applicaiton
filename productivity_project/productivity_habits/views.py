# productivity_habits/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
import datetime

from .models import (
    QuarterlyQuest,
    WeeklyReset,
    MorningManifesto,
    FocusSession,
    SocialEvent,
    Invitee,
    VoiceNote
)
from .forms import (
    QuarterlyQuestForm,
    QuarterlyQuestUpdateForm,
    WeeklyResetForm,
    MorningManifestoForm,
    FocusSessionStartForm,
    FocusSessionEndForm,
    ManualFocusEntryForm,
    SocialEventForm,
    InviteeForm,
    VoiceNoteForm
)

@login_required
def dashboard(request):
    """Main dashboard view showing all productivity habits."""
    today = timezone.now().date()
    user = request.user
    
    # Quarterly Quests
    active_quests = QuarterlyQuest.objects.filter(
        user=user,
        status='active',
    ).order_by('end_date')
    
    # Weekly Reset
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    weekly_reset = WeeklyReset.objects.filter(
        user=user,
        date__gte=current_week_start,
        date__lte=current_week_end
    ).first()
    
    # Morning Manifesto
    todays_manifesto = MorningManifesto.objects.filter(
        user=user,
        date=today
    ).first()
    
    # Focus Sessions
    active_focus_session = FocusSession.objects.filter(
        user=user,
        is_completed=False,
        start_time__date=today
    ).first()
    
    recent_focus_sessions = FocusSession.objects.filter(
        user=user,
        is_completed=True
    ).order_by('-end_time')[:5]
    
    # Focus stats for the week
    week_focus_time = FocusSession.objects.filter(
        user=user,
        is_completed=True,
        date__gte=current_week_start,
        date__lte=current_week_end
    ).aggregate(total=Sum('duration_minutes'))['total'] or 0
    
    # Social Events
    upcoming_events = SocialEvent.objects.filter(
        user=user,
        is_active=True
    ).order_by('day_of_week', 'time')
    
    # Voice Notes
    recent_voice_notes = VoiceNote.objects.filter(
        user=user
    ).order_by('-created_at')[:3]
    
    context = {
        'active_quests': active_quests,
        'weekly_reset': weekly_reset,
        'todays_manifesto': todays_manifesto,
        'active_focus_session': active_focus_session,
        'recent_focus_sessions': recent_focus_sessions,
        'week_focus_time': week_focus_time,
        'upcoming_events': upcoming_events,
        'recent_voice_notes': recent_voice_notes,
        'today': today,
        'current_week_start': current_week_start,
        'current_week_end': current_week_end,
    }
    
    return render(request, 'productivity_habits/dashboard.html', context)

# Quarterly Quest Views
@login_required
def quarterly_quest_list(request):
    """View for listing all quarterly quests."""
    user = request.user
    
    active_quests = QuarterlyQuest.objects.filter(
        user=user, 
        status='active'
    ).order_by('end_date')
    
    completed_quests = QuarterlyQuest.objects.filter(
        user=user, 
        status='completed'
    ).order_by('-end_date')[:10]
    
    context = {
        'active_quests': active_quests,
        'completed_quests': completed_quests,
    }
    
    return render(request, 'productivity_habits/quarterly_quest/list.html', context)

@login_required
def quarterly_quest_create(request):
    """View for creating a new quarterly quest."""
    if request.method == 'POST':
        form = QuarterlyQuestForm(request.POST)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.user = request.user
            quest.save()
            messages.success(request, f'Quest "{quest.title}" created successfully.')
            return redirect('quarterly_quest_detail', pk=quest.pk)
    else:
        form = QuarterlyQuestForm()
    
    context = {
        'form': form,
        'title': 'Create New Quarterly Quest',
    }
    
    return render(request, 'productivity_habits/quarterly_quest/form.html', context)

@login_required
def quarterly_quest_detail(request, pk):
    """View for viewing a quarterly quest's details."""
    quest = get_object_or_404(QuarterlyQuest, pk=pk, user=request.user)
    
    # Get focus sessions for this quest
    focus_sessions = FocusSession.objects.filter(
        user=request.user,
        project=quest,
        is_completed=True
    ).order_by('-date')
    
    # Calculate total focus time
    total_focus_time = focus_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
    
    # Get related voice notes
    voice_notes = VoiceNote.objects.filter(
        user=request.user,
        related_quest=quest
    ).order_by('-created_at')
    
    context = {
        'quest': quest,
        'focus_sessions': focus_sessions,
        'total_focus_time': total_focus_time,
        'voice_notes': voice_notes,
        'update_form': QuarterlyQuestUpdateForm(instance=quest),
    }
    
    return render(request, 'productivity_habits/quarterly_quest/detail.html', context)

@login_required
def quarterly_quest_update(request, pk):
    """View for updating a quarterly quest."""
    quest = get_object_or_404(QuarterlyQuest, pk=pk, user=request.user)
    
    if request.method == 'POST':
        if 'update_progress' in request.POST:
            form = QuarterlyQuestUpdateForm(request.POST, instance=quest)
        else:
            form = QuarterlyQuestForm(request.POST, instance=quest)
            
        if form.is_valid():
            form.save()
            messages.success(request, f'Quest "{quest.title}" updated successfully.')
            return redirect('quarterly_quest_detail', pk=quest.pk)
    else:
        form = QuarterlyQuestForm(instance=quest)
    
    context = {
        'form': form,
        'quest': quest,
        'title': 'Update Quarterly Quest',
    }
    
    return render(request, 'productivity_habits/quarterly_quest/form.html', context)

@login_required
def quarterly_quest_delete(request, pk):
    """View for deleting a quarterly quest."""
    quest = get_object_or_404(QuarterlyQuest, pk=pk, user=request.user)
    
    if request.method == 'POST':
        title = quest.title
        quest.delete()
        messages.success(request, f'Quest "{title}" deleted successfully.')
        return redirect('quarterly_quest_list')
    
    context = {
        'quest': quest,
    }
    
    return render(request, 'productivity_habits/quarterly_quest/confirm_delete.html', context)

# Weekly Reset Views
@login_required
def weekly_reset_current(request):
    """View for creating or updating the current weekly reset."""
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    user = request.user
    
    # Try to get an existing reset for the current week
    weekly_reset = WeeklyReset.objects.filter(
        user=user,
        date__gte=current_week_start,
        date__lte=current_week_start + timedelta(days=6)
    ).first()
    
    # Get active quests for the form context
    active_quests = QuarterlyQuest.objects.filter(
        user=user,
        status='active'
    ).order_by('category', 'end_date')
    
    if request.method == 'POST':
        if weekly_reset:
            form = WeeklyResetForm(request.POST, instance=weekly_reset)
        else:
            form = WeeklyResetForm(request.POST)
            
        if form.is_valid():
            reset = form.save(commit=False)
            if not weekly_reset:
                reset.user = user
                reset.date = current_week_start
            reset.save()
            messages.success(request, 'Weekly reset completed successfully.')
            return redirect('dashboard')
    else:
        form = WeeklyResetForm(instance=weekly_reset)
    
    context = {
        'form': form,
        'active_quests': active_quests,
        'today': today,
        'current_week_start': current_week_start,
        'current_week_end': current_week_start + timedelta(days=6),
        'weekly_reset': weekly_reset,
    }
    
    return render(request, 'productivity_habits/weekly_reset/form.html', context)

@login_required
def weekly_reset_history(request):
    """View for listing all weekly resets."""
    resets = WeeklyReset.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'resets': resets,
    }
    
    return render(request, 'productivity_habits/weekly_reset/history.html', context)

# Morning Manifesto Views
@login_required
def morning_manifesto_today(request):
    """View for creating or updating today's morning manifesto."""
    today = timezone.now().date()
    user = request.user
    
    # Try to get an existing manifesto for today
    manifesto = MorningManifesto.objects.filter(
        user=user,
        date=today
    ).first()
    
    # Get the current weekly priorities
    current_week_start = today - timedelta(days=today.weekday())
    weekly_reset = WeeklyReset.objects.filter(
        user=user,
        date__gte=current_week_start,
        date__lte=current_week_start + timedelta(days=6)
    ).first()
    
    if request.method == 'POST':
        if manifesto:
            form = MorningManifestoForm(request.POST, instance=manifesto)
        else:
            form = MorningManifestoForm(request.POST)
            
        if form.is_valid():
            new_manifesto = form.save(commit=False)
            if not manifesto:
                new_manifesto.user = user
                new_manifesto.date = today
            new_manifesto.save()
            messages.success(request, "Today's adventure is set. Have a productive day!")
            return redirect('dashboard')
    else:
        form = MorningManifestoForm(instance=manifesto)
    
    context = {
        'form': form,
        'today': today,
        'weekly_reset': weekly_reset,
        'manifesto': manifesto,
    }
    
    return render(request, 'productivity_habits/morning_manifesto/form.html', context)

@login_required
def morning_manifesto_history(request):
    """View for listing all morning manifestos."""
    manifestos = MorningManifesto.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'manifestos': manifestos,
    }
    
    return render(request, 'productivity_habits/morning_manifesto/history.html', context)

# Focus Log Views
@login_required
def focus_session_start(request):
    """View for starting a new focus session."""
    user = request.user
    today = timezone.now().date()
    
    # Check if there's already an active session
    active_session = FocusSession.objects.filter(
        user=user,
        is_completed=False,
        start_time__date=today
    ).first()
    
    if active_session:
        messages.warning(request, "You already have an active focus session.")
        return redirect('focus_session_active')
    
    if request.method == 'POST':
        form = FocusSessionStartForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = user
            session.start_time = timezone.now()
            session.date = today
            session.save()
            messages.success(request, "Focus session started. The timer is running!")
            return redirect('focus_session_active')
    else:
        form = FocusSessionStartForm()
    
    # Get active quests for project selection
    active_quests = QuarterlyQuest.objects.filter(
        user=user,
        status='active'
    ).order_by('title')
    
    context = {
        'form': form,
        'active_quests': active_quests,
    }
    
    return render(request, 'productivity_habits/focus_session/start.html', context)

@login_required
def focus_session_active(request):
    """View for the currently active focus session."""
    user = request.user
    today = timezone.now().date()
    
    active_session = FocusSession.objects.filter(
        user=user,
        is_completed=False,
        start_time__date=today
    ).first()
    
    if not active_session:
        messages.warning(request, "You don't have an active focus session.")
        return redirect('focus_session_start')
    
    if request.method == 'POST':
        form = FocusSessionEndForm(request.POST, instance=active_session)
        if form.is_valid():
            session = form.save(commit=False)
            session.end_time = timezone.now()
            session.is_completed = True
            session.save()
            
            duration_minutes = session.duration_minutes
            messages.success(
                request, 
                f"Focus session completed! You focused for {duration_minutes} minutes."
            )
            return redirect('dashboard')
    else:
        form = FocusSessionEndForm(instance=active_session)
    
    # Calculate elapsed time
    elapsed_time = timezone.now() - active_session.start_time
    elapsed_minutes = int(elapsed_time.total_seconds() / 60)
    
    context = {
        'form': form,
        'active_session': active_session,
        'elapsed_minutes': elapsed_minutes,
    }
    
    return render(request, 'productivity_habits/focus_session/active.html', context)

@login_required
def focus_session_manual(request):
    """View for manually entering a focus session."""
    if request.method == 'POST':
        form = ManualFocusEntryForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            messages.success(
                request, 
                f"Focus session added: {session.duration_minutes} minutes on {session.date}."
            )
            return redirect('focus_session_history')
    else:
        # Default to today's date
        form = ManualFocusEntryForm(initial={'date': timezone.now().date()})
    
    # Get active quests for project selection
    active_quests = QuarterlyQuest.objects.filter(
        user=request.user,
        status='active'
    ).order_by('title')
    
    context = {
        'form': form,
        'active_quests': active_quests,
    }
    
    return render(request, 'productivity_habits/focus_session/manual.html', context)

@login_required
def focus_session_history(request):
    """View for showing focus session history."""
    # Get date range filter from request parameters
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    
    today = timezone.now().date()
    
    # Default to last 7 days if no dates specified
    if not from_date_str:
        from_date = today - timedelta(days=6)
    else:
        try:
            from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
        except ValueError:
            from_date = today - timedelta(days=6)
    
    if not to_date_str:
        to_date = today
    else:
        try:
            to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            to_date = today
    
    # Get all sessions in the date range
    sessions = FocusSession.objects.filter(
        user=request.user,
        date__gte=from_date,
        date__lte=to_date,
        is_completed=True
    ).order_by('-date', '-start_time')
    
    # Calculate statistics
    total_time = sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
    daily_avg = total_time / 7 if total_time > 0 else 0
    
    # Group by date for the chart data
    date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]
    chart_data = []
    
    for date in date_range:
        day_sessions = sessions.filter(date=date)
        day_total = day_sessions.aggregate(total=Sum('duration_minutes'))['total'] or 0
        chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'minutes': day_total
        })
    
    context = {
        'sessions': sessions,
        'from_date': from_date,
        'to_date': to_date,
        'total_time': total_time,
        'daily_avg': daily_avg,
        'chart_data': chart_data,
    }
    
    return render(request, 'productivity_habits/focus_session/history.html', context)

# Social Event Views
@login_required
def social_event_list(request):
    """View for listing social events."""
    active_events = SocialEvent.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('day_of_week', 'time')
    
    inactive_events = SocialEvent.objects.filter(
        user=request.user,
        is_active=False
    ).order_by('-updated_at')
    
    context = {
        'active_events': active_events,
        'inactive_events': inactive_events,
    }
    
    return render(request, 'productivity_habits/social_event/list.html', context)

@login_required
def social_event_create(request):
    """View for creating a new social event."""
    if request.method == 'POST':
        form = SocialEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, f'Event "{event.title}" created successfully.')
            return redirect('social_event_detail', pk=event.pk)
    else:
        form = SocialEventForm()
    
    context = {
        'form': form,
        'title': 'Create New Standing Order Social Event',
    }
    
    return render(request, 'productivity_habits/social_event/form.html', context)

@login_required
def social_event_detail(request, pk):
    """View for viewing a social event's details."""
    event = get_object_or_404(SocialEvent, pk=pk, user=request.user)
    invitees = Invitee.objects.filter(social_event=event).order_by('name')
    
    # Handle adding a new invitee
    if request.method == 'POST':
        invitee_form = InviteeForm(request.POST)
        if invitee_form.is_valid():
            invitee = invitee_form.save(commit=False)
            invitee.social_event = event
            invitee.save()
            messages.success(request, f'{invitee.name} added to invitees.')
            return redirect('social_event_detail', pk=event.pk)
    else:
        invitee_form = InviteeForm()
    
    context = {
        'event': event,
        'invitees': invitees,
        'invitee_form': invitee_form,
    }
    
    return render(request, 'productivity_habits/social_event/detail.html', context)

@login_required
def social_event_update(request, pk):
    """View for updating a social event."""
    event = get_object_or_404(SocialEvent, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = SocialEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully.')
            return redirect('social_event_detail', pk=event.pk)
    else:
        form = SocialEventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': 'Update Social Event',
    }
    
    return render(request, 'productivity_habits/social_event/form.html', context)

@login_required
def social_event_toggle(request, pk):
    """View for toggling a social event's active status."""
    event = get_object_or_404(SocialEvent, pk=pk, user=request.user)
    
    event.is_active = not event.is_active
    event.save()
    
    status = "activated" if event.is_active else "deactivated"
    messages.success(request, f'Event "{event.title}" {status} successfully.')
    return redirect('social_event_list')

@login_required
def social_event_delete(request, pk):
    """View for deleting a social event."""
    event = get_object_or_404(SocialEvent, pk=pk, user=request.user)
    
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted successfully.')
        return redirect('social_event_list')
    
    context = {
        'event': event,
    }
    
    return render(request, 'productivity_habits/social_event/confirm_delete.html', context)

@login_required
def invitee_delete(request, pk):
    """View for removing an invitee from a social event."""
    invitee = get_object_or_404(Invitee, pk=pk)
    event = invitee.social_event
    
    # Check if the event belongs to the current user
    if event.user != request.user:
        messages.error(request, "You don't have permission to remove this invitee.")
        return redirect('social_event_list')
    
    if request.method == 'POST':
        name = invitee.name
        invitee.delete()
        messages.success(request, f'{name} removed from invitees.')
        return redirect('social_event_detail', pk=event.pk)
    
    context = {
        'invitee': invitee,
        'event': event,
    }
    
    return render(request, 'productivity_habits/social_event/invitee_confirm_delete.html', context)

# Voice Note Views
@login_required
def voice_note_list(request):
    """View for listing voice notes."""
    voice_notes = VoiceNote.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    context = {
        'voice_notes': voice_notes,
    }
    
    return render(request, 'productivity_habits/voice_note/list.html', context)

@login_required
def voice_note_create(request):
    """View for creating a new voice note."""
    if request.method == 'POST':
        form = VoiceNoteForm(request.POST, request.FILES)
        if form.is_valid():
            voice_note = form.save(commit=False)
            voice_note.user = request.user
            voice_note.date = timezone.now().date()
            voice_note.save()
            messages.success(request, 'Voice note uploaded successfully.')
            return redirect('voice_note_detail', pk=voice_note.pk)
    else:
        form = VoiceNoteForm()
    
    # Get active quests for related_quest selection
    active_quests = QuarterlyQuest.objects.filter(
        user=request.user,
        status='active'
    ).order_by('title')
    
    context = {
        'form': form,
        'active_quests': active_quests,
    }
    
    return render(request, 'productivity_habits/voice_note/form.html', context)

@login_required
def voice_note_detail(request, pk):
    """View for viewing a voice note's details."""
    voice_note = get_object_or_404(VoiceNote, pk=pk, user=request.user)
    
    context = {
        'voice_note': voice_note,
    }
    
    return render(request, 'productivity_habits/voice_note/detail.html', context)

@login_required
def voice_note_delete(request, pk):
    """View for deleting a voice note."""
    voice_note = get_object_or_404(VoiceNote, pk=pk, user=request.user)
    
    if request.method == 'POST':
        voice_note.delete()
        messages.success(request, 'Voice note deleted successfully.')
        return redirect('voice_note_list')
    
    context = {
        'voice_note': voice_note,
    }
    
    return render(request, 'productivity_habits/voice_note/confirm_delete.html', context)

# Simple Views
def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'productivity_habits/home.html')

def about(request):
    """About page view."""
    return render(request, 'productivity_habits/about.html')

def productivity_questions(request):
    """View with guidance questions for each productivity level."""
    return render(request, 'productivity_habits/productivity_questions.html')
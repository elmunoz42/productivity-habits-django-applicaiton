# Productivity Habits Django Application

## Overview
A Django application that helps users implement the 6 key productivity 
habits from Ali Abdaal's framework to make 2025 their best year ever. The 
application will guide users through quarterly, monthly, weekly, and daily 
reflection questions and tracking.

## Core Features

### 1. User Authentication
- User registration, login, and profile management
- Secure authentication system
- User profile with customizable settings

### 2. Quarterly Quests
- Create 3-4 goals for the next 90 days
- Separate work and life categories
- Progress tracking over time
- Begin at any time (not tied to calendar quarters)
- Notifications for quarterly reviews
- Templates for breaking down larger projects into 90-day chunks

### 3. Weekly Reset
- 20-minute guided review process
- Calendar review interface
- Win celebration section
- Quarterly quest progress check-in
- Top 1-3 priorities setting for upcoming week
- Weekly review reminders

### 4. Morning Manifesto
- 2-minute daily journaling prompt
- Reminder of weekly priorities
- "Today's adventure" setting (most important task)
- Mobile-friendly interface for morning check-ins
- Option to schedule reminders

### 5. Focus Log
- Time tracking for focused work
- Manual or automatic tracking options
- Visual metrics and trends
- Project-based focus tracking
- Daily/weekly/monthly reports

### 6. Standing Order Social Events
- Calendar for recurring social events
- Invitation management system
- Attendance tracking
- Reminder system
- Integration with calendar apps

### 7. Multimodality Multitasking
- Voice note capturing (simple version without AI processing initially)
- Task categorization by modality
- Suggestions for pairing compatible activities
- Resource library of multitasking ideas

## Database Models

### User
- Standard Django User model
- Extended profile information

### QuarterlyQuest
- Title
- Description
- Category (work/life)
- Start date
- End date (90 days from start)
- Status (active, completed, abandoned)
- Progress metric
- User (foreign key)

### WeeklyReset
- Date
- Wins from previous week (text array)
- Quarterly quest check-in notes
- Top priorities for upcoming week (1-3)
- User (foreign key)

### MorningManifesto
- Date
- Weekly priorities review (boolean)
- Today's adventure (main task)
- Notes
- User (foreign key)

### FocusLog
- Date
- Project (foreign key to QuarterlyQuest)
- Minutes focused
- Notes
- User (foreign key)

### SocialEvent
- Title
- Description
- Location
- Day of week
- Time
- Frequency (weekly, biweekly)
- Invitees (M2M to Users or email addresses)
- User (foreign key)

### VoiceNote
- Date
- Audio file
- Transcript (text field)
- Associated task (optional FK)
- User (foreign key)

## Views and Templates

### Dashboard
- Overview of all habits
- Quick access to daily and weekly inputs
- Progress metrics for quarterly quests
- Upcoming social events
- Recent focus log summary

### Quarterly Quest View
- Create/edit quarterly quests
- Progress visualization
- Breakdown into weekly milestones

### Weekly Reset View
- Guided weekly review process
- Calendar integration
- Prior week review
- Next week planning

### Daily View
- Morning manifesto input
- Focus log tracking
- Daily summary

### Social Calendar View
- Standing order events management
- Invitations interface
- Attendance tracking

### Reports View
- Focus metrics over time
- Quest completion rates
- Habit consistency tracking

## Technical Requirements

### Backend
- Django 4.2+
- PostgreSQL database
- RESTful API for potential mobile app integration
- Celery for background tasks (reminders)

### Frontend
- Django templates with Bootstrap 5
- JavaScript for interactive elements
- Chart.js for visualizations
- Mobile-responsive design

### Deployment
- Docker containerization
- Nginx and Gunicorn
- Cloud hosting options (AWS, DigitalOcean, etc.)

## Future Integration Points for Claude AI

- Analysis of quarterly quest patterns
- Suggestions based on weekly reset data
- Focus log insights and recommendations
- Voice notes processing
- Personalized productivity recommendations

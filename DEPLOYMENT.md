# Deployment checklist

## Roll-out part

Here is a simple deployment checklist:

2. Remove debug from environment variables
5. Install postgresql
2. Install redis
1. Install and launch managed instance of Celery
2. Change `MAIL_ASYNC` to True
3. Configure real mailgun API tokens
2. Create appropriate user logins for all the staff
5. Set server timezone to UTC


## Whet to test

1. Emails should be sent asynchronously (try to schedule a lesson and check Celery stats)
1. Emails should be send via mailgun
3. Async 'class start soon' notifications
2. User's timezone should be automatically guessed and applied. Lesson, planned to 08:00 should be displayed at 08:00 and stored as 05:00

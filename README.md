# Work Permit Django Project

## Features
- Authentication-protected portal.
- User dashboard for creating work-permit requests.
- Admin review panel for approve/reject workflow.
- Government ID submission enabled only after approval.
- Government ID types: Adhaar Card, Voter ID Card, Driver's License, Passport, Ration Card.
- ID photo via webcam capture or file upload.
- Black/green responsive UI.
- Country-code selector with flags and phone validation.

## Run
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`
5. `python manage.py runserver`

## URLs
- `/login/` login
- `/` user dashboard
- `/admin-panel/` custom admin review panel (staff only)
- `/django-admin/` Django admin

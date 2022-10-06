# EBS-Milestone (2-4)

## About project
EBS-Milestones shows the power and possibilities of REST API with close 
relation to Django. 

You can use this project as a cheat sheet.


## Used technologies

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Swagger](https://swagger.io/docs/specification/2-0/what-is-swagger/)
- [Docker](https://docs.docker.com/samples/django/)

## Installation
1. Clone project `git clone https://github.com/Cadi7/EBS-Milestone2.git`
2. Install requirements `pip install -r requirements.txt`
3. Apply migrations to database `python manage.py migrate`
4. Start the project `python manage.py runserver`

## Endpoints:
### Users:
1. User access token `POST | users/login/`
2. User refresh token `POST | users/refresh/`
3. User list `GET | users/`
4. User register `POST | users/register/`
### Tasks:
1. Task list `GET | tasks/`
2. Create task `POST | tasks/`
3. All completed tasks `GET | tasks/completed-tasks/`
4. My own tasks `GET | tasks/my-tasks/`
6. Task detail `GET | tasks/{id}/`
7. Delete task `DELETE | tasks/{id}/`
8. Assign new user to task `PATCH | tasks/{id}/assign/`
10. Update task status to true `GET | tasks/{id}/complete/`
### Comments:
1. Comment detail `GET | tasks/{task__pk}/comments`
2. Create comment `POST | tasks/{task__pk}/comments`
### TimeLogs:
1. Timelogs list `GET | timelogs/`
2. Timelog task detail `GET | tasks/{task__pk}/timelogs/`
3. Create task timelog `POST | tasks/{task__pk}/timelogs/`
4. Timelog start timer `POST | tasks/{task__pk}/timelogs/start/`
5. Timelog stop timer `POST | tasks/{task__pk}/timelogs/stop/`
6. Logged time in last month `GET | timelogs/month/`
7. Summary of timelogs for one task |GET | tasks/{task_pk}/timelogs/summary`
8. Top 20 tasks in last month `GET | timelogs/top-20/`

  

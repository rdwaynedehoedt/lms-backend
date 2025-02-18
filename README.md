# LMS Backend Setup Guide

## 1. Set Up Your Python Environment
First, make sure you have Python installed on your machine.

### Download and Install Python
You can download Python from [python.org](https://python.org).

### Install virtualenv (for creating an isolated environment):
```bash
pip install virtualenv
```

## 2. Create a Virtual Environment
Creating a virtual environment helps isolate your project dependencies:

```bash
# Navigate to your project folder
mkdir lms-backend
cd lms-backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## 3. Install Django
Once your virtual environment is activated, install Django:

```bash
pip install django
```

## 4. Create a New Django Project
Now, create a new Django project. For this example, we'll call it `lms`:

```bash
django-admin startproject lms .
```

## 5. Set Up the Database
You’ll likely want to use PostgreSQL for your database, but Django also supports SQLite by default, which is fine for testing. To use PostgreSQL:

### Install the PostgreSQL package:
```bash
pip install psycopg2
```

In your `settings.py`, update the `DATABASES` configuration to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lms_db',  # Name of your database
        'USER': 'your_username',  # Your PostgreSQL username
        'PASSWORD': 'your_password',  # Your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Create the database in PostgreSQL:
```bash
psql
CREATE DATABASE lms_db;
```

## 6. Create a Django App for Authentication
Now, let’s create an app to handle user authentication (students, teachers, admins).

### Create the app:
```bash
python manage.py startapp accounts
```

In the `settings.py`, add your new app to the `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    ...
    'accounts',
]
```

## 7. Set Up User Authentication in Django
You can use Django's built-in authentication system, but let's also create custom user roles (student, teacher, admin).

### Create a Custom User Model (Optional)
Django's default User model might be enough for basic authentication, but if you need custom fields (like roles), you can create a custom user model.

In your `accounts/models.py`, create a custom user model:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.username
```

In `settings.py`, tell Django to use your custom user model:

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

Run the migrations to create your user table:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 8. Create Views and Serializers for Authentication
For handling authentication (e.g., registration, login), we will use Django REST Framework (DRF) to expose APIs.

### Install DRF:
```bash
pip install djangorestframework
```

Add `rest_framework` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
]
```

Create a `serializers.py` in the `accounts` app for user registration:

```python
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
```

In your `views.py`, add a view for user registration:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Add URL routing in `accounts/urls.py`:

```python
from django.urls import path
from .views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]
```

Include accounts URLs in the main `lms/urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('api/accounts/', include('accounts.urls')),
    ...
]
```

## 9. Test the API
Run the Django server:

```bash
python manage.py runserver
```

Now, you can test the registration API by sending a POST request to `/api/accounts/register/` with the user's details (e.g., username, email, password, role).

## 10. Connect Django Backend to React Frontend
Once the backend is set up, you can connect your React frontend to the Django backend by making API calls using axios or fetch.

For example, to register a user from the React frontend:

```javascript
import axios from 'axios';

const registerUser = async (userData) => {
    try {
        const response = await axios.post('http://localhost:8000/api/accounts/register/', userData);
        console.log(response.data); // Successful registration
    } catch (error) {
        console.error(error); // Handle error
    }
};
```

## 11. Next Steps:
- Implement more authentication features (login, JWT tokens).
- Add course models, lesson management, and role-based access.
- Set up permissions and authentication tokens (JWT, for example) to secure your APIs.

## Conclusion
You now have a basic Django setup for your LMS backend with user registration. From here, you can expand it with features like course management, quizzes, role-based permissions, and more.

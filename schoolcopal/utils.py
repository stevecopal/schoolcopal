# utils.py
from django.contrib.auth import get_user_model

User = get_user_model()

def create_user_with_password(username, email, role, raw_password):
    user = User(username=username, email=email, role=role)
    user.set_password(raw_password)
    user._raw_password = raw_password
    user.save()
    return user

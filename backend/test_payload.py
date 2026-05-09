import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from accounts.serializers import UserSerializer
from accounts.models import User
from django.test import RequestFactory

user = User.objects.get(email='mateo.romero.contreras@gmail.com')

payload = {
    "age": 30,
    "weight": 80.5,
    "height": 1.80,
    "goal": "STRENGTH",
    "level": "ADVANCED",
    "training_weekdays": [1, 3, 5]
}

print("Original:", user.age, user.weight, user.height, user.goal, user.level)
serializer = UserSerializer(user, data=payload, partial=True)
print("Is valid:", serializer.is_valid())
if not serializer.is_valid():
    print(serializer.errors)
else:
    serializer.save()
    print("Updated:", user.age, user.weight, user.height, user.goal, user.level)

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from accounts.serializers import UserSerializer
from accounts.models import User

# Get the first user
user = User.objects.first()
if not user:
    print("No user found")
else:
    print("Current user goal:", user.goal, "level:", user.level)
    data = {
        "goal": "STRENGTH",
        "level": "ADVANCED"
    }
    serializer = UserSerializer(user, data=data, partial=True)
    print("Is valid:", serializer.is_valid())
    if not serializer.is_valid():
        print(serializer.errors)
    else:
        serializer.save()
        print("Updated user goal:", user.goal, "level:", user.level)

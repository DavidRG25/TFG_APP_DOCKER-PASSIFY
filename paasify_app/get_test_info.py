
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_passify.settings')
django.setup()

from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject
from django.contrib.auth.models import User
from paasify.models.TokenModel import ExpiringToken

def get_test_data():
    user = User.objects.get(username='alumno')
    token, _ = ExpiringToken.objects.get_or_create(user=user)
    
    subject = Subject.objects.filter(students=user).first()
    project = UserProject.objects.filter(user_profile__user=user).first()
    
    print(f"TOKEN={token.key}")
    if subject:
        print(f"SUBJECT_ID={subject.id}")
    if project:
        print(f"PROJECT_ID={project.id}")

if __name__ == "__main__":
    get_test_data()

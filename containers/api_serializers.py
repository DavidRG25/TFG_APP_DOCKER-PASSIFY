
from rest_framework import serializers
from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "category", "genero")


class ProjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    
    class Meta:
        model = UserProject
        fields = ("id", "place", "subject", "subject_name", "date")

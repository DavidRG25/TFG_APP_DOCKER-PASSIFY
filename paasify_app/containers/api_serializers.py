from rest_framework import serializers
from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject

class SubjectSerializer(serializers.ModelSerializer):
    year = serializers.CharField(source="genero")
    class Meta:
        model = Subject
        fields = ("id", "name", "category", "year")


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="place")
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    
    class Meta:
        model = UserProject
        fields = ("id", "name", "subject", "subject_name", "date")

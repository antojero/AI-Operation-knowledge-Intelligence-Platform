from rest_framework import serializers
from .models import AgentRun, RunStep

class RunStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunStep
        fields = '__all__'

class AgentRunSerializer(serializers.ModelSerializer):
    steps = RunStepSerializer(many=True, read_only=True)

    class Meta:
        model = AgentRun
        fields = '__all__'

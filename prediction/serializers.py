from rest_framework import serializers
from .models import predictions, schueler, sitzungssummary, gast, xmlsaetze, saetze


class PredictionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = predictions
        fields = "__all__"


class XmlsaetzeSerializer(serializers.ModelSerializer):
    class Meta:
        model = xmlsaetze
        fields = "__all__"


class SchuelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = schueler
        fields = "__all__"


class SitzungssummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = sitzungssummary
        fields = "__all__"


class GastSerializer(serializers.ModelSerializer):
    class Meta:
        model = gast
        fields = "__all__"


class SaetzeSerializer(serializers.ModelSerializer):
    class Meta:
        model = saetze
        fields = "__all__"

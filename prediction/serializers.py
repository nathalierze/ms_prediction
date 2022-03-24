from rest_framework import serializers

from .models import schueler, sitzungssummary, gast, xmlsaetze

class XmlsaetzeSerializer(serializers.ModelSerializer):
    class Meta:
        model = xmlsaetze
        fields = '__all__'


class SchuelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = schueler
        fields = '__all__'

class SitzungssummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = sitzungssummary
        fields = '__all__'

class GastSerializer(serializers.ModelSerializer):
    class Meta:
        model = gast
        fields = '__all__'


from rest_framework import serializers

from .models import schueler, sitzungssummary, gast, xmlsaetze

# class xmlsaetzeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = xmlsaetze
#         fields = '__all__'


class schuelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = schueler
        fields = '__all__'

class sitzungssummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = sitzungssummary
        fields = '__all__'

class gastSerializer(serializers.ModelSerializer):
    class Meta:
        model = gast
        fields = '__all__'


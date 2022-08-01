from copyreg import pickle
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, permissions, authentication
from rest_framework.response import Response
from .models import predictions, schueler, sitzungssummary, gast
from .serializers import SchuelerSerializer, SitzungssummarySerializer
import random
from rest_framework import generics
from .calculate_prediction import sendHistoricAndPrediction
from .get_next_sentence import next_sentence
from rest_framework.permissions import IsAuthenticated
from prediction_service.authentication import TokenAuthentication
from django.core.exceptions import PermissionDenied

"""
API endpoint Intervention 6 and 5
"""
class SchuelerViewSet(viewsets.ModelViewSet):
    queryset = schueler.objects.all()
    serializer_class = SchuelerSerializer
    authentication_classes = [authentication.SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_next_sentence(self, request, pk):        
        next = next_sentence(request.data)
        return Response(next)

"""
API endpoint Intervention 2 to 4
"""
class SitzungssummaryViewSet(viewsets.ModelViewSet):
    queryset = sitzungssummary.objects.all()
    serializer_class = SchuelerSerializer
    authentication_classes = [authentication.SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_prediction(self, request, pk):
        try:
            #auth = schueler.objects.get(Loginname = request.headers['Username'])
            prediction = sendHistoricAndPrediction(request.data)

            return Response(prediction)
        except schueler.DoesNotExist:
            raise PermissionDenied() 
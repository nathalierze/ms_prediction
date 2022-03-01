from copyreg import pickle
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import schueler, sitzungssummary, gast
from .serializers import schuelerSerializer, sitzungssummarySerializer
import random
from rest_framework import generics
from .calculatePrediction import featureEngineering

class SchuelerViewSet(viewsets.ModelViewSet):
    """
    API endpoint
    """
    queryset = schueler.objects.all()
    serializer_class = schuelerSerializer

    def list(self, request):
        schuelers = schueler.objects.all()
        print(schuelers.last)
        serializer = schuelerSerializer(schuelers, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = schuelerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        schuelers = schueler.objects.get(ID=pk)
        serializer = schuelerSerializer(schuelers)
        return Response(serializer.data)

    def update(self, request, pk=None):
        schuelers = schueler.objects.get(ID=pk)
        serializer = schuelerSerializer(instance=schuelers, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class SitzungssummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint
    """
    queryset = sitzungssummary.objects.all()
    serializer_class = schuelerSerializer

    def list(self, request):
        sitzungssummaries = sitzungssummary.objects.all()
        print(sitzungssummaries.last)
        serializer = sitzungssummarySerializer(sitzungssummaries, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = sitzungssummarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        sitzungssummaries = sitzungssummary.objects.get(ID=pk)
        serializer = sitzungssummarySerializer(sitzungssummaries)
        return Response(serializer.data)

    def getPrediction(self, request, pk):
        print(pk)
        prediction = featureEngineering(request.data)
        #prediction = 0.88

        return Response(prediction)
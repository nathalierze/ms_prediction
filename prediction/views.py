from copyreg import pickle
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import schueler, sitzungssummary, gast
from .serializers import SchuelerSerializer, SitzungssummarySerializer
import random
from rest_framework import generics
from .calculate_prediction import predict

class SchuelerViewSet(viewsets.ModelViewSet):
    """
    API endpoint
    """
    queryset = schueler.objects.all()
    serializer_class = SchuelerSerializer

    def list(self, request):
        schuelers = schueler.objects.all()
        print(schuelers.last)
        serializer = SchuelerSerializer(schuelers, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = SchuelerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        schuelers = schueler.objects.get(ID=pk)
        serializer = SchuelerSerializer(schuelers)
        return Response(serializer.data)

    def get_next_sentence():
        return 0

    # def update(self, request, pk=None):
    #     schuelers = schueler.objects.get(ID=pk)
    #     serializer = SchuelerSerializer(instance=schuelers, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class SitzungssummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint
    """
    queryset = sitzungssummary.objects.all()
    serializer_class = SchuelerSerializer

    def list(self, request):
        sitzungssummaries = sitzungssummary.objects.all()
        print(sitzungssummaries.last)
        serializer = SitzungssummarySerializer(sitzungssummaries, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = SitzungssummarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        sitzungssummaries = sitzungssummary.objects.get(ID=pk)
        serializer = SitzungssummarySerializer(sitzungssummaries)
        return Response(serializer.data)

    def getPrediction(self, request, pk):
        print(pk)
        prediction = predict(request.data)

        return Response(prediction)
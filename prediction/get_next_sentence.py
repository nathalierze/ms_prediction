from .models import schueler, xmlsaetze, saetze
import pandas as pd
import pickle
import datetime
from .serializers import SchuelerSerializer, XmlsaetzeSerializer
from rest_framework.renderers import JSONRenderer
from django.core import serializers
from .calculate_prediction import predict
import json

def next_sentence(data):

    aufgaben_id = data['AufgabenID']
    geloeste_saetze = data['geloesteSaetze']
    versionline = data['versionline']

    #checken, welche Satz IDs predicted werden müssen
    satz_ids, choosing_strategy = get_satz_ids(aufgaben_id, geloeste_saetze, versionline)

    # predictions = [[],[]]
    # for x in satz_ids:
    #     full_data = accumulate_satz_id(data, x)
    #     p = predict(full_data)
    #     predictions = predictions.append([x,p])
    
    # next_sentence_id = choose_next_sentence(predictions, choosing_strategy)

    # return next_sentence_id
    return 5
    
"""
takes aufgaben_id, geloeste_saetze and versionline
returns choosing strategy and list_of_ids to predict
"""
def get_satz_ids(aufgaben_id, geloeste_saetze, versionline):
    # get all SatzIDs from AufgabenID
    retrieve = saetze.objects.filter(AufgabenID =aufgaben_id, Versionsnr = versionline)
    data = serializers.serialize("json", retrieve, fields=('AufgabenID'))
    all_ids = json.loads(data)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x['pk'])
        all_ids_list.append(satz_ID)

    # compare lists and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    # choosing strategy shows, if the first sentence is calculated or any other sentence
    # important, bc if it is the first sentence, it is not checked it it is over threshold for versioning
    if(list_of_ids == 9):
        choosing_strategy = 1
    else:
        choosing_strategy = 0

    return list_of_ids, choosing_strategy


"""

"""
def accumulate_satz_id(data, id):
    data['satzID'] = id

    retrieve = saetze.objects.filter(satzID =id)
    data = serializers.serialize("json", retrieve, fields=('satzID','Schwierigkeit'))
    sentence = json.loads(data) # this is a list of dict
    data['Schwierigkeit'] = sentence['fields']['Schwierigkeit']


    
    #erstloesung
    #mehrfachfalsch


    return data

"""
 
"""
def choose_next_sentence(predictions, choosing_strategy):

    val, idx = max((val, idx) for (idx, val) in enumerate(predictions[1]))
    id = predictions[idx]
    threshold = 0.5

    # do not check for p and versioning
    if (choosing_strategy == 1):
        return id
    # check for p and versioning
    else:
        if val>threshold:
            return id
        else:
            return get_version_sentence(id)

"""

"""
def get_version_sentence(id):
    return 0
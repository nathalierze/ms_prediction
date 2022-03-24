from .models import schueler, xmlsaetze, saetze
import pandas as pd
import numpy as np
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

    predictions = []
    for x in satz_ids:
        full_data = accumulate_satz_id(x, data)
        p = predict(full_data)
        print(p)
        predictions.append([x,p])
    
    next_sentence_id = choose_next_sentence(predictions, choosing_strategy)

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
finds missing fields that are necessary for the predictionmodel
"""
def accumulate_satz_id(id, data):
    data['satzID'] = id

    #schwierigkeit
    retrieve = saetze.objects.filter(satzID =id)
    serialized = serializers.serialize("json", retrieve, fields=('Schwierigkeit'))
    sentence = json.loads(serialized) # this is a list of dict
    for x in sentence:
        data['Schwierigkeit'] = x['fields']['Schwierigkeit']

    #erstloesung
    #mehrfachfalsch
    retrieve = xmlsaetze.objects.filter(UebungsID = data['UebungsID'], SatzID = id)
    serialized = serializers.serialize("json", retrieve, fields=('Erstloesung','Loesungsnr'))
    sentence = json.loads(serialized)

    if not sentence:
        # list is empty
        data['Erstloesung'] = 1
        data['MehrfachFalsch'] = 0
    else:
        for x in sentence:
            data['Erstloesung'] = x['fields']['Erstloesung']
            data['MehrfachFalsch'] = x['fields']['Loesungsnr']

    return data

"""
 chooses from predictions the sentence with max p and checkes if it is below threshold
"""
def choose_next_sentence(predictions, choosing_strategy):

    array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
    index_of_max = array_of_max[1]

    id = predictions[index_of_max][0]
    val = predictions[index_of_max][1]

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
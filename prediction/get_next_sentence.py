from ensurepip import version
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
    modus = data['Testposition']

    if(modus == 'training'):
        #checken, welche Satz IDs predicted werden müssen
        predictions, choosing_strategy = get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data)
        next_sentence_id, modus = choose_next_sentence(predictions, choosing_strategy, aufgaben_id, versionline, geloeste_saetze, data)
    else:
        next_sentence_id, modus = get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data)

    sentence_nr, version_nr = get_sentence_nr_from_id(next_sentence_id)

    # return sentence_nr, version_nr, modus
    return 5, 1, 'training'

"""
takes aufgaben_id, geloeste_saetze and versionline
returns choosing strategy and list_of_ids to predict
"""
def get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data):
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

    predictions = send_to_prediction(list_of_ids)

    return predictions, choosing_strategy


def send_to_prediction(satz_ids, data):
    predictions = []
    for x in satz_ids:
        full_data = accumulate_satz_id(x, data)
        p = predict(full_data)
        print(p)
        predictions.append([x,p])

    return predictions



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
def choose_next_sentence(predictions, choosing_strategy, aufgaben_id, versionline, geloeste_saetze, data):

    array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
    index_of_max = array_of_max[1]

    id = predictions[index_of_max][0]
    val = predictions[index_of_max][1]

    threshold = 0.5

    # do not check for p and versioning
    if (choosing_strategy == 1):
        return id, 'training'
    # check for p and versioning
    else:
        if val>threshold:
            return id, 'training'
        else:
            return get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data)

"""
if p is <50%, all version sentences are retrieved, predicted, and the sentence with the highest p is taken
"""
def get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data):

    # get all SatzIDs from AufgabenID from other versions
    retrieve = saetze.objects.filter(AufgabenID =aufgaben_id).exclude(Versionsnr = versionline)
    data = serializers.serialize("json", retrieve, fields=('AufgabenID'))
    all_ids = json.loads(data)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x['pk'])
        all_ids_list.append(satz_ID)

    # compare lists and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    predictions = send_to_prediction(list_of_ids, data)

    array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
    index_of_max = array_of_max[1]

    id = predictions[index_of_max][0]
    val = predictions[index_of_max][1]

    return id, 'modus'

"""
Retrieves sentence_nr and version_nr from Satz ID
"""
def get_sentence_nr_from_id(id):
    retrieve = saetze.objects.filter(satzID =id)
    serialized = serializers.serialize("json", retrieve, fields=('Satznr','Versionsnr'))
    sentence = json.loads(serialized) # this is a list of dict
    for x in sentence:
        satz_nr = x['fields']['Satznr']
        version_nr = x['fields']['Versionsnr']

    return satz_nr, version_nr

from ensurepip import version
from operator import mod
from .models import schueler, xmlsaetze, saetze
import pandas as pd
import numpy as np
import pickle
import datetime
from .serializers import SchuelerSerializer, XmlsaetzeSerializer
from rest_framework.renderers import JSONRenderer
from django.core import serializers
from .calculate_prediction import send_to_prediction
import json
import random
from .savePredictions import sendError2Report, sendErrorReport, sendReport

def next_sentence(data):

    aufgaben_id = data['AufgabenID']
    geloeste_saetze = data['geloesteSaetze']
    versionline = data['versionline']
    modus = data['Testposition']
    seq_mode = data['seqMode'] # can be "normal", "onlyVersion", "onlyBaseline"
    error_function = data['callFrom']

    print('versionline')
    print(versionline)
    print('----')

    if(seq_mode == "normal"):
        predictions, choosing_strategy, pruefung = get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data, error_function)
        if(pruefung==1):
            next_sentence_id, modus, prediction = 0000,'pruefung',9.000
        else:
            next_sentence_id, modus, prediction = choose_next_sentence(predictions, choosing_strategy, aufgaben_id, versionline, geloeste_saetze, data)
    elif(seq_mode =="onlyBaseline"):
        predictions, choosing_strategy, pruefung = get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data, error_function)
        if(pruefung==1):
            next_sentence_id, modus, prediction = 1000,'pruefung',9.000
        else:
            next_sentence_id, modus, prediction = choose_next_sentence(predictions, 1, aufgaben_id, versionline, geloeste_saetze, data)
    elif(seq_mode== "onlyVersion"):
        next_sentence_id, modus, prediction = get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data)        

    sentence_nr, version_nr = get_sentence_nr_from_id(next_sentence_id)
    
    print("Version")
    print(version_nr)
    print("sentence nr")
    print(sentence_nr)
    print('---------------')

    #sends report to db
    n = sendReport(data, prediction, next_sentence_id, modus)


    return sentence_nr, version_nr, modus

"""
takes aufgaben_id, geloeste_saetze and versionline
returns choosing strategy and list_of_ids to predict
"""
def get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data, error_function):
    # get all SatzIDs from AufgabenID
    retrieve = saetze.objects.filter(AufgabenID =aufgaben_id, Versionsnr = versionline)
    serialized = serializers.serialize("json", retrieve, fields=('AufgabenID'))
    all_ids = json.loads(serialized)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x['pk'])
        all_ids_list.append(satz_ID)

    # compare lists and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    print("gelosest")
    print(geloeste_saetze)
    print("list ids")
    print(list_of_ids)

    if(len(list_of_ids) == 0):
        sendErrorReport(data, error_function)
        list_of_ids = geloeste_saetze
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, 1, 1
    # choosing strategy shows, if the first sentence is calculated or any other sentence
    # important, bc if it is the first sentence, it is not checked if it is over threshold for versioning
    elif(len(list_of_ids) == 9):
        choosing_strategy = 1
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, choosing_strategy, 0
    else:
        choosing_strategy = 0
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, choosing_strategy, 0

    

    


"""
 chooses from predictions the sentence with max p and checkes if it is below threshold
"""
def choose_next_sentence(predictions, choosing_strategy, aufgaben_id, versionline, geloeste_saetze, data):

    array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
    index_of_max = array_of_max[1]

    id = predictions[index_of_max][0]
    val = predictions[index_of_max][1]
    threshold = 0.5

    print("baseline")
    print("choosen value")
    print(val)
    print("id of highest value")
    print(id)
    print('-----')

    # do not check for p and versioning
    if (choosing_strategy == 1):
        return id, 'training', val
    # check for p and versioning
    else:
        if val>threshold:
            return id, 'training', val
        else:
            return get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data)

"""
if p is <50%, all version sentences are retrieved, predicted, and the sentence with the highest p is taken
"""
def get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data):
    # get all SatzIDs from AufgabenID from other versions
    retrieve = saetze.objects.filter(AufgabenID =aufgaben_id).exclude(Versionsnr = versionline)
    serialized = serializers.serialize("json", retrieve, fields=('AufgabenID'))
    all_ids = json.loads(serialized)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x['pk'])
        all_ids_list.append(satz_ID)

    # compare lists and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    if(len(list_of_ids) >0):
        predictions = send_to_prediction(list_of_ids, data)
        array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
        index_of_max = array_of_max[1]

        id = predictions[index_of_max][0]
        val = predictions[index_of_max][1]

        print("version line")
        print("choosen value")
        print(val)
        print("id of highest value")
        print(id)
        print('-----')

        return id, 'version', val
    else:
        print('allversions up')
        #if all versions up, we choose a random id from the max values -> otherwise it will be displayed the same sentence
        predictions = send_to_prediction(all_ids_list, data)
        array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list.
        get_length =len(array_of_max)
        rand = random.randint(0, get_length-1)
        index_of_max = array_of_max[rand]

        id = predictions[index_of_max][0]
        val = predictions[index_of_max][1]

        print("version line")
        print("choosen value")
        print(val)
        print("id of highest value")
        print(id)
        print('-----')

        return id, 'version', val

    

"""
Retrieves sentence_nr and version_nr from Satz ID
"""
def get_sentence_nr_from_id(id):
    try:
        retrieve = saetze.objects.filter(satzID =id)
        serialized = serializers.serialize("json", retrieve, fields=('Satznr','Versionsnr'))
        sentence = json.loads(serialized) # this is a list of dict
        for x in sentence:
            satz_nr = x['fields']['Satznr']
            version_nr = x['fields']['Versionsnr']

        return satz_nr, version_nr
    except:
        return 0,0

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
from .savePredictions import sendErrorReport, sendReport

def next_sentence(data):
    """
    manages if conditions to find out what sentences should be predicted
    :param data: data array with information about user, session
    :return: sentence_nr, version_nr, modus
    """
    aufgaben_id = data["AufgabenID"]
    geloeste_saetze = data["geloesteSaetze"]
    versionline = data["versionline"]
    modus = data["Testposition"]
    seq_mode = data["seqMode"]  # can be "normal", "onlyVersion", "onlyBaseline"
    error_function = data["callFrom"]

    if seq_mode == "normal":
        predictions, choosing_strategy, pruefung = get_satz_ids(
            aufgaben_id, geloeste_saetze, versionline, data, error_function
        )
        if pruefung == 1:
            next_sentence_id, modus, prediction = 0000, "pruefung", 9.000
        else:
            next_sentence_id, modus, prediction = choose_next_sentence(
                predictions,
                choosing_strategy,
                aufgaben_id,
                versionline,
                geloeste_saetze,
                data,
            )
    elif seq_mode == "onlyBaseline":
        predictions, choosing_strategy, pruefung = get_satz_ids(
            aufgaben_id, geloeste_saetze, versionline, data, error_function
        )
        if pruefung == 1:
            next_sentence_id, modus, prediction = 1000, "pruefung", 9.000
        else:
            next_sentence_id, modus, prediction = choose_next_sentence(
                predictions, 1, aufgaben_id, versionline, geloeste_saetze, data
            )
    elif seq_mode == "onlyVersion":
        next_sentence_id, modus, prediction = get_version_sentence(
            aufgaben_id, versionline, geloeste_saetze, data
        )

    sentence_nr, version_nr = get_sentence_nr_from_id(next_sentence_id)
    sendReport(data, prediction, next_sentence_id, modus)

    return sentence_nr, version_nr, modus


def get_satz_ids(aufgaben_id, geloeste_saetze, versionline, data, error_function):
    """
    takes aufgaben_id, geloeste_saetze and versionline
    returns choosing strategy and list_of_ids to predict
    :param aufgaben_id: exercise id
    :param geloeste_saetze: array with sentences already solved
    :param versionline: versionline the user is in 
    :param data: data array with information about user, session
    :param error_function: specifies where the call came from
    :return: prediction, choosing strategy, int that indicates if the test phase should start
    """
    # get all SatzIDs from AufgabenID
    retrieve = saetze.objects.filter(AufgabenID=aufgaben_id, Versionsnr=versionline)
    serialized = serializers.serialize("json", retrieve, fields=("AufgabenID"))
    all_ids = json.loads(serialized)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x["pk"])
        all_ids_list.append(satz_ID)

    # compare list of satz ids to geloeste saetze and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    # if list of ids == 0, the test mode should be starting -> this means, prediction 9.0 is sent back and php code handels the start of the test mode
    if len(list_of_ids) == 0:
        sendErrorReport(data, error_function)
        list_of_ids = geloeste_saetze
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, 1, 1

    # choosing strategy shows, if the first sentence is calculated or any other sentence
    # important, bc if it is the first sentence, it is not checked if it is over threshold for versioning
    elif len(list_of_ids) == 9:
        choosing_strategy = 1
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, choosing_strategy, 0
    else:
        choosing_strategy = 0
        predictions = send_to_prediction(list_of_ids, data)
        return predictions, choosing_strategy, 0


def choose_next_sentence(
    predictions, choosing_strategy, aufgaben_id, versionline, geloeste_saetze, data
):
    """
    chooses from predictions the sentence with max p and checkes if it is below threshold
    :return: sentence id, phase, value of prediction
    """
    array_of_max = np.argmax(predictions, axis=0)  # return list of max value in list
    index_of_max = array_of_max[1]

    id = predictions[index_of_max][0]
    val = predictions[index_of_max][1]
    threshold = 0.5

    # do not check for p and versioning
    if choosing_strategy == 1:
        return id, "training", val

    # check for p and versioning
    else:
        if val > threshold:
            return id, "training", val
        else:
            return get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data)


def get_version_sentence(aufgaben_id, versionline, geloeste_saetze, data):
    """
    if p is <50%, all version sentences are retrieved, predicted, and the sentence with the highest p is taken
    :param aufgaben_id: exercise id
    :param versionline: versionline the user is in 
    :param geloeste_saetze: array with sentences already solved
    :param data: data array with information about user, session
    :return: sentence id, phase, value of prediction
    """
    # get all SatzIDs from AufgabenID from other versions
    retrieve = saetze.objects.filter(AufgabenID=aufgaben_id).exclude(
        Versionsnr=versionline
    )
    serialized = serializers.serialize("json", retrieve, fields=("AufgabenID"))
    all_ids = json.loads(serialized)
    all_ids_list = []
    for x in all_ids:
        satz_ID = str(x["pk"])
        all_ids_list.append(satz_ID)

    # compare lists and keep non-matches
    list_of_ids = set(all_ids_list) - set(geloeste_saetze)

    if len(list_of_ids) > 0:
        predictions = send_to_prediction(list_of_ids, data)
        array_of_max = np.argmax(
            predictions, axis=0
        )  # return list of max value in list.
        index_of_max = array_of_max[1]

        id = predictions[index_of_max][0]
        val = predictions[index_of_max][1]

        return id, "version", val
    else:
        # if all versions up, we choose a random id from the max values -> otherwise it will be displayed the same sentence
        predictions = send_to_prediction(all_ids_list, data)
        array_of_max = np.argmax(
            predictions, axis=0
        )  # return list of max value in list.
        get_length = len(array_of_max)
        rand = random.randint(0, get_length - 1)
        index_of_max = array_of_max[rand]

        id = predictions[index_of_max][0]
        val = predictions[index_of_max][1]

        return id, "version", val


def get_sentence_nr_from_id(id):
    """
    Retrieves sentence_nr and version_nr from SatzID
    :param id: SatzID
    :returns: satznr and versionnr from SatzID
    """
    try:
        retrieve = saetze.objects.filter(satzID=id)
        serialized = serializers.serialize(
            "json", retrieve, fields=("Satznr", "Versionsnr")
        )
        sentence = json.loads(serialized)
        for x in sentence:
            satz_nr = x["fields"]["Satznr"]
            version_nr = x["fields"]["Versionsnr"]
        return satz_nr, version_nr
    except:
        return 0, 0

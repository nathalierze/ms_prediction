from decimal import Rounded
from .models import schueler, xmlsaetze, saetze
import pandas as pd
import pickle
import datetime
from .serializers import SchuelerSerializer, XmlsaetzeSerializer
from rest_framework.renderers import JSONRenderer
from django.core import serializers
import json
import random
from .savePredictions import sendReport, sendError2Report
import numpy as np

"""
intv 5 and 6
"""


def send_to_prediction(satz_ids, data):
    predictions = []
    global df_hisotorical
    df_hisotorical = get_historical_data(data["UserID"])

    for x in satz_ids:
        full_data = accumulate_satz_id(x, data)
        p = predict(full_data)
        predictions.append([x, p])

    return predictions


"""
intv 6 and 5 
finds missing fields that are necessary for the predictionmodel
"""


def accumulate_satz_id(id, data):
    print("Acc--------------------------")
    data["satzID"] = str(id)
    retrieve = saetze.objects.filter(satzID=id)
    serialized = serializers.serialize("json", retrieve, fields=("Schwierigkeit"))
    sentence = json.loads(serialized)  # this is a list of dict
    for x in sentence:
        data["Schwierigkeit"] = x["fields"]["Schwierigkeit"]

    retrieve = xmlsaetze.objects.filter(UebungsID=data["UebungsID"], SatzID=id)
    serialized = serializers.serialize(
        "json", retrieve, fields=("Erstloesung", "Loesungsnr")
    )
    sentence = json.loads(serialized)

    if not sentence:
        data["Erstloesung"] = 1
        data["MehrfachFalsch"] = 0
    else:
        for x in sentence:
            try:
                data["Erstloesung"] = x["fields"]["Erstloesung"]
                mehrfach = x["fields"]["Loesungsnr"]
                mehrfach = mehrfach.split()
                mehrfach = len(mehrfach)
                mehrfach = int(mehrfach)
                mehrfach = mehrfach - 1
                data["MehrfachFalsch"] = mehrfach
            except:
                data["MehrfachFalsch"] = 0
                sendError2Report(data, "error4")
    return data


"""
intv 2 to 4
feature engineering and prediction
called by view get_prediction
"""


def sendHistoricAndPrediction(data):
    global df_hisotorical
    df_hisotorical = get_historical_data(data["UserID"])
    data["seqMode"] = 0
    data["versionline"] = 0
    rounded_pred = predict(data)
    n = sendReport(data, rounded_pred, data["satzID"], "intv5")

    return rounded_pred


"""
call feature engineering, get prediction and return it
"""


def predict(data):
    engineered_set = feature_engineering(data)
    prediction = get_prediction(engineered_set, data)
    rounded_pred = round(prediction, 4)
    print(rounded_pred)
    if rounded_pred < 0.1:
        rounded_pred = 0.1

    return rounded_pred


"""
import predefined prediction model and predict on engineered set
"""


def get_prediction(engineered_set, data):
    clf = pickle.load(open("Decisiontreemodel_3months.pkl", "rb"))
    try:
        predicted = clf.predict_proba(engineered_set)[:, 1]
        return predicted[0]
    except:
        sendError2Report(data, "error2")
        return 0.9209  # value is not used


"""
Feature engineering of data
Merge data with historical data
"""


def feature_engineering(data):
    ft, nt, pruefung, training, version, vt, zt = get_testposition(data["Testposition"])
    HA, Self, HA_nt, HA_vt, HA_zt = get_HA(data["HA"])
    wochentag, ist_schulzeit = get_datetime_fields()
    sex_m, sex_w = get_sex(data["Sex"])
    jahredabei = get_jahre_dabei(data["UserID"])
    beendet = get_beendet(data["beendet"])
    klassenstufe = get_klassenstufe(data["Klassenstufe"])

    dataset = [
        [
            data["UserID"],
            data["UebungsID"],
            data["satzID"],
            data["Erstloesung"],
            data["Schwierigkeit"],
            data["Art"],
            data["AufgabenID"],
            wochentag,
            ist_schulzeit,
            data["MehrfachFalsch"],
            ft,
            nt,
            pruefung,
            training,
            version,
            vt,
            zt,
            beendet,
            data["Fehler"],
            HA,
            Self,
            HA_nt,
            HA_vt,
            HA_zt,
            klassenstufe,
            jahredabei,
            sex_m,
            sex_w,
        ]
    ]

    df = pd.DataFrame(
        dataset,
        columns=[
            "UserID",
            "UebungsID",
            "satzID",
            "Erstloesung",
            "Schwierigkeit",
            "Art",
            "AufgabenID",
            "Wochentag",
            "ist_Schulzeit",
            "MehrfachFalsch",
            "Testposition__FT",
            "Testposition__nt",
            "Testposition__pruefung",
            "Testposition__training",
            "Testposition__version",
            "Testposition__vt",
            "Testposition__zt",
            "beendet",
            "Fehler",
            "HA__HA",
            "HA__Self",
            "HA__nt",
            "HA__vt",
            "HA__zt",
            "Klassenstufe",
            "Jahredabei",
            "Sex__m",
            "Sex__w",
        ],
    )

    # merge data with historical data
    global df_hisotorical
    result = pd.merge(df, df_hisotorical, on="UserID")
    result = result.drop(columns=["UserID", "UebungsID", "satzID", "AufgabenID", "Art"])
    return result


"""
Get historical data from user ID
"""


def get_historical_data(userID):
    # import satz ID
    infile = open("satzIDs.pkl", "rb")
    saetze = pickle.load(infile)
    infile.close()
    satz_ID_list = list(saetze.satzID)
    satz_ID_list = [str(item) for item in satz_ID_list]
    indexlist = [userID]

    # create emtpy DF
    df = pd.DataFrame(0, index=indexlist, columns=satz_ID_list)

    # get xmlsaetze by userID
    retrieve = xmlsaetze.objects.filter(UserID=userID)
    data = serializers.serialize("json", retrieve, fields=("SatzID", "Erfolg", "Datum"))
    struct = json.loads(data)
    df_obj = pd.DataFrame(columns=["SatzID", "Erfolg", "Datum"])
    for x in struct:
        satz_ID = x["fields"]["SatzID"]
        erfolg = x["fields"]["Erfolg"]
        datum = x["fields"]["Datum"]
        df2 = pd.DataFrame({"SatzID": [satz_ID], "Erfolg": erfolg, "Datum": datum})
        df_obj = pd.concat([df_obj, df2], ignore_index=True, axis=0)

    # iterate trough dataframe and updates erfolg where user did something
    for i in range(df_obj.shape[0]):
        satz_ID_cell = df_obj.iloc[i, 0]
        erfolg_cell = df_obj.iloc[i, 1]
        datum_cell = df_obj.iloc[i, 2]
        current_time = datetime.datetime.now()
        accepted_date = current_time + pd.DateOffset(
            months=-3
        )  # accepted date calculates the date of the last login minus 3 months

        if satz_ID_cell in df.columns:
            if str(datum_cell) > str(accepted_date):
                if erfolg_cell == 1 | erfolg_cell == True:
                    df.loc[userID, satz_ID_cell] = 1
                if erfolg_cell == 0 | erfolg_cell == False:
                    df.loc[userID, satz_ID_cell] = -1

    df = df.reset_index()
    df = df.rename(columns={"index": "UserID"})

    global historical_data
    historical_data = df

    return df


"""
error catching of feature klassenstufe
"""


def get_klassenstufe(klassenstufe):
    try:
        return int(klassenstufe)
    except:
        return 14


"""
one hot encoding of feature testposition
"""


def get_testposition(testposition):
    ft, nt, pruefung, training, version, vt, zt = 0, 0, 0, 0, 0, 0, 0

    if testposition == "ft":
        ft = 1
    if testposition == "nt":
        nt = 1
    if testposition == "pruefung":
        pruefung = 1
    if testposition == "training":
        training = 1
    if testposition == "version":
        version = 1
    if testposition == "vt":
        vt = 1
    if testposition == "zt":
        zt = 1

    return ft, nt, pruefung, training, version, vt, zt


"""
one hot encoding of feature HA
"""


def get_HA(HA_):
    HA, Self, HA_nt, HA_vt, HA_zt = 0, 0, 0, 0, 0
    if HA_ == "HA":
        HA = 1
    if HA_ == "Self":
        Self = 1
    if HA_ == "nt":
        HA_nt = 1
    if HA_ == "vt":
        HA_vt = 1
    if HA_ == "zt":
        HA_zt = 1

    return HA, Self, HA_nt, HA_vt, HA_zt

"""
calculation of feature wochentag, ist schulzeit
"""


def get_datetime_fields():
    wochentag = datetime.datetime.today().weekday()
    now = datetime.datetime.now()

    if now.hour > 14:
        ist_schulzeit = 0
    elif now.hour < 8:
        ist_schulzeit = 0
    else:
        ist_schulzeit = 1

    return wochentag, ist_schulzeit


"""
one hot encoding of feature sex
"""


def get_sex(sex):
    sex_m, sex_w = 0, 0
    if sex == "w":
        sex_w = 1
    if sex == "m":
        sex_m = 1

    return sex_m, sex_w


"""
calculation of feature jahre dabei
"""


def get_jahre_dabei(userID):
    try:
        user = schueler.objects.get(pk=userID)
        serializer = SchuelerSerializer(user)
        jahre_dabei = int(serializer.data["Klassenstufe"]) - int(
            serializer.data["Anmeldeklassenstufe"]
        )
        return jahre_dabei
    except:
        return 0


"""
one hot encoding of feature beendet
"""


def get_beendet(beendet):
    if beendet == "u":
        return 0
    elif beendet == "b":
        return 1

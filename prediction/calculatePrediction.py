from .models import schueler, xmlsaetze
import pandas as pd
import pickle
import datetime
from .serializers import schuelerSerializer, xmlsaetzeSerializer
from rest_framework.renderers import JSONRenderer
from django.core import serializers
import json
import numpy
import sklearn

def predict(data):
    engineeredSet = featureEngineering(data)
    prediction = getPrediction(engineeredSet)
    roundedPred = round(prediction,2)
    
    return roundedPred

def getPrediction(engineeredSet):
    clf = pickle.load(open('DecisionTreemodel.pkl', 'rb'))
    predicted = clf.predict_proba(engineeredSet)[:,1]    
    return predicted[0]

def featureEngineering(data):

    ft, nt, pruefung, training, version, vt, zt = getTestposition(data["Testposition"])
    HA, Self, HA_nt, HA_vt, HA_zt = getHA(data["HA"])
    wochentag, ist_Schulzeit = getDateTimeFields()
    sex_m, sex_w = getSex(data['Sex'])
    jahredabei = getJahreDabei(data['UserID'])
    beendet = getBeendet(data['beendet'])

    #data['Schussel'],
    dataset = [[data['UserID'], data['UebungsID'], data['satzID'], data['Erstloesung'], 
       data['Schwierigkeit'], data['Art'], data['AufgabenID'], 
       wochentag, ist_Schulzeit,data['MehrfachFalsch'], ft, nt,pruefung, training,version, vt, zt,
       beendet, data['Fehler'], HA, Self, HA_nt, HA_vt, HA_zt,
       data['Klassenstufe'], jahredabei, sex_m, sex_w]]
    
    # 'Schussel',
    df = pd.DataFrame(dataset, columns=['UserID', 'UebungsID', 'satzID', 'Erstloesung',
       'Schwierigkeit', 'Art', 'AufgabenID','Wochentag', 'ist_Schulzeit',
       'MehrfachFalsch', 'Testposition__FT', 'Testposition__nt',
       'Testposition__pruefung', 'Testposition__training',
       'Testposition__version', 'Testposition__vt', 'Testposition__zt',
       'beendet', 'Fehler', 'HA__HA', 'HA__Self', 'HA__nt', 'HA__vt', 'HA__zt',
       'Klassenstufe', 'Jahredabei', 'Sex__m', 'Sex__w'])

    df_hisotorical = getHistoricaldata(data['UserID'])

    #merge data with historical data
    result = pd.merge(df, df_hisotorical, on="UserID")
    result = result.drop(columns=['UserID','UebungsID','satzID','AufgabenID','Art'])
    return result


def getHistoricaldata(userID):
    
    #importiert alle satzIDs aus der Kompetenzgruppe
    infile = open('satzIDs.pkl','rb')
    saetze = pickle.load(infile)
    infile.close()
    satzIDList = list(saetze.satzID)
    indexlist = [userID]
    # baut DF mit nur null values
    df = pd.DataFrame(0, index =indexlist,columns =satzIDList)

    #get xmlsaetze by userID
    retrieve = xmlsaetze.objects.filter(UserID=userID)
    data = serializers.serialize("json", retrieve, fields=('SatzID','Erfolg','Datum'))
    struct = json.loads(data) # this is a list of dict
    dfObj = pd.DataFrame(columns=['SatzID', 'Erfolg','Datum'])
    for x in struct:
        satzID = x['fields']['SatzID']
        erfolg = x['fields']['Erfolg']
        datum = x['fields']['Datum']
        df2 = pd.DataFrame({'SatzID': [satzID],'Erfolg' : erfolg,'Datum':datum})
        dfObj = pd.concat([dfObj, df2], ignore_index = True, axis = 0)

    #iterate trough dataframe and updates erfolg where user did something
    for i in range(dfObj.shape[0]):
        satzID_cell = dfObj.iloc[i,0]
        erfolg_cell = dfObj.iloc[i,1]
        datum_cell = dfObj.iloc[i,2]
        current_time = datetime.datetime.now()
        acceptedDate = current_time + pd.DateOffset(months=-3) # accepted date calculates the date of the last login minus 3 months

        if satzID_cell in df.columns:
            if str(datum_cell) > str(acceptedDate):
                if(erfolg_cell ==1 | erfolg_cell == True):
                    df.loc[userID,satzID_cell] = 1
                if(erfolg_cell ==0 | erfolg_cell == False):
                    df.loc[userID,satzID_cell] = -1

    df = df.reset_index()
    df = df.rename(columns={"index": "UserID"})
    return df

def getTestposition(testposition):
    ft, nt, pruefung, training, version, vt, zt =0,0,0,0,0,0,0

    if(testposition=="ft"):
        ft=1
    if(testposition=="nt"):
        nt=1
    if(testposition=="pruefung"):
        pruefung=1
    if(testposition=="training"):
        training=1
    if(testposition=="version"):
        version=1
    if(testposition=="vt"):
        vt=1
    if(testposition=="zt"):
        zt=1

    return ft, nt, pruefung, training, version, vt, zt

def getHA(HA_):
    HA,Self,HA_nt, HA_vt, HA_zt =0,0,0,0,0
    if(HA_=="HA"):
        HA=1
    if(HA_=="Self"):
        Self=1
    if(HA_=="nt"):
        HA_nt=1
    if(HA_=="vt"):
        HA_vt=1
    if(HA_=="zt"):
        HA_zt=1

    return HA, Self, HA_nt, HA_vt, HA_zt

def getDateTimeFields():
    wochentag = datetime.datetime.today().weekday()
    now = datetime.datetime.now()

    if now.hour > 14:
        ist_Schulzeit = 0
    elif now.hour < 8:
        ist_Schulzeit = 0
    else:
        ist_Schulzeit = 1

    return wochentag, ist_Schulzeit

def getSex(sex):
    sex_m,sex_w = 0,0
    if(sex=="w"):
        sex_w=1
    if(sex=="m"):
        sex_m=1

    return sex_m, sex_w

def getJahreDabei(userID):
    user = schueler.objects.get(pk=userID)
    serializer = schuelerSerializer(user)
    jahredabei = int(serializer.data['Klassenstufe']) - int(serializer.data['Anmeldeklassenstufe'])

    return jahredabei

def getBeendet(beendet):
    print(beendet)
    if(beendet == 'u'):
        return 0
    elif (beendet == 'b'):
        return 1
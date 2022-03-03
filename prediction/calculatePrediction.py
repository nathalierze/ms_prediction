from .models import schueler#, xmlsaetze
import pandas as pd
import pickle
import datetime
from .serializers import schuelerSerializer#, xmlsaetzeSerializer


def featureEngineering(data):

    p = getHistoricaldata(data['UserID'])

    # ft, nt, pruefung, training, version, vt, zt = getTestposition(data["Testposition"])
    # HA, Self, HA_nt, HA_vt, HA_zt = getHA(data["HA"])
    # wochentag, ist_Schulzeit = getDateTimeFields()
    # sex_m, sex_w = getSex(data['Sex'])
    # jahredabei = getJahreDabei(data['UserID'])

    # dataset = [[data['UserID'], data['UebungsID'], data['satzID'], data['Erstloesung'], data['Schussel'],
    #    data['Schwierigkeit'], data['Art'], data['AufgabenID'], 
    #    wochentag, ist_Schulzeit,data['MehrfachFalsch'], ft, nt,pruefung, training,version, vt, zt,
    #    data['beendet'], data['Fehler'], HA, Self, HA_nt, HA_vt, HA_zt,
    #    data['Klassenstufe'], jahredabei, sex_m, sex_w]]
    
    # df = pd.DataFrame(dataset, columns=['UserID', 'UebungsID', 'satzID', 'Erstloesung', 'Schussel',
    #    'Schwierigkeit', 'Art', 'AufgabenID','Wochentag', 'ist_Schulzeit',
    #    'MehrfachFalsch', 'Testposition__FT', 'Testposition__nt',
    #    'Testposition__pruefung', 'Testposition__training',
    #    'Testposition__version', 'Testposition__vt', 'Testposition__zt',
    #    'beendet', 'Fehler', 'HA__HA', 'HA__Self', 'HA__nt', 'HA__vt', 'HA__zt',
    #    'Klassenstufe', 'Jahredabei', 'Sex__m', 'Sex__w'])

    # print(df)

    prediction = 0.66

    return prediction


def getHistoricaldata(userID):
    
    #importiert alle satzIDs aus der Kompetenzgruppe
    infile = open('satzIDs.pkl','rb')
    saetze = pickle.load(infile)
    infile.close()
    satzIDList = list(saetze.satzID)
    indexlist = [userID]
    # baut DF mit nur null values
    df = pd.DataFrame(0, index =indexlist,columns =satzIDList)

    # retrieve = xmlsaetze.objects.get(UserID=userID)
    # xmlsaetze_userid = xmlsaetzeSerializer(retrieve)

    #print(xmlsaetze_userid)

    #iterate trough dataframe row-wise

    # for i in range(xmlsaetze_userid.shape[0]): #iterate over rows
    #     user_cell = xmlsaetze_userid.iloc[i,0]
    #     satz_cell = xmlsaetze_userid.iloc[i,1]
    #     erfolg_cell = xmlsaetze_userid.iloc[i,2]

    #     #check if sentence and user is in df
    #     if satz_cell in df.columns:
    #         if user_cell in df.index:
    #             # set new cell value
    #             if(erfolg_cell == 1):
    #                 df.loc[user_cell,satz_cell] = 1
    #             elif (erfolg_cell ==0):
    #                 df.loc[user_cell,satz_cell] = -1   

    return 1

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
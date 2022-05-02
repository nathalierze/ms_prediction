from datetime import datetime
from prediction.serializers import PredictionsSerializer
from .models import predictions, schueler, saetze

def sendReport(data, rounded_pred):
    user = schueler.objects.get(pk=data['UserID'])
    satz = saetze.objects.get(pk=data['satzID'])
    report = predictions(UebungsID=data['UebungsID'], SatzID=data['satzID'], UserID=data['UserID'], interventiongroup=user.interventiongroup, prediction=rounded_pred, seqMode=data['seqMode'], modus=data['Testposition'], versionline=data['versionline'], version=satz.Versionsnr, Datum=datetime.now())
    report.save()
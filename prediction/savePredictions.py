from datetime import datetime
import pytz
from pytz import timezone
from prediction.serializers import PredictionsSerializer
from .models import predictions, schueler, saetze

def sendReport(data, rounded_pred):
    german_tz = pytz.timezone('Europe/Berlin')
    print(datetime.now(tz=german_tz))
    user = schueler.objects.get(pk=data['UserID'])
    satz = saetze.objects.get(pk=data['satzID'])
    report = predictions(UebungsID=data['UebungsID'], SatzID=data['satzID'], UserID=data['UserID'], interventiongroup=user.interventiongroup, prediction=rounded_pred, seqMode=data['seqMode'], modus=data['Testposition'], versionline=data['versionline'], version=satz.Versionsnr, Datum=datetime.now(tz=german_tz))
    report.save()
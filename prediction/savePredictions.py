from datetime import datetime
import pytz
from pytz import timezone
from prediction.serializers import PredictionsSerializer
from .models import predictions, schueler, saetze

def sendReport(data, rounded_pred, next_sentence_id):
    german_tz = pytz.timezone('Europe/Berlin')
    time = datetime.now(tz=german_tz)
    user = schueler.objects.get(pk=data['UserID'])
    satz = saetze.objects.get(pk=data['satzID'])
    report = predictions(UebungsID=data['UebungsID'], SatzID=next_sentence_id, UserID=data['UserID'], interventiongroup=user.interventiongroup, prediction=rounded_pred, seqMode=data['seqMode'], modus=data['Testposition'], versionline=data['versionline'], version=satz.Versionsnr, Datum=time)
    report.save()
from datetime import datetime
import pytz
from pytz import timezone
from prediction.serializers import PredictionsSerializer
from .models import predictions, schueler, saetze


def sendReport(data, rounded_pred, next_sentence_id, modus):
    """
    method to store result in the data base
    :params: data to be stored
    """
    german_tz = pytz.timezone("Europe/Berlin")
    time = datetime.now(tz=german_tz)
    user = schueler.objects.get(pk=data["UserID"])
    satz = saetze.objects.get(pk=data["satzID"])
    report = predictions(
        UebungsID=data["UebungsID"],
        SatzID=next_sentence_id,
        UserID=data["UserID"],
        interventiongroup=user.interventiongroup,
        prediction=rounded_pred,
        seqMode=data["seqMode"],
        modus=modus,
        versionline=data["versionline"],
        version=satz.Versionsnr,
        Datum=time,
    )
    report.save()

def sendErrorReport(data, error_function):
    """
    method to store error in the data base
    :params: data to be stored
    """
    german_tz = pytz.timezone("Europe/Berlin")
    time = datetime.now(tz=german_tz)
    user = schueler.objects.get(pk=data["UserID"])
    report = predictions(
        UebungsID=data["UebungsID"],
        SatzID=0,
        UserID=data["UserID"],
        interventiongroup=user.interventiongroup,
        prediction=0,
        seqMode="error",
        modus=error_function,
        versionline=0,
        version=0,
        Datum=time,
    )
    report.save()
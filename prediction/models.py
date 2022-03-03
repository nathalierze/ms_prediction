from sqlite3 import TimestampFromTicks
from django.db import models


class prediction(models.Model):
    pass

class xmlsaetze(models.Model):
    class Meta:
        db_table = 'xmlsaetze'

    UserID = models.IntegerField(blank=True)
    UebungsID = models.IntegerField(blank=True)
    UserAttribut= models.CharField(max_length=7, blank=True )
    Testart= models.CharField(max_length=10, blank=True )
    Testposition= models.CharField(max_length=10, blank=True )
    SatzID = models.IntegerField(blank=True)
    Erstloesung = models.SmallIntegerField(blank=True)
    Schussel= models.IntegerField(blank=True)
    KorrekturBenutzt= models.IntegerField(blank=True )
    Datum = models.DateTimeField(blank=True)
    Erfolg = models.BooleanField(blank=True)
    XMLstring = models.TextField(blank=True)
    Loesungsnr= models.CharField(max_length=60, blank=True )

    def __str__(self) -> str:
        return super().__str__()


class schueler(models.Model):
    class Meta:
        db_table = 'schueler'

    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=30, blank=True )
    Passwort_express = models.CharField(max_length=32, blank=True )
    Email = models.CharField(max_length=40, blank=True )
    Loginname = models.CharField(max_length=60, blank=True )
    Passwort = models.IntegerField(blank=True )
    SessionID = models.CharField(max_length=32, blank=True )
    Lehrername = models.CharField(max_length=30, blank=True )
    LehrerID = models.IntegerField(blank=True)
    Klassenname = models.CharField(max_length=30, blank=True )
    Geschlecht = models.CharField(max_length=20, blank=True )
    Klassenstufe = models.CharField(max_length=20, blank=True )
    Anmeldedatum = models.IntegerField(blank=True)
    Anmeldeklassenstufe = models.CharField(max_length=30, blank=True )
    Altklasse = models.CharField(max_length=30, blank=True )
    gesperrt = models.CharField(max_length=30, blank=True )
    Aufgaben = models.CharField(max_length=300, blank=True )
    Altaufgaben = models.CharField(max_length=600, blank=True )
    done = models.IntegerField(blank=True)
    Info = models.CharField(max_length=60, blank=True )
    interventiongroup = models.CharField(max_length=10, blank=True)

    def __str__(self) -> str:
        return super().__str__()

class sitzungssummary(models.Model):
    class Meta:
        db_table = 'sitzungssummary'
    
    ID = models.IntegerField(primary_key=True)
    UserID = models.IntegerField()
    UserAttribut = models.CharField(max_length=7)
    AufgabenID = models.CharField(max_length=10)
    Version = models.IntegerField()
    TestID = models.IntegerField()
    Art = models.CharField(max_length=5)
    HA = models.CharField(max_length=10)
    Fehler = models.IntegerField()
    Altdatum = models.IntegerField()
    Datum = models.DateTimeField()
    Saetze = models.CharField(max_length=400)
    Korrektur = models.IntegerField()
    isExperiment = models.BooleanField()

    def __str__(self) -> str:
        return super().__str__()

class gast(models.Model):
    class Meta: 
        db_table = 'gaeste'

    ID = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=30)
    Passwort = models.CharField(max_length=32)
    Email = models.CharField(max_length=30)
    Vorname = models.CharField(max_length=30)
    Nachname = models.CharField(max_length=30)
    Geschlecht = models.CharField(max_length=30)
    Geburtsjahr = models.CharField(max_length=30)
    Land = models.CharField(max_length=30)
    Bundesland = models.CharField(max_length=30)
    Beruf = models.CharField(max_length=30)
    gesperrt = models.CharField(max_length=30)
    Info = models.CharField(max_length=60)
    Aufgaben = models.CharField(max_length=300)
    Vergleichsgruppe = models.CharField(max_length=30)
    done = models.SmallIntegerField()
    Anmeldedatum = models.DateTimeField()
    interventiongroup = models.CharField(max_length=10)

    def __str__(self) -> str:
        return super().__str__()

    
import time
from typing import List
import dataclasses
import re

@dataclasses.dataclass
class Kurs:
    name: str
    block: str
    leiter: str
    teilnehmer: List[str]

def kurse_extrahieren():
    alle_kurse = []  # Alle Kurse aus verschiedenen Zeilen
    kurse = []       # Temporäre Liste für Kurse aus einer Zeile

    with open("kurslisten.txt", "r") as file:
        lines = file.readlines()  # Alle Zeilen der Eingabedatei lesen

    indices = None  # Initialisierung der Positionsindizes

    for line in lines:
        if "Kurs:" in line:
            alle_kurse += kurse  # Temporäre Kurse zur Gesamtliste hinzufügen
            kurse = []           # Temporäre Kursliste leeren
            kursnamen = [x.strip() for x in line.split("Kurs:") if x.strip()]
            for name_block in kursnamen:
                parts = name_block.split(" / ")
                if len(parts) == 2:
                    name, block = map(str.strip, parts)  # Name und Block extrahieren
                    kurse.append(Kurs(name, block, None, []))
                else:
                    name = parts[0].strip()
                    kurse.append(Kurs(name, "", None, []))
        elif "Kursleiter:" in line:
            kursleiter = [x.strip() for x in line.split("Kursleiter:") if x.strip()]
            for kurs, leiter in zip(kurse, kursleiter):
                kurs.leiter = leiter
        elif "Nr. Name, Vorname" in line:
            indices = [m.start() for m in re.finditer(r'\bNr\. Name, Vorname\b', line)]
        else:
            if indices is not None:
                for i, (a, b) in enumerate(zip(indices, [*indices[1:], -1])):
                    name = line[a:b].strip()
                    if name:
                        match = re.search("\d +(.*), (.*)", name)
                        if match:
                            nachname, vorname = match.groups()
                            kurse[i].teilnehmer.append(f"{vorname} {nachname}")

    alle_kurse += kurse
    return alle_kurse

def suche_kurse_von_schueler(schueler_name, kurse_daten):
    gefunden_kurse = []  # Gefundene Kurse und Kursleiter

    for kurs in kurse_daten:
        if schueler_name in kurs.teilnehmer:
            gefunden_kurse.append((kurs.name, kurs.leiter))
    
    return gefunden_kurse

# Stundenplanvorlage
stundenplan = {
    "Montag": ["1./2. A", "3./4. 3", "5./6. D", "7./8. (Woche A) 2", "7./8. (Woche B) 1"],
    "Dienstag": ["1./2. B", "3./4. 2", "5./6. 1"],
    "Mittwoch": ["1./2. Sf", "3./4. (Woche A) C", "3./4. (Woche B) G", "5./6. 3", "7./8. F"],
    "Donnerstag": ["1./2. Sp", "3./4. 1", "5./6. 2", "7./8. (Woche A) D", "7./8. (Woche B) A", "9./10. SPT"],
    "Freitag": ["1./2. (Woche B) F", "3./4. G", "5./6. C", "7./8. (Woche A) B", "7./8. (Woche B) 3"]
}

# Funktion zur Zuordnung der Kurse zum Stundenplan
def fuege_kurse_in_stundenplan(gefundene_kurse, stundenplan):
    for kurs_name, kurs_leiter in gefundene_kurse:
        for tag, faecher in stundenplan.items():
            for i, fach in enumerate(faecher):
                fach_parts = fach.split()  
                fach_name = fach_parts[-1]  
                if (
                    kurs_name.endswith(fach_name) or
                    ("sp" in kurs_name and fach_name == "Sp") or
                    ("sf" in kurs_name and fach_name == "Sf") or
                    ("SPT" in kurs_name and fach_name == "SPT")
                ):
                    stundenplan[tag][i] = (f"{fach}-Kurs: {kurs_name}, Lehrer/-in: {kurs_leiter}")
                
kurse_daten = kurse_extrahieren()

# Begrüßungsnachricht
print("Hallo, herzlich Willkommen zum GAK-Stundenplanersteller für Jahrgang 12!")

# Benutzer nach dem Namen fragen
schueler_name = input("Geben Sie den Namen der Schülerin/des Schülers ein: ")


print("Ihr Stundenplan wird erstellt", end='', flush=True)
for _ in range(3):  
    print(".", end='', flush=True)
    time.sleep(1)  

gefundene_kurse = suche_kurse_von_schueler(schueler_name, kurse_daten)
fuege_kurse_in_stundenplan(gefundene_kurse, stundenplan)

if gefundene_kurse:
    # Ausgabe des Stundenplans
    print("\nStundenplan für", schueler_name)
    for tag, faecher in stundenplan.items():
        print(tag + ":")
        for fach in faecher:
            print(fach)
else:
    print(f"Keine Kurse für {schueler_name} gefunden.")

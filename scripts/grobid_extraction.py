""" 
Ce script permet d'extraire les références bibliographiques et le texte complet (texte + référence) d'un article PDF en utilisant GROBID.

A noter que GROBID doit être configuré pour fonctionner correctement.

Exemple d'utilisation (à exécuter depuis la racine du projet) :
python scripts/grobid_extraction.py
"""

import os
import subprocess
import urllib.request
import zipfile

def grobid_decorator(func):
    def wrapper(*args, **kwargs):
        # Chemin de base pour GROBID
        base_path = "grobid"
        print("Vérification et préparation de GROBID...")

        # Télécharger et configurer GROBID si nécessaire
        if not os.path.exists(base_path):
            print("GROBID n'est pas présent. Configuration en cours...")
            check_and_download_grobid(base_path)
            run_gradlew(base_path)
            print("GROBID est prêt à être utilisé.")
        else:
            print("GROBID est déjà configuré.")

        # Exécuter la fonction décorée
        return func(base_path, *args, **kwargs)
    return wrapper

@grobid_decorator
def check_and_download_grobid(base_path):
    if not os.path.exists(base_path):
        print("Grobid n'est pas présent. Téléchargement en cours...")
        url = "https://github.com/kermitt2/grobid/archive/0.8.1.zip"
        zip_file = "grobid-0.8.1.zip"
        
        # Télécharger le fichier ZIP
        urllib.request.urlretrieve(url, zip_file)
        print("Fichier ZIP téléchargé.")
        
        # Décompresser le fichier ZIP
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("Fichier ZIP décompressé.")
        
        # Renommer le dossier extrait
        os.rename("grobid-0.8.1", base_path)
        print("Grobid est maintenant configuré.")
        
        # Supprimer le fichier ZIP
        os.remove(zip_file)
    else:
        print("Grobid est déjà présent.")

@grobid_decorator
def run_gradlew(base_path):
    try:
        # Commande à exécuter
        command = "./gradlew clean install"
        
        # Changement de répertoire vers le dossier grobid
        result = subprocess.run(command, shell=True, check=True, text=True, cwd=base_path, capture_output=True)
        
        print("Commande exécutée avec succès :")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'exécution de la commande :")
        print(e.stderr)

@grobid_decorator
def run_grobid_command(command, command_args):
    try:
        # Préparation de la commande complète
        command = [
            "java",
            "-Xmx2G",
            f"-Djava.library.path={base_path}/grobid-home/lib/lin-64:{base_path}/grobid-home/lib/lin-64/jep",
            "-jar", f"{base_path}/grobid-core/build/libs/grobid-core-0.8.2-SNAPSHOT-onejar.jar"
        ] + command_args
        
        # Exécution de la commande
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Commande exécutée avec succès :")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'exécution de la commande :")
        print(e.stderr)

# Chemin de base pour grobid
base_path = "grobid"

# Chemins pour data et output (relatifs à la racine du projet)
data_path = "data/"
output_path = "output/"

# Exécution des commandes
data_path = os.path.abspath("data/")
output_path = os.path.abspath("output/")

# Commande pour extraire les références bibliographiques au format XML
command_args1 = [
    "-gH", "grobid/grobid-home",
    "-dIn", data_path,
    "-dOut", output_path,
    "-exe", "processReferences"
]

# Commande pour obtenir l'article complet au format XML
command_args2 = [
    "-gH", "grobid/grobid-home",
    "-dIn", data_path,
    "-dOut", output_path,
    "-exe", "processFullText"
]

# Exécution de la commande avec le décorateur
run_grobid_command(command_args2)
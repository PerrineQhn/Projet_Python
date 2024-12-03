import os
import subprocess
import urllib.request
import zipfile

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

def run_grobid_command(command):
    try:
        # Exécution de la commande
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print("Commande exécutée avec succès :")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Erreur lors de l'exécution de la commande :")
        print(e.stderr)

# Chemin de base pour grobid
base_path = "grobid"

# Vérifier et configurer Grobid si nécessaire
check_and_download_grobid(base_path)

# Lancer la commande gradlew
run_gradlew(base_path)

# Chemins pour data et output (relatifs à la racine du projet)
data_path = "data/"
output_path = "output/"

# Commandes à exécuter
command1 = f"java -Xmx2G -Djava.library.path={base_path}/grobid-home/lib/lin-64:{base_path}/grobid-home/lib/lin-64/jep " \
           f"-jar {base_path}/grobid-core/build/libs/grobid-core-0.8.2-SNAPSHOT-onejar.jar " \
           f"-gH {base_path}/grobid-home -dIn {data_path} -dOut {output_path} -exe processReferences"

command2 = f"java -Xmx2G -Djava.library.path={base_path}/grobid-home/lib/lin-64:{base_path}/grobid-home/lib/lin-64/jep " \
           f"-jar {base_path}/grobid-core/build/libs/grobid-core-0.8.2-SNAPSHOT-onejar.jar " \
           f"-gH {base_path}/grobid-home -dIn {data_path} -dOut {output_path} -exe processFullText"

# Exécution des commandes
# print("Exécution de la première commande : processReferences")
# run_grobid_command(command1)
print("Exécution de la deuxième commande : processFullText")
run_grobid_command(command2)
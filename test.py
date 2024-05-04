import subprocess, time


def demarrer_programme():
    # Commande pour démarrer votre programme externe
    commande = ["pcmanfm-qt"]

    # Démarrer le programme en arrière-plan
    processus = subprocess.Popen(
        commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    print(processus.pid)

    # Attendre que le programme démarre (facultatif)
    # processus.wait()
    out, err = processus.communicate()

    # Le programme est démarré
    print(processus.returncode)
    print(out.decode() or None)
    print(err.decode() or None)


# Appeler la fonction pour démarrer le programme
print(str(time.time()).replace(".", ""))

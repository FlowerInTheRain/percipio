from selenium import webdriver
from Tools import Tools
from time import sleep
import os
import sys
import getopt
import json


# Lancement d'un webdriver
def init_webdriver(debug, browser_type)-> webdriver:
    if not debug:
        os.environ['MOZ_HEADLESS'] = '1'

    # Les options du navigateur, ici Firefox
    # l'emplacement du navigateur

    # Lancement du browser
    # Options : -> emplacement exécutable geckodriver
    #           -> emplacement logs geckodriver
    #           -> options du navigateur
    if(browser_type == "ff"):
        browser = webdriver.Firefox()
    elif(browser_type == "ch"):
        browser = webdriver.Chrome()
    # browser.maximize_window()

    return browser


def usage():
    print("Pour que l'outil se lance correctement, il faut définir au premier lancement :")
    print("     - Le nom d'utilisateur (exemple : jean.dupont@gmail.com)")
    print("     - Le mot de passe associe (exemple : tonmeilleurmotdepasse)")
    print("     - La location de l'exe de firefox (exemple : C:/Program Files/Mozilla Firefox/firefox)")
    print("Ces informations sont stockees dans le fichier conf.json")
    print("Vous n'aurez pas à les remplir à chaque utilisation\n")

    print("-h --help Affiche l'aide")
    print("-u --username Met à jour le nom d'utilisateur")
    print("-p --password Met à jour le mot de passe de l'utilisateur")
    print("-b --browser Met à jour la location de l'exe de firefox")
    print("-d --debug Affiche la fenetre du navigateur")

    sys.exit()


def main():
    # Vérification des arguments passés dans la ligne de commande
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:b:hd", ["user=", "password=", "browser=", "debug", "help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit()

    # Argument optionnel
    debug = False

    # Argument obligatoire
    usr = ''
    pwd = ''
    browser_type = ''

    for o, a in opts:
        if o in ("-d", "--debug"):
            debug = True

        elif o in ("-h", "--help"):
            usage()

        elif o in ("-u", "--user"):
            usr = a

        elif o in ("-p", "--password"):
            pwd = a

        elif o in ("-b", "--browser"):
            browser_type = a

        else:
            assert False, "unhandled option"

    with open("conf.json", "r") as jsonFile:
        conf = json.load(jsonFile)

    if usr != '':
        conf["username"] = usr

    if pwd != '':
        conf["password"] = pwd

    with open("conf.json", "w") as jsonFile:
        json.dump(conf, jsonFile)

    if browser_type == '' or conf["password"] == '' or conf["username"] == '':
        print("Il manque un element a configurer : nom d'utilisateur, mot de passe ou la location du navigateur")
        sys.exit()

    browser = init_webdriver(debug, browser_type)

    tools = Tools(browser)

    tools.connection(conf["username"], conf["password"])

    tools.go_to_assignment()

    sleep(3)

    courses = tools.get_all_cours()

    sleep(1)

    for i in range(1, len(courses)):

        print("Starting courses with URL : ")
        print(courses[i])

        tools.get_cours(courses[i])

        tools.launch_video()

        print("Fin du cours : " + courses[i])

        #test_url = tools.check_for_test()

        #if test_url != '':
        #    browser.get(test_url)
        #    tools.passing_test()

    print('Tout les cours sont fini !')

    # Fin du programme
    browser.quit()


if __name__ == "__main__":
    main()
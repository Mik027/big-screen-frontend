import pygame
import os
import cv2
import subprocess
import win32gui
import win32con
import time
import threading
import psutil

def lire_parametres():
    """Lit les paramètres de placement depuis le fichier variables.ini."""
    try:
        with open("variables.ini", "r") as f:
            variables = {}
            for ligne in f:
                if '=' in ligne:
                    cle, valeur = ligne.strip().split('=')
                    variables[cle.strip()] = valeur.strip()
        return [
            int(variables.get('X', 0)),
            int(variables.get('Y', 0)),
            int(variables.get('LARGEUR_FENETRE', 240)),
            int(variables.get('HAUTEUR_FENETRE', 320)),
            variables.get('SANS_CONTOURS', 'True').lower() == 'true'
        ]
    except Exception as e:
        print(f"Erreur lors de la lecture des paramètres : {e}. Utilisation des valeurs par défaut.")
        return [0, 0, 240, 320, True]

# Lecture des variables depuis le fichier variables.ini
with open('variables.ini', 'r') as f:
    exec(f.read())

# Variables globales pour les dimensions et la position
X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE, sans_contours = lire_parametres()

# Initialisation de Pygame
pygame.init()

# Configuration de l'interface
TITRE_FENETRE = "Big Screen"
CHEMIN_ICONE = "assets/icon.png"
TAILLE_HEADER = (LARGEUR_FENETRE, 50)

# Définition des couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (100, 100, 100)

def mettre_a_jour_fenetre():
    """Met à jour la position et les dimensions de la fenêtre."""
    global X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE, sans_contours, fenetre
    X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE, sans_contours = lire_parametres()
    fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.NOFRAME)
    hwnd = pygame.display.get_wm_info()["window"]
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    if sans_contours:
        style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE, 
                          win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)

# Création de la fenêtre sans bordure et positionnement initial
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.NOFRAME)
pygame.display.set_caption(TITRE_FENETRE)
mettre_a_jour_fenetre()
pygame.time.wait(100)

# Chargement et définition de l'icône de la fenêtre
icone = pygame.image.load(CHEMIN_ICONE)
pygame.display.set_icon(icone)

# Choix du type d'arrière-plan (image ou vidéo)
utiliser_video = UTILISER_VIDEO

if utiliser_video:
    video = cv2.VideoCapture(CHEMIN_VIDEO)
    success, video_image = video.read()
    if success:
        video_surf = pygame.image.frombuffer(
            cv2.cvtColor(cv2.resize(video_image, (LARGEUR_FENETRE, HAUTEUR_FENETRE)), cv2.COLOR_BGR2RGB).tobytes(), 
            (LARGEUR_FENETRE, HAUTEUR_FENETRE), "RGB")
    else:
        print("Erreur lors du chargement de la vidéo")
        utiliser_video = False
else:
    fond = pygame.image.load(CHEMIN_IMAGE_FOND)
    fond = pygame.transform.scale(fond, (LARGEUR_FENETRE, HAUTEUR_FENETRE))

# Chargement de l'image du header
header = pygame.image.load(CHEMIN_IMAGE_HEADER)
header = pygame.transform.scale(header, TAILLE_HEADER)

# Chargement de la liste des jeux
jeux_dict = {}
with open(CHEMIN_LISTE_JEUX, "r") as fichier:
    for ligne in fichier:
        archive, nom = ligne.strip().split(";")
        jeux_dict[archive.strip()] = nom.strip()

def explorer_repertoire(chemin):
    """Explore le répertoire et retourne la liste des éléments."""
    contenu = os.listdir(chemin)
    dossiers = [item for item in contenu if os.path.isdir(os.path.join(chemin, item))]
    fichiers = [item for item in contenu if item.endswith('.zip')]
    
    elements = []
    elements.extend(dossiers)
    elements.extend([jeux_dict.get(fichier, fichier) for fichier in fichiers])
    
    return elements

def lancer_jeu(nom_jeu, chemin_actuel):
    """Lance un jeu avec MAME."""
    for archive, nom in jeux_dict.items():
        if nom == nom_jeu:
            chemin_complet = os.path.join(chemin_actuel, archive).replace("\\", "/")
            if os.path.exists(chemin_complet):
                rompath = f"./roms/{os.path.basename(chemin_actuel)}"
                commande = ["mame", "-rompath", rompath, os.path.splitext(archive)[0], "-window", 
                            "-resolution", f"{LARGEUR_FENETRE}x{HAUTEUR_FENETRE}", "-nokeepaspect", "-skip_gameinfo"]
                print(f"Lancement du jeu avec la commande : {' '.join(commande)}")
                subprocess.Popen(commande)
                return
            else:
                print(f"Erreur : Le fichier {chemin_complet} n'existe pas")
                return
    print(f"Erreur : Impossible de trouver l'archive pour le jeu {nom_jeu}")

# Paramètres pour l'affichage
police = pygame.font.Font(None, TAILLE_POLICE)
ligne_hauteur = HAUTEUR_LIGNE
max_lignes = MAX_LIGNES
element_selectionne = 0
element_selectionne_float = 0.0

# Paramètres pour le défilement
vitesse_defilement = VITESSE_DEFILEMENT
temps_defilement = 0
direction_defilement = 0
direction_defilement_horizontal = 0

# Chemin initial et historique
chemin_actuel = CHEMIN_INITIAL
historique_chemins = []
elements = explorer_repertoire(chemin_actuel)

# Création du menu contextuel
menu_contextuel = pygame.Surface((150, 120))
menu_contextuel.fill(GRIS)
texte_fermer = police.render("Fermer", True, BLANC)
texte_attract = police.render("Mode attract", True, BLANC)
texte_options = police.render("Options", True, BLANC)
texte_apropos = police.render("A propos", True, BLANC)
menu_contextuel.blit(texte_fermer, (10, 5))
menu_contextuel.blit(texte_attract, (10, 35))
menu_contextuel.blit(texte_options, (10, 65))
menu_contextuel.blit(texte_apropos, (10, 95))

# Création de la surface d'information "A propos"
info_apropos = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
info_apropos.fill(NOIR)
info_apropos.set_alpha(200)
texte_info = police.render("Programme créé par Mik", True, BLANC)
texte_licence = police.render("Sous licence GPL 3.0", True, BLANC)
texte_version = police.render("Version 1.0", True, BLANC)
info_apropos.blit(texte_info, (LARGEUR_FENETRE // 2 - texte_info.get_width() // 2, HAUTEUR_FENETRE // 2 - 50))
info_apropos.blit(texte_licence, (LARGEUR_FENETRE // 2 - texte_licence.get_width() // 2, HAUTEUR_FENETRE // 2))
info_apropos.blit(texte_version, (LARGEUR_FENETRE // 2 - texte_version.get_width() // 2, HAUTEUR_FENETRE // 2 + 50))

def executer_mamewindow():
    """Exécute mamewindow.exe en arrière-plan s'il n'est pas déjà en cours d'exécution."""
    if not any(p.name() == "mamewindow.exe" for p in psutil.process_iter(['name'])):
        subprocess.Popen(["mamewindow.exe"])

# Lancement de mamewindow.exe en arrière-plan
thread_mamewindow = threading.Thread(target=executer_mamewindow)
thread_mamewindow.daemon = True
thread_mamewindow.start()

# Boucle principale
en_cours = True
horloge = pygame.time.Clock()
afficher_menu = False
position_menu = (0, 0)
attract_mode = False
video_attract = None
derniere_verification = time.time()
afficher_apropos = False

while en_cours:
    temps_ecoule = horloge.tick(FPS)
    
    # Vérification périodique des paramètres de placement
    if time.time() - derniere_verification > 1:
        mettre_a_jour_fenetre()
        derniere_verification = time.time()
    
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False
        elif evenement.type == pygame.MOUSEBUTTONDOWN:
            if afficher_apropos:
                afficher_apropos = False
            elif evenement.button == 3:  # Clic droit
                afficher_menu = True
                position_menu = evenement.pos
                # Mise à jour du texte du menu contextuel
                menu_contextuel.fill(GRIS)
                menu_contextuel.blit(texte_fermer, (10, 5))
                if attract_mode:
                    texte_mode = police.render("Retour menu", True, BLANC)
                else:
                    texte_mode = police.render("Mode attract", True, BLANC)
                menu_contextuel.blit(texte_mode, (10, 35))
                menu_contextuel.blit(texte_options, (10, 65))
                menu_contextuel.blit(texte_apropos, (10, 95))
            elif evenement.button == 1:  # Clic gauche
                if afficher_menu:
                    rect_menu = pygame.Rect(position_menu, (150, 120))
                    if rect_menu.collidepoint(evenement.pos):
                        if evenement.pos[1] - position_menu[1] < 30:
                            # Arrêt de tous les processus mamewindow.exe
                            for proc in psutil.process_iter(['name']):
                                if proc.name() == "mamewindow.exe":
                                    proc.terminate()
                            en_cours = False  # Fermer la fenêtre
                        elif evenement.pos[1] - position_menu[1] < 60:
                            attract_mode = not attract_mode
                            if attract_mode:
                                video_attract = cv2.VideoCapture(CHEMIN_VIDEO_ATTRACT)
                            else:
                                if video_attract:
                                    video_attract.release()
                        elif evenement.pos[1] - position_menu[1] < 90:
                            subprocess.Popen(["options.exe"])
                        else:
                            afficher_apropos = True
                    afficher_menu = False
        elif evenement.type == pygame.KEYDOWN:
            if attract_mode:
                attract_mode = False
                if video_attract:
                    video_attract.release()
            else:
                if evenement.key == TOUCHE_HAUT:
                    direction_defilement = -1
                elif evenement.key == TOUCHE_BAS:
                    direction_defilement = 1
                elif evenement.key == TOUCHE_GAUCHE:
                    direction_defilement_horizontal = -1
                elif evenement.key == TOUCHE_DROITE:
                    direction_defilement_horizontal = 1
                elif evenement.key == TOUCHE_ENTREE:
                    if element_selectionne < len(elements):
                        element = elements[element_selectionne]
                        nouveau_chemin = os.path.join(chemin_actuel, element)
                        if os.path.isdir(nouveau_chemin):
                            historique_chemins.append(chemin_actuel)
                            chemin_actuel = nouveau_chemin
                            elements = explorer_repertoire(chemin_actuel)
                            element_selectionne = 0
                        else:
                            lancer_jeu(element, chemin_actuel)
                elif evenement.key == TOUCHE_RETOUR:
                    if historique_chemins:
                        chemin_actuel = historique_chemins.pop()
                        elements = explorer_repertoire(chemin_actuel)
                        element_selectionne = 0
        elif evenement.type == pygame.KEYUP:
            if evenement.key in (TOUCHE_HAUT, TOUCHE_BAS):
                direction_defilement = 0
            elif evenement.key in (TOUCHE_GAUCHE, TOUCHE_DROITE):
                direction_defilement_horizontal = 0

    if attract_mode:
        success, video_image = video_attract.read()
        if success:
            video_surf = pygame.image.frombuffer(
                cv2.cvtColor(cv2.resize(video_image, (LARGEUR_FENETRE, HAUTEUR_FENETRE)), cv2.COLOR_BGR2RGB).tobytes(), 
                (LARGEUR_FENETRE, HAUTEUR_FENETRE), "RGB")
            fenetre.blit(video_surf, (0, 0))
        else:
            video_attract.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        # Gestion du défilement continu vertical
        temps_defilement += temps_ecoule / 1000  # Temps écoulé en secondes
        if temps_defilement > 1 / vitesse_defilement:
            element_selectionne += direction_defilement
            element_selectionne = max(0, min(element_selectionne, len(elements) - 1))
            element_selectionne_float = float(element_selectionne)  # Mise à jour de la valeur flottante
            temps_defilement = 0

        # Gestion du défilement continu horizontal
        if direction_defilement_horizontal != 0:
            element_selectionne_float += direction_defilement_horizontal * VITESSE_DEFILEMENT_HORIZONTAL
            element_selectionne_float = max(0.0, min(element_selectionne_float, float(len(elements) - 1)))
            element_selectionne = int(element_selectionne_float)  # Conversion en entier pour l'indexation

        # Affichage de l'arrière-plan (vidéo ou image)
        if utiliser_video:
            success, video_image = video.read()
            if success:
                video_surf = pygame.image.frombuffer(
                    cv2.cvtColor(cv2.resize(video_image, (LARGEUR_FENETRE, HAUTEUR_FENETRE)), cv2.COLOR_BGR2RGB).tobytes(), (LARGEUR_FENETRE, HAUTEUR_FENETRE), "RGB")
                fenetre.blit(video_surf, (0, 0))
            else:
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            fenetre.blit(fond, (0, 0))

        # Affichage du header
        fenetre.blit(header, (0, 0))

        # Calcul de la position de défilement pour centrer l'élément sélectionné
        position_defilement = max(0, min(element_selectionne - max_lignes // 2, len(elements) - max_lignes))

        # Affichage des éléments
        for i in range(max_lignes):
            index = i + int(position_defilement)  # Assurez-vous que l'index est un entier
            if 0 <= index < len(elements):
                nom_element = elements[index]
                
                # Ajustement du texte pour tenir compte des espaces
                texte = police.render(nom_element, True, BLANC)
                largeur_texte = texte.get_width()
                
                if largeur_texte > LARGEUR_FENETRE - 20:  # 20 pixels de marge
                    # Si le texte est trop long, on le tronque et ajoute "..."
                    texte_tronque = nom_element
                    while largeur_texte > LARGEUR_FENETRE - 40:  # 40 pixels pour "..." et marge
                        texte_tronque = texte_tronque[:-1]
                        texte = police.render(texte_tronque + "...", True, BLANC)
                        largeur_texte = texte.get_width()
                
                texte_rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, i * ligne_hauteur + ligne_hauteur // 2 + TAILLE_HEADER[1]))
                
                # Mise en évidence de l'élément sélectionné
                if index == element_selectionne:
                    surface_grise = pygame.Surface((LARGEUR_FENETRE, ligne_hauteur))
                    surface_grise.set_alpha(128)
                    surface_grise.fill(GRIS)
                    fenetre.blit(surface_grise, (0, i * ligne_hauteur + TAILLE_HEADER[1]))
                
                fenetre.blit(texte, texte_rect)

    # Affichage de la surface "A propos" si nécessaire
    if afficher_apropos:
        fenetre.blit(info_apropos, (0, 0))

    # Affichage du menu contextuel si nécessaire
    if afficher_menu:
        fenetre.blit(menu_contextuel, position_menu)

    pygame.display.flip()

pygame.quit()
if utiliser_video:
    video.release()
if video_attract:
    video_attract.release()

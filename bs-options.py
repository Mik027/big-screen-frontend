import win32gui
import win32process
import psutil
import time
import tkinter as tk
from tkinter import ttk
import os
import ctypes
import win32con
import win32api
import configparser

class InterfaceCoordonnees:
    def __init__(self, master):
        self.master = master
        master.title("Options Big Screen")

        # Obtenir la résolution de l'écran
        user32 = ctypes.windll.user32
        self.largeur_ecran = user32.GetSystemMetrics(0)
        self.hauteur_ecran = user32.GetSystemMetrics(1)

        self.X, self.Y, self.LARGEUR_FENETRE, self.HAUTEUR_FENETRE = self.lire_parametres()

        self.X_var = tk.IntVar(value=self.X)
        self.Y_var = tk.IntVar(value=self.Y)
        self.LARGEUR_FENETRE_var = tk.IntVar(value=self.LARGEUR_FENETRE)
        self.HAUTEUR_FENETRE_var = tk.IntVar(value=self.HAUTEUR_FENETRE)

        self.X_entry = ttk.Entry(master, textvariable=self.X_var, width=10, validate="key", validatecommand=(master.register(self.valider_entree), '%P'))
        self.X_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(master, text="Coordonnée X:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Scale(master, from_=0, to=self.largeur_ecran, variable=self.X_var, orient=tk.HORIZONTAL, command=lambda v: self.mise_a_jour_arrondi('X', v)).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(master, text="+", command=lambda: self.incrementer('X', 1)).grid(row=0, column=3, padx=2, pady=5)
        ttk.Button(master, text="-", command=lambda: self.incrementer('X', -1)).grid(row=0, column=4, padx=2, pady=5)

        self.Y_entry = ttk.Entry(master, textvariable=self.Y_var, width=10, validate="key", validatecommand=(master.register(self.valider_entree), '%P'))
        self.Y_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(master, text="Coordonnée Y:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Scale(master, from_=0, to=self.hauteur_ecran, variable=self.Y_var, orient=tk.HORIZONTAL, command=lambda v: self.mise_a_jour_arrondi('Y', v)).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(master, text="+", command=lambda: self.incrementer('Y', 1)).grid(row=1, column=3, padx=2, pady=5)
        ttk.Button(master, text="-", command=lambda: self.incrementer('Y', -1)).grid(row=1, column=4, padx=2, pady=5)

        self.LARGEUR_FENETRE_entry = ttk.Entry(master, textvariable=self.LARGEUR_FENETRE_var, width=10, validate="key", validatecommand=(master.register(self.valider_entree), '%P'))
        self.LARGEUR_FENETRE_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(master, text="Largeur:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Scale(master, from_=1, to=self.largeur_ecran, variable=self.LARGEUR_FENETRE_var, orient=tk.HORIZONTAL, command=lambda v: self.mise_a_jour_arrondi('LARGEUR_FENETRE', v)).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(master, text="+", command=lambda: self.incrementer('LARGEUR_FENETRE', 1)).grid(row=2, column=3, padx=2, pady=5)
        ttk.Button(master, text="-", command=lambda: self.incrementer('LARGEUR_FENETRE', -1)).grid(row=2, column=4, padx=2, pady=5)

        self.HAUTEUR_FENETRE_entry = ttk.Entry(master, textvariable=self.HAUTEUR_FENETRE_var, width=10, validate="key", validatecommand=(master.register(self.valider_entree), '%P'))
        self.HAUTEUR_FENETRE_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(master, text="Hauteur:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Scale(master, from_=1, to=self.hauteur_ecran, variable=self.HAUTEUR_FENETRE_var, orient=tk.HORIZONTAL, command=lambda v: self.mise_a_jour_arrondi('HAUTEUR_FENETRE', v)).grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(master, text="+", command=lambda: self.incrementer('HAUTEUR_FENETRE', 1)).grid(row=3, column=3, padx=2, pady=5)
        ttk.Button(master, text="-", command=lambda: self.incrementer('HAUTEUR_FENETRE', -1)).grid(row=3, column=4, padx=2, pady=5)

        ttk.Button(master, text="Appliquer", command=self.appliquer_changements).grid(row=4, column=0, columnspan=5, padx=5, pady=5)

        for var in [self.X_var, self.Y_var, self.LARGEUR_FENETRE_var, self.HAUTEUR_FENETRE_var]:
            var.trace_add("write", self.mise_a_jour)

    def lire_parametres(self):
        parametres = {
            "X": 10,
            "Y": 10,
            "LARGEUR_FENETRE": 240,
            "HAUTEUR_FENETRE": 320
        }
        if os.path.exists("variables.ini"):
            with open("variables.ini", "r") as file:
                lignes = file.readlines()
                for ligne in lignes:
                    if "=" in ligne:
                        cle, valeur = ligne.strip().split("=", 1)
                        cle = cle.strip()
                        valeur = valeur.strip()
                        if cle in parametres:
                            try:
                                parametres[cle] = int(valeur)
                            except ValueError:
                                print(f"Erreur de conversion pour {cle}. Utilisation de la valeur par défaut.")
        
        return (parametres["X"], parametres["Y"], parametres["LARGEUR_FENETRE"], parametres["HAUTEUR_FENETRE"])

    def sauvegarder_parametres(self, X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE):
        nouvelles_valeurs = {
            "X": str(X),
            "Y": str(Y),
            "LARGEUR_FENETRE": str(LARGEUR_FENETRE),
            "HAUTEUR_FENETRE": str(HAUTEUR_FENETRE)
        }
        
        lignes_existantes = []
        if os.path.exists("variables.ini"):
            with open("variables.ini", "r") as file:
                lignes_existantes = file.readlines()
        
        with open("variables.ini", "w") as file:
            for ligne in lignes_existantes:
                if "=" in ligne:
                    cle, _ = ligne.strip().split("=", 1)
                    cle = cle.strip()
                    if cle in nouvelles_valeurs:
                        file.write(f"{cle} = {nouvelles_valeurs[cle]}\n")
                        del nouvelles_valeurs[cle]
                    else:
                        file.write(ligne)
                else:
                    file.write(ligne)
            
            # Ajouter les nouvelles valeurs qui n'étaient pas dans le fichier original
            for cle, valeur in nouvelles_valeurs.items():
                file.write(f"{cle} = {valeur}\n")

    def valider_entree(self, valeur):
        return valeur.isdigit() or valeur == ""

    def mise_a_jour(self, *args):
        # Ne rien faire ici, les changements seront appliqués lors du clic sur le bouton "Appliquer"
        pass

    def mise_a_jour_arrondi(self, parametre, valeur):
        valeur_arrondie = int(float(valeur))
        if parametre == 'X':
            self.X_var.set(valeur_arrondie)
        elif parametre == 'Y':
            self.Y_var.set(valeur_arrondie)
        elif parametre == 'LARGEUR_FENETRE':
            self.LARGEUR_FENETRE_var.set(valeur_arrondie)
        elif parametre == 'HAUTEUR_FENETRE':
            self.HAUTEUR_FENETRE_var.set(valeur_arrondie)
        self.appliquer_changements()

    def incrementer(self, parametre, valeur):
        if parametre == 'X':
            self.X_var.set(self.X_var.get() + valeur)
        elif parametre == 'Y':
            self.Y_var.set(self.Y_var.get() + valeur)
        elif parametre == 'LARGEUR_FENETRE':
            self.LARGEUR_FENETRE_var.set(self.LARGEUR_FENETRE_var.get() + valeur)
        elif parametre == 'HAUTEUR_FENETRE':
            self.HAUTEUR_FENETRE_var.set(self.HAUTEUR_FENETRE_var.get() + valeur)
        self.appliquer_changements()

    def appliquer_changements(self):
        try:
            X = self.X_var.get()
            Y = self.Y_var.get()
            LARGEUR_FENETRE = self.LARGEUR_FENETRE_var.get()
            HAUTEUR_FENETRE = self.HAUTEUR_FENETRE_var.get()
            placer_fenetre_mame(X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE)
            self.sauvegarder_parametres(X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE)
        except ValueError:
            pass  # Ignorer les valeurs non valides

def supprimer_contours_fenetre(hwnd):
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)

def placer_fenetre_mame(X=10, Y=10, LARGEUR_FENETRE=240, HAUTEUR_FENETRE=320):
    def enum_windows_callback(hwnd, _):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            if process.name().lower() == "mame.exe":
                win32gui.SetWindowPos(hwnd, None, X, Y, LARGEUR_FENETRE, HAUTEUR_FENETRE, 0x0004 | 0x0040)
                supprimer_contours_fenetre(hwnd)
        except psutil.NoSuchProcess:
            pass
        return True

    win32gui.EnumWindows(enum_windows_callback, None)

def verifier_et_corriger():
    root = tk.Tk()
    app = InterfaceCoordonnees(root)
    root.mainloop()

if __name__ == "__main__":
    verifier_et_corriger()

import win32gui
import win32process
import psutil
import time
import os
import win32con

def lire_parametres():
    if os.path.exists("variables.ini"):
        with open("variables.ini", "r") as f:
            variables = {}
            for line in f:
                if line.strip().startswith(('X', 'Y', 'LARGEUR_FENETRE', 'HAUTEUR_FENETRE')):
                    try:
                        exec(line.strip(), variables)
                    except:
                        pass  # Ignorer les lignes qui causent des erreurs
        return (
            variables.get('X', 10),
            variables.get('Y', 10),
            variables.get('LARGEUR_FENETRE', 240),
            variables.get('HAUTEUR_FENETRE', 320),
            True  # Nous gardons sans_contours à True par défaut
        )
    else:
        # Créer le fichier variables.ini avec des valeurs par défaut
        valeurs_par_defaut = """X = 10
Y = 10
LARGEUR_FENETRE = 240
HAUTEUR_FENETRE = 320"""
        with open("variables.ini", "w") as f:
            f.write(valeurs_par_defaut)
        return 10, 10, 240, 320, True

def placer_fenetre_mame(x, y, largeur, hauteur, sans_contours):
    def enum_windows_callback(hwnd, _):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            if process.name().lower() == "mame.exe":
                # Vérifier si le titre de la fenêtre ne contient pas "diemwin"
                window_title = win32gui.GetWindowText(hwnd).lower()
                if "diemwin" not in window_title:
                    win32gui.SetWindowPos(hwnd, None, x, y, largeur, hauteur, 0x0004 | 0x0040)
                    if sans_contours:
                        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                        style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
                        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                        win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)
        except psutil.NoSuchProcess:
            pass
        return True

    win32gui.EnumWindows(enum_windows_callback, None)

def boucle_principale():
    while True:
        x, y, largeur, hauteur, sans_contours = lire_parametres()
        placer_fenetre_mame(x, y, largeur, hauteur, sans_contours)
        time.sleep(1)

if __name__ == "__main__":
    boucle_principale()

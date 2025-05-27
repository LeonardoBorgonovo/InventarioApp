import tkinter as tk
from tkinter import messagebox

def stampa_a_video(testo):
    """Mostra un messaggio informativo in una finestra di dialogo Tkinter."""
    messagebox.showinfo("Informazione", testo)

def create_toplevel_window(parent_root, title):
    """Crea e restituisce una finestra TopLevel ben configurata."""
    window = tk.Toplevel(parent_root)
    window.title(title)
    window.transient(parent_root) # Rende la finestra figlia dipendente dalla principale
    window.grab_set() # Blocca l'interazione con la finestra principale finché questa è aperta
    return window
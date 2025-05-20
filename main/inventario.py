import tkinter as tk
from tkinter import messagebox
import os

# Importa le funzioni di basso livello per l'inizializzazione del DB
from functions.db_utils import create_tables, create_connection

# Importa le funzioni di alto livello per la gestione dell'UI
from functions.ui_common_utils import stampa_a_video # Se vuoi usare stampa_a_video nel main
from functions.ui_add_product import open_add_product_window
from functions.ui_view_product import open_view_products_window
from functions.ui_edit_delete_product import open_edit_delete_product_window
from functions.stampa_utils import stampa_ddt

# --- Configurazione del Path per il Database ---
DATABASE_DIR = 'db/' # Ora si aspetta 'db/' nella stessa directory di main.py
DATABASE_PATH = os.path.join(DATABASE_DIR, 'inventario.db')

# --- Funzione chiusura applicazione ---
def chiudi_applicazione():
    """Funzione per chiudere la finestra dell'applicazione."""
    # La gestione della connessione è incapsulata in db_utils,
    # quindi non c'è una 'conn' globale da chiudere qui direttamente.
    root.destroy()

# --- Inizializzazione App Tkinter ---
root = tk.Tk()
root.title("Inventario Azienda Elettrica")
root.geometry("400x300") # Dimensioni iniziali per la finestra del menu

# --- Inizializzazione Database ---
os.makedirs(DATABASE_DIR, exist_ok=True)
create_tables() # Assicurati che le tabelle siano create con lo schema completo

# --- Frame del Menu Principale ---
menu_frame = tk.Frame(root, padx=20, pady=20)
menu_frame.pack(expand=True)

tk.Label(menu_frame, text="Menu Principale", font=("Helvetica", 16, "bold")).pack(pady=20)

# Bottoni per le diverse funzionalità
tk.Button(menu_frame, text="Mostra Materiali", width=25, height=2,
          command=lambda: open_view_products_window(root)).pack(pady=5)

tk.Button(menu_frame, text="Aggiungi Materiali", width=25, height=2,
          command=lambda: open_add_product_window(root)).pack(pady=5)

tk.Button(menu_frame, text="Modifica/Cancella Materiali", width=25, height=2,
          command=lambda: open_edit_delete_product_window(root)).pack(pady=5)

tk.Button(menu_frame, text="Stampa DDT", width=25, height=2,
          command=stampa_ddt).pack(pady=5) # Stampa DDT è ancora generica

tk.Button(menu_frame, text="Esci", width=25, height=2,
          command=chiudi_applicazione).pack(pady=15)

# Protocollo per gestire la chiusura della finestra
root.protocol("WM_DELETE_WINDOW", chiudi_applicazione)

# Loop principale dell'applicazione
root.mainloop()
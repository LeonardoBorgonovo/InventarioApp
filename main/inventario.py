import tkinter as tk
from tkinter import messagebox
import os
import sys # Importa sys per la gestione dell'uscita in caso di errore


from functions.db_utils import create_tables

# Importa le funzioni di alto livello per la gestione dell'UI
from functions.ui_add_product import open_add_product_window
from functions.ui_view_product import open_view_products_window
from functions.ui_edit_delete_product import open_edit_delete_product_window
from functions.ui_print_ddt import open_print_ddt_window

# Importa la funzione per inizializzare i file dati persistenti
from functions.data_manager import initialize_data_files, PERSISTENT_DB_PATH, PERSISTENT_COUNTER_PATH


try:
    initialize_data_files()
except SystemExit:
    print("Errore durante l'inizializzazione dei file dati. L'applicazione verrà chiusa.")
    sys.exit(1)

# --- Funzione chiusura applicazione ---
def chiudi_applicazione():
    """Funzione per chiudere la finestra dell'applicazione."""
    root.destroy()

# --- Inizializzazione App Tkinter ---
root = tk.Tk()
root.title("Inventario TECNOLUX")
root.geometry("600x500") # Dimensioni iniziali per la finestra del menu

# --- Inizializzazione Database (Creazione Tabelle) ---
# Non è più necessario creare la directory 'db/' qui, perché i file saranno in PERSISTENT_DB_PATH
# os.makedirs(DATABASE_DIR, exist_ok=True) # Rimuovi questa riga
create_tables() # Questa funzione (da db_utils) DEVE ORA usare PERSISTENT_DB_PATH

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
          command=lambda: open_print_ddt_window(root)).pack(pady=5)

tk.Button(menu_frame, text="Esci", width=25, height=2,
          command=chiudi_applicazione).pack(pady=5)

# Protocollo per gestire la chiusura della finestra
root.protocol("WM_DELETE_WINDOW", chiudi_applicazione)

# Loop principale dell'applicazione
root.mainloop()
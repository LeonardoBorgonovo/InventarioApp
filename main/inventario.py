import tkinter as tk
import os
from tkinter import messagebox

# Importa le funzioni di basso livello per l'inizializzazione del DB
from functions.db_utils import create_tables, create_connection

# Importa le funzioni di alto livello per la gestione dell'UI
from functions.ui_add_product import create_add_product_frame # Funzione per creare la sezione "Aggiungi Prodotto"
from functions.ui_view_product import show_products_list_window # Funzione per mostrare la lista prodotti
from functions.stampa_utils import stampa_ddt # La tua funzione per stampare il DDT

DATABASE_PATH = '../db/inventario.db'

#Funzione per stampare a video
def stampa_a_video(testo):
    messagebox.showinfo("Contenuto da Stampare", testo)

#Funzione chiusura database
def chiudi_applicazione():
    """Funzione per chiudere la connessione al database e poi la finestra."""
    root.destroy() # Chiude la finestra principale

#Intestazione App
root = tk.Tk()
root.title("Inventario Azienda Elettrica")

# --- Inizializzazione Database ---
# Assicurati che la directory 'db' esista
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
create_tables() # Chiama la funzione per creare o verificare le tabelle del DB

# --- Creazione dell'Interfaccia Utente ---

# Frame principale per organizzare i contenuti (opzionale, ma buona pratica)
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Aggiungi il frame per l'aggiunta di prodotti
add_product_ui_frame = create_add_product_frame(main_frame)
# add_product_ui_frame.pack() # Già impacchettato all'interno di create_add_product_frame

# Sezione Operazioni (Bottoni generali)
operations_frame = tk.LabelFrame(main_frame, text="Operazioni Magazzino")
operations_frame.pack(padx=10, pady=10, fill="x")

tk.Button(operations_frame, text="Mostra Prodotti", command=lambda: show_products_list_window(root)).pack(side=tk.LEFT, padx=5, pady=5)
tk.Button(operations_frame, text="Stampa DDT", command=stampa_ddt).pack(side=tk.LEFT, padx=5, pady=5)
# Aggiungi qui altri bottoni per modificare, eliminare, ecc. che richiameranno le rispettive funzioni UI

root.protocol("WM_DELETE_WINDOW", chiudi_applicazione)
#Loop per far rimanere la finestra aperta
root.mainloop()

import tkinter as tk
import sqlite3
from tkinter import messagebox
from stampa_utils import genera_ddt, stampa_ddt
from salva_prodotti import salva_prod

#Funzione per stampare a video
def stampa_a_video(testo):
    messagebox.showinfo("Contenuto da Stampare", testo)

#Funzione chiusura database
def chiudi_applicazione():
    """Funzione per chiudere la connessione al database e poi la finestra."""
    if conn:
        conn.close()
        print("Connessione al database chiusa.")
    root.destroy() # Chiude la finestra principale

#Intestazione App
root = tk.Tk()
root.title("Inventario Azienda Elettrica")

#Connessione al dB (se non esiste viene creato)
conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

#Creazione tabella prodotti
cursor.execute('''
CREATE TABLE IF NOT EXISTS prodotti(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
    )
''')

#Commento delle modifiche
conn.commit()

#Etichetta per il nome Prodotto
label_nome = tk.Label(root, text="Nome Prodotto:")
label_nome.pack() #pack() è un gestore di layout

# Campo di testo per inserire il nome del prodotto
entry_nome = tk.Entry(root)
entry_nome.pack()

# Bottone per salvare il prodotto
bottone_salva = tk.Button(root, text="Salva Prodotto", command=lambda: salva_prod(root, entry_nome, conn, cursor))
bottone_salva.pack()

# Bottone per stampare il DDT
bottone_stampa_ddt = tk.Button(root, text="Stampa DDT", command=stampa_ddt)
bottone_stampa_ddt.pack()


root.protocol("WM_DELETE_WINDOW", chiudi_applicazione)
#Loop per far rimanere la finestra aperta
root.mainloop()

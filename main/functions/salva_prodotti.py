import tkinter as tk
from tkinter import messagebox
import sqlite3

#Funzione per stampare a video
def stampa_a_video(testo):
    messagebox.showinfo("Contenuto da Stampare", testo)
    
#Funzione salva prodotto
def salva_prod(root, entry_nome, conn, cursor):
    nome_prodotto = entry_nome.get()

    if not nome_prodotto:
        print("Il nome non può essere vuoto.")
        stampa = "Il nome non può essere vuoto"
        stampa_a_video(stampa)
        return # Uscita dalla funzione se il nome è vuoto

    cursor.execute("SELECT id FROM prodotti WHERE nome = ?", (nome_prodotto,))
    existing_product = cursor.fetchone()

    if existing_product:
        print(f"Il prodotto '{nome_prodotto}' esiste già nell'inventario (ID: {existing_product[0]}).")
        stampa = f"Il prodotto '{nome_prodotto}' esiste già nell'inventario (ID: {existing_product[0]})."
        stampa_a_video(stampa)
        entry_nome.delete(0, tk.END) # Pulisce il campo di testo
    else:
        cursor.execute("INSERT INTO prodotti (nome) VALUES (?)", (nome_prodotto,))
        conn.commit()
        entry_nome.delete(0, tk.END)
        print(f"Prodotto '{nome_prodotto}' salvato nel database.")
        stampa = f"Prodotto '{nome_prodotto}' salvato correttamente nel database."
        stampa_a_video(stampa)
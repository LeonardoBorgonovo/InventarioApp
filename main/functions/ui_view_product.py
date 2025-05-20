import tkinter as tk
from tkinter import messagebox
from functions.db_utils import get_all_prodotti # Importa solo la funzione CRUD necessaria

def show_products_list_window(parent_root):
    """Crea e mostra una finestra TopLevel con la lista dei prodotti."""
    list_window = tk.Toplevel(parent_root)
    list_window.title("Lista Prodotti Magazzino")
    list_window.transient(parent_root) # Rende la finestra figlia dipendente dalla principale
    list_window.grab_set() # Blocca l'interazione con la finestra principale finché questa è aperta

    products = get_all_prodotti() # Chiama la funzione di basso livello per recuperare i prodotti

    if products:
        # Intestazioni della "tabella"
        header_text = "ID | Codice | Nome | Descrizione | UM | Quantità | Prezzo"
        tk.Label(list_window, text=header_text, font=("Helvetica", 10, "bold")).pack(anchor='w', padx=5, pady=5)
        tk.Frame(list_window, height=1, bg="gray").pack(fill='x', padx=5, pady=2) # Linea divisoria

        # Scorri i prodotti e visualizzali
        for p in products:
            display_text = (
                f"ID: {p[0]} | Codice: {p[1]} | Nome: {p[2]} | Desc: {p[3] if p[3] else 'N/D'} | "
                f"UM: {p[4]} | Qta: {p[5]} | Prezzo: {f'{p[6]:.2f} €' if p[6] is not None else 'N/D'} "
            )
            tk.Label(list_window, text=display_text).pack(anchor='w', padx=5, pady=1)
    else:
        tk.Label(list_window, text="Nessun prodotto nel magazzino.").pack(padx=20, pady=20)

    # Pulsante per chiudere la finestra
    tk.Button(list_window, text="Chiudi", command=list_window.destroy).pack(pady=10)

    list_window.wait_window() # Attendi che la finestra secondaria venga chiusa
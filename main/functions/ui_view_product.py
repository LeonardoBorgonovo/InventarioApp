import tkinter as tk
from tkinter import ttk # Importa ttk per Treeview (più robusto per le tabelle)
from functions.db_utils import get_all_prodotti
from functions.ui_common_utils import create_toplevel_window

def open_view_products_window(parent_root):
    """Apre una finestra per visualizzare tutti i prodotti in una tabella."""
    view_window = create_toplevel_window(parent_root, "Lista Materiali in Magazzino")

    products = get_all_prodotti()

    # Usa Treeview per una visualizzazione a tabella più professionale
    tree = ttk.Treeview(view_window, columns=("ID", "Codice", "Nome", "Descrizione", "UM", "Quantità", "Prezzo"), show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Definisci intestazioni delle colonne
    tree.heading("ID", text="ID")
    tree.heading("Codice", text="Codice")
    tree.heading("Nome", text="Nome")
    tree.heading("Descrizione", text="Descrizione")
    tree.heading("UM", text="UM")
    tree.heading("Quantità", text="Quantità")
    tree.heading("Prezzo", text="Prezzo")

    # Larghezza delle colonne (puoi aggiustarle)
    tree.column("ID", width=40, anchor="center")
    tree.column("Codice", width=100, anchor="w")
    tree.column("Nome", width=150, anchor="w")
    tree.column("Descrizione", width=200, anchor="w")
    tree.column("UM", width=50, anchor="center")
    tree.column("Quantità", width=80, anchor="center")
    tree.column("Prezzo", width=80, anchor="e")

    # Inserisci i dati
    if products:
        for p in products:
            tree.insert("", "end", values=(
                p[0], p[1], p[2], p[3] if p[3] else "N/D", p[4], p[5], f"{p[6]:.2f} €" if p[6] is not None else "N/D"
            ))
    else:
        # Aggiungi una riga per indicare che non ci sono prodotti
        tree.insert("", "end", values=("", "", "Nessun materiale disponibile", "", "", "", ""), tags=('empty',))
        tree.tag_configure('empty', background='#FFFFAA') # Sfondo giallo per avviso

    # Aggiungi una scrollbar
    scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Bottone per chiudere la finestra
    tk.Button(view_window, text="Chiudi", command=view_window.destroy).pack(pady=10)

    view_window.wait_window()
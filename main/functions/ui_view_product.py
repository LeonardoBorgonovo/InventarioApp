import tkinter as tk
from tkinter import ttk
from functions.db_utils import get_all_prodotti, search_prodotti # Importa search_prodotti
from functions.ui_common_utils import create_toplevel_window

def open_view_products_window(parent_root):
    """Apre una finestra per visualizzare tutti i prodotti in una tabella, con funzionalità di ricerca."""
    view_window = create_toplevel_window(parent_root, "Lista Materiali in Magazzino")

    # --- Sezione di Ricerca ---
    search_frame = ttk.LabelFrame(view_window, text="Ricerca Materiali")
    search_frame.pack(padx=10, pady=5, fill="x")

    tk.Label(search_frame, text="Cerca per:").pack(side=tk.LEFT, padx=5, pady=2)
    
    search_query_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_query_var, width=30)
    search_entry.pack(side=tk.LEFT, padx=5, pady=2, fill="x", expand=True)

    search_by_var = tk.StringVar(value="nome_or_codice") # Valore predefinito
    
    # Opzioni di ricerca
    rb_nome = ttk.Radiobutton(search_frame, text="Nome", variable=search_by_var, value="nome")
    rb_nome.pack(side=tk.LEFT, padx=5)
    rb_codice = ttk.Radiobutton(search_frame, text="Codice", variable=search_by_var, value="codice")
    rb_codice.pack(side=tk.LEFT, padx=5)
    rb_entrambi = ttk.Radiobutton(search_frame, text="Nome o Codice", variable=search_by_var, value="nome_or_codice")
    rb_entrambi.pack(side=tk.LEFT, padx=5)

    # Treeview per la visualizzazione dei risultati
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

    # Funzione per caricare i prodotti nella Treeview
    def load_products_into_tree(products_list):
        for i in tree.get_children():
            tree.delete(i) # Pulisci la tabella
        
        if products_list:
            for p in products_list:
                tree.insert("", "end", iid=p[0], values=(
                    p[0], p[1], p[2], p[3] if p[3] else "N/D", p[4], p[5], f"{p[6]:.2f} €" if p[6] is not None else "N/D"
                ))
        else:
            tree.insert("", "end", values=("", "", "Nessun materiale trovato.", "", "", "", ""), tags=('empty',))
            tree.tag_configure('empty', background='#FFDDDD') # Sfondo rosso chiaro per nessun risultato

    # Funzione che verrà chiamata dal pulsante di ricerca
    def perform_search():
        query = search_query_var.get().strip()
        search_type = search_by_var.get()
        
        if query:
            results = search_prodotti(query, search_type)
            load_products_into_tree(results)
        else:
            # Se la query è vuota, mostra tutti i prodotti
            load_products_into_tree(get_all_prodotti())
            
    # Pulsante di ricerca
    search_button = ttk.Button(search_frame, text="Cerca", command=perform_search)
    search_button.pack(side=tk.LEFT, padx=5, pady=2)

    # Pulsante per resettare la ricerca (mostra tutti i prodotti)
    reset_button = ttk.Button(search_frame, text="Reset", command=lambda: [search_query_var.set(""), perform_search()])
    reset_button.pack(side=tk.LEFT, padx=5, pady=2)

    # Inizialmente carica tutti i prodotti
    load_products_into_tree(get_all_prodotti())
    
    # Aggiungi una scrollbar
    scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Bottone per chiudere la finestra
    tk.Button(view_window, text="Chiudi", command=view_window.destroy).pack(pady=10)

    view_window.wait_window()
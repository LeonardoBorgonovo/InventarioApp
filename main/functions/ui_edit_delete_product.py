import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from functions.db_utils import get_all_prodotti, get_prodotto_by_codice, update_prodotto, delete_prodotto, get_prodotto_by_codice, search_prodotti # Importa search_prodotti
from functions.ui_common_utils import stampa_a_video, create_toplevel_window

def open_edit_delete_product_window(parent_root):
    """Apre una finestra per modificare o eliminare prodotti, con funzionalità di ricerca."""
    edit_delete_window = create_toplevel_window(parent_root, "Modifica / Elimina Materiali")

    # --- Sezione di Ricerca ---
    search_frame = ttk.LabelFrame(edit_delete_window, text="Ricerca Materiali")
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

    # Treeview per mostrare i prodotti
    tree = ttk.Treeview(edit_delete_window, columns=("ID", "Codice", "Nome", "UM", "Quantità", "Prezzo"), show="headings")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    tree.heading("ID", text="ID")
    tree.heading("Codice", text="Codice")
    tree.heading("Nome", text="Nome")
    tree.heading("UM", text="UM")
    tree.heading("Quantità", text="Quantità")
    tree.heading("Prezzo", text="Prezzo")

    tree.column("ID", width=40, anchor="center")
    tree.column("Codice", width=100, anchor="w")
    tree.column("Nome", width=150, anchor="w")
    tree.column("UM", width=50, anchor="center")
    tree.column("Quantità", width=80, anchor="center")
    tree.column("Prezzo", width=80, anchor="e")

    # Funzione per caricare i prodotti nella Treeview
    def load_products_into_tree(products_list): # Ora accetta una lista di prodotti da visualizzare
        for i in tree.get_children():
            tree.delete(i) # Pulisci la tabella
        
        if products_list:
            for p in products_list:
                tree.insert("", "end", iid=p[0], values=(
                    p[0], p[1], p[2], p[4], p[5], f"{p[6]:.2f} €" if p[6] is not None else "N/D"
                ))
        else:
            tree.insert("", "end", values=("", "", "Nessun materiale trovato.", "", "", ""), tags=('empty',))
            tree.tag_configure('empty', background='#FFDDDD')

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

    # Sezione per i bottoni Modifica ed Elimina
    button_frame = tk.Frame(edit_delete_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Modifica Materiale Selezionato", command=lambda: handle_edit_product(tree, edit_delete_window, perform_search)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Elimina Materiale Selezionato", command=lambda: handle_delete_product(tree, edit_delete_window, perform_search)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Chiudi", command=edit_delete_window.destroy).pack(side=tk.LEFT, padx=5)

    edit_delete_window.wait_window()

def handle_edit_product(tree_widget, parent_window, refresh_callback):
    selected_item = tree_widget.focus()
    if not selected_item:
        stampa_a_video("Seleziona un materiale dalla lista per modificarlo.")
        return

    product_id = int(selected_item)
    current_product = get_prodotto_by_codice(product_id)

    if not current_product:
        stampa_a_video("Errore: Materiale non trovato nel database.")
        return

    edit_dialog = create_toplevel_window(parent_window, f"Modifica Materiale: {current_product[2]}")

    entries = {}
    
    fields = [
        ("Codice:", 'codice', current_product[1]),
        ("Nome:", 'nome', current_product[2]),
        ("Descrizione:", 'descrizione', current_product[3] if current_product[3] else ''),
        ("Unità di Misura:", 'unita_misura', current_product[4]),
        ("Quantità:", 'quantita', str(current_product[5])),
        ("Prezzo Unitario:", 'prezzo', str(current_product[6]) if current_product[6] is not None else '')
    ]

    for label_text, key, default_value in fields:
        tk.Label(edit_dialog, text=label_text).pack(anchor='w', padx=5, pady=2)
        entry = tk.Entry(edit_dialog)
        entry.insert(0, default_value)
        entry.pack(fill="x", padx=5, pady=2)
        entries[key] = entry

    def save_changes():
        new_codice = entries['codice'].get().strip()
        new_nome = entries['nome'].get().strip()
        new_descrizione = entries['descrizione'].get().strip() if entries['descrizione'].get().strip() else None
        new_unita_misura = entries['unita_misura'].get().strip()
        new_quantita_str = entries['quantita'].get().strip()
        new_prezzo_str = entries['prezzo'].get().strip() if entries['prezzo'].get().strip() else None

        if not new_codice or not new_nome or not new_unita_misura or not new_quantita_str:
            stampa_a_video("Errore: Codice, Nome, Unità di Misura e Quantità sono campi obbligatori!")
            return

        try:
            new_quantita = int(new_quantita_str)
            if new_quantita < 0:
                raise ValueError("La quantità non può essere negativa.")
            new_prezzo = float(new_prezzo_str) if new_prezzo_str else None
        except ValueError:
            stampa_a_video("Errore: Quantità e Prezzo devono essere numeri validi.")
            return

        existing_product_with_new_code = get_prodotto_by_codice(new_codice)
        if existing_product_with_new_code and existing_product_with_new_code[0] != product_id:
            stampa_a_video(f"Errore: Il nuovo codice '{new_codice}' è già utilizzato da un altro materiale.")
            return
            
        success = update_prodotto(product_id, new_codice, new_nome, new_unita_misura, new_quantita, new_descrizione, new_prezzo)

        if success:
            stampa_a_video(f"Materiale '{new_nome}' (Codice: {new_codice}) aggiornato con successo!")
            edit_dialog.destroy()
            refresh_callback() # Ricarica la lista nella Treeview
        else:
            stampa_a_video("Errore durante l'aggiornamento del materiale. Controlla il log.")

    tk.Button(edit_dialog, text="Salva Modifiche", command=save_changes).pack(pady=10)
    tk.Button(edit_dialog, text="Annulla", command=edit_dialog.destroy).pack(pady=5)
    edit_dialog.wait_window()


def handle_delete_product(tree_widget, parent_window, refresh_callback):
    selected_item = tree_widget.focus()
    if not selected_item:
        stampa_a_video("Seleziona un materiale dalla lista per eliminarlo.")
        return

    product_id = int(selected_item)
    product_name = tree_widget.item(selected_item, "values")[2] 

    confirm = messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare il materiale '{product_name}'?")
    if confirm:
        success = delete_prodotto(product_id)
        if success:
            stampa_a_video(f"Materiale '{product_name}' eliminato con successo!")
            refresh_callback() # Ricarica la lista nella Treeview
        else:
            stampa_a_video("Errore durante l'eliminazione del materiale. Controlla il log.")
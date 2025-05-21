import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functions.db_utils import get_all_prodotti, search_prodotti
from functions.ui_common_utils import create_toplevel_window, stampa_a_video
from functions.stampa_utils import stampa_ddt_wrapper 

def open_print_ddt_window(parent_root):
    """Apre una finestra per selezionare i materiali e generare il DDT."""
    print_ddt_window = create_toplevel_window(parent_root, "Stampa DDT")

    # --- Frame Informazioni DDT (Mittente, Destinatario, Causale, Luogo) ---
    info_frame = ttk.LabelFrame(print_ddt_window, text="Dettagli DDT")
    info_frame.pack(padx=10, pady=5, fill="x")

    # Variabili per i dati del DDT
    mittente_var = tk.StringVar(value="TECNOLUX S.n.c.") 
    piva_mittente_var = tk.StringVar(value="02789820228")
    destinatario_var = tk.StringVar()
    piva_destinatario_var = tk.StringVar()
    causale_var = tk.StringVar(value="Vendita") 
    luogo_destinazione_var = tk.StringVar()

    info_grid_row = 0
    tk.Label(info_frame, text="Mittente:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=mittente_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1
    tk.Label(info_frame, text="P.I./C.F. Mittente:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=piva_mittente_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1

    tk.Label(info_frame, text="Destinatario:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=destinatario_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1
    tk.Label(info_frame, text="P.I./C.F. Destinatario:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=piva_destinatario_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1

    tk.Label(info_frame, text="Causale del Trasporto:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=causale_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1
    tk.Label(info_frame, text="Luogo di Destinazione:").grid(row=info_grid_row, column=0, sticky="w", padx=5, pady=2)
    tk.Entry(info_frame, textvariable=luogo_destinazione_var, width=40).grid(row=info_grid_row, column=1, sticky="ew", padx=5, pady=2)
    info_grid_row += 1

    info_frame.grid_columnconfigure(1, weight=1)

    # --- Frame Selezione Materiali ---
    materials_frame = ttk.LabelFrame(print_ddt_window, text="Seleziona Materiali (Doppio click per modificare quantità e selezionare)")
    materials_frame.pack(padx=10, pady=5, fill="both", expand=True)

    # Variabile per il campo di ricerca
    search_query_var = tk.StringVar()

    # Layout per la barra di ricerca
    search_frame = tk.Frame(materials_frame)
    search_frame.pack(padx=5, pady=5, fill="x")

    tk.Label(search_frame, text="Cerca:").pack(side=tk.LEFT, padx=(0, 5))
    search_entry = tk.Entry(search_frame, textvariable=search_query_var)
    search_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
    
    # Opzioni di ricerca (Nome, Codice, Nome o Codice)
    search_by_options = ["Nome o Codice", "Nome", "Codice"]
    search_by_var = tk.StringVar(value=search_by_options[0]) # Default
    search_by_menu = ttk.OptionMenu(search_frame, search_by_var, *search_by_options)
    search_by_menu.pack(side=tk.LEFT, padx=(0, 5))

    # Funzione per l'handler del tasto Invio (Enter)
    def handle_search_key(event):
        perform_search()

    search_entry.bind("<Return>", handle_search_key) # Lega il tasto Invio alla funzione di ricerca

    tree = ttk.Treeview(materials_frame, columns=("ID", "Codice", "Nome", "UM", "Quantità Magazzino", "Seleziona", "Quantità DDT"), show="headings")
    tree.pack(fill="both", expand=True, padx=5, pady=5) # Spostato qui dopo la barra di ricerca

    tree.heading("ID", text="ID")
    tree.heading("Codice", text="Codice")
    tree.heading("Nome", text="Nome")
    tree.heading("UM", text="UM")
    tree.heading("Quantità Magazzino", text="Q.tà Mag.")
    tree.heading("Seleziona", text="Sel.")
    tree.heading("Quantità DDT", text="Q.tà DDT")

    tree.column("ID", width=40, anchor="center")
    tree.column("Codice", width=80, anchor="w")
    tree.column("Nome", width=120, anchor="w")
    tree.column("UM", width=50, anchor="center")
    tree.column("Quantità Magazzino", width=80, anchor="center")
    tree.column("Seleziona", width=50, anchor="center")
    tree.column("Quantità DDT", width=80, anchor="center")

    # Dizionario per tenere traccia dello stato di selezione e della quantità per ogni item
    # key: iid del Treeview (che sarà l'ID numerico del prodotto dal DB convertito a stringa)
    # value: {'product_data': tuple, 'is_selected': Boolean, 'qty_for_ddt': int}
    selected_products_state = {} 

    def load_products_into_tree(products_to_display=None):
        for i in tree.get_children():
            tree.delete(i)
        
        # Non pulire selected_products_state qui se vogliamo mantenere le selezioni
        # durante la ricerca. Puliamo solo le righe del treeview.

        products = products_to_display if products_to_display is not None else get_all_prodotti()
        if products:
            for p in products:
                # p: (id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario)
                item_id_str = str(p[0]) 
                
                # Recupera lo stato esistente o inizializzalo
                current_state = selected_products_state.get(item_id_str, {
                    'product_data': p,
                    'is_selected': False,
                    'qty_for_ddt': 0 
                })
                # Aggiorna i dati del prodotto nel caso siano cambiati nel DB
                current_state['product_data'] = p
                selected_products_state[item_id_str] = current_state

                selection_mark = "✓" if current_state['is_selected'] and current_state['qty_for_ddt'] > 0 else ""
                display_qty_ddt = str(current_state['qty_for_ddt']) if current_state['qty_for_ddt'] > 0 else "0"

                tree.insert("", "end", iid=item_id_str, values=(
                    p[0], p[1], p[2], p[4], p[5], selection_mark, display_qty_ddt 
                ))
        else:
            tree.insert("", "end", iid="no_data_row", values=("", "", "Nessun materiale disponibile", "", "", "", ""), tags=('empty',))
            tree.tag_configure('empty', background='#FFFFAA')
            
    
    def perform_search():
        query = search_query_var.get().strip()
        search_by_option = search_by_var.get()
        
        # Mappa l'opzione di testo alla chiave della funzione di ricerca
        if search_by_option == "Nome":
            search_type = "nome"
        elif search_by_option == "Codice":
            search_type = "codice"
        else: # "Nome o Codice"
            search_type = "nome_or_codice"

        if query:
            results = search_prodotti(query, search_type)
            load_products_into_tree(results)
        else:
            # Se la query è vuota, ricarica tutti i prodotti
            load_products_into_tree()

    search_button = tk.Button(search_frame, text="Cerca", command=perform_search)
    search_button.pack(side=tk.LEFT, padx=(0, 5))

    # --- Funzione per il reset della ricerca ---
    def reset_search():
        search_query_var.set("") # Pulisce il campo di ricerca
        search_by_var.set(search_by_options[0]) # Reimposta l'opzione di ricerca predefinita
        load_products_into_tree() # Ricarica tutti i prodotti (senza filtro)
        stampa_a_video("Ricerca azzerata. Tutti i materiali visualizzati.")

    reset_button = tk.Button(search_frame, text="Reset", command=reset_search)
    reset_button.pack(side=tk.LEFT, padx=(0, 5)) # Posiziona il tasto Reset

    load_products_into_tree() # Carica tutti i prodotti all'apertura

    # Funzione per gestire il doppio click sulla riga
    def on_item_double_click(event):
        item_id = tree.focus() # Ottiene l'iid della riga cliccata (es. "1", "2", o "no_data_row")
        
        if not item_id or item_id == "no_data_row": # Se non c'è selezione o è la riga "nessun dato"
            stampa_a_video("Seleziona un materiale valido dalla lista (doppio click) per modificarlo.")
            return

        current_state = selected_products_state.get(item_id)
        if not current_state:
            stampa_a_video("Errore interno: stato del materiale non trovato per la riga selezionata. Riprova.")
            return 

        product_name = current_state['product_data'][2]
        current_qty_ddt = current_state['qty_for_ddt']
        current_mag_qty = current_state['product_data'][5] # Quantità in magazzino

        # Richiedi la nuova quantità
        new_qty_str = simpledialog.askstring(
            "Modifica Quantità DDT",
            f"Inserisci la quantità per il DDT di '{product_name}'\n"
            f"(Disponibile in magazzino: {current_mag_qty}):",
            initialvalue=str(current_qty_ddt if current_qty_ddt > 0 else current_mag_qty),
            parent=print_ddt_window
        )

        if new_qty_str is None: # Utente ha cliccato Annulla
            return

        try:
            new_qty = float(new_qty_str)
            if new_qty < 0:
                raise ValueError("La quantità non può essere negativa.")
            if new_qty > current_mag_qty:
                raise ValueError(f"Quantità richiesta ({new_qty}) supera la disponibilità ({current_mag_qty}).")

            # Aggiorna lo stato nel dizionario
            selected_products_state[item_id]['qty_for_ddt'] = new_qty
            selected_products_state[item_id]['is_selected'] = (new_qty > 0) # Se la quantità è > 0, consideralo selezionato

            # Aggiorna la visualizzazione nel Treeview
            selection_mark = "✓" if new_qty > 0 else ""
            tree.item(item_id, values=(
                current_state['product_data'][0], # ID originale
                current_state['product_data'][1], # Codice
                current_state['product_data'][2], # Nome
                current_state['product_data'][4], # UM
                current_state['product_data'][5], # Quantità Magazzino
                selection_mark,                   # Selezione
                str(new_qty)                      # Quantità DDT
            ))
        except ValueError as e:
            stampa_a_video(f"Errore quantità: {e}. Inserisci un numero valido.")
            
    tree.bind("<Double-1>", on_item_double_click) # Lega il doppio click alla funzione

    # Funzione per generare il DDT
    def generate_ddt_from_selection():
        selected_products_for_ddt = []
        for item_id, state in selected_products_state.items():
            if item_id != "no_data_row" and state['is_selected'] and state['qty_for_ddt'] > 0:
                original_product_data = list(state['product_data'])
                original_product_data[5] = state['qty_for_ddt'] 
                selected_products_for_ddt.append(tuple(original_product_data))

        if not selected_products_for_ddt:
            stampa_a_video("Nessun materiale selezionato o quantità zero per il DDT.")
            return

        mittente = mittente_var.get().strip()
        piva_mittente = piva_mittente_var.get().strip()
        destinatario = destinatario_var.get().strip()
        piva_destinatario = piva_destinatario_var.get().strip()
        causale = causale_var.get().strip()
        luogo_destinazione = luogo_destinazione_var.get().strip()

        if not mittente or not destinatario or not causale or not luogo_destinazione:
            stampa_a_video("Compila tutti i campi obbligatori (Mittente, Destinatario, Causale, Luogo di Destinazione)!")
            return

        ddt_details = {
            'mittente': {'nome': mittente, 'piva_cf': piva_mittente},
            'destinatario': {'nome': destinatario, 'piva_cf': piva_destinatario},
            'causale': causale,
            'luogo_destinazione': luogo_destinazione
        }

        try:
            stampa_ddt_wrapper(selected_products_for_ddt, ddt_details) 
            messagebox.showinfo("DDT Generato", "DDT generato e magazzino aggiornato con successo!")

            # Ricarica i prodotti per mostrare le quantità aggiornate e resetta lo stato
            load_products_into_tree() 
            selected_products_state.clear() 
            stampa_a_video("DDT generato con successo e magazzino aggiornato.")
            
        except Exception as e:
            messagebox.showerror("Errore Generazione DDT", f"Si è verificato un errore: {e}")

    # --- Bottoni ---
    button_frame = tk.Frame(print_ddt_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Genera DDT", command=generate_ddt_from_selection).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Chiudi", command=print_ddt_window.destroy).pack(side=tk.LEFT, padx=5)

    print_ddt_window.wait_window()
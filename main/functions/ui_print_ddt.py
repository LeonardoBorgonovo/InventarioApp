import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functions.db_utils import get_all_prodotti, search_prodotti
from functions.ui_common_utils import create_toplevel_window, stampa_a_video
from functions.stampa_utils import stampa_ddt_wrapper 

# Per tenere traccia dei prodotti selezionati per il DDT
selected_products_state = {}

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

    tree = ttk.Treeview(materials_frame, columns=("ID", "Codice", "Nome", "UM", "Quantità Magazzino", "Seleziona", "Quantità DDT"), show="headings")
    tree.pack(fill="both", expand=True, padx=5, pady=5)

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

    def load_products_into_tree():
        for i in tree.get_children():
            tree.delete(i)
        selected_products_state.clear() 

        products = get_all_prodotti()
        if products:
            for p in products:
                # p: (id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario)
                # Usiamo l'ID numerico del prodotto come iid della riga del Treeview (convertito a stringa)
                item_id_str = str(p[0]) 
                
                # Inizializza lo stato: non selezionato, quantità 0 per il DDT
                selected_products_state[item_id_str] = {
                    'product_data': p,
                    'is_selected': False,
                    'qty_for_ddt': 0 
                }
                # Visualizza " " per non selezionato, 0 per quantità DDT inizialmente
                tree.insert("", "end", iid=item_id_str, values=(
                    p[0], p[1], p[2], p[4], p[5], "", "0" 
                ))
        else:
            # Se non ci sono prodotti, inserisci una riga speciale che non è un prodotto reale
            tree.insert("", "end", iid="no_data_row", values=("", "", "Nessun materiale disponibile", "", "", "", ""), tags=('empty',))
            tree.tag_configure('empty', background='#FFFFAA')
            
    load_products_into_tree()

    # Funzione per gestire il doppio click sulla riga
    def on_item_double_click(event):
        item_id = tree.focus() # Ottiene l'iid della riga cliccata (es. "1", "2", o "no_data_row")
        
        # --- Aggiungi questa verifica ---
        if not item_id or item_id == "no_data_row": # Se non c'è selezione o è la riga "nessun dato"
            stampa_a_video("Seleziona un materiale valido dalla lista (doppio click) per modificarlo.")
            return

        # L'item_id ottenuto da tree.focus() sarà l'ID numerico del prodotto (come stringa)
        current_state = selected_products_state.get(item_id)
        if not current_state:
            # Questo caso si verifica solo se c'è un iid nel Treeview che non corrisponde
            # a una chiave valida nel nostro dizionario di stato.
            # Dovrebbe essere raro con la logica attuale, ma è una buona safety net.
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
            initialvalue=str(current_qty_ddt if current_qty_ddt > 0 else current_mag_qty), # Prepopola con q.tà attuale per DDT o q.tà magazzino
            parent=print_ddt_window # Associa il simpledialog alla finestra principale del DDT
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
            stampa_a_video(f"Errore quantità: {e}. Inserisci un numero intero valido.")
            
    tree.bind("<Double-1>", on_item_double_click) # Lega il doppio click alla funzione

    # Funzione per generare il DDT
    def generate_ddt_from_selection():
        selected_products_for_ddt = []
        for item_id, state in selected_products_state.items():
            # Assicurati che l'item_id non sia la riga speciale di "nessun dato"
            if item_id != "no_data_row" and state['is_selected'] and state['qty_for_ddt'] > 0:
                original_product_data = list(state['product_data'])
                # Sostituisci la quantità in magazzino con la quantità per il DDT
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

            # --- AGGIUNGI QUESTE RIGHE per aggiornare la UI ---
            load_products_into_tree() # Ricarica i prodotti per mostrare le quantità aggiornate
            selected_products_state.clear() # Pulisci lo stato dei prodotti selezionati
            stampa_a_video("DDT generato con successo e magazzino aggiornato.")
            
        except Exception as e:
            messagebox.showerror("Errore Generazione DDT", f"Si è verificato un errore: {e}")

    # --- Bottoni ---
    button_frame = tk.Frame(print_ddt_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Genera DDT", command=generate_ddt_from_selection).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Chiudi", command=print_ddt_window.destroy).pack(side=tk.LEFT, padx=5)

    print_ddt_window.wait_window()
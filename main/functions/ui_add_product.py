import tkinter as tk
from tkinter import messagebox
from functions.db_utils import insert_prodotto, get_prodotto_by_codice
from functions.ui_common_utils import stampa_a_video, create_toplevel_window

def open_add_product_window(parent_root):
    """Apre una finestra per aggiungere un nuovo prodotto."""
    add_window = create_toplevel_window(parent_root, "Aggiungi Nuovo Materiale")

    # Dizionario per tenere traccia delle entry widget
    entries = {}

    tk.Label(add_window, text="Codice Materiale:").pack(anchor='w', padx=5, pady=2)
    entries['codice'] = tk.Entry(add_window)
    entries['codice'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_window, text="Nome Materiale:").pack(anchor='w', padx=5, pady=2)
    entries['nome'] = tk.Entry(add_window)
    entries['nome'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_window, text="Descrizione (opzionale):").pack(anchor='w', padx=5, pady=2)
    entries['descrizione'] = tk.Entry(add_window)
    entries['descrizione'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_window, text="Unità di Misura (es: pz, kg):").pack(anchor='w', padx=5, pady=2)
    entries['unita_misura'] = tk.Entry(add_window)
    entries['unita_misura'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_window, text="Quantità Disponibile:").pack(anchor='w', padx=5, pady=2)
    entries['quantita'] = tk.Entry(add_window)
    entries['quantita'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_window, text="Prezzo Unitario (opzionale):").pack(anchor='w', padx=5, pady=2)
    entries['prezzo'] = tk.Entry(add_window)
    entries['prezzo'].pack(fill="x", padx=5, pady=2)

    tk.Button(add_window, text="Salva Materiale",
              command=lambda: handle_add_product(entries, add_window)
             ).pack(pady=10)

    tk.Button(add_window, text="Annulla", command=add_window.destroy).pack(pady=5)

    add_window.wait_window() # Attendi che la finestra secondaria venga chiusa


def handle_add_product(entries, window_to_close):
    """Gestisce la logica di aggiunta di un prodotto dall'interfaccia utente."""
    codice = entries['codice'].get().strip()
    nome = entries['nome'].get().strip()
    descrizione = entries['descrizione'].get().strip() if entries['descrizione'].get().strip() else None
    unita_misura = entries['unita_misura'].get().strip()
    quantita_str = entries['quantita'].get().strip()
    prezzo_str = entries['prezzo'].get().strip() if entries['prezzo'].get().strip() else None

    if not codice or not nome or not unita_misura or not quantita_str:
        stampa_a_video("Errore: Codice, Nome, Unità di Misura e Quantità sono campi obbligatori!")
        return

    try:
        quantita = float(quantita_str)
        if quantita < 0:
            raise ValueError("La quantità non può essere negativa.")
        prezzo = float(prezzo_str) if prezzo_str else None
    except ValueError:
        stampa_a_video("Errore: Quantità e Prezzo devono essere numeri validi.")
        return

    if get_prodotto_by_codice(codice):
        stampa_a_video(f"Errore: Il materiale con codice '{codice}' esiste già. Usa un codice unico.")
        return

    success = insert_prodotto(codice, nome, unita_misura, quantita, descrizione, prezzo)

    if success:
        stampa_a_video(f"Materiale '{nome}' (Codice: {codice}) aggiunto con successo!")
        # Pulisci i campi
        for entry in entries.values():
            entry.delete(0, tk.END)
        window_to_close.destroy() # Chiudi la finestra dopo il successo
    else:
        stampa_a_video("Errore generico durante il salvataggio del materiale. Controlla il log.")
import tkinter as tk
from tkinter import messagebox
from functions.db_utils import insert_prodotto, get_prodotto_by_codice # Importa solo le funzioni CRUD necessarie

def create_add_product_frame(parent_frame):
    """Crea e restituisce un LabelFrame per l'aggiunta di nuovi prodotti."""
    add_product_frame = tk.LabelFrame(parent_frame, text="Aggiungi Nuovo Prodotto")
    add_product_frame.pack(padx=10, pady=10, fill="x", expand=True)

    # Campi di input
    entries = {} # Dizionario per tenere traccia delle entry widget

    tk.Label(add_product_frame, text="Codice Prodotto:").pack(anchor='w', padx=5, pady=2)
    entries['codice'] = tk.Entry(add_product_frame)
    entries['codice'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_product_frame, text="Nome Prodotto:").pack(anchor='w', padx=5, pady=2)
    entries['nome'] = tk.Entry(add_product_frame)
    entries['nome'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_product_frame, text="Descrizione (opzionale):").pack(anchor='w', padx=5, pady=2)
    entries['descrizione'] = tk.Entry(add_product_frame)
    entries['descrizione'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_product_frame, text="Unità di Misura (es: pz, kg):").pack(anchor='w', padx=5, pady=2)
    entries['unita_misura'] = tk.Entry(add_product_frame)
    entries['unita_misura'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_product_frame, text="Quantità Disponibile:").pack(anchor='w', padx=5, pady=2)
    entries['quantita'] = tk.Entry(add_product_frame)
    entries['quantita'].pack(fill="x", padx=5, pady=2)

    tk.Label(add_product_frame, text="Prezzo Unitario (opzionale):").pack(anchor='w', padx=5, pady=2)
    entries['prezzo'] = tk.Entry(add_product_frame)
    entries['prezzo'].pack(fill="x", padx=5, pady=2)

    # Bottone di salvataggio
    tk.Button(add_product_frame, text="Aggiungi Prodotto",
              command=lambda: handle_add_product(entries)
             ).pack(pady=10)

    return add_product_frame

def handle_add_product(entries):
    """Gestisce la logica di aggiunta di un prodotto dall'interfaccia utente."""
    codice = entries['codice'].get().strip()
    nome = entries['nome'].get().strip()
    descrizione = entries['descrizione'].get().strip() if entries['descrizione'].get().strip() else None
    unita_misura = entries['unita_misura'].get().strip()
    quantita_str = entries['quantita'].get().strip()
    prezzo_str = entries['prezzo'].get().strip() if entries['prezzo'].get().strip() else None

    # Validazione input
    if not codice or not nome or not unita_misura or not quantita_str:
        messagebox.showerror("Errore", "Codice, Nome, Unità di Misura e Quantità sono campi obbligatori!")
        return

    try:
        quantita = int(quantita_str)
        if quantita < 0:
            raise ValueError("La quantità non può essere negativa.")
        prezzo = float(prezzo_str) if prezzo_str else None
    except ValueError:
        messagebox.showerror("Errore", "Quantità e Prezzo devono essere numeri validi.")
        return

    # Controlla se il codice prodotto esiste già usando la funzione di basso livello
    if get_prodotto_by_codice(codice):
        messagebox.showerror("Errore", f"Il prodotto con codice '{codice}' esiste già. Usa un codice unico.")
        return

    # Chiama la funzione di basso livello per inserire il prodotto nel DB
    success = insert_prodotto(codice, nome, unita_misura, quantita, descrizione, prezzo)

    if success:
        messagebox.showinfo("Successo", f"Prodotto '{nome}' (Codice: {codice}) aggiunto con successo!")
        # Pulisci i campi
        for entry in entries.values():
            entry.delete(0, tk.END)
    else:
        messagebox.showerror("Errore", "Impossibile aggiungere il prodotto. Controlla il log per i dettagli (es. errore DB).")
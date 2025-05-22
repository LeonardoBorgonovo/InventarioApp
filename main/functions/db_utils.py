import sqlite3
import os
import sys

# Importa il percorso persistente del database dal modulo data_manager.
# Questo è il percorso dove il database verrà effettivamente salvato e letto
# sul sistema dell'utente, garantendo la persistenza dei dati.
from .data_manager import PERSISTENT_DB_PATH

# Il percorso del database non deve più essere costruito qui,
# ma deve usare la variabile PERSISTENT_DB_PATH importata.
# DATABASE_PATH = os.path.join(os.path.dirname(__file__),'..','db','inventario.db')

def create_connection():
    """Crea una connessione al database SQLite utilizzando il percorso persistente."""
    try:
        # La directory per PERSISTENT_DB_PATH viene creata da initialize_data_files()
        # all'avvio dell'applicazione. Non è più necessario chiamare os.makedirs qui.
        conn = sqlite3.connect(PERSISTENT_DB_PATH) # Usa il percorso persistente
        return conn
    except sqlite3.Error as e:
        print(f"Errore di connessione al database: {e}")
        # In caso di errore critico, potrebbe essere utile uscire dall'applicazione
        # o mostrare un messaggio all'utente.
        sys.exit(1) # Termina l'applicazione in caso di errore grave di connessione
        return None

def create_tables():
    """Crea le tabelle necessarie nel database, se non esistono."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prodotti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codice TEXT NOT NULL UNIQUE,
                    nome TEXT NOT NULL,
                    descrizione TEXT,
                    unita_misura TEXT NOT NULL,
                    quantita_disponibile REAL NOT NULL,
                    prezzo_unitario REAL
                )
            ''')
            conn.commit()
            print("Tabelle create o già esistenti.")
        except sqlite3.Error as e:
            print(f"Errore DB durante la creazione delle tabelle: {e}")
        finally:
            conn.close()
    else:
        print("Impossibile creare le tabelle senza una connessione al database.")

# --- Funzioni CRUD per i Prodotti ---
# Tutte le funzioni CRUD (insert_prodotto, get_prodotto_by_codice, get_all_prodotti,
# search_prodotti, update_prodotto, delete_prodotto) chiamano create_connection().
# Poiché create_connection() ora utilizza PERSISTENT_DB_PATH, tutte queste funzioni
# opereranno automaticamente sul database persistente corretto.

# --- INSERISCE PRODOTTI ---
def insert_prodotto(codice, nome, unita_misura, quantita_disponibile, descrizione=None, prezzo_unitario=None):
    """Inserisce un nuovo prodotto nel database. Restituisce True se successo, False altrimenti."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prodotti (codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Errore DB: Codice prodotto '{codice}' già esistente.")
            return False
        except sqlite3.Error as e:
            print(f"Errore DB durante l'inserimento del prodotto: {e}")
            return False
        finally:
            conn.close()
    return False

def get_prodotto_by_codice(codice):
    """Recupera un prodotto tramite il suo codice. Restituisce la tupla del prodotto o None."""
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario FROM prodotti WHERE codice = ?", (codice,))
            result = cursor.fetchone()  

            return result
        except sqlite3.Error as e:
            print(f"ERRORE SQLite in get_prodotto_by_codice: {e}")
            return None
        finally:
            conn.close()
    
    return None

# --- OTTIENE TUTTI I PRODOTTI ---
def get_all_prodotti():
    """Recupera tutti i prodotti dal database. Restituisce una lista di tuple."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario FROM prodotti ORDER BY nome")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Errore DB durante il recupero di tutti i prodotti: {e}")
            return []
        finally:
            conn.close()
    return []

# --- FUNZIONE DI RICERCA ---
def search_prodotti(query, search_by="nome_or_codice"):
    """
    Cerca prodotti nel database.
    search_by può essere "nome", "codice", o "nome_or_codice".
    """
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sql_query = "SELECT id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario FROM prodotti WHERE "
            params = []

            if search_by == "nome":
                sql_query += "nome LIKE ?"
                params.append(f"%{query}%")
            elif search_by == "codice":
                sql_query += "codice LIKE ?"
                params.append(f"%{query}%")
            elif search_by == "nome_or_codice":
                sql_query += "nome LIKE ? OR codice LIKE ?"
                params.append(f"%{query}%")
                params.append(f"%{query}%")
            else:
                # Fallback, ritorna tutti i prodotti se il tipo di ricerca non è valido
                return get_all_prodotti()

            sql_query += " ORDER BY nome" # Ordina sempre per nome
            cursor.execute(sql_query, tuple(params))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Errore DB durante la ricerca dei prodotti: {e}")
            return []
        finally:
            conn.close()
    return []

# --- FUNZIONE DI AGGIORNAMENTO PRODOTTI ---
def update_prodotto(id_prodotto, codice, nome, unita_misura, quantita_disponibile, descrizione=None, prezzo_unitario=None):
    """Aggiorna i dati di un prodotto esistente tramite il suo ID."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE prodotti SET codice = ?, nome = ?, descrizione = ?, unita_misura = ?, quantita_disponibile = ?, prezzo_unitario = ?
                WHERE id = ?
            ''', (codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario, id_prodotto))
            conn.commit()
            return cursor.rowcount > 0 # True se una riga è stata aggiornata, False altrimenti
        except sqlite3.IntegrityError:
            print(f"Errore DB: Codice prodotto '{codice}' già esistente per un altro prodotto.")
            return False
        except sqlite3.Error as e:
            print(f"Errore DB durante l'aggiornamento del prodotto: {e}")
            return False
        finally:
            conn.close()
    return False

# --- FUNZIONE DI ELIMINAZIONE ---
def delete_prodotto(id_prodotto):
    """Elimina un prodotto dal database tramite il suo ID."""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prodotti WHERE id = ?", (id_prodotto,))
            conn.commit()
            return cursor.rowcount > 0 # True se una riga è stata eliminata, False altrimenti
        except sqlite3.Error as e:
            print(f"Errore DB durante l'eliminazione del prodotto: {e}")
            return False
        finally:
            conn.close()
    return False
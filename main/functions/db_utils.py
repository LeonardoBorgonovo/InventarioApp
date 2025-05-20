import sqlite3
import os

DATABASE_PATH = '../../../db/inventario.db' # Aggiornato con il percorso della cartella 'db'

def create_connection():
    """Crea una connessione al database SQLite."""
    try:
        # Assicurati che la directory esista prima di connetterti
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Errore di connessione al database: {e}")
        return None

def create_tables():
    """Crea le tabelle necessarie nel database, se non esistono."""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prodotti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                descrizione TEXT,
                unita_misura TEXT NOT NULL,
                quantita_disponibile INTEGER NOT NULL,
                prezzo_unitario REAL
            )
        ''')
        conn.commit()
        conn.close()
        print("Tabelle create o già esistenti.")
    else:
        print("Impossibile creare le tabelle senza una connessione al database.")

# --- Funzioni CRUD per i Prodotti ---
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
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Errore DB durante il recupero del prodotto: {e}")
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
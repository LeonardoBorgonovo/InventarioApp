# InventarioApp/main/functions/data_manager.py

import os
import sys
import shutil

# --- Funzione per ottenere il percorso della cartella dati dell'applicazione ---
def get_app_data_dir():
    """Restituisce il percorso della directory permanente per i dati dell'applicazione."""
    if sys.platform.startswith('win'):
        app_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), "InventarioApp")
    elif sys.platform.startswith('darwin'):
        app_data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', "InventarioApp")
    else: # Linux
        app_data_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', "InventarioApp")
    
    os.makedirs(app_data_dir, exist_ok=True)
    return app_data_dir

# --- Funzione per ottenere il percorso delle risorse incluse da PyInstaller (modello) ---
def get_bundled_resource_path(relative_path_from_bundle_root):
    """
    Restituisce il percorso assoluto di una risorsa all'interno del bundle PyInstaller
    o nella struttura di sviluppo quando non è impacchettato.
    `relative_path_from_bundle_root` deve essere il percorso relativo
    dalla directory InventarioApp/ (la root del tuo progetto di sviluppo)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path_from_bundle_root)
    else:
        # Quando eseguiamo in modalità sviluppo, questo script è in
        # InventarioApp/main/functions/. Dobbiamo risalire a InventarioApp/
        # __file__ -> InventarioApp/main/functions/data_manager.py
        # os.path.dirname(__file__) -> InventarioApp/main/functions/
        # os.path.dirname(os.path.dirname(__file__)) -> InventarioApp/main/
        # os.path.dirname(os.path.dirname(os.path.dirname(__file__))) -> InventarioApp/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(project_root, relative_path_from_bundle_root)

# --- Logica per la gestione dei percorsi dei file (eseguita all'importazione del modulo) ---
app_data_location = get_app_data_dir()

persistent_db_filename = "inventario.db"
persistent_counter_filename = "ddt_counter.txt"

# Variabili che verranno usate in tutto il tuo codice per i percorsi persistenti
PERSISTENT_DB_PATH = os.path.join(app_data_location, persistent_db_filename)
PERSISTENT_COUNTER_PATH = os.path.join(app_data_location, persistent_counter_filename)

# Percorsi dei file "modello" all'interno del bundle PyInstaller
# Questi devono corrispondere a come li hai inclusi con --add-data
BUNDLED_DB_MODEL_PATH = get_bundled_resource_path(os.path.join("main", "db", "inventario.db"))
BUNDLED_COUNTER_MODEL_PATH = get_bundled_resource_path(os.path.join("main", "counter", "ddt_counter.txt"))

# --- Gestione del primo avvio: copia i modelli se i file persistenti non esistono ---
def initialize_data_files():
    """
    Questa funzione deve essere chiamata una volta all'avvio dell'applicazione principale.
    """
    print("Inizializzazione dei file dati dell'applicazione...")
    if not os.path.exists(PERSISTENT_DB_PATH):
        print(f"Database persistente non trovato in {PERSISTENT_DB_PATH}. Copia dal modello...")
        try:
            shutil.copy(BUNDLED_DB_MODEL_PATH, PERSISTENT_DB_PATH)
        except FileNotFoundError as e:
            print(f"ERRORE GRAVE: Impossibile copiare il database modello. Controlla --add-data in PyInstaller. {e}")
            sys.exit(1) # Esci dall'applicazione se il database iniziale non può essere copiato
    else:
        print(f"Database persistente già esistente in {PERSISTENT_DB_PATH}.")

    if not os.path.exists(PERSISTENT_COUNTER_PATH):
        print(f"Contatore persistente non trovato in {PERSISTENT_COUNTER_PATH}. Copia dal modello...")
        try:
            shutil.copy(BUNDLED_COUNTER_MODEL_PATH, PERSISTENT_COUNTER_PATH)
        except FileNotFoundError as e:
            print(f"ERRORE GRAVE: Impossibile copiare il contatore modello. Controlla --add-data in PyInstaller. {e}")
            sys.exit(1) # Esci dall'applicazione
    else:
        print(f"Contatore persistente già esistente in {PERSISTENT_COUNTER_PATH}.")

    print("Inizializzazione file dati completata.")

# La chiamata a initialize_data_files() non deve essere qui direttamente,
# ma nel tuo script principale (inventario.py)
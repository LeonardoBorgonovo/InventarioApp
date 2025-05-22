import os

def get_desktop_path():
    """Restituisce il percorso assoluto della cartella Desktop."""
    if os.name == 'nt':  # Windows
        desktop_path = os.path.join(os.environ.get('USERPROFILE') or os.environ.get('HOMEPATH'), 'Desktop')
    elif os.name == 'posix':  # macOS o Linux
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    else:
        print("Sistema operativo non riconosciuto per trovare il Desktop.")
        return None
    return desktop_path

def create_app_folder_on_desktop(folder_name="LaMiaAppFolder"):
    """
    Crea una cartella sul desktop dell'utente per l'applicazione.
    Restituisce il percorso completo della cartella creata.
    """
    desktop_path = get_desktop_path()
    if not desktop_path:
        print("Impossibile trovare il percorso del Desktop.")
        return None

    app_folder_path = os.path.join(desktop_path, folder_name)

    if not os.path.exists(app_folder_path):
        try:
            os.makedirs(app_folder_path)
            print(f"Cartella '{folder_name}' creata su: {app_folder_path}")
        except OSError as e:
            print(f"Errore durante la creazione della cartella '{folder_name}': {e}")
            return None
    else:
        print(f"La cartella '{folder_name}' esiste già su: {app_folder_path}")
    
    return app_folder_path
# Gestione Materiali e DDT

Un'applicazione desktop semplice e intuitiva per la gestione del magazzino e la generazione di Documenti di Trasporto (DDT), sviluppata in Python con Tkinter e SQLite. Ideale per piccole e medie imprese che necessitano di tracciare i propri materiali e emettere DDT in modo efficiente.

## Indice

- [Caratteristiche Principali](#caratteristiche-principali)
- [Requisiti di Sistema](#requisiti-di-sistema)
- [Installazione](#installazione)
  - [Da Codice Sorgente](#da-codice-sorgente)
  - [Da Eseguibile (Presto Disponibile)](#da-eseguibile-presto-disponibile)
- [Come Usare](#come-usare)
  - [Aggiungere un Nuovo Materiale](#aggiungere-un-nuovo-materiale)
  - [Visualizzare e Modificare Materiali](#visualizzare-e-modificare-materiali)
  - [Generare un DDT](#generare-un-ddt)
- [Struttura del Progetto](#struttura-del-progetto)
- [Contributi](#contributi)
- [Licenza](#licenza)
- [Contatti](#contatti)

## Caratteristiche Principali

* **Gestione Anagrafica Materiali:** Aggiungi, visualizza, modifica e rimuovi materiali con codice, nome, descrizione, unità di misura, quantità disponibile e prezzo unitario.
* **Gestione Magazzino:** Monitora la quantità disponibile di ogni materiale.
* **Generazione DDT:** Crea Documenti di Trasporto personalizzabili, selezionando i materiali dal magazzino e specificando le quantità.
* **Aggiornamento Automatico Magazzino:** Le quantità dei materiali vengono automaticamente decrementate dal magazzino dopo la generazione di un DDT.
* **Ricerca Avanzata:** Funzionalità di ricerca per codice o nome materiale con opzione di reset.
* **Interfaccia Utente Intuitiva:** Sviluppata con Tkinter per una facile navigazione.
* **Database Locale:** Utilizza SQLite per una gestione dei dati semplice e senza necessità di configurazioni server esterne.
* **Supporto Quantità Decimali:** Gestione accurata delle quantità con numeri in virgola mobile.

## Requisiti di Sistema

* **Sistema Operativo:** Windows, macOS, Linux
* **Python:** Versione 3.x (si consiglia 3.8 o superiore)
* **Librerie Python:**
    * `tkinter` (solitamente inclusa con Python)
    * `sqlite3` (inclusa con Python)
    * `reportlab` (per la generazione di PDF - dovrà essere installata)
    * `openpyxl` (se prevedi funzionalità di import/export da Excel in futuro, altrimenti rimuovi)

## Installazione

### Da Codice Sorgente

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/IL_TUO_USERNAME/IL_TUO_REPO.git](https://github.com/IL_TUO_USERNAME/IL_TUO_REPO.git)
    cd IL_TUO_REPO
    ```
    *(Sostituisci `IL_TUO_USERNAME` e `IL_TUO_REPO` con i tuoi dati reali)*

2.  **Crea e attiva un ambiente virtuale (consigliato):**
    ```bash
    python -m venv venv
    # Su Windows:
    .\venv\Scripts\activate
    # Su macOS/Linux:
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install reportlab openpyxl # Rimuovi openpyxl se non lo usi
    ```

4.  **Avvia l'applicazione:**
    ```bash
    python main_app.py # O il nome del tuo file principale
    ```

### Da Eseguibile (Presto Disponibile)

* *(Qui potrai aggiungere istruzioni su come scaricare e avviare l'eseguibile, una volta che lo avrai generato con PyInstaller o strumenti simili.)*
* *(Esempio: Scarica l'ultima versione dell'eseguibile dalla sezione [Releases](https://github.com/IL_TUO_USERNAME/IL_TUO_REPO/releases) e lancialo direttamente.)*

## Come Usare

### Aggiungere un Nuovo Materiale

1.  Dalla finestra principale, clicca su "Aggiungi Materiale".
2.  Compila i campi richiesti (Codice, Nome, Unità di Misura, Quantità Disponibile).
    * Le quantità possono essere numeri interi o decimali (es. `10` o `10.5`).
    * Utilizza il punto (`.`) o la virgola (`,`) come separatore decimale; l'applicazione gestirà automaticamente la conversione.
3.  Clicca "Salva Materiale".

### Visualizzare e Modificare Materiali

* La finestra principale mostrerà un elenco di tutti i materiali.
* *(Aggiungi qui istruzioni su come modificare i materiali esistenti, se hai implementato questa funzionalità. Es: "Doppio click su un materiale per modificarne i dettagli.")*

### Generare un DDT

1.  Dalla finestra principale, clicca su "Stampa DDT".
2.  Compila i dettagli del DDT (Mittente, Destinatario, Causale, Luogo di Destinazione).
3.  Nella sezione "Seleziona Materiali":
    * Cerca i materiali per nome o codice usando la barra di ricerca.
    * **Doppio click** su una riga per specificare la quantità di quel materiale da includere nel DDT. Puoi inserire quantità decimali.
    * La quantità disponibile in magazzino verrà mostrata come riferimento.
4.  Una volta selezionati tutti i materiali e le relative quantità, clicca "Genera DDT".
5.  Il DDT verrà salvato come PDF nella cartella `output/ddt` (o la tua cartella configurata) e la quantità dei materiali usati verrà automaticamente decrementata dal magazzino.

## Struttura del Progetto

.
├── main_app.py             # Punto di ingresso dell'applicazione
├── functions/              # Contiene le funzioni logiche modulari
│   ├── init.py
│   ├── db_utils.py         # Funzioni per l'interazione con il database SQLite
│   ├── ui_common_utils.py  # Funzioni utili per l'interfaccia utente (es. stampa_a_video)
│   ├── ui_add_product.py   # Logica e UI per l'aggiunta di prodotti
│   ├── ui_print_ddt.py     # Logica e UI per la generazione del DDT
│   └── stampa_utils.py     # Funzioni per la generazione del PDF del DDT
├── database/               # Cartella per il file del database SQLite (es. magazzino.db)
├── output/                 # Cartella per i DDT generati
│   └── ddt/
└── README.md               # Questo file!


## Contributi

I contributi sono i benvenuti! Se hai idee per nuove funzionalità, miglioramenti o correzioni di bug, non esitare a:

1.  Forkare il repository.
2.  Creare un nuovo branch (`git checkout -b feature/NomeNuovaFunzionalita`).
3.  Effettuare le modifiche e committarle (`git commit -m 'Aggiunta nuova funzionalità X'`).
4.  Pushare il branch (`git push origin feature/NomeNuovaFunzionalita`).
5.  Aprire una Pull Request.

## Licenza

Questo progetto è rilasciato senza licenza

## Contatti

Per domande o suggerimenti, puoi contattare l'autore all'indirizzo:
[leonardo.borgonovo@mat.tn.it](leonardo.borgonovo@mat.tn.it)

---

import os
import sqlite3
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 # Usiamo A4, che è più comune in Italia
from reportlab.lib.units import cm, inch, mm # Possiamo usare diverse unità
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from functions.find_desktop import create_app_folder_on_desktop
from .data_manager import PERSISTENT_DB_PATH, PERSISTENT_COUNTER_PATH
import subprocess 

# Percorso per il file contatore DDT (relativo alla posizione di questo script)
DDT_COUNTER_FILE = PERSISTENT_COUNTER_PATH
# Percorso per il database (relativo alla posizione di questo script)
DATABASE_PATH_FOR_STAMPA_UTILS = PERSISTENT_DB_PATH # Usa il percorso persistente

# --- Nuova gestione del percorso di output dei PDF ---
DDT_FOLDER_NAME = "DDT_AppInventario" 
# Ottieni il percorso dinamico per la cartella di output dei PDF
DDT_OUTPUT_PATH = create_app_folder_on_desktop(DDT_FOLDER_NAME)

# Se DDT_OUTPUT_PATH è None (es. sistema operativo non riconosciuto o errore creazione),

if DDT_OUTPUT_PATH is None:
    print("ERRORE: Impossibile determinare il percorso di output per i PDF. La generazione del DDT potrebbe fallire.")
    

# --- Funzioni per il contatore DDT ---
def get_current_ddt_number():
    """Legge il numero corrente di DDT dal file."""
    try:
        with open(DDT_COUNTER_FILE, "r") as f:
            current_number = int(f.read().strip())
    except FileNotFoundError:
        current_number = 1
    return current_number

def get_next_ddt_number():
    """Legge l'ultimo numero di DDT dal file, lo incrementa e lo salva."""
    last_number = get_current_ddt_number()
    next_number = last_number + 1
    with open(DDT_COUNTER_FILE, "w") as f:
        f.write(str(next_number))
    return next_number

# Funzione per decrementare le quantità in magazzino
def decrementa_quantita_magazzino(prodotti_da_aggiornare):
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH_FOR_STAMPA_UTILS)
        cursor = conn.cursor()

        for id_prodotto, quantita_per_ddt in prodotti_da_aggiornare:
            # Aggiungi una stampa per vedere cosa sta tentando di aggiornare
            print(f"DEBUG (decrementa): Tentando di aggiornare ID {id_prodotto} sottraendo {quantita_per_ddt}")

            cursor.execute(
                "UPDATE prodotti SET quantita_disponibile = quantita_disponibile - ? WHERE id = ?",
                (quantita_per_ddt, id_prodotto)
            )

            # Aggiungi una stampa per vedere se la riga è stata modificata
            # (rowcount > 0 indica che almeno una riga è stata influenzata dall'UPDATE)
            if cursor.rowcount > 0:
                print(f"DEBUG (decrementa): Aggiornato con successo ID {id_prodotto}.")
            else:
                print(f"DEBUG (decrementa): Nessuna riga aggiornata per ID {id_prodotto}. Potrebbe non esistere o quantità già a zero.")


        conn.commit()
        print("DEBUG (decrementa): Quantità magazzino aggiornate con successo e commit eseguito!")

    except sqlite3.Error as e:
        print(f"ERRORE GRAVE (decrementa_quantita_magazzino): {e}")
        if conn:
            conn.rollback() # Annulla le modifiche in caso di errore
            print("DEBUG (decrementa): Rollback eseguito a causa dell'errore.")
    finally:
        if conn:
            conn.close()
            print("DEBUG (decrementa): Connessione DB chiusa.")

# --- Costanti e Variabili di Layout (prese dal tuo codice originale) ---
PAGE_WIDTH, PAGE_HEIGHT = A4

# Margini (definizione aggiunta)
margin_bottom = 0.5 * inch # Un margine inferiore per la pagina

# Stili Globali per Testo e Linee (definiti qui per coerenza)
line_color = colors.black
text_color = colors.black
fill_color_header = colors.HexColor('#4A4A4A') # Grigio scuro per le intestazioni

# Intestazione principale (Rettangolo grigio scuro e testo bianco)
header_height = 0.5 * inch
header_y = PAGE_HEIGHT - header_height - (0.5 * inch)

# Area Mittente / Destinatario / Dati DDT
box_margin_top = 0.3 * inch
box_padding_left = 0.2 * inch
line_indent = 0.2 * inch # Indentazione delle linee dai bordi del box

# Coordinate di riferimento Y per le caselle (dal basso)
current_y_top = header_y - box_margin_top # Bordo superiore delle caselle

# Definiamo altezze e larghezze per coerenza
single_line_box_height = 0.45 * inch
double_line_box_height = 0.75 * inch

# Larghezze delle colonne
left_col_x = 0.5 * inch
right_col_x = (PAGE_WIDTH / 2) + (0.25 * inch)
col_width = (PAGE_WIDTH / 2) - left_col_x - (0.15 * inch) # Meno un po' di spazio centrale

# MITTENTE box
mittente_box_height = double_line_box_height + 0.5 * inch # Altezza leggermente maggiore per P.I./C.F.
mittente_y_bottom = current_y_top - mittente_box_height

# CAMPI DDT (N. / DEL)
ddt_box_height = single_line_box_height + single_line_box_height # Due linee di testo
ddt_y_bottom = current_y_top - ddt_box_height
ddt_num_line_y = current_y_top - (0.8 * inch) # Un po' sotto "N."
ddt_del_line_y = current_y_top - (0.8 * inch) # Stessa Y per la linea DEL

# DESTINATARIO box
destinatario_box_height = ddt_box_height # Stessa altezza del box DDT
destinatario_y_bottom = ddt_y_bottom - (0.1 * inch) - destinatario_box_height # Margine sotto box DDT

# Aggiorna la posizione Y corrente dopo l'area superiore (per causale/luogo)
current_y_bottom_of_top_boxes = mittente_y_bottom
if destinatario_y_bottom < current_y_bottom_of_top_boxes:
    current_y_bottom_of_top_boxes = destinatario_y_bottom

# CAUSALE DEL TRASPORTO box
causale_height = single_line_box_height + 0.2 * inch
causale_y_bottom = current_y_bottom_of_top_boxes - (0.1 * inch) - causale_height

# LUOGO DI DESTINAZIONE box
luogo_height = single_line_box_height + 0.2 * inch
luogo_y_bottom = causale_y_bottom - (0.1 * inch) - luogo_height

# TABELLA DESCRIZIONE BENI
table_y_start = luogo_y_bottom - (0.5 * inch) # Spazio dalla casella precedente
table_available_width = PAGE_WIDTH - (1.80 * left_col_x) # Larghezza disponibile per la tabella

# SEZIONE INFERIORE - TRASPORTO A MEZZO, DATA RITIRO, ANNOTAZIONI, FIRME
section_bottom_margin_top = 0.5 * inch

# TRASPORTO A MEZZO
trasporto_box_height = 0.8 * inch

# DATA RITIRO (usa la stessa altezza del trasporto)
data_ritiro_box_height = trasporto_box_height

# ANNOTAZIONI
annotazioni_box_height = 0.8 * inch
# annotazioni_box_y_bottom verrà calcolata dinamicamente in add_footer_elements

# SEZIONE FIRME (UNA ACCANTO ALL'ALTRA)
# firme_section_top_y sarà calcolata dinamicamente in add_footer_elements
firma_block_height = 0.3 * inch # Altezza stimata per ogni blocco firma (etichetta + linea)
firme_available_width = PAGE_WIDTH - (2 * left_col_x)
firma_col_width = firme_available_width / 3

# Le coordinate di x per le firme sono fisse
firma1_x = left_col_x
firma2_x = firma1_x + firma_col_width
firma3_x = firma2_x + firma_col_width


# --- Funzione per aggiungere gli elementi fissi del DDT a una pagina ---
# Questa funzione usa le coordinate definite sopra
def add_fixed_elements(c, ddt_number, ddt_date, page_num, total_pages, ddt_details):
    c.setStrokeColor(line_color) # Colore predefinito per le linee
    c.setFillColor(text_color)   # Colore predefinito per il testo
    c.setLineWidth(1) # Spessore linea standard

    # --- Intestazione principale (Rettangolo grigio scuro e testo bianco) ---
    c.setFillColor(fill_color_header)
    c.rect(0, header_y, PAGE_WIDTH, header_height, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_WIDTH / 2, header_y + (header_height / 2) - (16/2.5), "DOCUMENTO DI TRASPORTO")

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)

    # --- MITTENTE box ---
    c.rect(left_col_x, mittente_y_bottom, col_width, mittente_box_height, fill=0, stroke=1)
    c.drawString(left_col_x + box_padding_left, current_y_top - (0.2 * inch), "MITTENTE")

    c.setFont("Helvetica", 10)

    # Qui inseriamo i dati dinamici del mittente
    c.drawString(left_col_x + box_padding_left, current_y_top - (0.5 * inch), ddt_details['mittente']['nome']) # Nome Mittente
    c.drawString(left_col_x + box_padding_left, current_y_top - (0.95 * inch), f"P.I./C.F.:        {ddt_details['mittente']['piva_cf']}") # P.I./C.F. Mittente
    c.line(left_col_x + 1 * inch, current_y_top - (1 * inch), left_col_x + col_width - line_indent, current_y_top - (1 * inch))


    # --- CAMPI DDT (N. / DEL) ---
    c.rect(right_col_x, ddt_y_bottom, col_width, ddt_box_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_col_x + box_padding_left, current_y_top - (0.2 * inch), "DOCUMENTO DI TRASPORTO")
    c.setFont("Helvetica", 10)
    
    c.drawString(right_col_x + box_padding_left, current_y_top - (0.77 * inch), "N.")
    c.line(right_col_x + box_padding_left + (0.11 * inch), ddt_num_line_y, right_col_x + box_padding_left + (1.2 * inch), ddt_num_line_y)
    c.drawString(right_col_x + box_padding_left + (0.4 * inch), current_y_top - (0.77 * inch), str(ddt_number)) # Numero DDT dinamico

    c.drawString(right_col_x + box_padding_left + (1.5 * inch), current_y_top - (0.77 * inch), "DEL")
    c.line(right_col_x + box_padding_left + (1.81 * inch), ddt_del_line_y, right_col_x + col_width - line_indent, ddt_del_line_y)
    c.drawString(right_col_x + box_padding_left + (2 * inch), current_y_top - (0.77 * inch), str(ddt_date)) # Data dinamica


    # --- DESTINATARIO box ---
    c.rect(right_col_x, destinatario_y_bottom, col_width, destinatario_box_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.3 * inch), "DESTINATARIO")
    c.setFont("Helvetica", 10)

    # Qui inseriamo i dati dinamici del destinatario
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.6 * inch), ddt_details['destinatario']['nome']) # Nome Destinatario
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.85 * inch), f"P.I./C.F.:        {ddt_details['destinatario']['piva_cf']}") # P.I./C.F. Destinatario
    c.line(right_col_x + 1 * inch, ddt_y_bottom - (0.88 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.88 * inch))


    # --- CAUSALE DEL TRASPORTO box ---
    c.rect(left_col_x, causale_y_bottom, PAGE_WIDTH - (1.80 * left_col_x), causale_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_col_x + box_padding_left, causale_y_bottom + (0.45 * inch), "CAUSALE DEL TRASPORTO")
    c.setFont("Helvetica", 10)

    # Qui inseriamo i dati dinamici della causale
    c.drawString(left_col_x + box_padding_left, causale_y_bottom + (0.15 * inch), ddt_details['causale']) # Causale dinamica
    c.line(left_col_x + line_indent, causale_y_bottom + (0.07 * inch), PAGE_WIDTH - left_col_x - line_indent, causale_y_bottom + (0.05 * inch))


    # --- LUOGO DI DESTINAZIONE box ---
    c.rect(left_col_x, luogo_y_bottom, PAGE_WIDTH - (1.80 * left_col_x), luogo_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_col_x + box_padding_left, luogo_y_bottom + (0.45 * inch), "LUOGO DI DESTINAZIONE")
    c.setFont("Helvetica", 10)

    # Qui inseriamo i dati dinamici del luogo
    c.drawString(left_col_x + box_padding_left, luogo_y_bottom + (0.15 * inch), ddt_details['luogo_destinazione']) # Luogo dinamico
    c.line(left_col_x + line_indent, luogo_y_bottom + (0.07 * inch), PAGE_WIDTH - left_col_x - line_indent, luogo_y_bottom + (0.05 * inch))


# --- Funzione per aggiungere gli elementi del footer (solo sull'ultima pagina) ---
# Questa funzione usa le coordinate definite sopra
def add_footer_elements(c, current_y_after_table):
    # Ricalcola current_y per il footer basandosi sulla fine della tabella
    current_y = current_y_after_table - section_bottom_margin_top

    # --- Box TRASPORTO A MEZZO ---
    trasporto_box_y_bottom = current_y - trasporto_box_height
    c.rect(left_col_x, trasporto_box_y_bottom, col_width + (1 * inch), trasporto_box_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_col_x + box_padding_left, current_y - (0.2 * inch), "TRASPORTO A MEZZO:")
    c.setFont("Helvetica", 10)

    # Checkbox
    checkbox_size = 0.15 * inch
    checkbox_y = current_y - (0.45 * inch)
    checkbox_x_mittente = left_col_x + 0.3 * inch
    checkbox_x_vettore = checkbox_x_mittente + 1.2 * inch
    checkbox_x_destinatario = checkbox_x_vettore + 1.2 * inch

    c.rect(checkbox_x_mittente, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_mittente + checkbox_size + (0.05 * inch), checkbox_y, "MITTENTE")

    c.rect(checkbox_x_vettore, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_vettore + checkbox_size + (0.05 * inch), checkbox_y, "VETTORE")

    c.rect(checkbox_x_destinatario, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_destinatario + checkbox_size + (0.05 * inch), checkbox_y, "DESTINATARIO")

    c.drawString(left_col_x + box_padding_left, current_y - (0.7 * inch), "VETTORE:")
    c.line(left_col_x + 1 * inch, current_y - (0.7 * inch), left_col_x + col_width - box_padding_left + (0.2 * inch), current_y - (0.7 * inch))


    # --- Box DATA RITIRO ---
    data_ritiro_box_y_bottom = current_y - data_ritiro_box_height
    c.rect(right_col_x + (1 * inch), data_ritiro_box_y_bottom, col_width - (1 * inch), data_ritiro_box_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_col_x + box_padding_left + (1 * inch), current_y - (0.2 * inch), "DATA RITIRO")
    c.setFont("Helvetica", 10)
    c.line(right_col_x + box_padding_left + (1 * inch), current_y - (0.7 * inch), right_col_x + col_width - box_padding_left - (0.3 * inch), current_y - (0.70 * inch))


    # --- Box ANNOTAZIONI ---
    # Ora annotazioni_box_y_bottom viene calcolata qui
    annotazioni_box_y_bottom = trasporto_box_y_bottom - (0.1 * inch) - annotazioni_box_height 
    c.rect(left_col_x, annotazioni_box_y_bottom, PAGE_WIDTH - (1.80 * left_col_x), annotazioni_box_height, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_col_x + box_padding_left, annotazioni_box_y_bottom + (0.6 * inch), "ANNOTAZIONI")
    c.setFont("Helvetica", 10)
    c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.4 * inch), PAGE_WIDTH - left_col_x - line_indent, annotazioni_box_y_bottom + (0.4 * inch))
    c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.2 * inch), PAGE_WIDTH - left_col_x - line_indent, annotazioni_box_y_bottom + (0.2 * inch))


    # --- SEZIONE FIRME (UNA ACCANTO ALL'ALTRA) ---
    # Ora firme_section_top_y viene calcolata qui
    firme_section_top_y_footer = annotazioni_box_y_bottom - (0.5 * inch) # Inizio sezione firme, sotto annotazioni

    # Colonna 1: FIRMA MITTENTE (usa firme_section_top_y_footer per la Y)
    c.drawString(firma1_x + box_padding_left, firme_section_top_y_footer, "FIRMA MITTENTE")
    c.line(firma1_x + box_padding_left, firme_section_top_y_footer - (0.15 * inch), firma1_x + firma_col_width - (0.5 * inch), firme_section_top_y_footer - (0.15 * inch))

    # Colonna 2: FIRMA VETTORE (usa firme_section_top_y_footer per la Y)
    c.drawString(firma2_x + box_padding_left, firme_section_top_y_footer, "FIRMA VETTORE")
    c.line(firma2_x + box_padding_left, firme_section_top_y_footer - (0.15 * inch), firma2_x + firma_col_width - (0.5 * inch), firme_section_top_y_footer - (0.15 * inch))

    # Colonna 3: FIRMA DESTINATARIO (usa firme_section_top_y_footer per la Y)
    c.drawString(firma3_x + box_padding_left, firme_section_top_y_footer, "FIRMA DESTINATARIO")
    c.line(firma3_x + box_padding_left, firme_section_top_y_footer - (0.15 * inch), firma3_x + firma_col_width - (0.5 * inch), firme_section_top_y_footer - (0.15 * inch))

    # Linee divisorie verticali tra le firme (opzionale, ma può aiutare a separarle)
    # Linea tra Mittente e Vettore
    c.line(firma2_x - (0.1 * inch), firme_section_top_y_footer + (0.1 * inch), firma2_x - (0.1 * inch), firme_section_top_y_footer - firma_block_height - (0.1 * inch))
    # Linea tra Vettore e Destinatario
    c.line(firma3_x - (0.1 * inch), firme_section_top_y_footer + (0.1 * inch), firma3_x - (0.1 * inch), firme_section_top_y_footer - firma_block_height - (0.1 * inch))


# --- Funzione Principale per Generare il DDT ---
# Ora accetta una lista di prodotti selezionati e i dettagli del DDT
def genera_ddt(prodotti_selezionati, ddt_details):
    next_ddt_num = get_next_ddt_number()
    today = datetime.date.today()
    formatted_date = today.strftime("%d/%m/%Y")

    MAX_RIGHE_MATERIALI_PER_PAGINA = 12 # Numero massimo di righe nella tabella per pagina

    # Dividi i prodotti in blocchi per le pagine
    pagine_prodotti = [prodotti_selezionati[i:i + MAX_RIGHE_MATERIALI_PER_PAGINA] 
                       for i in range(0, len(prodotti_selezionati), MAX_RIGHE_MATERIALI_PER_PAGINA)]

    if not pagine_prodotti: # Se non ci sono prodotti, almeno una pagina vuota per il footer
        pagine_prodotti = [[]]

    total_pages = len(pagine_prodotti)
    generated_pdf_files = []

    for page_index, prodotti_pagina in enumerate(pagine_prodotti):
        page_num = page_index + 1 # Numero di pagina da 1 in su
        filename = f"DDT_{next_ddt_num}_Pagina_{page_num}.pdf"
        pdf_path = os.path.join(DDT_OUTPUT_PATH, filename)
        c = canvas.Canvas(pdf_path, pagesize=A4)

        # Aggiungi gli elementi fissi a ogni pagina
        add_fixed_elements(c, next_ddt_num, formatted_date, page_num, total_pages, ddt_details)

        # --- TABELLA DESCRIZIONE BENI (Popolata dinamicamente) ---
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        normal_style.fontSize = 10 # Assicurati che il font size sia quello desiderato
        normal_style.leading = 12 # Spaziatura tra le righe del paragrafo

        table_header = ["DESCRIZIONE DEI BENI", "Unità di misura", "Quantità"]
        table_rows_data = []

        # Popola la tabella con i prodotti per questa pagina
        for p in prodotti_pagina:
            # p è una tupla: (id, codice, nome, descrizione, unita_misura, quantita_per_ddt, prezzo_unitario)
            descrizione_completa = f"Cod: {p[1]} - {p[2]}" # Codice e Nome
            
            table_rows_data.append([
                Paragraph(descrizione_completa, normal_style),
                Paragraph(str(p[4]), normal_style), # Unità di misura
                Paragraph(str(p[5]), normal_style)  # Quantità per DDT
            ])

        # Aggiungi righe vuote per riempire la tabella fino al MAX_RIGHE_MATERIALI_PER_PAGINA
        while len(table_rows_data) < MAX_RIGHE_MATERIALI_PER_PAGINA:
            table_rows_data.append([Paragraph("\u00A0", normal_style), Paragraph("\u00A0", normal_style), Paragraph("\u00A0", normal_style)])
            
        final_table_data = [table_header] + table_rows_data

        # Calcola le larghezze delle colonne.
        col_widths = [table_available_width * 0.60, # Descrizione beni (60%)
                      table_available_width * 0.20, # Unità di misura (20%)
                      table_available_width * 0.20] # Quantità (20%)
        
        table = Table(final_table_data, colWidths=col_widths)
        
        table_style = TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), fill_color_header), # Intestazione grigio scuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),       # Testo bianco nell'intestazione
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),               # Allineamento testo intestazione
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),              # Padding sotto l'intestazione

        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black), # Griglia interna
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),       # Bordo esterno

        ('MINROWHEIGHT', (0, 1), (-1, -1), 0.25 * inch),    #Altezza minima righe
        ])

        table.setStyle(table_style)

        # Calcola l'altezza della tabella per posizionarla
        table_width_calc, table_height = table.wrapOn(c, table_available_width, PAGE_HEIGHT) # Spazio disponibile
        table.drawOn(c, left_col_x, table_y_start - table_height) # Posiziona la tabella

        current_y_after_table_for_footer = table_y_start - table_height # Aggiorna la posizione Y corrente dopo la tabella


        # Aggiungi il footer solo sull'ultima pagina
        if page_num == total_pages:
            add_footer_elements(c, current_y_after_table_for_footer)
        
        c.save()
        generated_pdf_files.append(pdf_path)
    
    return generated_pdf_files

# --- Funzione per stampare il DDT (Wrapper per l'apertura) ---
# Ora stampa_ddt_wrapper ha un parametro per i prodotti selezionati e i dettagli
def stampa_ddt_wrapper(prodotti_da_stampare, ddt_details):
    """
    Wrapper per generare e aprire i DDT e aggiornare il magazzino.

    Args:
        prodotti_da_stampare (list): Lista di prodotti selezionati (con id e quantità per DDT).
                                     Si assume che ogni elemento sia una tupla/lista
                                     con id_prodotto in posizione 0 e quantita_per_ddt in posizione 5.
        ddt_details (dict): Dettagli del DDT (mittente, destinatario, causale, luogo_destinazione).
    """
    if not prodotti_da_stampare and not ddt_details:
        print("Nessun prodotto selezionato e nessun dettaglio DDT fornito.")
        return

    try:
        pdf_paths = genera_ddt(prodotti_da_stampare, ddt_details)

        # --- AGGIUNGI QUESTO BLOCCO per l'aggiornamento del magazzino ---
        # Prepara i dati necessari per la funzione di decremento
        prodotti_per_db_update = []
        for p in prodotti_da_stampare:
            # p è una tupla: (id, codice, nome, descrizione, unita_misura, quantita_per_ddt, prezzo_unitario)
            id_prodotto = p[0]
            quantita_da_decrementare = p[5]
            prodotti_per_db_update.append((id_prodotto, quantita_da_decrementare))

        if prodotti_per_db_update: # Esegui l'aggiornamento solo se ci sono prodotti
            decrementa_quantita_magazzino(prodotti_per_db_update)
        # ---------------------------------------------------------------

        for pdf_path in pdf_paths:
            print(f"DDT generato: {pdf_path}")
            try:
                os.startfile(pdf_path)
            except AttributeError:
                subprocess.call(['xdg-open', pdf_path])
            except FileNotFoundError:
                print(f"Impossibile trovare il visualizzatore PDF per: {pdf_path}")
            except Exception as e:
                print(f"Errore nell'apertura del PDF {pdf_path}: {e}")
    except Exception as e:
        print(f"Errore durante la generazione del DDT o l'aggiornamento del magazzino: {e}")
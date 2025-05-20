import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch, mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
import subprocess

DDT_COUNTER_FILE = "../db/ddt_counter.txt" # Ho modificato il percorso per coerenza, supponendo che 'db' sia la cartella principale
DDT_OUTPUT_PATH = r"C:\Users\KLB\Desktop\ProvaPdf" # Ho modificato il percorso per maggiore chiarezza

# Assicurati che le directory esistano
os.makedirs(os.path.dirname(DDT_COUNTER_FILE), exist_ok=True)
os.makedirs(DDT_OUTPUT_PATH, exist_ok=True)

# Per numero DDT
def get_current_ddt_number():
    """Legge il numero corrente di DDT dal file."""
    try:
        with open(DDT_COUNTER_FILE, "r") as f:
            current_number = int(f.read().strip())
    except FileNotFoundError:
        current_number = 0 # Inizializza a 0 se il file non esiste, così il primo DDT è 1
    return current_number

def get_next_ddt_number():
    """Legge l'ultimo numero di DDT dal file, lo incrementa e lo salva."""
    last_number = get_current_ddt_number()
    next_number = last_number + 1
    with open(DDT_COUNTER_FILE, "w") as f:
        f.write(str(next_number))
    return next_number

# --- Funzione Principale per Generare il DDT ---
# Ora accetta una lista di prodotti selezionati
def genera_ddt(prodotti_selezionati):
    next_ddt_num = get_next_ddt_number()
    today = datetime.date.today()
    formatted_date = today.strftime("%d/%m/%Y")

    # Numero massimo di righe per i materiali per pagina
    MAX_RIGHE_MATERIALI_PER_PAGINA = 12 # Basato sul layout fornito (image_abb45f.png)

    # Dividi i prodotti in blocchi per le pagine
    pagine_prodotti = [prodotti_selezionati[i:i + MAX_RIGHE_MATERIALI_PER_PAGINA] 
                       for i in range(0, len(prodotti_selezionati), MAX_RIGHE_MATERIALI_PER_PAGINA)]

    if not pagine_prodotti: # Se non ci sono prodotti, almeno una pagina vuota
        pagine_prodotti = [[]]

    # Prepara un elenco di nomi di file PDF generati
    generated_pdf_files = []

    for page_num, prodotti_pagina in enumerate(pagine_prodotti):
        nome_file_pdf = os.path.join(DDT_OUTPUT_PATH, f"DDT_N{next_ddt_num}_Pag{page_num + 1}.pdf")
        generated_pdf_files.append(nome_file_pdf)

        c = canvas.Canvas(nome_file_pdf, pagesize=A4)
        width, height = A4
        styles = getSampleStyleSheet()
        
        # --- Stili Globali per Testo e Linee ---
        line_color = colors.black
        text_color = colors.black
        fill_color_header = colors.HexColor('#4A4A4A')
        c.setStrokeColor(line_color)
        c.setFillColor(text_color)
        c.setLineWidth(1)

        # --- Intestazione principale ---
        header_height = 0.5 * inch
        header_y = height - header_height - (0.5 * inch)
        c.setFillColor(fill_color_header)
        c.rect(0, header_y, width, header_height, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, header_y + (header_height / 2) - (16/2.5), "DOCUMENTO DI TRASPORTO")
        
        c.setFillColor(text_color)
        c.setFont("Helvetica", 10)

        # --- Area Mittente / Destinatario / Dati DDT ---
        box_margin_top = 0.3 * inch
        box_padding_left = 0.2 * inch

        current_y_top = header_y - box_margin_top

        single_line_box_height = 0.45 * inch
        double_line_box_height = 0.75 * inch

        left_col_x = 0.5 * inch
        right_col_x = (width / 2) + (0.25 * inch)
        col_width = (width / 2) - left_col_x - (0.15 * inch)

        # --- MITTENTE box ---
        mittente_box_height = double_line_box_height + 0.5 * inch
        mittente_y_bottom = current_y_top - mittente_box_height
        c.rect(left_col_x, mittente_y_bottom, col_width, mittente_box_height, fill=0, stroke=1)
        
        c.drawString(left_col_x + box_padding_left, current_y_top - (0.2 * inch), "MITTENTE")
        # Linee sotto MITTENTE
        line_indent = 0.2 * inch
        c.drawString(left_col_x + box_padding_left, current_y_top - (1 * inch), "P.I./C.F.:")
        c.line(left_col_x + 1 * inch, current_y_top - (1 * inch), left_col_x + col_width - line_indent, current_y_top - (1 * inch))

        # --- CAMPI DDT (N. / DEL) ---
        ddt_box_height = single_line_box_height + single_line_box_height
        ddt_y_bottom = current_y_top - ddt_box_height
        c.rect(right_col_x, ddt_y_bottom, col_width, ddt_box_height, fill=0, stroke=1)
        
        c.drawString(right_col_x + box_padding_left, current_y_top - (0.2 * inch), "DOCUMENTO DI TRASPORTO")
        
        ddt_num_line_y = current_y_top - (0.8 * inch)
        ddt_del_line_y = current_y_top - (0.8 * inch)

        c.drawString(right_col_x + box_padding_left, current_y_top - (0.77 * inch), "N.")
        c.line(right_col_x + box_padding_left + (0.11 * inch), ddt_num_line_y, right_col_x + box_padding_left + (1.2 * inch), ddt_num_line_y)

        c.drawString(right_col_x + box_padding_left + (1.5 * inch), current_y_top - (0.77 * inch), "DEL")
        c.line(right_col_x + box_padding_left + (1.81 * inch), ddt_del_line_y, right_col_x + col_width - line_indent, ddt_del_line_y)

        # Inserisci i valori effettivi del DDT
        c.drawString(right_col_x + box_padding_left + (0.4 * inch), current_y_top - (0.77 * inch), str(next_ddt_num))
        c.drawString(right_col_x + box_padding_left + (2.2 * inch), current_y_top - (0.77 * inch), str(formatted_date)) 

        # --- DESTINATARIO box ---
        destinatario_box_height = ddt_box_height
        destinatario_y_bottom = ddt_y_bottom - (0.1 * inch) - destinatario_box_height
        c.rect(right_col_x, destinatario_y_bottom, col_width, destinatario_box_height, fill=0, stroke=1)
        
        c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.3 * inch), "DESTINATARIO")
        c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.85 * inch), "P.I./C.F.:")
        c.line(right_col_x + 1 * inch, ddt_y_bottom - (0.88 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.88 * inch))

        current_y_bottom_of_top_boxes = min(mittente_y_bottom, destinatario_y_bottom)

        # --- CAUSALE DEL TRASPORTO box ---
        causale_height = single_line_box_height + 0.2 * inch
        causale_y_bottom = current_y_bottom_of_top_boxes - (0.1 * inch) - causale_height
        c.rect(left_col_x, causale_y_bottom, width - (1.80 * left_col_x), causale_height, fill=0, stroke=1)
        c.drawString(left_col_x + box_padding_left, causale_y_bottom + (0.45 * inch), "CAUSALE DEL TRASPORTO")
        c.line(left_col_x + line_indent, causale_y_bottom + (0.07 * inch), width - left_col_x - line_indent, causale_y_bottom + (0.05 * inch))

        # --- LUOGO DI DESTINAZIONE box ---
        luogo_height = single_line_box_height + 0.2 * inch
        luogo_y_bottom = causale_y_bottom - (0.1 * inch) - luogo_height
        c.rect(left_col_x, luogo_y_bottom, width - (1.80 * left_col_x), luogo_height, fill=0, stroke=1)
        c.drawString(left_col_x + box_padding_left, luogo_y_bottom + (0.45 * inch), "LUOGO DI DESTINAZIONE")
        c.line(left_col_x + line_indent, luogo_y_bottom + (0.07 * inch), width - left_col_x - line_indent, luogo_y_bottom + (0.05 * inch))


        # --- TABELLA DESCRIZIONE BENI ---
        table_y_start = luogo_y_bottom - (0.5 * inch)

        table_header = ["DESCRIZIONE DEI BENI", "Unità di misura", "Quantità"]
        table_rows = []

        # Popola la tabella con i prodotti per questa pagina
        for p in prodotti_pagina:
            # p è una tupla: (id, codice, nome, descrizione, unita_misura, quantita_disponibile, prezzo_unitario)
            descrizione_completa = f"Cod: {p[1]} - {p[2]}" # Codice e Nome
            if p[3]: # Se c'è una descrizione
                descrizione_completa += f" ({p[3]})"
            table_rows.append([descrizione_completa, p[4], str(p[5])]) # UM e Quantità

        # Aggiungi righe vuote per riempire la tabella fino al MAX_RIGHE_MATERIALI_PER_PAGINA
        while len(table_rows) < MAX_RIGHE_MATERIALI_PER_PAGINA:
            table_rows.append(["", "", ""])
            
        table_data = [table_header] + table_rows

        table_available_width = width - (1.80 * left_col_x)
        col_widths = [table_available_width * 0.60,
                      table_available_width * 0.20,
                      table_available_width * 0.20]
        
        table = Table(table_data, colWidths=col_widths)
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), fill_color_header),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            
            # Allineamento del testo nelle righe dei dati
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Descrizione a sinistra
            ('ALIGN', (1, 1), (1, -1), 'CENTER'), # UM al centro
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Quantità a destra
        ])
        table.setStyle(table_style)

        table_width, table_height = table.wrapOn(c, table_available_width, height)
        table.drawOn(c, left_col_x, table_y_start - table_height)

        current_y_after_table = table_y_start - table_height

        # --- SEZIONE INFERIORE - TRASPORTO A MEZZO, DATA RITIRO, ANNOTAZIONI, FIRME ---
        # Questa sezione viene aggiunta SOLO sull'ultima pagina
        if page_num == len(pagine_prodotti) - 1:
            section_bottom_margin_top = 0.5 * inch
            current_y = current_y_after_table - section_bottom_margin_top

            # --- Box TRASPORTO A MEZZO ---
            trasporto_box_height = 0.8 * inch
            trasporto_box_y_bottom = current_y - trasporto_box_height
            c.rect(left_col_x, trasporto_box_y_bottom, col_width + (1 * inch), trasporto_box_height, fill=0, stroke=1)
            
            c.drawString(left_col_x + box_padding_left, current_y - (0.2 * inch), "TRASPORTO A MEZZO:")
            
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
            c.line(left_col_x + 1.2 * inch, current_y - (0.7 * inch), left_col_x + col_width - box_padding_left, current_y - (0.7 * inch))


            # --- Box DATA RITIRO ---
            data_ritiro_box_height = trasporto_box_height
            data_ritiro_box_y_bottom = current_y - data_ritiro_box_height
            c.rect(right_col_x + (1 * inch), data_ritiro_box_y_bottom, col_width - (1 * inch), data_ritiro_box_height, fill=0, stroke=1)
            c.drawString(right_col_x + box_padding_left + (1 * inch), current_y - (0.2 * inch), "DATA RITIRO")
            c.line(right_col_x + box_padding_left + (1 * inch), current_y - (0.7 * inch), right_col_x + col_width - box_padding_left - (0.3 * inch), current_y - (0.70 * inch))
            
            # --- Box ANNOTAZIONI ---
            annotazioni_box_height = 0.8 * inch
            annotazioni_box_y_bottom = trasporto_box_y_bottom - (0.1 * inch) - annotazioni_box_height
            
            c.rect(left_col_x, annotazioni_box_y_bottom, width - (1.80 * left_col_x), annotazioni_box_height, fill=0, stroke=1)
            c.drawString(left_col_x + box_padding_left, annotazioni_box_y_bottom + (0.6 * inch), "ANNOTAZIONI")
            c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.4 * inch), width - left_col_x - line_indent, annotazioni_box_y_bottom + (0.4 * inch))
            c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.2 * inch), width - left_col_x - line_indent, annotazioni_box_y_bottom + (0.2 * inch))

            # --- SEZIONE FIRME ---
            firme_section_top_y = annotazioni_box_y_bottom - (0.5 * inch)
            firma_block_height = 0.3 * inch 
            firme_available_width = width - (2 * left_col_x)
            firma_col_width = firme_available_width / 3
            
            firma1_x = left_col_x
            firma1_y = firme_section_top_y
            c.drawString(firma1_x + box_padding_left, firma1_y, "FIRMA MITTENTE")
            c.line(firma1_x + box_padding_left, firma1_y - (0.15 * inch), firma1_x + firma_col_width - (0.5 * inch), firma1_y - (0.15 * inch))

            firma2_x = firma1_x + firma_col_width
            firma2_y = firme_section_top_y
            c.drawString(firma2_x + box_padding_left, firma2_y, "FIRMA VETTORE")
            c.line(firma2_x + box_padding_left, firma2_y - (0.15 * inch), firma2_x + firma_col_width - (0.5 * inch), firma2_y - (0.15 * inch))

            firma3_x = firma2_x + firma_col_width
            firma3_y = firme_section_top_y
            c.drawString(firma3_x + box_padding_left, firma3_y, "FIRMA DESTINATARIO")
            c.line(firma3_x + box_padding_left, firma3_y - (0.15 * inch), firma3_x + firma_col_width - (0.5 * inch), firma3_y - (0.15 * inch))

            c.line(firma2_x - (0.1 * inch), firme_section_top_y + (0.1 * inch), firma2_x - (0.1 * inch), firme_section_top_y - firma_block_height - (0.1 * inch))
            c.line(firma3_x - (0.1 * inch), firme_section_top_y + (0.1 * inch), firma3_x - (0.1 * inch), firme_section_top_y - firma_block_height - (0.1 * inch))

        # Aggiungi il numero di pagina in basso (opzionale ma utile)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 0.5 * inch, f"Pagina {page_num + 1} di {len(pagine_prodotti)}")

        c.save()
    return generated_pdf_files

# --- Funzione per stampare il DDT ---
# Ora stampa_ddt ha un parametro per i prodotti selezionati
def stampa_ddt_wrapper(prodotti_da_stampare): # Rinominata per evitare conflitti, chiamata dal menu
    filepaths_pdf = genera_ddt(prodotti_da_stampare)
    if filepaths_pdf:
        for filepath_pdf in filepaths_pdf:
            if os.path.exists(filepath_pdf):
                try:
                    if os.name == 'nt': # Windows
                        # Apro tutti i PDF generati
                        subprocess.Popen([filepath_pdf], shell=True)
                    elif os.name == 'posix': # Linux, macOS
                        subprocess.Popen(['open', filepath_pdf])
                    print(f"Aperto il file PDF '{filepath_pdf}'.")
                except Exception as e:
                    print(f"Errore nell'apertura del PDF '{filepath_pdf}': {e}")
            else:
                print(f"File PDF non trovato: {filepath_pdf}")
    else:
        print("Nessun PDF generato.")
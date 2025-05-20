import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 # Usiamo A4, che è più comune in Italia
from reportlab.lib.units import cm, inch, mm # Possiamo usare diverse unità
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
import subprocess



DDT_COUNTER_FILE = "../counter/ddt_counter.txt"
DDT_OUTPUT_PATH = r"C:\Users\KLB\Desktop\ProvaPdf"

# Assicurati che la directory di output per i PDF esista
os.makedirs(DDT_OUTPUT_PATH, exist_ok=True)

# Per numero DDT
def get_current_ddt_number():
    """Legge il numero corrente di DDT dal file."""
    try:
        with open(DDT_COUNTER_FILE, "r") as f:
            current_number = int(f.read().strip())
    except FileNotFoundError:
        current_number = 1
    return current_number

# Per nome file DDT
def get_next_ddt_number():
    """Legge l'ultimo numero di DDT dal file e lo incrementa."""
    try:
        with open(DDT_COUNTER_FILE, "r") as f:
            last_number = int(f.read().strip())
    except FileNotFoundError:
        last_number = 0
    next_number = last_number + 1
    with open(DDT_COUNTER_FILE, "w") as f:
        f.write(str(next_number))
    return next_number


# --- Funzione Principale per Generare il DDT ---
def genera_ddt():
    current_ddt_number = get_current_ddt_number()
    next_ddt_number = get_next_ddt_number()
    nome_file_pdf = os.path.join(DDT_OUTPUT_PATH, f"DDT{next_ddt_number}.pdf")

    # Creazione del canvas (A4: 595.27 x 841.89 punti)
    c = canvas.Canvas(nome_file_pdf, pagesize=A4)
    width, height = A4 # Ottieni larghezza e altezza della pagina in punti
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # --- Stili Globali per Testo e Linee ---
    line_color = colors.black
    text_color = colors.black
    fill_color_header = colors.HexColor('#4A4A4A') # Grigio scuro per le intestazioni
    c.setStrokeColor(line_color) # Colore predefinito per le linee
    c.setFillColor(text_color)   # Colore predefinito per il testo
    c.setLineWidth(1) # Spessore linea standard

    # --- Intestazione principale (Rettangolo grigio scuro e testo bianco) ---
    header_height = 0.5 * inch # Altezza dell'header principale
    header_y = height - header_height - (0.5 * inch) # Posizione Y (dal basso, quindi sottrai dall'altezza totale)
    c.setFillColor(fill_color_header)
    c.rect(0, header_y, width, header_height, fill=1, stroke=0) # Rettangolo da bordo a bordo
    
    # Ripristina il colore del testo a bianco per il titolo
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, header_y + (header_height / 2) - (16/2.5), "DOCUMENTO DI TRASPORTO")
    
    # Ripristina il colore del testo a nero
    c.setFillColor(text_color)
    c.setFont("Helvetica", 10) # Ripristina il font predefinito

    # --- Area Mittente / Destinatario / Dati DDT ---
    box_margin_top = 0.3 * inch # Margine dal rettangolo superiore
    box_padding_left = 0.2 * inch # Padding interno per il testo nelle caselle

    # Coordinate di riferimento Y per le caselle (dal basso)
    current_y_top = header_y - box_margin_top # Bordo superiore delle caselle

    # Definiamo altezze e larghezze per coerenza
    # Altezza standard per una riga di testo in un box
    single_line_box_height = 0.45 * inch
    double_line_box_height = 0.75 * inch # Per es. MITTENTE con 2 linee sottostanti

    # Larghezze delle colonne
    left_col_x = 0.5 * inch
    right_col_x = (width / 2) + (0.25 * inch)
    col_width = (width / 2) - left_col_x - (0.15 * inch) # Meno un po' di spazio centrale

    # --- MITTENTE box ---
    mittente_box_height = double_line_box_height + 0.5 * inch # Altezza leggermente maggiore per P.I./C.F.
    mittente_y_bottom = current_y_top - mittente_box_height
    c.rect(left_col_x, mittente_y_bottom, col_width, mittente_box_height, fill=0, stroke=1)
    
    # Testo "MITTENTE"
    c.drawString(left_col_x + box_padding_left, current_y_top - (0.2 * inch), "MITTENTE")
    
    # Linee sotto MITTENTE
    line_indent = 0.2 * inch # Indentazione delle linee dai bordi del box

    # Testo "P.I./C.F.:"
    c.drawString(left_col_x + box_padding_left, current_y_top - (1 * inch), "P.I./C.F.:")
    # Linea sotto P.I./C.F.
    c.line(left_col_x + 1 * inch, current_y_top - (1 * inch), left_col_x + col_width - line_indent, current_y_top - (1 * inch))

    # --- CAMPI DDT (N. / DEL) ---
    ddt_box_height = single_line_box_height + single_line_box_height # Due linee di testo
    ddt_y_bottom = current_y_top - ddt_box_height
    c.rect(right_col_x, ddt_y_bottom, col_width, ddt_box_height, fill=0, stroke=1)
    
    # Testo "DOCUMENTO DI TRASPORTO"
    c.drawString(right_col_x + box_padding_left, current_y_top - (0.2 * inch), "DOCUMENTO DI TRASPORTO")
    
    # Testo "N.  xx  DEL gg/mm/aaaa"
    # Adatta le posizioni e le lunghezze delle linee per farle combaciare
    ddt_num_line_y = current_y_top - (0.8 * inch) # Un po' sotto "N."
    ddt_del_line_y = current_y_top - (0.8 * inch) # Stessa Y per la linea DEL

    c.drawString(right_col_x + box_padding_left, current_y_top - (0.77 * inch), "N.")
    c.line(right_col_x + box_padding_left + (0.11 * inch), ddt_num_line_y, right_col_x + box_padding_left + (1.2 * inch), ddt_num_line_y) # Linea per N.

    c.drawString(right_col_x + box_padding_left + (1.5 * inch), current_y_top - (0.77 * inch), "DEL")
    c.line(right_col_x + box_padding_left + (1.81 * inch), ddt_del_line_y, right_col_x + col_width - line_indent, ddt_del_line_y) # Linea per DEL

    # Inserisci i valori effettivi
    today = datetime.date.today()
    formatted_date = today.strftime("%d/%m/%Y")

    c.drawString(right_col_x + box_padding_left + (0.4 * inch), current_y_top - (0.77 * inch), str(current_ddt_number))
    c.drawString(right_col_x + box_padding_left + (2.2 * inch), current_y_top - (0.77 * inch), str(formatted_date)) # Data hardcoded per esempio


    # --- DESTINATARIO box ---
    destinatario_box_height = ddt_box_height # Stessa altezza del box DDT
    destinatario_y_bottom = ddt_y_bottom - (0.1 * inch) - destinatario_box_height # Margine sotto box DDT
    c.rect(right_col_x, destinatario_y_bottom, col_width, destinatario_box_height, fill=0, stroke=1)
    
    # Testo "DESTINATARIO"
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.3 * inch), "DESTINATARIO")

    # Testo "P.I./C.F.:"
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.85 * inch), "P.I./C.F.:")
    # Linea sotto P.I./C.F.
    c.line(right_col_x + 1 * inch, ddt_y_bottom - (0.88 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.88 * inch))


    # Aggiorna la posizione Y corrente dopo l'area superiore
    current_y_bottom_of_top_boxes = mittente_y_bottom
    if destinatario_y_bottom < current_y_bottom_of_top_boxes:
        current_y_bottom_of_top_boxes = destinatario_y_bottom


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
    table_y_start = luogo_y_bottom - (0.5 * inch) # Spazio dalla casella precedente

    table_data = [
        ["DESCRIZIONE DEI BENI", "Unità di misura", "Quantità"],
        # Qui verranno i dati dei prodotti dal tuo database.
        # Per ora, mettiamo delle righe vuote per il layout.
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]

    # Calcola le larghezze delle colonne. Useremo larghezze fisse in base alla foto.
    # Larghezza disponibile per la tabella
    table_available_width = width - (1.80 * left_col_x)
    col_widths = [table_available_width * 0.60, # Descrizione beni (60%)
                  table_available_width * 0.20, # Unità di misura (20%)
                  table_available_width * 0.20] # Quantità (20%)
    
    table = Table(table_data, colWidths=col_widths)
    
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), fill_color_header), # Intestazione grigio scuro
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),       # Testo bianco nell'intestazione
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),               # Allineamento testo intestazione
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),              # Padding sotto l'intestazione

        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black), # Griglia interna
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),       # Bordo esterno
    ])
    table.setStyle(table_style)

    # Calcola l'altezza della tabella per posizionarla
    table_width, table_height = table.wrapOn(c, table_available_width, height) # Spazio disponibile
    table.drawOn(c, left_col_x, table_y_start - table_height) # Posiziona la tabella

    current_y_after_table = table_y_start - table_height # Aggiorna la posizione Y corrente dopo la tabella


    # --- SEZIONE INFERIORE - TRASPORTO A MEZZO, DATA RITIRO, ANNOTAZIONI, FIRME ---
    # Partiamo da current_y_after_table e scendiamo

    # Margine tra la tabella e la sezione inferiore
    section_bottom_margin_top = 0.5 * inch
    current_y = current_y_after_table - section_bottom_margin_top

    # --- Box TRASPORTO A MEZZO ---
    trasporto_box_height = 0.8 * inch # Altezza come da immagine
    trasporto_box_y_bottom = current_y - trasporto_box_height
    c.rect(left_col_x, trasporto_box_y_bottom, col_width + (1 * inch), trasporto_box_height, fill=0, stroke=1)
    
    c.drawString(left_col_x + box_padding_left, current_y - (0.2 * inch), "TRASPORTO A MEZZO:")
    
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
    c.line(left_col_x + 1.2 * inch, current_y - (0.7 * inch), left_col_x + col_width - box_padding_left, current_y - (0.7 * inch))


    # --- Box DATA RITIRO ---
    data_ritiro_box_height = trasporto_box_height # Stessa altezza del box TRASPORTO A MEZZO
    data_ritiro_box_y_bottom = current_y - data_ritiro_box_height
    c.rect(right_col_x + (1 * inch), data_ritiro_box_y_bottom, col_width - (1 * inch), data_ritiro_box_height, fill=0, stroke=1)
    c.drawString(right_col_x + box_padding_left + (1 * inch), current_y - (0.2 * inch), "DATA RITIRO")
    c.line(right_col_x + box_padding_left + (1 * inch), current_y - (0.7 * inch), right_col_x + col_width - box_padding_left - (0.3 * inch), current_y - (0.70 * inch))
    


    # --- Box ANNOTAZIONI ---
    annotazioni_box_height = 0.8 * inch # Altezza simile a TRASPORTO
    annotazioni_box_y_bottom = trasporto_box_y_bottom - (0.1 * inch) - annotazioni_box_height # Sotto TRASPORTO
    
    # Questo box si estende per tutta la larghezza della pagina (come Luogo Destinazione)
    c.rect(left_col_x, annotazioni_box_y_bottom, width - (1.80 * left_col_x), annotazioni_box_height, fill=0, stroke=1)
    c.drawString(left_col_x + box_padding_left, annotazioni_box_y_bottom + (0.6 * inch), "ANNOTAZIONI") # Etichetta in alto nel box
    c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.4 * inch), width - left_col_x - line_indent, annotazioni_box_y_bottom + (0.4 * inch))
    c.line(left_col_x + line_indent, annotazioni_box_y_bottom + (0.2 * inch), width - left_col_x - line_indent, annotazioni_box_y_bottom + (0.2 * inch))


    # --- SEZIONE FIRME (UNA ACCANTO ALL'ALTRA) ---
    firme_section_top_y = annotazioni_box_y_bottom - (0.5 * inch) # Inizio sezione firme, sotto annotazioni
    
    # Altezza stimata per ogni blocco firma (etichetta + linea)
    firma_block_height = 0.3 * inch 
    
    # Larghezza disponibile per le 3 colonne di firme
    firme_available_width = width - (2 * left_col_x)
    firma_col_width = firme_available_width / 3
    
    # Colonna 1: FIRMA MITTENTE
    firma1_x = left_col_x
    firma1_y = firme_section_top_y
    c.drawString(firma1_x + box_padding_left, firma1_y, "FIRMA MITTENTE")
    c.line(firma1_x + box_padding_left, firma1_y - (0.15 * inch), firma1_x + firma_col_width - (0.5 * inch), firma1_y - (0.15 * inch))

    # Colonna 2: FIRMA VETTORE
    firma2_x = firma1_x + firma_col_width
    firma2_y = firme_section_top_y # Stessa altezza della prima firma
    c.drawString(firma2_x + box_padding_left, firma2_y, "FIRMA VETTORE")
    c.line(firma2_x + box_padding_left, firma2_y - (0.15 * inch), firma2_x + firma_col_width - (0.5 * inch), firma2_y - (0.15 * inch))

    # Colonna 3: FIRMA DESTINATARIO
    firma3_x = firma2_x + firma_col_width
    firma3_y = firme_section_top_y # Stessa altezza della prima firma
    c.drawString(firma3_x + box_padding_left, firma3_y, "FIRMA DESTINATARIO")
    c.line(firma3_x + box_padding_left, firma3_y - (0.15 * inch), firma3_x + firma_col_width - (0.5 * inch), firma3_y - (0.15 * inch))

    # Linee divisorie verticali tra le firme (opzionale, ma può aiutare a separarle)
    # Linea tra Mittente e Vettore
    c.line(firma2_x - (0.1 * inch), firme_section_top_y + (0.1 * inch), firma2_x - (0.1 * inch), firme_section_top_y - firma_block_height - (0.1 * inch))
    # Linea tra Vettore e Destinatario
    c.line(firma3_x - (0.1 * inch), firme_section_top_y + (0.1 * inch), firma3_x - (0.1 * inch), firme_section_top_y - firma_block_height - (0.1 * inch))



    c.save()
    return nome_file_pdf

# --- Funzione per stampare il DDT ---
def stampa_ddt():
    filepath_pdf = genera_ddt()
    if os.path.exists(filepath_pdf):
        try:
            if os.name == 'nt':
                subprocess.Popen([filepath_pdf], shell=True)
            elif os.name == 'posix':
                subprocess.Popen(['open', filepath_pdf])
            print(f"Aperto il file PDF '{filepath_pdf}'.")
        except Exception as e:
            print(f"Errore nell'apertura del PDF: {e}")
    else:
        print(f"File PDF non trovato: {filepath_pdf}")
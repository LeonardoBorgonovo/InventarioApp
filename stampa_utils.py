import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 # Usiamo A4, che è più comune in Italia
from reportlab.lib.units import cm, inch, mm # Possiamo usare diverse unità
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
import subprocess



DDT_COUNTER_FILE = "ddt_counter.txt"
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
    c.line(left_col_x + line_indent, current_y_top - (0.4 * inch), left_col_x + col_width - line_indent, current_y_top - (0.4 * inch))
    c.line(left_col_x + line_indent, current_y_top - (0.43 * inch), left_col_x + col_width - line_indent, current_y_top - (0.43 * inch)) # Doppia linea

    # Testo "P.I./C.F.:"
    c.drawString(left_col_x + box_padding_left, current_y_top - (0.7 * inch), "P.I./C.F.:")
    # Linea sotto P.I./C.F.
    c.line(left_col_x + 1.2 * inch, current_y_top - (0.85 * inch), left_col_x + col_width - line_indent, current_y_top - (0.85 * inch))


    # --- CAMPI DDT (N. / DEL) ---
    ddt_box_height = single_line_box_height + single_line_box_height # Due linee di testo
    ddt_y_bottom = current_y_top - ddt_box_height
    c.rect(right_col_x, ddt_y_bottom, col_width, ddt_box_height, fill=0, stroke=1)
    
    # Testo "DOCUMENTO DI TRASPORTO"
    c.drawString(right_col_x + box_padding_left, current_y_top - (0.2 * inch), "DOCUMENTO DI TRASPORTO")
    
    # Testo "N.  xx  DEL gg/mm/aaaa"
    # Adatta le posizioni e le lunghezze delle linee per farle combaciare
    ddt_num_line_y = current_y_top - (0.43 * inch) # Un po' sotto "N."
    ddt_del_line_y = current_y_top - (0.43 * inch) # Stessa Y per la linea DEL

    c.drawString(right_col_x + box_padding_left, current_y_top - (0.4 * inch), "N.")
    c.line(right_col_x + box_padding_left + (0.3 * inch), ddt_num_line_y, right_col_x + box_padding_left + (1.2 * inch), ddt_num_line_y) # Linea per N.

    c.drawString(right_col_x + box_padding_left + (1.5 * inch), current_y_top - (0.4 * inch), "DEL")
    c.line(right_col_x + box_padding_left + (1.8 * inch), ddt_del_line_y, right_col_x + col_width - line_indent, ddt_del_line_y) # Linea per DEL

    # Inserisci i valori effettivi
    # Usiamo 20/05/2025 come da immagine, per la data corrente usa datetime.date.today().strftime('%d/%m/%Y')
    c.drawString(right_col_x + box_padding_left + (0.4 * inch), current_y_top - (0.4 * inch), str(current_ddt_number))
    c.drawString(right_col_x + box_padding_left + (2.2 * inch), current_y_top - (0.4 * inch), "20/05/2025") # Data hardcoded per esempio


    # --- DESTINATARIO box ---
    destinatario_box_height = ddt_box_height # Stessa altezza del box DDT
    destinatario_y_bottom = ddt_y_bottom - (0.1 * inch) - destinatario_box_height # Margine sotto box DDT
    c.rect(right_col_x, destinatario_y_bottom, col_width, destinatario_box_height, fill=0, stroke=1)
    
    # Testo "DESTINATARIO"
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.1 * inch) - (0.2 * inch), "DESTINATARIO")
    
    # Linee sotto DESTINATARIO
    c.line(right_col_x + line_indent, ddt_y_bottom - (0.1 * inch) - (0.4 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.1 * inch) - (0.4 * inch))
    c.line(right_col_x + line_indent, ddt_y_bottom - (0.1 * inch) - (0.43 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.1 * inch) - (0.43 * inch)) # Doppia linea

    # Testo "P.I./C.F.:"
    c.drawString(right_col_x + box_padding_left, ddt_y_bottom - (0.1 * inch) - (0.7 * inch), "P.I./C.F.:")
    # Linea sotto P.I./C.F.
    c.line(right_col_x + 1.2 * inch, ddt_y_bottom - (0.1 * inch) - (0.85 * inch), right_col_x + col_width - line_indent, ddt_y_bottom - (0.1 * inch) - (0.85 * inch))

    # Linea verticale che divide MITTENTE/DESTINATARIO
    # Inizia dalla cima del box mittente/DDT e scende fino alla fine del P.I./C.F. destinatario
    vertical_line_x = right_col_x - (0.15 * inch) # Posizione tra le due colonne
    vertical_line_start_y = current_y_top
    vertical_line_end_y = destinatario_y_bottom
    c.line(vertical_line_x, vertical_line_start_y, vertical_line_x, vertical_line_end_y)

    # Linee orizzontali interne che dividono i 4 box
    c.line(vertical_line_x, ddt_y_bottom, right_col_x + col_width, ddt_y_bottom) # Linea sotto box DDT
    c.line(vertical_line_x, destinatario_y_bottom + destinatario_box_height - double_line_box_height + 0.1 * inch, right_col_x + col_width, destinatario_y_bottom + destinatario_box_height - double_line_box_height + 0.1 * inch) # Linea sotto DESTINATARIO


    # Aggiorna la posizione Y corrente dopo l'area superiore
    current_y_bottom_of_top_boxes = mittente_y_bottom
    if destinatario_y_bottom < current_y_bottom_of_top_boxes:
        current_y_bottom_of_top_boxes = destinatario_y_bottom


    # --- CAUSALE DEL TRASPORTO box ---
    causale_height = single_line_box_height + 0.2 * inch
    causale_y_bottom = current_y_bottom_of_top_boxes - (0.1 * inch) - causale_height
    c.rect(left_col_x, causale_y_bottom, width - (2 * left_col_x), causale_height, fill=0, stroke=1)
    c.drawString(left_col_x + box_padding_left, causale_y_bottom + (0.2 * inch), "CAUSALE DEL TRASPORTO")
    c.line(left_col_x + line_indent, causale_y_bottom + (0.05 * inch), width - left_col_x - line_indent, causale_y_bottom + (0.05 * inch))


    # --- LUOGO DI DESTINAZIONE box ---
    luogo_height = single_line_box_height + 0.2 * inch
    luogo_y_bottom = causale_y_bottom - (0.1 * inch) - luogo_height
    c.rect(left_col_x, luogo_y_bottom, width - (2 * left_col_x), luogo_height, fill=0, stroke=1)
    c.drawString(left_col_x + box_padding_left, luogo_y_bottom + (0.2 * inch), "LUOGO DI DESTINAZIONE")
    c.line(left_col_x + line_indent, luogo_y_bottom + (0.05 * inch), width - left_col_x - line_indent, luogo_y_bottom + (0.05 * inch))


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
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
        ["", "", ""],
    ]

    # Calcola le larghezze delle colonne. Useremo larghezze fisse in base alla foto.
    # Larghezza disponibile per la tabella
    table_available_width = width - (2 * left_col_x)
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

    current_y = table_y_start - table_height # Aggiorna la posizione Y corrente dopo la tabella


    # --- Sezione Finale (Trasporto, Annotazioni, Firme) ---
    final_section_margin_top = 0.5 * inch
    current_y = current_y - final_section_margin_top

    # Trasporto a mezzo
    trasporto_x = 0.5 * inch
    trasporto_y_start = current_y
    trasporto_width = (width / 2) - trasporto_x - (0.25 * inch)
    trasporto_height = 0.8 * inch # Altezza per Trasporto
    c.rect(trasporto_x, trasporto_y_start - trasporto_height, trasporto_width, trasporto_height, fill=0, stroke=1)
    c.drawString(trasporto_x + box_padding_left, trasporto_y_start - (0.2 * inch), "TRASPORTO A MEZZO:")
    
    # Checkbox
    checkbox_size = 0.15 * inch
    checkbox_y = trasporto_y_start - (0.4 * inch)
    checkbox_x_mittente = trasporto_x + 0.3 * inch
    checkbox_x_vettore = checkbox_x_mittente + 1.2 * inch
    checkbox_x_destinatario = checkbox_x_vettore + 1.2 * inch
    
    c.rect(checkbox_x_mittente, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_mittente + checkbox_size + 0.05 * inch, checkbox_y, "MITTENTE")
    
    c.rect(checkbox_x_vettore, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_vettore + checkbox_size + 0.05 * inch, checkbox_y, "VETTORE")
    
    c.rect(checkbox_x_destinatario, checkbox_y, checkbox_size, checkbox_size, fill=0, stroke=1)
    c.drawString(checkbox_x_destinatario + checkbox_size + 0.05 * inch, checkbox_y, "DESTINATARIO")

    c.drawString(trasporto_x + box_padding_left, trasporto_y_start - (0.6 * inch), "VETTORE:")
    c.line(trasporto_x + 1.2 * inch, trasporto_y_start - (0.7 * inch), trasporto_x + trasporto_width - box_padding_left, trasporto_y_start - (0.7 * inch))


    # Data ritiro
    data_ritiro_x = width / 2 + 0.25 * inch
    data_ritiro_width = (width / 2) - data_ritiro_x - (0.5 * inch)
    data_ritiro_height = trasporto_height # Stessa altezza del trasporto
    c.rect(data_ritiro_x, trasporto_y_start - data_ritiro_height, data_ritiro_width, data_ritiro_height, fill=0, stroke=1)
    c.drawString(data_ritiro_x + box_padding_left, trasporto_y_start - (0.2 * inch), "DATA RITIRO")
    c.line(data_ritiro_x + box_padding_left, trasporto_y_start - (0.4 * inch), data_ritiro_x + data_ritiro_width - box_padding_left, trasporto_y_start - (0.4 * inch))


    # Annotazioni
    annotazioni_x = 0.5 * inch
    annotazioni_y_start = current_y - (0.1 * inch)
    annotazioni_width = width - (2 * annotazioni_x)
    annotazioni_height = 0.8 * inch # Altezza per Annotazioni
    c.rect(annotazioni_x, annotazioni_y_start - annotazioni_height, annotazioni_width, annotazioni_height, fill=0, stroke=1)
    c.drawString(annotazioni_x + box_padding_left, annotazioni_y_start - (0.2 * inch), "ANNOTAZIONI")
    c.line(annotazioni_x + line_indent, annotazioni_y_start - (0.4 * inch), annotazioni_x + annotazioni_width - line_indent, annotazioni_y_start - (0.4 * inch))


    # Firme
    firme_x = annotazioni_x
    firme_y_start = annotazioni_y_start - annotazioni_height - (0.1 * inch)
    # Calcola l'altezza necessaria per 3 firme con spazi
    firme_text_spacing = 0.25 * inch # Spazio tra le righe del testo della firma
    firme_line_spacing = 0.15 * inch # Spazio tra il testo e la linea della firma
    firma_section_height = (3 * firme_text_spacing) + (3 * firme_line_spacing) + (2 * 0.05 * inch) # Aggiungi piccoli margini

    # Firme box (non presente nell'immagine, ma utile per delimitare)
    # c.rect(firme_x, firme_y_start - firma_section_height, firme_width, firma_section_height, fill=0, stroke=1)

    # FIRMA MITTENTE
    c.drawString(firme_x + box_padding_left, firme_y_start - (0.2 * inch), "FIRMA MITTENTE")
    c.line(firme_x + box_padding_left, firme_y_start - (0.35 * inch), firme_x + 3 * inch, firme_y_start - (0.35 * inch))

    # FIRMA VETTORE
    c.drawString(firme_x + box_padding_left, firme_y_start - (0.55 * inch), "FIRMA VETTORE")
    c.line(firme_x + box_padding_left, firme_y_start - (0.7 * inch), firme_x + 3 * inch, firme_y_start - (0.7 * inch))

    # FIRMA DESTINATARIO
    c.drawString(firme_x + box_padding_left, firme_y_start - (0.8 * inch), "FIRMA DESTINATARIO")
    c.line(firme_x + box_padding_left, firme_y_start - (0.95 * inch), firme_x + 3 * inch, firme_y_start - (0.95 * inch))


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
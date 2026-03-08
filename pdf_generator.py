from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(invoice_data):
    """Générer un PDF de facture au format professionnel"""
    
    # Créer un BytesIO pour stocker le PDF en mémoire
    pdf_buffer = BytesIO()
    
    # Créer le document PDF avec plus de marges
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )
    
    # Contenu du PDF
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style pour le titre (nom entreprise)
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.black,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style pour le statut
    status_style = ParagraphStyle(
        'Status',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style pour l'activité
    activity_style = ParagraphStyle(
        'Activity',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # En-tête
    elements.append(Paragraph(invoice_data.get('company_name', 'ENTREPRISE').upper(), title_style))
    elements.append(Paragraph(invoice_data.get('company_status', 'STATUT'), status_style))
    elements.append(Paragraph(invoice_data.get('company_activity', 'ACTIVITÉ').upper(), activity_style))
    
    # Espace
    elements.append(Spacer(1, 0.8*cm))
    
    # Informations facture (Date et Numéro)
    date_facture = invoice_data.get('invoice_date', datetime.now().strftime("%d/%m/%Y"))
    numero_facture = invoice_data.get('invoice_number', '000/00')
    
    invoice_info_style = ParagraphStyle(
        'InvoiceInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_LEFT
    )
    
    elements.append(Paragraph(f"<b>Date facture:</b>        {date_facture}", invoice_info_style))
    elements.append(Paragraph(f"<b>Facture n°:</b>         {numero_facture}", invoice_info_style))
    
    # Espace
    elements.append(Spacer(1, 0.8*cm))
    
    # Client info
    client_name = invoice_data.get('client_name', 'CLIENT').upper()
    client_number = invoice_data.get('client_number', '')
    
    client_title_style = ParagraphStyle(
        'ClientTitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        underline=True
    )
    
    client_number_style = ParagraphStyle(
        'ClientNumber',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    elements.append(Paragraph(f"CLIENT: {client_name}", client_title_style))
    if client_number:
        elements.append(Paragraph(client_number, client_number_style))
    
    # Espace avant le tableau
    elements.append(Spacer(1, 0.6*cm))
    
    # Préparer les données du tableau
    lines = invoice_data.get('lines', [])
    
    # En-têtes du tableau
    table_data = [['QTE', 'Désignation', 'P-U', 'Montant']]
    
    # Ajouter les lignes de produits avec espaces généreux
    for line in lines:
        qte_str = str(int(line.get('qte', 0))) if line.get('qte', 0) % 1 == 0 else str(line.get('qte', 0))
        pu_str = f"{line.get('pu', 0):.2f}"
        montant_str = f"{line.get('montant', 0):.2f}"
        
        table_data.append([
            qte_str,
            line.get('designation', ''),
            pu_str,
            montant_str
        ])
    
    # Ajouter des lignes vides pour l'esthétique (comme dans le modèle)
    while len(table_data) < 6:
        table_data.append(['', '', '', ''])
    
    # Calculs des totaux
    tva_rate = invoice_data.get('tva_rate', 10)
    montant_ht = sum(line.get('montant', 0) for line in lines) if lines else 0
    montant_tva = montant_ht * (tva_rate / 100)
    montant_ttc = montant_ht + montant_tva
    
    # Ajouter une ligne vide avant les totaux
    table_data.append(['', '', '', ''])
    
    # Ajouter les totaux avec alignement à droite
    table_data.append(['', '', 'H.T', f'{montant_ht:.2f}'])
    table_data.append(['', '', f'TVA{tva_rate}%', f'{montant_tva:.2f}'])
    table_data.append(['', '', 'TTC', f'{montant_ttc:.2f}'])
    
    # Créer le tableau
    col_widths = [1.2*cm, 8.5*cm, 1.8*cm, 1.8*cm]
    table = Table(table_data, colWidths=col_widths)
    
    table.setStyle(TableStyle([
        # En-tête - noir avec texte blanc
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        
        # Contenu - lignes de produits
        ('ALIGN', (0, 1), (0, -5), 'CENTER'),  # QTE centré
        ('ALIGN', (1, 1), (1, -5), 'LEFT'),    # Désignation alignée à gauche
        ('ALIGN', (2, 1), (-1, -5), 'RIGHT'),  # P-U et Montant alignés à droite
        ('FONTNAME', (0, 1), (-1, -5), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -5), 9),
        ('TOPPADDING', (0, 1), (-1, -5), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -5), 10),
        ('BACKGROUND', (0, 1), (-1, -5), colors.white),
        
        # Grille complète pour toutes les cellules
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Ligne vide avant totaux (pas de contenu)
        ('BACKGROUND', (0, -4), (-1, -4), colors.white),
        ('GRID', (0, -4), (-1, -4), 1, colors.black),
        
        # H.T (ligne après vide)
        ('ALIGN', (2, -3), (-1, -3), 'RIGHT'),
        ('FONTNAME', (2, -3), (-1, -3), 'Helvetica'),
        ('FONTSIZE', (2, -3), (-1, -3), 9),
        ('TOPPADDING', (0, -3), (-1, -3), 8),
        ('BOTTOMPADDING', (0, -3), (-1, -3), 8),
        ('GRID', (0, -3), (-1, -3), 1, colors.black),
        
        # TVA (ligne avant TTC)
        ('ALIGN', (2, -2), (-1, -2), 'RIGHT'),
        ('FONTNAME', (2, -2), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (2, -2), (-1, -2), 9),
        ('TOPPADDING', (0, -2), (-1, -2), 8),
        ('BOTTOMPADDING', (0, -2), (-1, -2), 8),
        ('GRID', (0, -2), (-1, -2), 1, colors.black),
        
        # TTC (dernière ligne - mise en évidence)
        ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        
        # Valign
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    
    # Espace avant les notes
    elements.append(Spacer(1, 0.6*cm))
    
    # Notes/Conclusion
    notes = invoice_data.get('notes', '')
    if notes:
        note_style = ParagraphStyle(
            'Note',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=0,
            alignment=TA_LEFT
        )
        elements.append(Paragraph(notes, note_style))
    
    # Espace avant le pied de page
    elements.append(Spacer(1, 1.2*cm))
    
    # Séparateur
    from reportlab.platypus import HRFlowable
    hr = HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black)
    elements.append(hr)
    
    # Pied de page
    footer_text = invoice_data.get('company_info', 'ADRESSE: --- RC: --- ID FISCAL: ---')
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.black,
        spaceAfter=0,
        alignment=TA_CENTER,
        leading=10
    )
    
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(footer_text.upper(), footer_style))
    
    # Générer le PDF
    doc.build(elements)
    
    # Revenir au début du BytesIO
    pdf_buffer.seek(0)
    
    return pdf_buffer

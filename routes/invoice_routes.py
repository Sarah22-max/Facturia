from flask import Blueprint, jsonify, request, send_file, render_template
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

# Données temporaires (en memory)
invoices = []
invoice_counter = 1

@bp.route('/', methods=['GET'])
def get_invoices():
    """Récupérer toutes les factures"""
    return jsonify(invoices), 200

@bp.route('/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Récupérer une facture spécifique"""
    invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
    if not invoice:
        return {'error': 'Facture non trouvée'}, 404
    return jsonify(invoice), 200

@bp.route('/', methods=['POST'])
def create_invoice():
    """Créer une nouvelle facture et retourner un PDF"""
    global invoice_counter
    
    data = request.get_json()
    if not data:
        return {'error': 'Données manquantes'}, 400
    
    # Calculer les totaux
    lines = data.get('lines', [])
    tva_rate = data.get('tva_rate', 10)
    total_ht = sum(line.get('montant', 0) for line in lines) if lines else 0
    total_tva = total_ht * (tva_rate / 100)
    total_ttc = total_ht + total_tva
    
    invoice = {
        'id': invoice_counter,
        'numero': data.get('invoice_number', f'FAC-{invoice_counter:04d}'),
        'company_name': data.get('company_name', ''),
        'company_status': data.get('company_status', ''),
        'company_activity': data.get('company_activity', ''),
        'company_address': data.get('company_address', ''),
        'company_info': data.get('company_info', ''),
        'client': data.get('client_name', 'Client'),
        'client_name': data.get('client_name', ''),
        'client_number': data.get('client_number', ''),
        'lines': data.get('lines', []),
        'montant': data.get('montant', 0),
        'date': data.get('invoice_date', ''),
        'invoice_date': data.get('invoice_date', ''),
        'invoice_number': data.get('invoice_number', f'FAC-{invoice_counter:04d}'),
        'tva_rate': data.get('tva_rate', 10),
        'notes': data.get('notes', ''),
        'statut': data.get('statut', 'Brouillon')
    }
    
    invoices.append(invoice)
    invoice_counter += 1
    
    # Générer le PDF avec ReportLab
    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10
        )
        
        # Titre
        elements.append(Paragraph(f"Facture {invoice['invoice_number']}", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informations de l'entreprise
        company_info = f"""
        <b>{invoice['company_name']}</b><br/>
        Statut: {invoice['company_status']}<br/>
        Activité: {invoice['company_activity']}<br/>
        Adresse: {invoice['company_address']}<br/>
        {invoice['company_info']}
        """
        elements.append(Paragraph(company_info, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informations client
        client_info = f"""
        <b>Client:</b><br/>
        Nom: {invoice['client_name']}<br/>
        Numéro: {invoice['client_number']}
        """
        elements.append(Paragraph(client_info, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Détails de la facture
        invoice_details = f"""
        <b>Date:</b> {invoice['invoice_date']}<br/>
        <b>Numéro de facture:</b> {invoice['invoice_number']}
        """
        elements.append(Paragraph(invoice_details, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Tableau des lignes
        table_data = [['Description', 'Quantité', 'Prix Unitaire', 'Montant']]
        for line in invoice['lines']:
            table_data.append([
                str(line.get('description', '')),
                str(line.get('quantity', '')),
                str(line.get('unit_price', '')),
                str(line.get('montant', ''))
            ])
        
        # Totaux
        table_data.append(['', '', 'Total HT:', f"{total_ht:.2f}"])
        table_data.append(['', '', f'TVA {tva_rate}%:', f"{total_tva:.2f}"])
        table_data.append(['', '', 'Total TTC:', f"{total_ttc:.2f}"])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -4), [colors.white, colors.HexColor('#f0f0f0')]),
            ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#e8f0f7')),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (-2, -3), (-1, -1), 'RIGHT'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Notes
        if invoice['notes']:
            notes_text = f"<b>Notes:</b><br/>{invoice['notes']}"
            elements.append(Paragraph(notes_text, styles['Normal']))
        
        # Générer le PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        # Retourner le PDF
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"facture_{invoice['invoice_number'].replace('/', '-')}.pdf"
        )
    except Exception as e:
        return {'error': f'Erreur lors de la génération du PDF: {str(e)}'}, 500

@bp.route('/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """Mettre à jour une facture"""
    invoice = next((inv for inv in invoices if inv['id'] == invoice_id), None)
    if not invoice:
        return {'error': 'Facture non trouvée'}, 404
    
    data = request.get_json()
    invoice.update(data)
    
    return jsonify(invoice), 200

@bp.route('/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    """Supprimer une facture"""
    global invoices
    invoices = [inv for inv in invoices if inv['id'] != invoice_id]
    return {'message': 'Facture supprimée'}, 200

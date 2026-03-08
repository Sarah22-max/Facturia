from flask import Blueprint, jsonify, request, send_file, render_template
from weasyprint import HTML
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
    
    # Rendre le template HTML
    try:
        html_string = render_template(
            'invoice_template.html',
            company_name=invoice['company_name'],
            legal_form=invoice['company_status'],
            activity_description=invoice['company_activity'],
            invoice_date=invoice['invoice_date'],
            invoice_number=invoice['invoice_number'],
            client_name=invoice['client_name'],
            client_identifier=invoice['client_number'],
            lines=invoice['lines'],
            total_ht=total_ht,
            total_tva=total_tva,
            total_ttc=total_ttc,
            tva_rate=invoice['tva_rate'],
            notes=invoice['notes'],
            company_info=invoice['company_info']
        )
        
        # Convertir HTML en PDF avec weasyprint
        pdf_buffer = BytesIO()
        HTML(string=html_string).write_pdf(pdf_buffer)
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

// API base URL
const API_URL = '/api/invoices';

// État global
let invoiceLines = [];
let lineCounter = 0;

// Charger les factures au démarrage
document.addEventListener('DOMContentLoaded', () => {
    loadInvoices();
    setupFormListener();
    // Ajouter une première ligne vide
    addInvoiceLine();
    // Écouter les changements du taux TVA
    document.getElementById('tva-rate').addEventListener('change', calculateTotals);
    document.getElementById('tva-rate').addEventListener('input', updateTVALabel);
});

// Ajouter une ligne de facture
function addInvoiceLine() {
    lineCounter++;
    const lineId = `line-${lineCounter}`;
    
    const lineHtml = `
        <div class="invoice-line" id="${lineId}">
            <input type="number" class="line-qte" placeholder="0" min="0" step="1" value="1">
            <input type="text" class="line-designation" placeholder="Désignation du produit/service">
            <input type="number" class="line-pu" placeholder="0.00" min="0" step="0.01" value="0">
            <div class="line-amount">0.00 DH</div>
            <button type="button" class="btn-delete-line" onclick="deleteInvoiceLine('${lineId}')">Supprimer</button>
        </div>
    `;
    
    document.getElementById('invoice-lines').insertAdjacentHTML('beforeend', lineHtml);
    
    // Ajouter les listeners pour les calculs
    const line = document.getElementById(lineId);
    line.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('change', calculateTotals);
    });
}

// Supprim une ligne de facture
function deleteInvoiceLine(lineId) {
    document.getElementById(lineId).remove();
    calculateTotals();
}

// Mettre à jour le label de la TVA
function updateTVALabel() {
    const tvaRate = parseFloat(document.getElementById('tva-rate').value) || 0;
    document.getElementById('tva-label').textContent = `TVA ${tvaRate.toFixed(2)}%:`;
}

// Calculer les totaux
function calculateTotals() {
    let totalHT = 0;
    const tvaRate = parseFloat(document.getElementById('tva-rate').value) || 0;
    
    document.querySelectorAll('.invoice-line').forEach(line => {
        const qte = parseFloat(line.querySelector('.line-qte').value) || 0;
        const pu = parseFloat(line.querySelector('.line-pu').value) || 0;
        const montant = qte * pu;
        
        // Afficher le montant de la ligne
        const montantElement = line.querySelector('.line-amount');
        montantElement.textContent = montant.toFixed(2) + ' DH';
        
        totalHT += montant;
    });
    
    // Calculer la TVA avec le taux modifiable
    const totalTVA = totalHT * (tvaRate / 100);
    const totalTTC = totalHT + totalTVA;
    
    // Afficher les totaux
    document.getElementById('total-ht').textContent = totalHT.toFixed(2) + ' DH';
    document.getElementById('total-tva').textContent = totalTVA.toFixed(2) + ' DH';
    document.getElementById('total-ttc').textContent = totalTTC.toFixed(2) + ' DH';
}

// Écouter la soumission du formulaire
function setupFormListener() {
    const form = document.getElementById('invoiceForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Collecter les lignes de facture
        const lines = [];
        document.querySelectorAll('.invoice-line').forEach(line => {
            const qte = parseFloat(line.querySelector('.line-qte').value) || 0;
            const designation = line.querySelector('.line-designation').value;
            const pu = parseFloat(line.querySelector('.line-pu').value) || 0;
            
            if (designation && qte > 0 && pu > 0) {
                lines.push({
                    qte: qte,
                    designation: designation,
                    pu: pu,
                    montant: qte * pu
                });
            }
        });
        
        if (lines.length === 0) {
            alert('Veuillez ajouter au moins une ligne de produit/service');
            return;
        }
        
        // Récupérer les données du formulaire
        const formData = {
            company_name: document.getElementById('company-name').value,
            company_status: document.getElementById('company-status').value,
            company_activity: document.getElementById('company-activity').value,
            company_address: document.getElementById('company-address').value,
            company_info: document.getElementById('company-info').value,
            invoice_number: document.getElementById('invoice-number').value,
            invoice_date: document.getElementById('invoice-date').value,
            client_name: document.getElementById('client-name').value,
            client_number: document.getElementById('client-number').value,
            lines: lines,
            notes: document.getElementById('notes').value,
            tva_rate: parseFloat(document.getElementById('tva-rate').value) || 10,
            montant: lines.reduce((sum, line) => sum + line.montant, 0)
        };
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                // Télécharger le PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `facture_${formData.invoice_number.replace('/', '-')}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert('Facture créée et téléchargée avec succès!');
                form.reset();
                document.getElementById('invoice-lines').innerHTML = '';
                addInvoiceLine();
                loadInvoices();
            } else {
                const errorData = await response.json();
                alert(`Erreur: ${errorData.error || 'Erreur lors de la création de la facture'}`);
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur de connexion au serveur');
        }
    });
}

// Charger et afficher toutes les factures
async function loadInvoices() {
    try {
        const response = await fetch(API_URL);
        const invoices = await response.json();
        
        const invoicesList = document.getElementById('invoicesList');
        
        if (invoices.length === 0) {
            invoicesList.innerHTML = '<p class="empty-state">Aucune facture créée</p>';
            return;
        }

        invoicesList.innerHTML = invoices.map(invoice => {
            const linesText = invoice.lines && invoice.lines.length > 0 
                ? invoice.lines.map(l => `${l.qte}x ${l.designation}`).join(', ')
                : 'N/A';
            
            return `
                <div class="invoice-card">
                    <div class="invoice-info">
                        <div class="invoice-numero">${invoice.numero || invoice.invoice_number}</div>
                        <div class="invoice-details">
                            <span><strong>Entreprise:</strong> ${invoice.company_name || invoice.client}</span>
                            <span><strong>Client:</strong> ${invoice.client_name || 'N/A'}</span>
                            <span><strong>Date:</strong> ${new Date(invoice.date || invoice.invoice_date).toLocaleDateString('fr-FR')}</span>
                            <span><strong>Lignes:</strong> ${linesText}</span>
                        </div>
                    </div>
                    <div class="invoice-montant">${invoice.montant.toFixed(2)} DH</div>
                    <button class="btn btn-delete" onclick="deleteInvoice(${invoice.id})">Supprimer</button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erreur lors du chargement:', error);
    }
}

// Supprimer une facture
async function deleteInvoice(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette facture ?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            loadInvoices();
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur de connexion au serveur');
    }
}

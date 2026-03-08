# 🚀 Guide de Déploiement Facturia

## Option 1: Render.com (RECOMMANDÉ - Gratuit et Simple)

### Prérequis:
- Repository GitHub (Sarah22-max/Facturia)
- Compte Render.com (gratuit)

### Étapes:

1. **Créer un compte sur https://render.com** (libre)

2. **Connecter GitHub**
   - Cliquez sur "Connect GitHub" lors de l'inscription
   - Autorisez Render à accéder à vos repositories

3. **Créer un nouveau Web Service**
   - Cliquez sur "New +" → "Web Service"
   - Sélectionnez le repository "Facturia"
   - Branch: `main`

4. **Configurer le service**
   - **Name:** `facturia` (ou votre nom préféré)
   - **Region:** `Frankfurt` (ou plus proche de vous)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

5. **Configurer les variables d'environnement** (optionnel)
   - Cliquez sur "Environment" et ajoutez si nécessaire:
   ```
   PORT=3000
   ```

6. **Cliquer "Create Web Service"**
   - Render va automatiquement déployer votre application
   - Vous verrez un URL public comme: `https://facturia-xxxx.onrender.com`

7. **Configurations avancées** (optionnel)
   - Allez dans "Settings"
   - Auto-deploy: Activé (redéploie à chaque push sur GitHub)
   - Health Check: `/health` (endpoint déjà configuré)

### Avantages:
✅ Gratuit (avec ralentissements actifs après 15 min d'inactivité)
✅ Déploiement automatique avec GitHub
✅ Support des variables d'environnement
✅ HTTPS inclus

---

## Option 2: Railway.app

1. Aller sur https://railway.app
2. Cliquer "Deploy Now"
3. Autoriser GitHub et sélectionner Facturia
4. Railway configure automatiquement Python/Flask
5. Obtenez un domaine public gratuit

---

## Option 3: ngrok (Tunnel temporaire - Développement)

Si vous voulez tester rapidement le site de manière publique:

```bash
pip install ngrok
ngrok http 3000
```

Vous recevrez une URL comme: `https://xxxx-xx-xxx-xxx-xx.ngrok-free.app`

⚠️ Cet URL change chaque redémarrage, c'est pour tester seulement.

---

## Après le déploiement:

### Tester le site public:
1. Accédez à votre URL public (ex: https://facturia-xxxx.onrender.com)
2. Remplissez le formulaire
3. Vérifiez que le PDF se télécharge correctement

### Dépanner les problèmes:

**Erreur 500:**
- Vérifiez les logs: Dans Render → "Logs"
- Vérifiez que tous les packages sont dans `requirements.txt`

**Port non correct:**
- Vérifiez que `Start Command` est: `gunicorn app:app`
- Ne spécifiez pas le port dans gunicorn, Render l'attribue dynamiquement

**Pas de CSS/images:**
- Vérifiez les chemins statiques dans Flask
- Si besoin, mettez à jour les chemins dans `app.py`

---

## Prochaines étapes (Optionnel):

1. **Domaine personnalisé:** 
   - Render permet de connecter un domaine `.com` payant
   - Allez dans Settings → "Custom Domain"

2. **Base de données:**
   - Actuellement: données en mémoire (réinitialisées au redéploiement)
   - Pour persistance: ajoutez PostgreSQL (gratuit dans Render)

3. **Email de notification:**
   - Render peut envoyer des alertes si le site tombe

---

## 💾 Avant le déploiement - Assurez-vous:

```
✅ Tous les changements sont commités sur GitHub
✅ requirements.txt est à jour
✅ .gitignore contient __pycache__ et .env
✅ Pas de secrets en dur dans le code
✅ app.py écoute sur l'hôte 0.0.0.0 et le port assigné par l'hôte
```

---

## Questions?

- Documentation Render: https://render.com/docs
- Documentation Flask-Gunicorn: https://gunicorn.org/

Bonne chance! 🎉

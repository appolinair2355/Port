"""
Main entry point for the Telegram bot deployment on render.com
"""
import os
import logging
from flask import Flask, request
from bot import TelegramBot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot
config = Config()
bot = TelegramBot(config.BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from Telegram"""
    try:
        update = request.get_json()
        
        # Log type de message reçu
        if 'message' in update:
            logger.info(f"📨 Webhook - Message normal reçu")
        elif 'edited_message' in update:
            logger.info(f"✏️ Webhook - Message édité reçu")
        
        logger.info(f"Webhook received update: {update}")
        
        if update:
            # Traitement direct pour meilleure réactivité
            bot.handle_update(update)
            logger.info("Update processed successfully")
        
        return 'OK', 200
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return 'Error', 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for render.com"""
    return {'status': 'healthy', 'service': 'telegram-bot'}, 200

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return {'message': 'Telegram Bot is running', 'status': 'active'}, 200

def setup_webhook():
    """Set up webhook on startup"""
    try:
        # Utiliser l'URL configurée dans Config
        webhook_url = config.WEBHOOK_URL
        if webhook_url and webhook_url != "https://.repl.co":
            full_webhook_url = f"{webhook_url}/webhook"
            logger.info(f"🔗 Configuration webhook: {full_webhook_url}")
            
            # Configure webhook for Render.com with your specific URL
            success = bot.set_webhook(full_webhook_url)
            if success:
                logger.info(f"✅ Webhook configuré avec succès: {full_webhook_url}")
                logger.info(f"🎯 Bot prêt pour prédictions automatiques et vérifications via webhook")
            else:
                logger.error("❌ Échec configuration webhook")
        else:
            logger.warning("⚠️ WEBHOOK_URL non configurée, mode polling recommandé pour le développement")
            logger.info("💡 Pour activer le webhook, configurez la variable WEBHOOK_URL")
    except Exception as e:
        logger.error(f"❌ Erreur configuration webhook: {e}")

if __name__ == '__main__':
    # Set up webhook on startup
    setup_webhook()
    
    # Get port from environment (render.com provides this)
    port = int(os.getenv('PORT', 10000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

"""
Configuration settings for the Telegram bot
"""
import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # BOT_TOKEN - OBLIGATOIRE depuis variable d'environnement
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Auto-génération URL pour Replit
        if os.getenv('REPLIT_DOMAINS'):
            # URL automatique basée sur le domaine Replit
            auto_webhook = f"https://{os.getenv('REPLIT_DOMAINS')}"
        else:
            # Fallback URL Replit
            auto_webhook = f'https://{os.getenv("REPL_SLUG", "")}.{os.getenv("REPL_OWNER", "")}.repl.co'
        
        # Priority: WEBHOOK_URL explicite > Auto-génération
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL', auto_webhook)
        logger.info(f"Webhook URL configuré: {self.WEBHOOK_URL}")
        # Port pour le serveur - utilise PORT env ou 5000 par défaut (Replit)
        self.PORT = int(os.getenv('PORT', 5000))
        # Canal de destination pour les prédictions
        self.PREDICTION_CHANNEL_ID = -1002887687164
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Validate configuration
        self._validate_config()
    
    def _get_bot_token(self) -> str:
        """Get bot token from environment variables only"""
        token = os.getenv('BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN', ''))
        
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        return token
    
    def _validate_config(self) -> None:
        """Validate configuration settings"""
        if not self.BOT_TOKEN:
            raise ValueError("Bot token is required")
        
        if len(self.BOT_TOKEN.split(':')) != 2:
            raise ValueError("Invalid bot token format")
        
        if self.WEBHOOK_URL and not self.WEBHOOK_URL.startswith('https://'):
            logger.warning("Webhook URL should use HTTPS for production")
        
        logger.info("Configuration validated successfully")
    
    def get_webhook_url(self) -> str:
        """Get full webhook URL"""
        if self.WEBHOOK_URL:
            return f"{self.WEBHOOK_URL}/webhook"
        return ""
    
    def __str__(self) -> str:
        """String representation of config (without sensitive data)"""
        return f"Config(webhook_url={self.WEBHOOK_URL}, port={self.PORT}, debug={self.DEBUG})"

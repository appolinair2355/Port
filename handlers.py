"""
Event handlers for the Telegram bot - adapted for webhook deployment
"""

import logging
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Rate limiting storage
user_message_counts = defaultdict(list)

# ID de l'utilisateur autorisé (Sossou Kouamé)
AUTHORIZED_USER_ID = 1190237801

# Target channel ID for Baccarat Kouamé
TARGET_CHANNEL_ID = -1002682552255

# Target channel ID for predictions and updates
PREDICTION_CHANNEL_ID = -1002887687164

# Configuration constants
GREETING_MESSAGE = """
🎭 Salut ! Je suis le bot de Joker DEPLOY299999 !
Ajoutez-moi à votre canal pour que je puisse saluer tout le monde ! 👋

🔮 Je peux analyser les combinaisons de cartes et faire des prédictions !
Utilisez /help pour voir toutes mes commandes.
"""

WELCOME_MESSAGE = """
🎭 **BIENVENUE DANS LE MONDE DE JOKER DEPLOY299999 !** 🔮

🎯 **COMMANDES DISPONIBLES:**
• `/start` - Accueil
• `/help` - Aide détaillée complète
• `/about` - À propos du bot  
• `/dev` - Informations développeur
• `/deploy` - Obtenir le fichier deploy299999.zip

🔧 **CONFIGURATION AVANCÉE:**
• `/cos [1|2]` - Position de carte
• `/cooldown [secondes]` - Délai entre prédictions  
• `/redirect` - Redirection des prédictions
• `/announce [message]` - Annonce officielle
• `/reset` - Réinitialiser le système

🔮 **FONCTIONNALITÉS SPÉCIALES:**
✓ Prédictions automatiques avec cooldown configurable
✓ Analyse des combinaisons de cartes en temps réel
✓ Système de vérification séquentiel avancé
✓ Redirection multi-canaux flexible
✓ Accès sécurisé avec autorisation utilisateur

🎯 **Version DEPLOY299999 - Port 10000**
"""

HELP_MESSAGE = """
🎯 **GUIDE D'UTILISATION DU BOT JOKER** 🔮

📝 **COMMANDES DE BASE:**
• `/start` - Message d'accueil
• `/help` - Afficher cette aide
• `/about` - Informations sur le bot
• `/dev` - Contact développeur
• `/deploy` - Package de déploiement
• `/ni` - Package modifié
• `/fin` - Package final complet

🔧 **COMMANDES DE CONFIGURATION:**
• `/cos [1|2]` - Position de carte pour prédictions
• `/cooldown [secondes]` - Modifier le délai entre prédictions
• `/redirect [source] [target]` - Redirection avancée des prédictions
• `/redi` - Redirection rapide vers le chat actuel
• `/announce [message]` - Envoyer une annonce officielle
• `/reset` - Réinitialiser toutes les prédictions

🔮 Fonctionnalités avancées :
- Le bot analyse automatiquement les messages contenant des combinaisons de cartes
- Il fait des prédictions basées sur les patterns détectés
- Gestion intelligente des messages édités
- Support des canaux et groupes
- Configuration personnalisée de la position de carte

🎴 Format des cartes :
Le bot reconnaît les symboles : ♠️ ♥️ ♦️ ♣️

📊 Le bot peut traiter les messages avec format #nXXX pour identifier les jeux.

🎯 Configuration des prédictions :
• /cos 1 - Utiliser la première carte
• /cos 2 - Utiliser la deuxième carte
⚠️ Si les deux premières cartes ont le même costume, la troisième sera utilisée automatiquement.
"""

ABOUT_MESSAGE = """
🎭 Bot Joker - Prédicteur de Cartes

🤖 Version : 2.0
🛠️ Développé avec Python et l'API Telegram
🔮 Spécialisé dans l'analyse de combinaisons de cartes

✨ Fonctionnalités :
- Prédictions automatiques
- Analyse de patterns
- Support multi-canaux
- Interface intuitive

🌟 Créé pour améliorer votre expérience de jeu !
"""

DEV_MESSAGE = """
👨‍💻 Informations Développeur :

🔧 Technologies utilisées :
- Python 3.11+
- API Telegram Bot
- Flask pour les webhooks
- Déployé sur Render.com

📧 Contact : 
Pour le support technique ou les suggestions d'amélioration, 
contactez l'administrateur du bot.

🚀 Le bot est open source et peut être déployé facilement !
"""

MAX_MESSAGES_PER_MINUTE = 30
RATE_LIMIT_WINDOW = 60

def is_rate_limited(user_id: int) -> bool:
    """Check if user is rate limited"""
    now = datetime.now()
    user_messages = user_message_counts[user_id]

    # Remove old messages outside the window
    user_messages[:] = [msg_time for msg_time in user_messages 
                       if now - msg_time < timedelta(seconds=RATE_LIMIT_WINDOW)]

    # Check if user exceeded limit
    if len(user_messages) >= MAX_MESSAGES_PER_MINUTE:
        return True

    # Add current message time
    user_messages.append(now)
    return False

class TelegramHandlers:
    """Handlers for Telegram bot using webhook approach"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.deployment_file_path = "deploo299999_final_complete.zip"
        # Import card_predictor locally to avoid circular imports
        try:
            from card_predictor import card_predictor
            self.card_predictor = card_predictor
        except ImportError:
            logger.error("Failed to import card_predictor")
            self.card_predictor = None

        # Store redirected channels for each source chat
        self.redirected_channels = {} # {source_chat_id: target_chat_id}

    def handle_update(self, update: Dict[str, Any]) -> None:
        """Handle incoming Telegram update with enhanced webhook support"""
        try:
            if 'message' in update:
                message = update['message']
                logger.info(f"🔄 Handlers - Traitement message normal")
                self._handle_message(message)
            elif 'edited_message' in update:
                message = update['edited_message']
                logger.info(f"🔄 Handlers - Traitement message édité pour prédictions/vérifications")
                self._handle_edited_message(message)
            else:
                logger.info(f"⚠️ Type d'update non géré: {list(update.keys())}")

        except Exception as e:
            logger.error(f"Error handling update: {e}")

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle regular messages"""
        try:
            chat_id = message['chat']['id']
            user_id = message.get('from', {}).get('id')
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id) # If sender_chat is missing, assume it's the chat itself

            # Rate limiting check (skip for channels/groups)
            chat_type = message['chat'].get('type', 'private')
            if user_id and chat_type == 'private' and is_rate_limited(user_id):
                self.send_message(chat_id, "⏰ Veuillez patienter avant d'envoyer une autre commande.")
                return

            # Handle commands
            if 'text' in message:
                text = message['text'].strip()

                if text == '/start':
                    self._handle_start_command(chat_id, user_id)
                elif text == '/help':
                    self._handle_help_command(chat_id, user_id)
                elif text == '/about':
                    self._handle_about_command(chat_id, user_id)
                elif text == '/dev':
                    self._handle_dev_command(chat_id, user_id)
                elif text == '/deploy':
                    self._handle_deploy_command(chat_id, user_id)
                elif text == '/ni':
                    self._handle_ni_command(chat_id, user_id)
                elif text.startswith('/cos'):
                    self._handle_cos_command(chat_id, text, user_id)
                elif text == '/redi':
                    self._handle_redi_command(chat_id, sender_chat_id, user_id)
                elif text == '/reset':
                    self._handle_reset_command(sender_chat_id, user_id)
                elif text.startswith('/cooldown'):
                    self._handle_cooldown_command(chat_id, text, user_id)
                elif text.startswith('/redirect'):
                    self._handle_redirect_command(chat_id, text, user_id)
                elif text.startswith('/announce'):
                    self._handle_announce_command(chat_id, text, user_id)
                elif text == '/fin':
                    self._handle_fin_command(chat_id, user_id)
                else:
                    # Handle regular messages - check for card predictions even in regular messages
                    self._handle_regular_message(message)

                    # Also process for card prediction in channels/groups (for polling mode)
                    if chat_type in ['group', 'supergroup', 'channel'] and self.card_predictor:
                        self._process_card_message(message)

                        # NOUVEAU: Vérification sur messages normaux aussi
                        self._process_verification_on_normal_message(message)

            # Handle new chat members
            if 'new_chat_members' in message:
                self._handle_new_chat_members(message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _handle_edited_message(self, message: Dict[str, Any]) -> None:
        """Handle edited messages with enhanced webhook processing for predictions and verification"""
        try:
            chat_id = message['chat']['id']
            chat_type = message['chat'].get('type', 'private')
            user_id = message.get('from', {}).get('id')
            message_id = message.get('message_id')
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id) # If sender_chat is missing, assume it's the chat itself

            logger.info(f"✏️ WEBHOOK - Message édité reçu ID:{message_id} | Chat:{chat_id} | Sender:{sender_chat_id}")

            # Rate limiting check (skip for channels/groups)
            if user_id and chat_type == 'private' and is_rate_limited(user_id):
                return

            # Process edited messages
            if 'text' in message:
                text = message['text']
                logger.info(f"✏️ WEBHOOK - Contenu édité: {text[:100]}...")

                # Skip card prediction if card_predictor is not available
                if not self.card_predictor:
                    logger.warning("❌ Card predictor not available")
                    return

                # Vérifier que c'est du canal autorisé
                if sender_chat_id != TARGET_CHANNEL_ID:
                    logger.info(f"🚫 Message édité ignoré - Canal non autorisé: {sender_chat_id}")
                    return

                logger.info(f"✅ WEBHOOK - Message édité du canal autorisé: {TARGET_CHANNEL_ID}")

                # TRAITEMENT MESSAGES ÉDITÉS AMÉLIORÉ - Prédiction ET Vérification
                has_completion = self.card_predictor.has_completion_indicators(text)
                has_bozato = '🔰' in text
                has_checkmark = '✅' in text
                
                logger.info(f"🔍 ÉDITION - Finalisation: {has_completion}, 🔰: {has_bozato}, ✅: {has_checkmark}")

                if has_completion:
                    logger.info(f"🎯 ÉDITION FINALISÉE - Traitement prédiction ET vérification")

                    # SYSTÈME 1: PRÉDICTION AUTOMATIQUE (messages édités avec finalisation)
                    should_predict, game_number, combination = self.card_predictor.should_predict(text)

                    if should_predict and game_number is not None and combination is not None:
                        prediction = self.card_predictor.make_prediction(game_number, combination)
                        logger.info(f"🔮 PRÉDICTION depuis ÉDITION: {prediction}")

                        # Envoyer la prédiction et stocker les informations
                        target_channel = self.get_redirect_channel(sender_chat_id)
                        sent_message_info = self.send_message(target_channel, prediction)
                        if sent_message_info and isinstance(sent_message_info, dict) and 'message_id' in sent_message_info:
                            target_game = game_number + 2
                            self.card_predictor.sent_predictions[target_game] = {
                                'chat_id': target_channel,
                                'message_id': sent_message_info['message_id']
                            }
                            logger.info(f"📝 PRÉDICTION STOCKÉE pour jeu {target_game} vers canal {target_channel}")

                    # SYSTÈME 2: VÉRIFICATION UNIFIÉE (messages édités avec finalisation)
                    verification_result = self.card_predictor._verify_prediction_common(text, is_edited=True)
                    if verification_result:
                        logger.info(f"🔍 ✅ VÉRIFICATION depuis ÉDITION: {verification_result}")
                        
                        if verification_result.get('type') == 'edit_message':
                            predicted_game = verification_result.get('predicted_game')
                            new_message = verification_result.get('new_message')

                            # Tenter d'éditer le message de prédiction existant
                            if predicted_game in self.card_predictor.sent_predictions:
                                message_info = self.card_predictor.sent_predictions[predicted_game]
                                edit_success = self.edit_message(
                                    message_info['chat_id'],
                                    message_info['message_id'],
                                    new_message
                                )

                                if edit_success:
                                    logger.info(f"🔍 ✅ MESSAGE ÉDITÉ avec succès - Prédiction {predicted_game}")
                                else:
                                    logger.error(f"🔍 ❌ ÉCHEC ÉDITION - Prédiction {predicted_game}")
                                    # Fallback: envoyer nouveau message
                                    target_channel = self.get_redirect_channel(sender_chat_id)
                                    self.send_message(target_channel, new_message)
                            else:
                                logger.info(f"🔍 📤 NOUVEAU MESSAGE - Pas de message stocké pour {predicted_game}")
                                target_channel = self.get_redirect_channel(sender_chat_id)
                                self.send_message(target_channel, new_message)
                    else:
                        logger.info(f"🔍 ⭕ AUCUNE VÉRIFICATION depuis édition")

                # Gestion des messages temporaires
                elif self.card_predictor.has_pending_indicators(text):
                    logger.info(f"⏰ WEBHOOK - Message temporaire détecté, en attente de finalisation")
                    if message_id:
                        self.card_predictor.pending_edits[message_id] = {
                            'original_text': text,
                            'timestamp': datetime.now()
                        }

        except Exception as e:
            logger.error(f"❌ Error handling edited message via webhook: {e}")

    def _process_card_message(self, message: Dict[str, Any]) -> None:
        """Process message for card prediction (works for both regular and edited messages)"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id) # If sender_chat is missing, assume it's the chat itself

            # Only process messages from Baccarat Kouamé channel
            if sender_chat_id != TARGET_CHANNEL_ID:
                logger.info(f"🚫 Message ignoré - Canal non autorisé: {sender_chat_id} (attendu: {TARGET_CHANNEL_ID})")
                return

            if not text or not self.card_predictor:
                return

            logger.info(f"🎯 Traitement message CANAL AUTORISÉ pour prédiction: {text[:50]}...")
            logger.info(f"📍 Canal source: {sender_chat_id} | Chat destination: {chat_id}")

            # Les messages normaux ne font PAS de prédiction mais PEUVENT faire de la vérification
            logger.info(f"📨 Message normal - Vérification possible, prédiction seulement sur éditions")

            # Store temporary messages with pending indicators
            if self.card_predictor.has_pending_indicators(text):
                message_id = message.get('message_id')
                if message_id:
                    self.card_predictor.temporary_messages[message_id] = text
                    logger.info(f"⏰ Message temporaire stocké: {message_id}")

            # VÉRIFICATION UNIFIÉE - Messages normaux avec 🔰 ou ✅
            has_completion = self.card_predictor.has_completion_indicators(text)
            
            if has_completion:
                logger.info(f"🔍 MESSAGE NORMAL avec finalisation: {text[:50]}...")
                verification_result = self.card_predictor._verify_prediction_common(text, is_edited=False)
                if verification_result:
                    logger.info(f"🔍 ✅ VÉRIFICATION depuis MESSAGE NORMAL: {verification_result}")
                    
                    if verification_result['type'] == 'edit_message':
                        predicted_game = verification_result['predicted_game']
                        if predicted_game in self.card_predictor.sent_predictions:
                            message_info = self.card_predictor.sent_predictions[predicted_game]
                            edit_success = self.edit_message(
                                message_info['chat_id'],
                                message_info['message_id'],
                                verification_result['new_message']
                            )
                            if edit_success:
                                logger.info(f"✅ MESSAGE ÉDITÉ depuis message normal - Prédiction {predicted_game}")
                            else:
                                target_channel = self.get_redirect_channel(sender_chat_id)
                                self.send_message(target_channel, verification_result['new_message'])
                        else:
                            logger.info(f"📤 NOUVEAU MESSAGE - Prédiction {predicted_game}")
                            target_channel = self.get_redirect_channel(sender_chat_id)
                            self.send_message(target_channel, verification_result['new_message'])
                else:
                    logger.info(f"🔍 ⭕ AUCUNE VÉRIFICATION trouvée")
            else:
                logger.info(f"🔍 MESSAGE NORMAL sans finalisation - Pas de vérification: {text[:30]}...")

        except Exception as e:
            logger.error(f"Error processing card message: {e}")

    def _process_verification_on_normal_message(self, message: Dict[str, Any]) -> None:
        """Process verification on normal messages (not just edited ones) - AMÉLIORÉ"""
        try:
            text = message.get('text', '')
            chat_id = message['chat']['id']
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id)

            # Only process messages from Baccarat Kouamé channel
            if sender_chat_id != TARGET_CHANNEL_ID:
                return

            if not text or not self.card_predictor:
                return

            logger.info(f"🔍 VÉRIFICATION MESSAGE NORMAL: {text[:50]}...")

            # VÉRIFICATION AMÉLIORÉE - Messages normaux avec 🔰 ou ✅
            has_completion = self.card_predictor.has_completion_indicators(text)
            has_bozato = '🔰' in text
            has_checkmark = '✅' in text

            logger.info(f"🔍 INDICATEURS - Finalisation: {has_completion}, 🔰: {has_bozato}, ✅: {has_checkmark}")

            if has_completion:
                logger.info(f"🎯 MESSAGE NORMAL FINALISÉ - Lancement vérification complète")

                # Utiliser le système de vérification unifié
                verification_result = self.card_predictor._verify_prediction_common(text, is_edited=False)
                if verification_result:
                    logger.info(f"🔍 ✅ VÉRIFICATION RÉUSSIE depuis MESSAGE NORMAL: {verification_result}")
                    
                    if verification_result['type'] == 'edit_message':
                        predicted_game = verification_result['predicted_game']
                        
                        # Tenter d'éditer le message original de prédiction
                        if predicted_game in self.card_predictor.sent_predictions:
                            message_info = self.card_predictor.sent_predictions[predicted_game]
                            edit_success = self.edit_message(
                                message_info['chat_id'],
                                message_info['message_id'],
                                verification_result['new_message']
                            )
                            
                            if edit_success:
                                logger.info(f"✅ MESSAGE ÉDITÉ avec succès - Prédiction {predicted_game} mise à jour depuis message normal")
                            else:
                                logger.warning(f"⚠️ ÉCHEC ÉDITION - Envoi nouveau message pour {predicted_game}")
                                target_channel = self.get_redirect_channel(sender_chat_id)
                                self.send_message(target_channel, verification_result['new_message'])
                        else:
                            logger.info(f"📤 NOUVEAU MESSAGE - Aucun message stocké pour {predicted_game}")
                            target_channel = self.get_redirect_channel(sender_chat_id)
                            self.send_message(target_channel, verification_result['new_message'])
                else:
                    logger.info(f"🔍 ⭕ AUCUNE VÉRIFICATION - Pas de prédiction éligible trouvée")
            else:
                logger.info(f"🔍 ⏸️ MESSAGE NORMAL sans finalisation - Pas de vérification")

        except Exception as e:
            logger.error(f"❌ Error processing verification on normal message: {e}")

    def _process_completed_edit(self, message: Dict[str, Any]) -> None:
        """Process a message that was edited and now contains completion indicators"""
        try:
            chat_id = message['chat']['id']
            chat_type = message['chat'].get('type', 'private')
            text = message['text']
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id) # If sender_chat is missing, assume it's the chat itself


            # Only process in groups/channels
            if chat_type in ['group', 'supergroup', 'channel'] and self.card_predictor:
                # Check if we should make a prediction from this completed edit
                should_predict, game_number, combination = self.card_predictor.should_predict(text)

                if should_predict and game_number is not None and combination is not None:
                    prediction = self.card_predictor.make_prediction(game_number, combination)
                    logger.info(f"Making prediction from completed edit: {prediction}")

                    # Send prediction to the chat
                    target_channel = self.get_redirect_channel(sender_chat_id) # Utiliser le canal redirigé
                    sent_message_info = self.send_message(target_channel, prediction)
                    if sent_message_info and isinstance(sent_message_info, dict) and 'message_id' in sent_message_info:
                        target_game = game_number + 2
                        self.card_predictor.sent_predictions[target_game] = {
                            'chat_id': target_channel, # Stocker le chat_id redirigé
                            'message_id': sent_message_info['message_id']
                        }
                        logger.info(f"📝 CORRECTION - Prédiction stockée CORRECTEMENT pour jeu {target_game} (prédit depuis jeu {game_number}) vers {target_channel}")


                # Also check for verification with enhanced logic for edited messages
                verification_result = self.card_predictor.verify_prediction_from_edit(text)
                if verification_result:
                    logger.info(f"Verification from completed edit: {verification_result}")

                    if verification_result['type'] == 'update_message':
                        predicted_game = verification_result['predicted_game']
                        if predicted_game in self.card_predictor.sent_predictions:
                            message_info = self.card_predictor.sent_predictions[predicted_game]
                            edit_success = self.edit_message(
                                message_info['chat_id'], # Utiliser le chat_id stocké (redirigé)
                                message_info['message_id'],
                                verification_result['new_message']
                            )
                            if edit_success:
                                logger.info(f"✅ Message de prédiction édité pour jeu {predicted_game}")
                            else:
                                target_channel = self.get_redirect_channel(sender_chat_id) # Utiliser le canal redirigé
                                self.send_message(target_channel, verification_result['new_message'])
                        else:
                            target_channel = self.get_redirect_channel(sender_chat_id) # Utiliser le canal redirigé
                            self.send_message(target_channel, verification_result['new_message'])

        except Exception as e:
            logger.error(f"Error processing completed edit: {e}")

    def _is_authorized_user(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        return user_id == AUTHORIZED_USER_ID

    def _handle_start_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /start command with authorization check"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                logger.warning(f"🚫 Tentative d'accès non autorisée: {user_id}")
                return

            self.send_message(chat_id, WELCOME_MESSAGE)
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            self.send_message(chat_id, "❌ Une erreur s'est produite. Veuillez réessayer.")

    def _handle_help_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /help command with authorization check"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return
            self.send_message(chat_id, HELP_MESSAGE)
        except Exception as e:
            logger.error(f"Error in help command: {e}")

    def _handle_about_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /about command with authorization check"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return
            self.send_message(chat_id, ABOUT_MESSAGE)
        except Exception as e:
            logger.error(f"Error in about command: {e}")

    def _handle_dev_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /dev command with authorization check"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return
            self.send_message(chat_id, DEV_MESSAGE)
        except Exception as e:
            logger.error(f"Error in dev command: {e}")

    def _handle_deploy_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /deploy command with authorization check"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            # Send initial message
            self.send_message(
                chat_id, 
                "🚀 Préparation du fichier de déploiement... Veuillez patienter."
            )

            # Check if deployment file exists
            if not os.path.exists(self.deployment_file_path):
                self.send_message(
                    chat_id,
                    "❌ Fichier de déploiement non trouvé. Contactez l'administrateur."
                )
                logger.error(f"Deployment file {self.deployment_file_path} not found")
                return

            # Send the file
            success = self.send_document(chat_id, self.deployment_file_path)

            if success:
                self.send_message(
                    chat_id,
                    "✅ Fichier de déploiement envoyé avec succès !\n\n"
                    "📋 Instructions de déploiement :\n"
                    "1. Téléchargez le fichier zip\n"
                    "2. Créez un nouveau service sur render.com\n"
                    "3. Uploadez le zip ou connectez votre repository\n"
                    "4. Configurez les variables d'environnement :\n"
                    "   - BOT_TOKEN : Votre token de bot\n"
                    "   - WEBHOOK_URL : https://votre-app.onrender.com\n"
                    "   - PORT : 10000\n\n"
                    "🎯 Votre bot sera déployé automatiquement !"
                )
            else:
                self.send_message(
                    chat_id,
                    "❌ Échec de l'envoi du fichier. Réessayez plus tard."
                )

        except Exception as e:
            logger.error(f"Error handling deploy command: {e}")
            self.send_message(
                chat_id,
                "❌ Une erreur s'est produite lors du traitement de votre demande."
            )
        except Exception as e:
            logger.error(f"Error in deploy command: {e}")

    def _handle_ni_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /ni command - send modified files package"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            # Send initial message
            self.send_message(
                chat_id, 
                "📦 Préparation du package des fichiers modifiés... Veuillez patienter."
            )

            # Check if deployment file exists
            if not os.path.exists(self.deployment_file_path):
                self.send_message(
                    chat_id,
                    "❌ Package des fichiers modifiés non trouvé. Contactez l'administrateur."
                )
                logger.error(f"Modified files package {self.deployment_file_path} not found")
                return

            # Send the file
            success = self.send_document(chat_id, self.deployment_file_path)

            if success:
                self.send_message(
                    chat_id,
                    f"✅ **PACKAGE DEPLOYER37.ZIP ENVOYÉ !**\n\n"
                    f"📦 **Fichier :** {self.deployment_file_path}\n\n"
                    "📋 **Contenu du package :**\n"
                    "• card_predictor.py (reconnaissance 🔰 ✅)\n"
                    "• handlers.py (commandes /ni et /deploy)\n"
                    "• config.py (URL Render.com)\n"
                    "• main.py, bot.py (serveur webhook)\n"
                    "• Fichiers config (requirements, render.yaml)\n\n"
                    "🎯 **DEPLOYER37 - DRAPEAU AU DÉBUT :**\n"
                    "• ⚡ Vérification 0: ✅0️⃣ ARRÊT si trouvé\n"
                    "• ⚡ Vérification +1: ✅1️⃣ ARRÊT si trouvé\n"
                    "• ⚡ Vérification +2: ✅2️⃣ ARRÊT si trouvé\n"
                    "• ⚡ Vérification +3: ✅3️⃣ ARRÊT si trouvé\n"
                    "• ❌ Si pas trouvé: 📍⭕ ARRÊT définitif\n"
                    "• 🇧🇯 FORMAT: 🔵🇧🇯715🔵👉🏻:♦️statut :✅2️⃣\n"
                    "• 🚀 Status: Bot actif et fonctionnel\n\n"
                    "🇧🇯 DRAPEAU AU DÉBUT DU MESSAGE !"
                )
            else:
                self.send_message(
                    chat_id,
                    "❌ Échec de l'envoi du package. Réessayez plus tard."
                )

        except Exception as e:
            logger.error(f"Error handling ni command: {e}")
            self.send_message(
                chat_id,
                "❌ Une erreur s'est produite lors du traitement de votre demande."
            )

    def _handle_cooldown_command(self, chat_id: int, text: str, user_id: int = None) -> None:
        """Handle /cooldown command to modify prediction cooldown"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            parts = text.strip().split()
            if len(parts) == 1:
                # Show current cooldown
                current_cooldown = self.card_predictor.prediction_cooldown if self.card_predictor else 190
                self.send_message(
                    chat_id,
                    f"⏰ **COOLDOWN ACTUEL**\n\n"
                    f"🕒 Délai actuel: {current_cooldown} secondes\n\n"
                    f"💡 **Utilisation:**\n"
                    f"• `/cooldown` - Voir le délai actuel\n"
                    f"• `/cooldown [secondes]` - Modifier le délai\n\n"
                    f"📝 **Exemples:**\n"
                    f"• `/cooldown 120` - Délai de 2 minutes\n"
                    f"• `/cooldown 300` - Délai de 5 minutes\n"
                    f"• `/cooldown 60` - Délai de 1 minute"
                )
                return

            if len(parts) != 2:
                self.send_message(
                    chat_id,
                    "❌ Format incorrect !\n\n"
                    "🎯 Utilisation : `/cooldown [secondes]`\n"
                    "📍 Minimum : 30 secondes\n"
                    "📍 Maximum : 600 secondes (10 minutes)\n\n"
                    "💡 Exemples :\n"
                    "• `/cooldown 190` - Délai de 3m10s (défaut)\n"
                    "• `/cooldown 120` - Délai de 2 minutes\n"
                    "• `/cooldown 60` - Délai de 1 minute"
                )
                return

            try:
                seconds = int(parts[1])
                if seconds < 30 or seconds > 600:
                    self.send_message(
                        chat_id,
                        "❌ Délai invalide !\n\n"
                        "📍 Minimum : 30 secondes\n"
                        "📍 Maximum : 600 secondes (10 minutes)\n"
                        "🎯 Recommandé : 190 secondes"
                    )
                    return
            except ValueError:
                self.send_message(chat_id, "❌ Veuillez entrer un nombre valide de secondes.")
                return

            # Update cooldown in card predictor
            if self.card_predictor:
                old_cooldown = self.card_predictor.prediction_cooldown
                self.card_predictor.prediction_cooldown = seconds
                minutes = seconds // 60
                remaining_seconds = seconds % 60
                time_text = f"{minutes}m{remaining_seconds:02d}s" if minutes > 0 else f"{seconds}s"

                self.send_message(
                    chat_id,
                    f"✅ **COOLDOWN MIS À JOUR !**\n\n"
                    f"🕒 Ancien délai : {old_cooldown}s\n"
                    f"🕒 Nouveau délai : {seconds}s ({time_text})\n\n"
                    f"⏰ Le bot attendra maintenant {time_text} entre chaque prédiction automatique."
                )
                logger.info(f"🔧 COOLDOWN modifié par l'utilisateur {user_id}: {old_cooldown}s → {seconds}s")
            else:
                self.send_message(chat_id, "❌ Erreur : Système de prédiction non disponible.")

        except Exception as e:
            logger.error(f"Error handling cooldown command: {e}")
            self.send_message(chat_id, "❌ Une erreur s'est produite lors du traitement de votre commande.")

    def _handle_announce_command(self, chat_id: int, text: str, user_id: int = None) -> None:
        """Handle /announce command to send announcements to prediction channel"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            parts = text.strip().split(maxsplit=1)
            if len(parts) == 1:
                # Show usage instructions
                self.send_message(
                    chat_id,
                    "📢 **COMMANDE D'ANNONCE**\n\n"
                    "🎯 **Utilisation :**\n"
                    "• `/announce [votre message]` - Envoyer une annonce\n\n"
                    "📝 **Exemple :**\n"
                    "• `/announce Nouvelle règle de prédiction activée !`\n\n"
                    "📍 **Destination :**\n"
                    "L'annonce sera envoyée dans le canal de prédictions configuré.\n\n"
                    "💡 **Note :**\n"
                    "Seul l'utilisateur autorisé peut envoyer des annonces."
                )
                return

            # Extract announcement message
            announcement_text = parts[1]

            # Get target channel for announcements (same as predictions)
            # Use the configured source channel ID with proper format
            source_channel_id = -1002682552255  # Canal source Baccarat Kouamé
            target_channel = self.get_redirect_channel(source_channel_id)

            # Calculate success rate from last 20 predictions
            success_rate = self._calculate_success_rate()

            # Format announcement message with success rate
            formatted_message = f"📢 **ANNONCE OFFICIELLE** 📢\n\n{announcement_text}\n\n🤖 _Bot de prédiction automatique des cartes enseignes baccara développé par Sossou Kouamé Appolinaire_\n📊 _Taux de réussite: {success_rate}% (basé sur les 20 dernières prédictions vérifiées)_"

            # Send announcement
            sent_message_info = self.send_message(target_channel, formatted_message)

            if sent_message_info and isinstance(sent_message_info, dict):
                self.send_message(
                    chat_id,
                    f"✅ **ANNONCE ENVOYÉE !**\n\n"
                    f"📍 Canal destination: {target_channel}\n"
                    f"💬 Message: {announcement_text[:50]}{'...' if len(announcement_text) > 50 else ''}\n\n"
                    f"📢 Votre annonce a été diffusée avec succès."
                )
                logger.info(f"📢 ANNONCE envoyée par l'utilisateur {user_id} vers {target_channel}: {announcement_text[:50]}...")
            else:
                self.send_message(chat_id, "❌ Erreur lors de l'envoi de l'annonce. Veuillez réessayer.")

        except Exception as e:
            logger.error(f"Error handling announce command: {e}")
            self.send_message(chat_id, "❌ Une erreur s'est produite lors de l'envoi de l'annonce.")

    def _calculate_success_rate(self) -> str:
        """Calculate success rate based on last 20 verified predictions"""
        try:
            if not self.card_predictor:
                return "N/A"

            # Get last 20 verified predictions
            verified_predictions = []
            for game_num, prediction_info in self.card_predictor.sent_predictions.items():
                if 'status' in prediction_info and prediction_info['status'] != 'pending':
                    verified_predictions.append(prediction_info)

            # Sort by game number and take last 20
            verified_predictions.sort(key=lambda x: x.get('game_number', 0))
            last_20 = verified_predictions[-20:] if len(verified_predictions) >= 20 else verified_predictions

            if not last_20:
                return "En attente"

            # Count successful predictions (✅0️⃣, ✅1️⃣, ✅2️⃣, ✅3️⃣)
            successful_count = 0
            for prediction in last_20:
                status = prediction.get('status', '')
                if status in ['correct', 'verified_0', 'verified_1', 'verified_2', 'verified_3']:
                    successful_count += 1

            # Calculate percentage
            success_percentage = round((successful_count / len(last_20)) * 100, 1)
            return f"{success_percentage}"

        except Exception as e:
            logger.error(f"Error calculating success rate: {e}")
            return "N/A"

    def _handle_redirect_command(self, chat_id: int, text: str, user_id: int = None) -> None:
        """Handle /redirect command for advanced channel redirection"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            parts = text.strip().split()
            if len(parts) == 1:
                # Show current redirections
                if self.card_predictor and self.card_predictor.redirect_channels:
                    redirect_info = []
                    for source_id, target_id in self.card_predictor.redirect_channels.items():
                        redirect_info.append(f"📍 {source_id} → {target_id}")

                    redirections_text = "\n".join(redirect_info)
                    self.send_message(
                        chat_id,
                        f"📍 **REDIRECTIONS ACTIVES**\n\n"
                        f"{redirections_text}\n\n"
                        f"💡 **Utilisation:**\n"
                        f"• `/redirect` - Voir les redirections\n"
                        f"• `/redirect [source_id] [target_id]` - Ajouter redirection\n"
                        f"• `/redirect clear` - Supprimer toutes les redirections"
                    )
                else:
                    self.send_message(
                        chat_id,
                        f"📍 **AUCUNE REDIRECTION ACTIVE**\n\n"
                        f"🎯 Canal par défaut: -1002646551216\n\n"
                        f"💡 **Utilisation:**\n"
                        f"• `/redirect [source_id] [target_id]` - Ajouter redirection\n"
                        f"• `/redirect clear` - Supprimer toutes les redirections\n\n"
                        f"📝 **Exemples:**\n"
                        f"• `/redirect -1002682552255 -1002646551216`\n"
                        f"• `/redirect clear`"
                    )
                return

            if parts[1] == "clear":
                # Clear all redirections
                if self.card_predictor:
                    self.card_predictor.redirect_channels.clear()
                    self.send_message(
                        chat_id,
                        "✅ **REDIRECTIONS SUPPRIMÉES !**\n\n"
                        "🎯 Toutes les redirections ont été supprimées.\n"
                        "📍 Le canal par défaut sera utilisé: -1002646551216"
                    )
                    logger.info(f"🔧 Toutes les redirections supprimées par l'utilisateur {user_id}")
                return

            if len(parts) != 3:
                self.send_message(
                    chat_id,
                    "❌ Format incorrect !\n\n"
                    "🎯 Utilisation : `/redirect [source_id] [target_id]`\n\n"
                    "💡 Exemples :\n"
                    "• `/redirect -1002682552255 -1002646551216`\n"
                    "• `/redirect clear` - Supprimer toutes les redirections"
                )
                return

            try:
                # Handle IDs with or without minus sign
                source_str = parts[1].strip()
                target_str = parts[2].strip()

                # Ensure proper negative format for channel IDs
                if not source_str.startswith('-') and len(source_str) > 10:
                    source_str = '-' + source_str
                if not target_str.startswith('-') and len(target_str) > 10:
                    target_str = '-' + target_str

                source_id = int(source_str)
                target_id = int(target_str)
            except ValueError:
                self.send_message(chat_id, "❌ Les IDs de canaux doivent être des nombres.")
                return

            # Add redirection
            if self.card_predictor:
                self.card_predictor.set_redirect_channel(source_id, target_id)
                self.send_message(
                    chat_id,
                    f"✅ **REDIRECTION CONFIGURÉE !**\n\n"
                    f"📍 Canal source: {source_id}\n"
                    f"📍 Canal destination: {target_id}\n\n"
                    f"🔮 Les prédictions du canal {source_id} seront maintenant envoyées vers {target_id}."
                )
                logger.info(f"🔧 Redirection configurée par l'utilisateur {user_id}: {source_id} → {target_id}")
            else:
                self.send_message(chat_id, "❌ Erreur : Système de prédiction non disponible.")

        except Exception as e:
            logger.error(f"Error handling redirect command: {e}")
            self.send_message(chat_id, "❌ Une erreur s'est produite lors du traitement de votre commande.")

    def _handle_cos_command(self, chat_id: int, text: str, user_id: int = None) -> None:
        """Handle /cos command to set card position preference"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            # Parse command: /cos 1 or /cos 2
            parts = text.strip().split()
            if len(parts) != 2:
                self.send_message(
                    chat_id,
                    "❌ Format incorrect !\n\n"
                    "🎯 Utilisation : /cos [position]\n"
                    "📍 Position 1 : Prendre la première carte\n"
                    "📍 Position 2 : Prendre la deuxième carte\n\n"
                    "💡 Exemples :\n"
                    "• /cos 1 - Prendre la première carte\n"
                    "• /cos 2 - Prendre la deuxième carte\n\n"
                    "⚠️ Si les deux premières cartes ont le même costume, le bot prendra automatiquement la troisième carte."
                )
                return

            try:
                position = int(parts[1])
                if position not in [1, 2]:
                    self.send_message(
                        chat_id,
                        "❌ Position invalide !\n\n"
                        "📍 Positions disponibles :\n"
                        "• 1 : Première carte\n"
                        "• 2 : Deuxième carte"
                    )
                    return
            except ValueError:
                self.send_message(
                    chat_id,
                    "❌ Position invalide ! Utilisez 1 ou 2."
                )
                return

            # Set position preference in card predictor
            if self.card_predictor:
                self.card_predictor.set_position_preference(position)
                position_text = "première" if position == 1 else "deuxième"
                self.send_message(
                    chat_id,
                    f"✅ Configuration mise à jour !\n\n"
                    f"🎯 Position choisie : {position} ({position_text} carte)\n\n"
                    f"🔮 Le bot utilisera maintenant la {position_text} carte pour ses prédictions.\n\n"
                    f"⚠️ Note : Si les deux premières cartes ont le même costume, le bot prendra automatiquement la troisième carte, peu importe votre choix."
                )
            else:
                self.send_message(
                    chat_id,
                    "❌ Erreur : Système de prédiction non disponible."
                )

        except Exception as e:
            logger.error(f"Error handling cos command: {e}")
            self.send_message(
                chat_id,
                "❌ Une erreur s'est produite lors du traitement de votre commande."
            )



    def _handle_regular_message(self, message: Dict[str, Any]) -> None:
        """Handle regular text messages"""
        try:
            chat_id = message['chat']['id']
            chat_type = message['chat'].get('type', 'private')
            text = message.get('text', '')
            message_id = message.get('message_id')
            sender_chat = message.get('sender_chat', {})
            sender_chat_id = sender_chat.get('id', chat_id) # If sender_chat is missing, assume it's the chat itself


            # In private chats, provide help
            if chat_type == 'private':
                self.send_message(
                    chat_id,
                    "🎭 Salut ! Je suis le bot de Joker.\n"
                    "Utilisez /help pour voir mes commandes disponibles.\n\n"
                    "Ajoutez-moi à un canal pour que je puisse analyser les cartes ! 🎴"
                )

            # In groups/channels, analyze for card patterns
            elif chat_type in ['group', 'supergroup', 'channel'] and self.card_predictor:
                # Check if this message has pending indicators
                if message_id and self.card_predictor.should_wait_for_edit(text, message_id):
                    logger.info(f"Message {message_id} has pending indicators, waiting for edit: {text[:50]}...")
                    # Don't process for predictions yet, wait for the edit
                    return

                # Les messages normaux dans les groupes/canaux ne font PAS de prédiction ni vérification
                # Seuls les messages ÉDITÉS déclenchent les systèmes
                logger.info(f"📨 Message normal groupe/canal - AUCUNE ACTION (systèmes actifs seulement sur éditions)")
                logger.info(f"Group message in {chat_id}: {text[:50]}...")

        except Exception as e:
            logger.error(f"Error handling regular message: {e}")

    def _handle_new_chat_members(self, message: Dict[str, Any]) -> None:
        """Handle when bot is added to a channel or group"""
        try:
            chat_id = message['chat']['id']
            chat_title = message['chat'].get('title', 'ce chat')

            for member in message['new_chat_members']:
                # Check if our bot was added (we can't know our own ID easily in webhook mode)
                # So we'll just send greeting when any bot is added
                if member.get('is_bot', False):
                    logger.info(f"Bot added to chat {chat_id}: {chat_title}")
                    self.send_message(chat_id, GREETING_MESSAGE)
                    break

        except Exception as e:
            logger.error(f"Error handling new chat members: {e}")

    def _handle_redi_command(self, chat_id: int, sender_chat_id: int, user_id: int = None) -> None:
        """Handle /redi command to redirect predictions to the current chat"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return

            # Store the redirection: source chat ID -> target chat ID
            # We use sender_chat_id as the source of the command, and chat_id as the target (where the command was issued)
            if sender_chat_id == chat_id: # If command is issued in a private chat or a channel the bot directly manages
                self.redirected_channels[sender_chat_id] = chat_id
                self.send_message(chat_id, "✅ Les prédictions seront maintenant envoyées à ce chat.")
            else: # If command is issued in a group/supergroup where bot is an admin
                self.redirected_channels[sender_chat_id] = chat_id
                self.send_message(chat_id, "✅ Les prédictions seront maintenant envoyées à ce chat.")

        except Exception as e:
            logger.error(f"Error handling redi command: {e}")
            self.send_message(chat_id, "❌ Une erreur s'est produite lors de la configuration de la redirection.")

    def _handle_reset_command(self, sender_chat_id: int, user_id: int = None) -> None:
        """Handle /reset command to clear all predictions"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                # Pas de réponse car c'est souvent dans un groupe
                logger.warning(f"🚫 Tentative de reset non autorisée: {user_id}")
                return

            if self.card_predictor:
                self.card_predictor.sent_predictions = {}
                self.send_message(sender_chat_id, "✅ Toutes les prédictions ont été supprimées.")
            else:
                self.send_message(sender_chat_id, "❌ Erreur : Système de prédiction non disponible.")
        except Exception as e:
            logger.error(f"Error handling reset command: {e}")
            self.send_message(sender_chat_id, "❌ Une erreur s'est produite lors de la suppression des prédictions.")

    def _handle_fin_command(self, chat_id: int, user_id: int = None) -> None:
        """Handle /fin command - send final deployment package"""
        try:
            if user_id and not self._is_authorized_user(user_id):
                self.send_message(chat_id, "🚫 Vous n'êtes pas autorisé à utiliser ce bot.")
                return
            
            # Send initial message
            self.send_message(
                chat_id, 
                "📦 Préparation du package de déploiement final... Veuillez patienter."
            )

            # Check if deployment file exists
            if not os.path.exists(self.deployment_file_path):
                self.send_message(
                    chat_id,
                    "❌ Package de déploiement final non trouvé. Contactez l'administrateur."
                )
                logger.error(f"Final deployment package {self.deployment_file_path} not found")
                return

            # Send the file
            success = self.send_document(chat_id, self.deployment_file_path)

            if success:
                self.send_message(
                    chat_id,
                    f"✅ **PACKAGE FINAL COMPLET ENVOYÉ !**\n\n"
                    f"📦 **Fichier :** {self.deployment_file_path}\n\n"
                    "📋 **Package de déploiement FINAL avec TOUS les fichiers :**\n"
                    "• bot.py - Gestionnaire principal du bot\n"
                    "• handlers.py - Toutes les commandes (/fin, /deploy, /ni)\n"
                    "• card_predictor.py - Système de prédiction complet\n"
                    "• main.py - Serveur webhook optimisé\n"
                    "• config.py - Configuration Render.com\n"
                    "• requirements.txt - Dépendances Python\n"
                    "• render.yaml - Configuration déploiement\n"
                    "• Procfile - Script de démarrage\n"
                    "• README.md - Instructions détaillées\n\n"
                    "🎯 **DEPLOY299999 - VERSION FINALE :**\n"
                    "• 🔮 Prédictions automatiques avec cooldown\n"
                    "• ✅ Vérifications avec FORMAT EXACT :\n"
                    "  ⏳ : Prédiction en attente\n"
                    "  ✅0️⃣ : Succès immédiat (offset 0)\n"
                    "  ✅1️⃣ : Succès à +1 jeu\n"
                    "  ⭕ : Échec après 2\n"
                    "• 📊 Système d'annonces avec taux de réussite\n"
                    "• 🔧 Commandes de configuration avancées\n"
                    "• 🚀 Prêt pour render.com - Port 10000\n\n"
                    "🌐 **Instructions de déploiement :**\n"
                    "1. Téléchargez deploo299999_final_complete.zip\n"
                    "2. Créez un service sur render.com\n"
                    "3. Uploadez le ZIP complet\n"
                    "4. Variables d'environnement :\n"
                    "   - BOT_TOKEN : 7644537698:AAFjBt4dBfCB5YH4hxaPXV1bIXlNyIAQwjc\n"
                    "   - WEBHOOK_URL : https://votre-app.onrender.com\n"
                    "   - PORT : 10000\n\n"
                    "🚀 **VOTRE BOT DEPLOY299999 SERA 100% OPÉRATIONNEL !**"
                )
            else:
                self.send_message(
                    chat_id,
                    "❌ Échec de l'envoi du package final. Réessayez plus tard."
                )

        except Exception as e:
            logger.error(f"Error handling fin command: {e}")
            self.send_message(
                chat_id,
                "❌ Une erreur s'est produite lors du traitement de votre demande."
            )

    def get_redirect_channel(self, source_chat_id: int) -> int:
        """Get the target channel for redirection, defaults to -1002887687164"""
        logger.info(f"🔍 REDIRECTION - Recherche pour canal source: {source_chat_id}")

        # Vérifier d'abord les redirections du card_predictor
        if self.card_predictor and hasattr(self.card_predictor, 'redirect_channels'):
            redirect_target = self.card_predictor.redirect_channels.get(source_chat_id)
            if redirect_target:
                logger.info(f"✅ REDIRECTION card_predictor trouvée: {source_chat_id} -> {redirect_target}")
                return redirect_target

        # Vérifier les redirections locales
        local_redirect = self.redirected_channels.get(source_chat_id)
        if local_redirect:
            logger.info(f"✅ REDIRECTION locale trouvée: {source_chat_id} -> {local_redirect}")
            return local_redirect

        # Canal par défaut pour DEPLOY299999
        default_channel = -1002887687164
        logger.info(f"📍 REDIRECTION - Aucune redirection trouvée, utilisation du canal par défaut: {default_channel}")
        return default_channel


    def send_message(self, chat_id: int, text: str) -> Any: # Changed return type to Any to match potential dict return
        """Send text message to user"""
        try:
            import requests

            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=data, timeout=10)
            result = response.json()

            if result.get('ok'):
                logger.info(f"Message sent successfully to chat {chat_id}")
                return result.get('result', {})  # Return message info including message_id
            else:
                logger.error(f"Failed to send message: {result}")
                return False

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def send_document(self, chat_id: int, file_path: str) -> bool:
        """Send document file to user"""
        try:
            import requests

            url = f"{self.base_url}/sendDocument"

            with open(file_path, 'rb') as file:
                files = {
                    'document': (os.path.basename(file_path), file, 'application/zip')
                }
                data = {
                    'chat_id': chat_id,
                    'caption': '📦 Package de déploiement pour render.com\n\n🎯 Tout est inclus pour déployer votre bot !'
                }

                response = requests.post(url, data=data, files=files, timeout=60)
                result = response.json()

                if result.get('ok'):
                    logger.info(f"Document sent successfully to chat {chat_id}")
                    return True
                else:
                    logger.error(f"Failed to send document: {result}")
                    return False

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return False

    def edit_message(self, chat_id: int, message_id: int, new_text: str) -> bool:
        """Edit an existing message"""
        try:
            import requests

            url = f"{self.base_url}/editMessageText"
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': new_text,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, json=data, timeout=10)
            result = response.json()

            if result.get('ok'):
                logger.info(f"Message edited successfully in chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to edit message: {result}")
                return False

        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return False
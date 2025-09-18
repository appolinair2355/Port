# Overview

This is a sophisticated French-language Telegram bot (@Appma_bot) for automated card game predictions with real-time result verification. The bot monitors statistics channels, generates anticipatory predictions on specific trigger numbers (7, 8), edits messages in-place with status updates, and provides comprehensive performance tracking. Features include private channel configuration, automatic message editing, scheduled automatic predictions system, and complete deployment packages for Render.com hosting.

# Recent Changes (Août 2025)

✅ **Commande /intervalle et Package 2D Implémentés (16 Août 2025)**
- 🆕 NOUVELLE: Commande `/intervalle [minutes]` pour configurer le délai de prédiction
- ⏱️ Intervalle personnalisable entre 1-60 minutes (défaut: 5 minutes)
- 💾 Configuration persistante en base de données et JSON de secours
- 📦 Nouveau package de déploiement "deployment_2d.zip" avec toutes les fonctionnalités
- 🔧 Variables d'environnement étendues avec PREDICTION_INTERVAL
- 📚 Documentation complète README_2D.md et .env.example mis à jour
- ✅ Commande `/status` mise à jour pour afficher l'intervalle configuré
- 🎯 Package 2D remplace l'ancien système avec améliorations août 2025

✅ **Système de Vérification Corrigé et Messages Édités (16 Août 2025)**
- NOUVEAU: Messages ⏰/🕐 complètement IGNORÉS pour la vérification
- Vérification uniquement sur messages normaux (2 cartes + 2 cartes)
- Système d'offsets: 0→✅0️⃣, 1→✅1️⃣, 2→✅2️⃣, >2→❌❌ (arrêt au premier succès)
- CORRIGÉ: Vérification complète des 3 offsets avant marquage d'échec
- Détection des messages en cours d'édition avec ⏰ et 🕐
- Système d'attente: Messages ⏰/🕐 mis en attente jusqu'à édition finale avec 🔰/✅
- Surveillance des éditions: Handler MessageEdited() ajouté pour traiter les modifications
- Format: 🔵{numéro}— JOKER 2D| {statut} (remplace ancien format complexe)
- Exemple initial: 🔵910— JOKER 2D| ⏳
- Exemple final: 🔵910— JOKER 2D| ✅0️⃣
- Système As: Prédiction déclenchée uniquement par As (A) dans le premier groupe de parenthèses
- RÈGLE 1: Prédire SEULEMENT si As dans le premier groupe (ex: #n909. 1(A♦️J♣️) - ✅9(10♣️9♠️))
- RÈGLE 2: NE PAS prédire si As dans le deuxième groupe (ex: #n894. ✅3(5♣️8♣️Q♥️) - 1(K♣️A♠️K♠️))
- RÈGLE 3: NE PAS prédire si As dans les deux groupes
- Prédiction du numéro SUIVANT: #n909 → prédit #n910 (au lieu de multiples de 10)
- Packages de déploiement Render.com mis à jour (81.8 KB et 89.3 KB) avec toutes nouvelles fonctionnalités

✅ **Token API Mis à Jour (15 Août 2025)**
- Token Telegram bot mis à jour: 7815360317:AAGsrFzeUZrHOjujf5aY2UjlBj4GOblHSig
- Bot connecté avec succès: @Prsossou_bot
- Configuration complète des secrets Replit (API_ID, API_HASH, BOT_TOKEN, ADMIN_ID)
- Serveur web opérationnel sur port 10000
- Canaux configurés: Stats (-1002682552255), Display (-1002646800237)

✅ **Système de Déclenchement Variable Implémenté (6 Août 2025)**
- Déclencheurs variables: 6, 7, 8, 9 (au lieu de seulement 7, 8)
- Système anti-répétition: 30% chance d'ignorer le même déclencheur consécutif
- Exemple de variabilité: #137→#140, #146→#150, #158→#160, #169→#170
- Lancement variable de 1-4 minutes AVANT l'heure de prédiction (scheduler)
- Format de numérotation basé sur l'heure (ex: 7h50 → N0750)
- Package de déploiement Render.com complet avec toutes les fonctionnalités

✅ **Algorithme de Vérification Automatique Implémenté**
- Système de vérification selon offsets (0→✅0️⃣, 1→✅1️⃣, 2→✅2️⃣, sinon→📌❌)
- Comptage précis des cartes (symboles ♠️, ♣️, ♥️, ♦️ uniquement)
- Format de prédiction mis à jour: `🎯Nº:70 🔵Dis🔵tri🚥:statut :⌛`
- **Logique ⏰ corrigée**: ⏰ marque le jeu comme "plus de 2 cartes" et attend jeu > prédiction+2 pour échec
- Vérification temps réel lors de la réception des messages (pas d'API restrictive)
- Intégration complète entre prédictions manuelles et automatiques

✅ **Correction du Comptage des Cartes (Août 2025)**
- Résolution du problème de double comptage des symboles emoji
- Comptage précis des cartes dans les groupes de résultats
- Amélioration de la validation 2+2 pour la vérification des prédictions

✅ **Système de Planification Automatique Ajouté**
- Nouveau module `scheduler.py` pour prédictions automatiques programmées
- Système de vérification automatique des résultats
- Commandes `/scheduler` et `/schedule_info` pour la gestion
- Format YAML pour persistance des données de planification
- Intégration complète avec le bot principal

# User Preferences

Preferred communication style: Simple, everyday language.
Bot messaging: User wants clean, minimal bot responses without spam or unwanted messages.
Prediction format: Nouveau format simple "🔵{numéro}— JOKER 2D| {statut}" pour les prédictions.
Message updates: Original prediction messages should be edited in-place with final status, not new messages.
Trigger system: Bot should activate on numbers ending in 7, 8 to predict next number ending in 0.
Deployment: Complete Render.com deployment packages with all files included in ZIP format.
Variable Launch Timing: User requested variable launch timing (1-4 minutes before prediction time) not variable prediction intervals. Predictions at fixed times but launch time varies randomly 1-4 minutes before.
Verification Algorithm: Specific offset-based verification (exact→✅0️⃣, +1→✅1️⃣, +2→✅2️⃣, else→📌❌) with card symbol counting only. ⏰ symbol indicates "more than 2 cards" and continues verification until game > prediction+2 before marking failure.

# System Architecture

## Bot Framework
- **Telethon-based Telegram Bot**: Uses the Telethon library for Telegram API interactions, providing full client capabilities rather than just bot API access
- **Async Event-Driven Architecture**: Built on Python's asyncio for handling multiple concurrent Telegram events and messages
- **Session Management**: Maintains persistent bot sessions for reliable connectivity

## Prediction Engine
- **Pattern Matching System**: Custom CardPredictor class that uses regex patterns to extract game numbers and card symbols from messages
- **State Tracking**: Maintains prediction history, status tracking, and duplicate message detection
- **Symbol Counting Algorithm**: Counts card symbols (♠️, ♥️, ♦️, ♣️) from parentheses-enclosed content in messages

## Channel Management
- **Auto-Detection Logic**: Automatically identifies statistics and display channels when the bot joins
- **Dual Channel Architecture**: Separates data collection (stat channel) from result display (display channel)
- **Admin Confirmation System**: Requires administrator approval for channel assignments

## Data Flow
- **Message Processing Pipeline**: Monitors stat channels → extracts game data → generates predictions → posts to display channels
- **Result Verification**: Tracks prediction outcomes and maintains accuracy statistics
- **Duplicate Prevention**: Uses message tracking to avoid processing the same content multiple times

## Configuration Management
- **Environment-Based Config**: Uses .env files for sensitive data like API credentials and admin IDs
- **Runtime State Variables**: Maintains channel assignments and pending confirmations in memory

# External Dependencies

## Telegram Integration
- **Telethon Library**: Full-featured Telegram client library for Python
- **Telegram Bot API**: For bot token authentication and basic bot operations
- **Telegram Client API**: For advanced channel monitoring and message handling

## Environment Management
- **python-dotenv**: For loading environment variables from .env files
- **Environment Variables**: API_ID, API_HASH, BOT_TOKEN, ADMIN_ID for secure configuration

## Core Dependencies
- **Python asyncio**: For asynchronous operations and event handling
- **Python re (regex)**: For pattern matching and text extraction
- **Python os**: For environment variable access
- **PyYAML**: For automatic scheduling data persistence
- **datetime/timedelta**: For time-based scheduling and prediction timing

## Automatic Scheduling System
- **PredictionScheduler Class**: Manages automated prediction launches and verification
- **YAML Configuration**: Stores daily prediction schedule with timing and status
- **Background Task Management**: Runs concurrent scheduling and verification loops
- **Multi-Channel Integration**: Source channel monitoring and target channel broadcasting
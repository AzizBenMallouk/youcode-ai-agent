# Storyboard Visuel : YouCode AI Platform

Ce document détaille la composition "Visual-First" de chaque slide pour respecter les contraintes strictes : moins de 45 mots, formes éditables, minimum de 70% de surface visuelle, palette de couleurs moderne.

## Slide 1 — Couverture
- **Layout :** Split Vertical (50/50).
- **Gauche (Texte) :**
  - Titre principal : YouCode AI Platform
  - Sous-titre : Intelligence conversationnelle
  - Auteur : Aziz BENMALLOUK
- **Droite (Visuel) :**
  - Illustration abstraite (formes géométriques) d'un noyau central (FastAPI/LangGraph) relié à WhatsApp et 3 sous-agents.

## Slide 2 — Problématique
- **Layout :** Comparaison Avant/Après.
- **Gauche (Problème) :**
  - 4 icônes grises (Texte secondaire) : Infos dispersées, requêtes répétitives, suivi manuel, disponibilité limitée.
- **Milieu :** Flèche transitionnelle vers la droite (Terracotta principal).
- **Droite (Besoin) :**
  - Une carte blanche centrée avec le texte : "Une assistance fiable, multilingue et disponible sur WhatsApp."

## Slide 3 — Solution
- **Layout :** Pipeline Horizontal (5 blocs).
- **Contenu :**
  - WhatsApp (Icône + "Canal")
  - FastAPI (Icône + "Entrée")
  - Multi-agent (Icône + "Orchestration")
  - RAG/MCP (Icône + "Services")
  - Réponse (Icône + "Sortie")
- **Visuel :** Flèches de connexion entre les blocs.

## Slide 4 — Cas d’utilisation
- **Layout :** Carte Mentale Radiale (Hub & Spoke).
- **Centre :** Icône Utilisateur ("Visiteur").
- **Branches :**
  - Découvrir YouCode
  - Support
  - Report de test
  - Newsletter

## Slide 5 — Architecture globale
- **Layout :** Couches Verticales.
- **Couches :**
  - Haut : Canal (WhatsApp)
  - Couche 2 : Entrée (Webhook FastAPI)
  - Couche 3 : Orchestration (LangGraph + Supervisor)
  - Couche 4 : Agents (Guide | Support | Newsletter) - 3 cartes côte à côte.
  - Couche 5 : Données (Qdrant | Google Sheets)

## Slide 6 — Architecture multi-agent
- **Layout :** Centre avec Satellites.
- **Centre :** Supervisor
- **Autour :**
  - Guide (Rôle : Info, Outil : RAG)
  - Support (Rôle : Démarches, Outil : MCP)
  - Newsletter (Rôle : Inscription, Outil : MCP)

## Slide 7 — Routage et continuité
- **Layout :** Comparaison en deux colonnes.
- **Gauche (Nouvelle intention) :**
  - START → Supervisor → Agent
- **Droite (Conversation active) :**
  - START → Phase active → Agent actuel
- **Bas :** "Un workflow actif conserve la conversation sans nouvelle classification."

## Slide 8 — Graph LangGraph
- **Layout :** Diagramme d'état simplifié.
- **Groupes :**
  - Supervisor (Haut)
  - Support Workflow (Gauche) : Extract → Consent → Process → Decision
  - Newsletter Workflow (Droite) : Extract → Consent → Process
- **Visuel :** Flèches pleines (transition), pointillées (reprise depuis WhatsApp).

## Slide 9 — Pipeline RAG
- **Layout :** Pipeline Horizontal.
- **Étapes :** Question → Embedding → Recherche child → Parent context → LLM → Réponse.
- **Bas :** 3 garanties (Documents officiels, Multilingue, Aucune invention).

## Slide 10 — Support conversationnel
- **Layout :** Timeline Verticale + Carte d'État.
- **Gauche (Timeline) :** 1. Détection → 2. Extraction → 3. Consentement → 4. Enregistrement.
- **Droite (Carte) :** Affichage du State (active_agent: Support).

## Slide 11 — Report de test
- **Layout :** Diagramme de Séquence (Lignes de vie).
- **Acteurs :** Visiteur, Support Agent, MCP, Responsable.
- **Flux :** Demande → Collecte → Proposition → Validation → Confirmed.

## Slide 12 — Choix d’une session
- **Layout :** Arbre de Décision (Gauche) + Mockup WhatsApp (Droite).
- **Gauche :** Session proposée → Convient ? → Oui (Validation) / Non (Alternative).
- **Droite :** Fausse capture anonymisée simple (Bulle verte / Bulle blanche).

## Slide 13 — Newsletter
- **Layout :** Boucle Temporelle (Tour 1 / Tour 2).
- **Haut (Tour 1) :** Extraction → Demande Consentement → END (Attente).
- **Bas (Tour 2) :** Reprise → Oui → MCP → Confirmation.

## Slide 14 — MCP et Google Sheets
- **Layout :** Diagramme technique (Haut) + Comparaison (Bas).
- **Diagramme :** Agent → Tool → MCP Client → Serveur → Sheets.
- **Comparaison :** State LangGraph (Temporaire/Conversation) vs Sheets (Persistant/Suivi).

## Slide 15 — FastAPI et intégrations
- **Layout :** Hub & Spoke.
- **Centre :** FastAPI.
- **Satellites :** WhatsApp, LangGraph, MCP, Qdrant.

## Slide 16 — Sécurité et fiabilité
- **Layout :** 4 Piliers Verticaux.
- **Piliers :** Consentement, Validation, Contrôle tools, Humain dans la boucle.
- **Visuel :** Ligne de fond commune (Défense en profondeur).

## Slide 17 — Résultats
- **Layout :** Dashboard de KPI (Cartes).
- **KPIs (Basé sur le repo) :**
  - 3 Agents Spécialisés
  - 1 Supervisor
  - 2 Workflows Transactionnels
  - 1 Serveur MCP

## Slide 18 — Limites et perspectives
- **Layout :** Roadmap (3 horizons temporels).
- **Cartes :**
  - Aujourd'hui (WhatsApp, RAG, MCP)
  - Court terme (Interface Admin)
  - Long terme (PostgreSQL, Analytics)

## Slide 19 — Conclusion
- **Layout :** 3 points forts centrés.
- **Texte :** Point d'entrée simple (WhatsApp), Intelligence (Agents), Exécution (MCP).
- **Bas :** "Merci pour votre attention / Questions ?"

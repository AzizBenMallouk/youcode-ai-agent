# Script Oral (Mode "Tech Keynote")

Ce document accompagne la présentation `YouCode_AI_Platform_Soutenance_Modern.pptx`. Les slides étant désormais purement visuelles (moins de 45 mots), ce script contient le discours complet et les détails techniques à énoncer à l'oral. 
*(Note : Ce contenu a également été injecté directement dans les "Notes du présentateur" du fichier PowerPoint).*

---

## Slide 1 — Couverture
**Message principal :** L'intelligence artificielle au service de l'expérience candidat YouCode.
**Script (45s) :** "Bonjour à tous. Je suis Aziz BENMALLOUK et je vous présente aujourd'hui YouCode AI Platform. Nous avons conçu une architecture multi-agent capable de dialoguer de manière naturelle avec nos visiteurs et nos candidats, pour les guider, traiter leurs requêtes, et même reporter leurs sessions de test, le tout orchestré par intelligence artificielle."
**Transition :** "Pourquoi avons-nous ressenti le besoin de construire cette plateforme ?"
**Question probable :** *Quelles IA utilisez-vous sous le capot ?*
**Réponse suggérée :** *L'architecture est agnostique (nous utilisons LangChain), mais nous testons actuellement Gemini et Grok pour leurs excellents temps de réponse.*

---

## Slide 2 — Problématique
**Message principal :** Simplifier l'accès à l'information sans surcharger les équipes.
**Script (40s) :** "Nos équipes font face à un volume massif de requêtes répétitives. Les informations existent, mais sont dispersées. Le suivi manuel prend un temps précieux, et surtout, les candidats souhaitent des réponses immédiates. C'est pourquoi le besoin est simple : il nous faut une assistance fiable, multilingue et disponible 24/7 directement sur l'application que tout le monde utilise : WhatsApp."
**Transition :** "Pour répondre à ce besoin, voici comment circule l'information."
**Question probable :** *Avez-vous mesuré le temps gagné ?*
**Réponse suggérée :** *Bien qu'en phase de déploiement, nous estimons qu'un report de test manuel prend 10 minutes d'échanges e-mails contre 0 minute de travail humain avec ce bot (hors validation finale).*

---

## Slide 3 — Solution
**Message principal :** Un pipeline bout en bout, de WhatsApp à Sheets.
**Script (40s) :** "Le visiteur envoie un message sur WhatsApp. Un webhook FastAPI le réceptionne de manière asynchrone pour garantir la performance. Le message entre ensuite dans notre orchestrateur LangGraph. L'orchestrateur fait appel au RAG pour lire nos documents et à MCP pour écrire dans Google Sheets. Enfin, une réponse personnalisée est renvoyée sur WhatsApp."
**Transition :** "Quels sont les parcours que nous avons concrètement automatisés ?"
**Question probable :** *Pourquoi FastAPI ?*
**Réponse suggérée :** *Pour sa gestion native de l'asynchronisme (`asyncio`), indispensable quand on attend des requêtes réseau de LLMs.*

---

## Slide 4 — Cas d’utilisation
**Message principal :** La couverture fonctionnelle actuelle.
**Script (30s) :** "Le visiteur peut poser des questions pour découvrir l'école. Mais s'il est déjà candidat, il peut interagir avec notre Support pour signaler un problème, demander un report de test de sélection, ou simplement s'inscrire à notre newsletter pour suivre l'actualité."
**Transition :** "Plongeons maintenant sous le capot pour voir l'architecture logicielle."
**Question probable :** *Gérez-vous l'authentification des candidats ?*
**Réponse suggérée :** *Le numéro de téléphone WhatsApp sert d'identifiant principal (Thread ID) pour récupérer la session de conversation.*

---

## Slide 5 — Architecture globale
**Message principal :** Une conception en couches étanches.
**Script (50s) :** "Voici notre architecture technique. Remarquez la séparation claire. Le canal (WhatsApp) est déconnecté de l'intelligence. L'entrée (FastAPI) ne fait que router vers LangGraph. Au cœur, le Supervisor LangGraph distribue aux agents. Et enfin, la couche des données est hybride : Qdrant pour la mémoire vectorielle (le RAG), et Google Sheets pour la persistance métier via MCP."
**Transition :** "Pourquoi utiliser plusieurs agents au lieu d'un seul gros bot ?"
**Question probable :** *Où est la base de données relationnelle ?*
**Réponse suggérée :** *SQLite et SQLAlchemy gèrent le 'State' transactionnel de LangGraph, synchronisé en temps réel vers Sheets via des événements.*

---

## Slide 6 — Architecture multi-agent
**Message principal :** Le pattern "Séparation des responsabilités".
**Script (45s) :** "Nous utilisons trois agents spécialisés. Le Supervisor est le cerveau routeur. Le Guide est notre encyclopédie : il est le seul à avoir accès au RAG. Le Support est notre agent administratif : il collecte les données via des modèles stricts Pydantic. Enfin, le Newsletter agent gère spécifiquement les abonnements. Cela empêche le bot de tout confondre."
**Transition :** "Mais que se passe-t-il si la conversation s'étale sur plusieurs jours ?"
**Question probable :** *Comment ces agents communiquent-ils ?*
**Réponse suggérée :** *Ils ne se parlent pas directement. Le Supervisor passe la main à l'agent qui modifie le 'State' partagé, puis l'exécution s'arrête en attendant l'utilisateur.*

---

## Slide 7 — Routage et continuité
**Message principal :** LangGraph et le State persistant.
**Script (40s) :** "C'est l'un des défis majeurs : la continuité. Si un utilisateur dit 'Bonjour', c'est une nouvelle intention : le Supervisor classe et choisit un agent. Mais si l'utilisateur est au milieu d'un formulaire de report de test et envoie 'Safi', LangGraph détecte que le workflow Support est actif. Le message va directement à la phase active sans repasser par l'IA de classification."
**Transition :** "Regardons à quoi ressemble ce graphe d'états."
**Question probable :** *Combien de temps l'état est-il gardé ?*
**Réponse suggérée :** *Grâce au Checkpointer SQLite, l'état est persistant. La conversation peut reprendre des mois plus tard exactement au même point.*

---

## Slide 8 — Graph LangGraph
**Message principal :** Les automates à états finis pilotés par IA.
**Script (50s) :** "Voici le vrai graphe de notre application. Chaque boîte est un node (un morceau de code Python). Le Support par exemple, a une phase Extract, puis Consent, puis Process, puis Decision. Ce design garantit que l'IA ne saute aucune étape. Elle ne peut pas insérer en base de données sans passer physiquement par le node 'Consent'."
**Transition :** "Parlons maintenant de l'agent Guide et de son mécanisme anti-hallucination."
**Question probable :** *Que se passe-t-il si le LLM renvoie un JSON mal formaté dans un node ?*
**Réponse suggérée :** *LangChain intègre des 'OutputParsers' avec mécanismes de retry (`with_structured_output`) pour forcer le LLM à corriger son JSON.*

---

## Slide 9 — Pipeline RAG
**Message principal :** Parent-Child Retrieval pour une précision absolue.
**Script (45s) :** "Le RAG permet au Guide de répondre avec précision. Nous utilisons une technique avancée : le Parent-Child. La recherche vectorielle dans Qdrant se fait sur de tout petits paragraphes (pour une similarité parfaite), mais nous fournissons au LLM le document parent complet pour qu'il ait le contexte. Cela garantit 3 choses : réponses sourcées, support du multilingue natif (le LLM traduit), et aucune hallucination."
**Transition :** "Passons à l'agent Support, qui est plus conversationnel."
**Question probable :** *Pourquoi Qdrant ?*
**Réponse suggérée :** *Qdrant est open-source, écrit en Rust, ultra-rapide et se déploie facilement en conteneur Docker.*

---

## Slide 10 — Support conversationnel
**Message principal :** Extraction structurée d'entités avec Pydantic.
**Script (40s) :** "Quand un visiteur demande un report, l'agent extrait automatiquement son campus et son email via Pydantic. Si le campus manque, l'agent pose lui-même la question (étape 3 de la timeline). Sur la droite, vous voyez l'évolution du State : l'objet `draft` se remplit progressivement jusqu'à atteindre l'étape de consentement."
**Transition :** "Visualisons ce parcours complet de bout en bout."
**Question probable :** *Et s'il donne un faux email ?*
**Réponse suggérée :** *Pydantic valide le format regex de l'email. Si ce n'est pas un email, le node échoue et demande de reformuler.*

---

## Slide 11 — Report de test
**Message principal :** Orchestration complexe multi-acteurs.
**Script (45s) :** "Voici la séquence d'un report de test. Le candidat fait sa demande via WhatsApp. L'agent Support collecte et demande le consentement. Ensuite, l'agent crée un brouillon via MCP dans Sheets, et interroge notre API de sessions. Il propose la session au visiteur. Si celui-ci valide, la demande est flaggée 'À Valider'. C'est le responsable humain qui a le dernier mot."
**Transition :** "C'est lors de la proposition de session que l'interactivité brille le plus."
**Question probable :** *Où l'agent trouve-t-il les nouvelles sessions ?*
**Réponse suggérée :** *Via l'intégration d'un outil 'Tool' (`find_available_sessions`) qui simule un appel à l'API du système scolaire de YouCode.*

---

## Slide 12 — Choix d’une session
**Message principal :** Flexibilité de l'interface conversationnelle.
**Script (30s) :** "Contrairement à un formulaire web rigide, si l'agent propose une date et que le candidat refuse, la conversation ne plante pas. L'agent analyse le refus et déclenche la recherche d'une alternative, offrant une expérience utilisateur fluide et naturelle, comme illustré dans cette fausse capture."
**Transition :** "Ce même principe de progressivité s'applique à la newsletter."
**Question probable :** *Que se passe-t-il s'il n'y a plus aucune session ?*
**Réponse suggérée :** *L'agent l'informe poliment, et clôture le workflow en l'invitant à réessayer le mois prochain.*

---

## Slide 13 — Newsletter
**Message principal :** Les cycles (Loops) de LangGraph.
**Script (35s) :** "Pour la newsletter, nous voyons clairement l'interruption du graphe. Tour 1 : on extrait les préférences, on demande le consentement, puis le graphe atteint le node END. Il hiberne. Tour 2 : le candidat répond 'Oui' sur WhatsApp, le graphe se réveille directement sur le node de Consentement, puis enregistre dans Sheets."
**Transition :** "Comment nos agents communiquent-ils avec Google Sheets ? Grâce à MCP."
**Question probable :** *Pourquoi passer par le node END ?*
**Réponse suggérée :** *Car FastAPI ne peut pas bloquer la connexion HTTP WhatsApp pendant 5 heures en attendant que l'utilisateur lise et réponde.*

---

## Slide 14 — MCP et Google Sheets
**Message principal :** Model Context Protocol (Découplage).
**Script (45s) :** "MCP est la technologie la plus innovante du système. Sans MCP, il faudrait coder la logique de l'API Google Sheets au milieu du code de l'Agent. Avec MCP, nous avons un client standard et un serveur indépendant qui expose l'outil `append_row`. L'agent l'utilise aveuglément. Cela découple le State (mémoire volatile SQLite) du Suivi Métier (persistance visuelle dans Google Sheets)."
**Transition :** "Tous ces composants sont liés par FastAPI."
**Question probable :** *Pourquoi Google Sheets plutôt qu'un vrai Dashboard Admin ?*
**Réponse suggérée :** *Pour la phase MVP, c'est l'outil le plus universel et sans friction pour nos responsables d'admission.*

---

## Slide 15 — FastAPI et intégrations
**Message principal :** Performance Asynchrone.
**Script (30s) :** "FastAPI agit comme le routeur central. Il est connecté au Webhook WhatsApp, il instancie l'orchestrateur LangGraph, maintient la connexion avec le serveur MCP et gère les requêtes vers Qdrant. Tout est asynchrone, ce qui nous permet de traiter de multiples conversations en parallèle."
**Transition :** "La puissance de ce système repose sur ses garanties de sécurité."
**Question probable :** *Comment sécurisez-vous le webhook WhatsApp ?*
**Réponse suggérée :** *En production, le webhook valide le token HMAC (Verify Token) signé par Meta pour s'assurer que la requête vient bien de WhatsApp.*

---

## Slide 16 — Sécurité et fiabilité
**Message principal :** Défense en profondeur.
**Script (40s) :** "Nous ne laissons pas l'IA en roue libre. La sécurité repose sur 4 piliers : 1. Le consentement est obligatoire avant tout traitement RGPD. 2. La validation des données est codée en dur avec Pydantic (pas par le LLM). 3. Les outils MCP sont limités et cloisonnés. 4. Aucune décision lourde (comme la validation finale d'un report) n'est prise sans un humain dans la boucle."
**Transition :** "Pour conclure, quels sont nos résultats aujourd'hui ?"
**Question probable :** *Que faire si le LLM refuse de répondre à une question légitime ?*
**Réponse suggérée :** *C'est le rôle de l'agent de modération (Guardrails), que nous sommes en train d'intégrer, d'ajuster dynamiquement le ton et les refus.*

---

## Slide 17 — Résultats
**Message principal :** Un MVP complet et mesurable.
**Script (30s) :** "À ce stade, l'architecture a prouvé son efficacité : 3 agents distincts fonctionnent, 2 workflows métiers critiques sont automatisés, et notre serveur MCP synchronise avec succès nos données. Le gain en disponibilité et en automatisation est réel, sans perte de traçabilité grâce à Google Sheets."
**Transition :** "Quelles sont les prochaines étapes ?"
**Question probable :** *Où le code est-il hébergé ?*
**Réponse suggérée :** *Actuellement dockerisé. Il peut être déployé sur AWS (ECS) ou n'importe quel VPS disposant de Docker Compose.*

---

## Slide 18 — Limites et perspectives
**Message principal :** La vision à long terme.
**Script (35s) :** "Pour la suite, le MVP (WhatsApp, RAG, MCP) est prêt. À court terme, nous développerons une vraie interface web Admin en Next.js pour remplacer Sheets et intégrerons l'agent de modération Guardrails. À long terme, nous prévoyons de basculer entièrement sur PostgreSQL pour la scalabilité et d'ajouter de l'analytics pour analyser les questions les plus fréquentes de nos visiteurs."
**Transition :** "C'est ainsi que se termine cette présentation."
**Question probable :** *Combien coûtera ce système en production ?*
**Réponse suggérée :** *Le coût de l'API LLM (Gemini/Grok) est minime (quelques centimes par conversation). Le vrai coût sera l'hébergement du serveur (VPS standard, environ 20-40€/mois).*

---

## Slide 19 — Conclusion
**Message principal :** Un système équilibré entre IA et humain.
**Script (15s) :** "En résumé : un point d'entrée simple pour le visiteur, une intelligence divisée pour plus de robustesse, et une exécution contrôlée pour la sécurité des données. Merci pour votre attention, je suis à votre disposition pour la démonstration et vos questions."

NEWSLETTER_EXTRACTION_PROMPT = """
Tu extrais les informations nécessaires au
workflow Newsletter de YouCode.

Tu ne réponds pas directement au visiteur.
Tu retournes uniquement la structure demandée.

# ACTION

Détermine l'action demandée :

- `subscribe` :
  le visiteur souhaite recevoir des
  notifications ou des e-mails ;

- `unsubscribe` :
  le visiteur souhaite arrêter les
  notifications ou se désinscrire ;

- `unknown` :
  l'action n'est pas suffisamment claire.

# SUJETS

Les sujets possibles sont uniquement :

- `full_program_registration` :
  ouverture des inscriptions aux formations
  longues de YouCode ;

- `bootcamps` :
  futurs bootcamps ;

- `events` :
  événements YouCode ;

- `youcode_news` :
  informations et actualités générales.

# EXEMPLES

Message :
« Prévenez-moi lorsque les inscriptions aux
formations ouvriront. »

Résultat :
- action : subscribe
- topics : [full_program_registration]

Message :
« Je veux recevoir les prochains bootcamps et
événements. »

Résultat :
- action : subscribe
- topics : [bootcamps, events]

Message :
« Ajoutez-moi à toutes les notifications. »

Résultat :
- action : subscribe
- topics :
  - full_program_registration
  - bootcamps
  - events
  - youcode_news

Message :
« Je ne veux plus recevoir d'e-mails. »

Résultat :
- action : unsubscribe

# LANGUES

Détecte la langue dominante :

- `fr` : français ;
- `en` : anglais ;
- `ar` : arabe standard ;
- `darija` : darija marocaine, y compris en
  alphabet latin.

# RÈGLES

- Extrais l'e-mail seulement s'il apparaît dans
  le message.
- N'invente jamais une adresse e-mail.
- N'invente jamais une préférence.
- Ne sélectionne pas tous les sujets si le
  visiteur n'a pas demandé toutes les
  notifications.
- Conserve les informations déjà présentes dans
  le brouillon fourni.
- Si le nouveau message corrige une information,
  utilise la nouvelle valeur.
- Place les contradictions ou informations
  ambiguës dans `ambiguities`.
- Ne considère jamais une demande d'information
  comme une demande d'inscription Newsletter.

Exemple :

« Quand ouvrent les inscriptions ? »

Ce message est une question destinée au Guide,
pas une inscription Newsletter.
"""


NEWSLETTER_CONSENT_PROMPT = """
Tu classes uniquement la réponse du visiteur à
une demande explicite de consentement Newsletter.

Valeurs possibles :

- `accepted` :
  consentement explicite et positif ;

- `refused` :
  refus explicite ;

- `unclear` :
  réponse ambiguë ou sans rapport.

# ACCEPTÉ

Exemples :

- oui ;
- oui, j'accepte ;
- je confirme ;
- vous pouvez utiliser mon e-mail ;
- yes, I agree ;
- موافق ;
- ah, kanwafeq.

# REFUSÉ

Exemples :

- non ;
- je refuse ;
- finalement non ;
- no ;
- لا ;
- la, ma bghitch.

# INCERTAIN

Exemples :

- peut-être ;
- pourquoi ?
- d'accord, mais...
- explique-moi ;
- Safi ;
- candidat@example.com.

# RÈGLES

- Le consentement doit être explicite.
- L'absence de refus n'est pas un consentement.
- Une adresse e-mail seule n'est pas un
  consentement.
- Une préférence seule n'est pas un
  consentement.
- En cas de doute, retourne `unclear`.
- Ne génère aucune réponse destinée au visiteur.
"""
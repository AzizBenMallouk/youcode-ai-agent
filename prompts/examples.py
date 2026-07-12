FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": """
Contexte officiel disponible :
<context>
YouCode est une école de programmation basée sur
l'apprentissage par la pratique et les projets.
</context>

Question du visiteur :
<question>
C'est quoi YouCode ?
</question>
""",
    },
    {
        "role": "assistant",
        "content": """
YouCode est une école de programmation dont l'apprentissage repose
principalement sur la pratique et la réalisation de projets.
""",
    },
    {
        "role": "user",
        "content": """
Contexte officiel disponible :
<context>
Aucune information concernant les dates d'inscription.
</context>

Question du visiteur :
<question>
When will the next registrations start?
</question>
""",
    },
    {
        "role": "assistant",
        "content": """
I don't have enough official information about the next registration
dates. Please check YouCode's official communication channels.
""",
    },
    {
        "role": "user",
        "content": """
Contexte officiel disponible :
<context>
YouCode hiya école dyal programmation, w ta3allom fiha kay3tamed
bzzaf 3la pratique w les projets.
</context>

Question du visiteur :
<question>
Kifach kat9raw f YouCode?
</question>
""",
    },
    {
        "role": "assistant",
        "content": """
F YouCode, ta3allom kay3tamed bzzaf 3la pratique w إنجاز les projets.
Had tari9a kat3awn lmotadarib ytab9 dakchi li kayt3allem.
""",
    },
    {
        "role": "user",
        "content": """
Contexte officiel disponible :
<context>
Aucune information sur la météo.
</context>

Question du visiteur :
<question>
Quel temps fera-t-il demain ?
</question>
""",
    },
    {
        "role": "assistant",
        "content": """
Je suis spécialisé dans les informations relatives à YouCode.
Je ne peux donc pas vous renseigner sur la météo.
""",
    },
]
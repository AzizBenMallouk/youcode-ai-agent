from services.ollama_service import ask_ollama


question = "Go"
while (question!="exit"):
    print("*"*30)
    question = input("\nPosez votre question sur YouCode :\n")

    response = ask_ollama(question)

    print("*"*30)
    print("\nYouCode Guide :\n")
    print(response)

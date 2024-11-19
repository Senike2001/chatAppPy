import asyncio

async def send_message(reader, writer):
    """Cette fonction envoie un message au serveur et lit la réponse."""
    while True:
        message = input("Vous: ")  # Demande de message à l'utilisateur
        writer.write(message.encode())  # Envoie du message au serveur
        await writer.drain()  # Attend que l'écriture soit terminée

        # Lecture de la réponse du serveur
        data = await reader.read(100)
        print(f"Serveur: {data.decode()}")

        if message.lower() == "quit":
            break  # Si le message est "quit", on arrête la communication

async def main():
    """Se connecte au serveur et gère l'échange de messages."""
    ip = '192.168.49.2'  # L'adresse IP de Minikube
    port = 8888          # Le NodePort exposé par Minikube pour le service

    # Connexion au serveur
    print(f"Connexion à {ip}:{port}...")
    reader, writer = await asyncio.open_connection(ip, port)

    print(f"Connecté à {ip}:{port}")
    
    # Fonction pour envoyer et recevoir des messages
    await send_message(reader, writer)

    print("Déconnexion du serveur...")
    writer.close()  # Fermeture de la connexion
    await writer.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())

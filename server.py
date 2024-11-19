import asyncio

# Stockage des clients connectés et des sessions
clients = {}  # {client_id: (reader, writer)}
sessions = {}  # {sID: (client1_id, client2_id)}

async def handle_client(reader, writer):
    # Identifier le client
    addr = writer.get_extra_info('peername')
    print(f"Nouveau client connecté : {addr}")

    # Lire l'ID du client
    writer.write("Veuillez entrer votre ID unique : ".encode("utf-8"))
    await writer.drain()
    client_id = (await reader.read(100)).decode().strip()
    
    if client_id in clients:
        # Utiliser UTF-8 pour envoyer un message contenant des caractères spéciaux
        writer.write("ID déjà utilisé. Déconnexion...\n".encode("utf-8"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return
    # ma midification 
    
    # Ajouter le client à la liste des clients connectés
    clients[client_id] = (reader, writer)
    writer.write("Vous êtes connecté au serveur !\n".encode("utf-8"))
    await writer.drain()

    try:
        while True:
            # Attendre une commande du client
            writer.write("Entrez une commande (CONNECT, SEND, EXIT) : ".encode("utf-8"))
            await writer.drain()
            command = (await reader.read(100)).decode().strip()

            if command == "CONNECT":
                writer.write("Entrez l'ID du client avec lequel vous voulez vous connecter : ".encode("utf-8"))
                await writer.drain()
                target_id = (await reader.read(100)).decode().strip()

                if target_id not in clients:
                    writer.write("Client non trouvé.\n".encode("utf-8"))
                    await writer.drain()
                else:
                    # Créer une session entre les deux clients
                    sID = f"{client_id}-{target_id}"
                    sessions[sID] = (client_id, target_id)
                    writer.write(f"Session créée avec {target_id} (sID: {sID})\n".encode("utf-8"))
                    await writer.drain()
                    target_writer = clients[target_id][1]
                    target_writer.write(f"Vous êtes connecté à {client_id} (sID: {sID})\n".encode("utf-8"))
                    await target_writer.drain()

            elif command == "SEND":
                writer.write("Entrez le sID de la session : ".encode("utf-8"))
                await writer.drain()
                sID = (await reader.read(100)).decode().strip()

                if sID not in sessions or client_id not in sessions[sID]:
                    writer.write("Session invalide.\n".encode("utf-8"))
                    await writer.drain()
                else:
                    # Trouver l'autre client dans la session
                    other_id = sessions[sID][1] if sessions[sID][0] == client_id else sessions[sID][0]
                    writer.write("Entrez votre message : ".encode("utf-8"))
                    await writer.drain()
                    message = (await reader.read(500)).decode().strip()
                    other_writer = clients[other_id][1]
                    other_writer.write(f"Message de {client_id}: {message}\n".encode("utf-8"))
                    await other_writer.drain()
                    writer.write("Message envoyé.\n".encode("utf-8"))
                    await writer.drain()

            elif command == "EXIT":
                writer.write("Déconnexion...\n".encode("utf-8"))
                await writer.drain()
                break
            else:
                writer.write("Commande inconnue.\n".encode("utf-8"))
                await writer.drain()
    except asyncio.IncompleteReadError:
        pass
    finally:
        # Nettoyer la connexion à la déconnexion
        print(f"Client {client_id} déconnecté.")
        del clients[client_id]
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f"Serveur démarré sur {addr}")

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

import requests, re, os, dotenv

dotenv.load_dotenv()
URL_WEBHOOK = os.getenv("URL_WEBHOOK")
HEADERS = {
    "Content-Type": 'application/json'
}

def formatar_mensagem(texto):
    texto = re.sub(r"\[B\]Enviado do messenger\[/B\]", "", texto)
    texto = re.sub(r"\[URL=(.*\.oga)\].*\[/URL\]", "[Audio]", texto)
    texto = re.sub(r'\[icon=.*\]', "", texto)
    return texto

def buscar_conversas():
    resposta = requests.post(URL_WEBHOOK + "im.recent.list.json", headers=HEADERS, json={"SKIP_CHAT": 'Y'})
    conversas = resposta.json()["result"]["items"]
    return [conversa for conversa in conversas if conversa["type"] == "chat" and conversa["chat"]["message_type"] == "L"]

def buscar_mensagens(id):
    body = {
        "DIALOG_ID": id
    }
    resposta = requests.post(URL_WEBHOOK + "im.dialog.messages.get.json", headers=HEADERS, json=body)
    conversas = resposta.json()["result"]
    mensagens = conversas["messages"]
    mensagens_formatadas = []
    for mensagem in mensagens:
        mensagens_formatadas.append([str(mensagem["author_id"]), mensagem["text"]])
    mensagens_formatadas.reverse()
    return mensagens_formatadas

def buscar_user():
    body = {}
    resposta = requests.post(URL_WEBHOOK + "user.current.json", headers=HEADERS, json=body)
    usuario = resposta.json()
    return usuario['result']


def buscar_mensagens_melhorado(id):
    body = {
        "DIALOG_ID": id
    }
    resposta = requests.post(URL_WEBHOOK + "im.dialog.messages.get.json", headers=HEADERS, json=body)
    conversas = resposta.json()["result"]

    mensagens = [mensagem for mensagem in conversas["messages"] if mensagem["author_id"] != 0]
    usuarios = {user["id"]: user["name"] for user in conversas["users"]}
    clientes = {user["id"]: user["phones"] != False for user in conversas["users"]}

    mensagens_formatadas = []

    for mensagem in mensagens:
        id = mensagem["author_id"]
        mensagens_formatadas.append(
            {
                "role": "user" if id != 0 and clientes[id] else "assistant",
                "name": usuarios[id] if id != 0 else "Sistema", 
                "content": formatar_mensagem(mensagem["text"])
            }
        )
    
    mensagens_formatadas.reverse()

    return mensagens_formatadas


def buscar_conversas_brutas():
    resposta = requests.post(URL_WEBHOOK + "im.recent.list.json", headers=HEADERS)
    conversas = resposta.json()["result"]["items"]
    return [conversa for conversa in conversas if conversa["type"] == "chat" and conversa["chat"]["message_type"] == "L"]

def buscar_mensagens_brutas():
    body = {
        "DIALOG_ID": 'chat63'
    }
    resposta = requests.post(URL_WEBHOOK + "im.dialog.messages.get.json", headers=HEADERS, json=body)
    conversas = resposta.json()
    return conversas

def main():
    print(buscar_conversas())

if __name__ == "__main__":
    main()
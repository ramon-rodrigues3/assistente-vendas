import streamlit as st
import app, openai, os, dotenv

dotenv.load_dotenv()
conversas = app.buscar_conversas()

@st.dialog("Autorização")
def login():
    st.write(f"Digite a senha:")
    submit = st.text_input("Sua senha")
    if st.button("Login"):
        if submit == os.getenv("SENHA"):
            st.session_state.autorizado = True
            st.rerun()
        else:
            st.error("Senha Inválida!")
            st.stop()

def menu_selecao():
    escolha = st.selectbox("Selecione a conversa", conversas, format_func=lambda x: x["title"])
    if escolha:
        if escolha["id"] != st.session_state.get("id_conversa", 0):
            st.session_state["chat_mensagens"] = [{"role": "assistant", "content": "Precisa de ajuda?"}]
            st.session_state["id_conversa"] = escolha["id"]

        colunas = st.columns(3)

        with colunas[0]:
            st.write(f"Cliente: {escolha['title']}")
        with colunas[1]:
            st.write(f"Ultima mensagem: ```{escolha['message']['text']}```")
        with colunas[2]:
            st.write(f"Última atividade: {escolha['message']['date']}")

def adicionar_mensagem(chat_ui, conversa, client, chat_mensagens, input):
    with chat_ui:
        #input = "Como eu poderia continuar esta conversa?"
        chat_user = st.chat_message('user')
        chat_user.markdown(input)

        pergunta = f"""
        Esta é a conversa do usuário com seu cliente:
        {str(conversa)}

        Com base nisso responda a pergunta:
        {input}
        """
        
        chat_ai = st.chat_message('assistant')
        resposta = chat_ai.write_stream(
            client.chat.completions.create(
                messages = chat_mensagens + [{"role": 'user', "content": pergunta}], 
                model='gpt-4o-mini', stream=True
            )
        )

        chat_mensagens.append({"role": "user", "content": input})
        chat_mensagens.append({"role": "assistant", "content": resposta})
        
        st.session_state["chat_mensagens"] = chat_mensagens

def assistente_vendas():
    client = openai.Client()
    
    conversa = app.buscar_mensagens_melhorado(st.session_state.get("id_conversa"))
    chat_mensagens = st.session_state.get("chat_mensagens", [{"role": "assistant", "content": "Precisa de ajuda?"}])
    
    chat_ui = st.container()
    with chat_ui:
        for mensagem in chat_mensagens:
            with st.chat_message(mensagem["role"]):
                st.markdown(mensagem["content"])   

    input = st.chat_input("Digite sua mensagem")

    if input:
        with chat_ui:
            chat_user = st.chat_message('user')
            chat_user.markdown(input)

            pergunta = f"""
            Esta é a conversa do usuário com seu cliente:
            {str(conversa)}

            Com base nisso responda a pergunta:
            {input}
            """
            
            chat_ai = st.chat_message('assistant')
            resposta = chat_ai.write_stream(
                client.chat.completions.create(
                    messages = chat_mensagens + [{"role": 'user', "content": pergunta}], 
                    model='gpt-4o-mini', stream=True
                )
            )
            
            chat_mensagens.append({"role": "user", "content": input})
            chat_mensagens.append({"role": "assistant", "content": resposta})
            
            st.session_state["chat_mensagens"] = chat_mensagens

    colunas = st.columns(3)

    with colunas[0]:
        botao = st.button("Como eu poderia continuar esta conversa?")
        
        if botao:
            adicionar_mensagem(chat_ui, conversa, client, chat_mensagens, "Como eu poderia continuar essa conversa?")

    with colunas[1]:
        botao = st.button("Quais produtos eu poderia oferecer?")
        
        if botao:
            adicionar_mensagem(chat_ui, conversa, client, chat_mensagens, "Quais produtos eu poderia oferecer")

    with colunas[2]:
        botao = st.button("Qual é sua avaliação do atendimento?")
        
        if botao:
            adicionar_mensagem(chat_ui, conversa, client, chat_mensagens, "Qual a sua avaliação do atendimento? positiva, negativa. O que pode ser melhorado?")

def historico_conversa():
    conversa = app.buscar_mensagens_melhorado(st.session_state.get("id_conversa"))

    for mensagem in conversa:
        with st.chat_message(mensagem["role"], avatar="👨‍💼" if mensagem["role"] == "assistant" else "🙂"):
            st.markdown(f"(**{mensagem['name']}**)")
            st.markdown(mensagem["content"])
    
def chat():
    st.divider()
    tabs = st.tabs(["Assistente de Vendas", "Histórico da Conversa"])

    with tabs[0]:
        assistente_vendas()    
    
    with tabs[1]:
        historico_conversa()

if __name__ == "__main__":
    if "autorizado" not in st.session_state:
        if st.button("Fazer Login"):
            login()

    elif st.session_state.autorizado:
        st.set_page_config(page_title="Assistente de Vendas", page_icon="🤖",layout="wide")
        st.header("Assistente de Vendas", divider="gray") 
        menu_selecao()
        chat()
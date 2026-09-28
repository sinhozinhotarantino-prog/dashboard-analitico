import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Agente Analítico Universal", page_icon="🤖", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
modelo = genai.GenerativeModel('gemini-flash-latest')

st.title("🤖 Agente Analítico Universal")
st.write("Faça o upload de qualquer base de dados. O Agente fará a leitura inicial e aguardará suas instruções.")

arquivo_upload = st.file_uploader("Suba sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo_upload is not None:
    # Leitura do arquivo
    try:
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
            
        st.write("🔍 Prévia dos dados brutos:")
        st.dataframe(df.head(3))
        
        st.divider()

        # INICIALIZAÇÃO DA MEMÓRIA DO CHAT
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        # Se um arquivo novo for enviado, reseta a memória e faz a primeira leitura
        if "arquivo_atual" not in st.session_state or st.session_state.arquivo_atual != arquivo_upload.name:
            st.session_state.arquivo_atual = arquivo_upload.name
            st.session_state.chat_history = []
            
            # Prepara um resumo técnico para a IA entender do que se trata
            amostra_dados = df.head(3).to_string()
            info_colunas = df.dtypes.to_string()
            
            prompt_reconhecimento = f"""
            Você é um assistente de análise de dados. O usuário acabou de fazer o upload de um arquivo desconhecido.
            Tipos de colunas detectadas:
            {info_colunas}
            
            Amostra das 3 primeiras linhas:
            {amostra_dados}
            
            Escreva uma mensagem curta em português do Brasil para o usuário com a seguinte estrutura:
            1. Diga do que parece se tratar este arquivo (ex: "Parece ser um relatório de vendas...", "Notei que é uma lista de alunos...").
            2. Cite os principais tipos de informações que ele contém.
            3. Termine perguntando ao usuário o que ele deseja analisar, cruzar ou descobrir com esses dados.
            """
            
            with st.spinner("Analisando a estrutura do arquivo..."):
                resposta = modelo.generate_content(prompt_reconhecimento)
                st.session_state.chat_history.append({"role": "ai", "content": resposta.text})

        # EXIBE O HISTÓRICO DA CONVERSA
        for msg in st.session_state.chat_history:
            with st.chat_message("🤖" if msg["role"] == "ai" else "🧑‍💻"):
                st.write(msg["content"])

        # CAIXA DE INTERAÇÃO PARA O USUÁRIO TOMAR A DECISÃO
        user_input = st.chat_input("Digite o que você quer saber sobre estes dados...")
        
        if user_input:
            # Mostra a mensagem do usuário na tela e salva na memória
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("🧑‍💻"):
                st.write(user_input)
                
            # Manda a dúvida para a IA, junto com o contexto da tabela
            with st.chat_message("🤖"):
                with st.spinner("Processando..."):
                    contexto_conversa = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                    resumo_estatistico = df.describe(include='all').to_string()
                    
                    prompt_chat = f"""
                    O usuário está fazendo perguntas sobre uma tabela de dados.
                    Resumo estatístico da tabela:
                    {resumo_estatistico}
                    
                    Últimas mensagens da conversa:
                    {contexto_conversa}
                    
                    Responda à pergunta do usuário de forma direta e analítica. Use o resumo estatístico para embasar sua resposta.
                    """
                    resposta_chat = modelo.generate_content(prompt_chat)
                    st.write(resposta_chat.text)
                    st.session_state.chat_history.append({"role": "ai", "content": resposta_chat.text})

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

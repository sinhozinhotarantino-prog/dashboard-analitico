import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Agente Analítico", page_icon="🤖", layout="wide")

st.title("🤖 Agente Analítico Autônomo")
st.write("Bem-vindo! Arraste sua base de dados bruta para iniciar a análise automática.")

# Componente de Upload de Arquivos
arquivo_upload = st.file_uploader("Faça o upload da sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

# Se o usuário enviou um arquivo, o código abaixo entra em ação
if arquivo_upload is not None:
    try:
        # Verifica a extensão para ler da forma correta
        if arquivo_upload.name.endswith('.csv'):
            # Lemos o CSV. O pandas cria um DataFrame (df)
            df = pd.read_csv(arquivo_upload)
        else:
            # Lemos o Excel
            df = pd.read_excel(arquivo_upload)
        
        st.success(f"Arquivo '{arquivo_upload.name}' carregado com sucesso!")
        
        # Mostra uma prévia da tabela na tela
        st.write("🔍 Prévia dos dados:")
        st.dataframe(df.head()) # Mostra apenas as 5 primeiras linhas
        
    except Exception as e:
        # Se algo der errado (ex: arquivo corrompido), mostra um erro amigável
        st.error(f"Ops! Ocorreu um erro ao ler o arquivo: {e}")

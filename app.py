import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Agente Analítico", page_icon="🤖", layout="wide")

# Conectando com a IA usando a chave secreta do cofre
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🤖 Agente Analítico Autônomo")
st.write("Bem-vindo! Arraste sua base de dados bruta para iniciar a análise automática.")

arquivo_upload = st.file_uploader("Faça o upload da sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo_upload is not None:
    try:
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
        
        st.success(f"Arquivo '{arquivo_upload.name}' carregado com sucesso!")
        st.write("🔍 Prévia dos dados:")
        st.dataframe(df.head()) 
        
        # --- O MOTOR DE IA ENTRA EM AÇÃO ---
        st.subheader("🧠 Interpretação do Agente")
        
        with st.spinner("Verificando os modelos disponíveis na sua conta..."):
            try:
                # Lista todos os modelos que suportam geração de texto
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                st.write("✅ Modelos autorizados para a sua chave:")
                st.write(modelos)
                
            except Exception as e:
                st.error(f"Erro ao conectar com o Google: {e}")

    except Exception as e:
        st.error(f"Ops! Ocorreu um erro ao ler a planilha: {e}")

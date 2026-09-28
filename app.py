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
        # Verifica a extensão para ler da forma correta
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
        
        st.success(f"Arquivo '{arquivo_upload.name}' carregado com sucesso!")
        st.write("🔍 Prévia dos dados:")
        st.dataframe(df.head()) 
        
        # --- O MOTOR DE IA ENTRA EM AÇÃO ---
        st.subheader("🧠 Interpretação do Agente")
        
        with st.spinner("Analisando padrões matemáticos e escrevendo o relatório..."):
            try:
                # Inicializa o modelo validado na sua conta
                modelo = genai.GenerativeModel('gemini-flash-latest')
                
                # Prepara os dados da planilha para a IA ler
                resumo_estatistico = df.describe().to_string()
                nome_colunas = ", ".join(df.columns)
                
                # Instrução (prompt) para o Gemini
                prompt = f"""
                Você é um analista de dados sênior. O usuário acabou de fazer o upload de uma planilha.
                As colunas presentes são: {nome_colunas}.
                Aqui está o resumo estatístico dos dados numéricos:
                {resumo_estatistico}
                
                Escreva um parágrafo curto, direto e em português do Brasil explicando as principais tendências que você consegue notar nesses números. 
                Fale com um tom profissional, mas acessível. Não utilize formatação exagerada, apenas texto corrido e negritos onde for importante.
                """
                
                # Envia a requisição e mostra a resposta na tela
                resposta = modelo.generate_content(prompt)
                st.write(resposta.text)
                
            except Exception as e:
                st.error(f"Erro ao gerar a interpretação da IA: {e}")

    except Exception as e:
        st.error(f"Ops! Ocorreu um erro ao ler o arquivo: {e}")

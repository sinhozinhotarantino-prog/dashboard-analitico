import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configuração da página
st.set_page_config(page_title="Agente Analítico", page_icon="🤖", layout="wide")

# Conectando com a IA usando a chave secreta do cofre
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
modelo = genai.GenerativeModel('gemini-pro')

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
        
        # O spinner cria aquela animação de "carregando" enquanto a IA pensa
        with st.spinner("Analisando padrões matemáticos e escrevendo o relatório..."):
            
            # Pegamos um resumo estatístico da tabela (médias, máximos, mínimos)
            resumo_estatistico = df.describe().to_string()
            nome_colunas = ", ".join(df.columns)
            
            # Montamos a instrução (prompt) que será enviada para o Gemini
            prompt = f"""
            Você é um analista de dados sênior. O usuário acabou de fazer upload de uma planilha.
            As colunas presentes são: {nome_colunas}.
            Aqui está o resumo estatístico dos dados numéricos:
            {resumo_estatistico}
            
            Escreva um parágrafo curto, direto e em português do Brasil explicando as principais tendências que você consegue notar nesses números. 
            Fale com tom profissional, mas acessível. Não use formatação em markdown exagerada, apenas texto corrido e negritos onde importar.
            """
            
            # Enviamos a requisição para a IA e guardamos a resposta
            resposta = modelo.generate_content(prompt)
            
            # Exibimos o texto gerado na tela
            st.write(resposta.text)

    except Exception as e:
        st.error(f"Ops! Ocorreu um erro: {e}")

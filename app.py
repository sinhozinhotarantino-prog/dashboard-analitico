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
        
        # --- NOVA PARTE: INDICADORES VISUAIS (KPIs) ---
        # Filtra apenas as colunas que têm números para podermos fazer contas
        colunas_numericas = df.select_dtypes(include='number').columns
        
        if len(colunas_numericas) > 0:
            st.markdown("### 📊 Indicadores Principais")
            
            # Divide a tela em 3 colunas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # O primeiro indicador sempre será o total de linhas (ex: Total de Alunos)
                st.metric(label="Total de Registros", value=len(df))
            
            with col2:
                # O segundo indicador pega a média da última coluna numérica (ex: Média Final)
                ultima_col = colunas_numericas[-1]
                media_1 = df[ultima_col].mean()
                st.metric(label=f"Média: {ultima_col}", value=round(media_1, 2))
                
            with col3:
                # O terceiro indicador pega a média da penúltima coluna (se existir)
                if len(colunas_numericas) > 1:
                    penultima_col = colunas_numericas[-2]
                    media_2 = df[penultima_col].mean()
                    st.metric(label=f"Média: {penultima_col}", value=round(media_2, 2))
                else:
                    st.metric(label="Colunas Analisadas", value=len(colunas_numericas))
            
            st.divider() # Adiciona uma linha horizontal para separar as seções
            
        # ----------------------------------------------
        
        st.write("🔍 Prévia dos dados:")
        st.dataframe(df.head()) 
        
        # --- O MOTOR DE IA ENTRA EM AÇÃO ---
        st.subheader("🧠 Interpretação do Agente")
        
        with st.spinner("Analisando padrões matemáticos e escrevendo o relatório..."):
            try:
                modelo = genai.GenerativeModel('gemini-flash-latest')
                resumo_estatistico = df.describe().to_string()
                nome_colunas = ", ".join(df.columns)
                
                prompt = f"""
                Você é um analista de dados sênior. O usuário acabou de fazer o upload de uma planilha.
                As colunas presentes são: {nome_colunas}.
                Aqui está o resumo estatístico dos dados numéricos:
                {resumo_estatistico}
                
                Escreva um parágrafo curto, direto e em português do Brasil explicando as principais tendências que você consegue notar nesses números. 
                Fale com um tom profissional, mas acessível. Não utilize formatação exagerada, apenas texto corrido e negritos onde for importante.
                """
                
                resposta = modelo.generate_content(prompt)
                st.write(resposta.text)
                
            except Exception as e:
                st.error(f"Erro ao gerar a interpretação da IA: {e}")

    except Exception as e:
        st.error(f"Ops! Ocorreu um erro ao ler o arquivo: {e}")

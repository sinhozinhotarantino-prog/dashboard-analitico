import streamlit as st
import pandas as pd
from groq import Groq
import re

# Configuração da página
st.set_page_config(page_title="Agente Analítico Universal", page_icon="🤖", layout="wide")

# Inicializa o motor Llama 3 via Groq
try:
    cliente_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Configure a GROQ_API_KEY nos secrets do Streamlit.")
    st.stop()

st.title("🤖 Agente Analítico Universal")
st.write("Faça o upload de qualquer base de dados. O Agente fará a leitura inicial, um diagnóstico de qualidade e aguardará suas instruções.")

arquivo_upload = st.file_uploader("Suba sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

def renderizar_grafico(texto, df):
    match = re.search(r'\|\|GRAFICO\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\|\|', texto)
    if match:
        tipo = match.group(1).strip().upper()
        eixo_x = match.group(2).strip()
        eixo_y_raw = match.group(3).strip()
        col_filtro = match.group(4).strip()
        val_filtro = match.group(5).strip()
        
        # Permite plotar múltiplas colunas no Eixo Y se a IA separar por vírgula
        if ',' in eixo_y_raw:
            eixo_y = [col.strip() for col in eixo_y_raw.split(',')]
        else:
            eixo_y = eixo_y_raw
            
        df_plot = df.copy()
        
        try:
            if col_filtro.upper() != "NENHUM" and val_filtro.upper() != "NENHUM" and col_filtro in df.columns:
                df_plot = df_plot[df_plot[col_filtro].astype(str).str.contains(val_filtro, case=False, na=False)]
                st.markdown(f"**📊 Visualização Gerada:** {tipo} ({eixo_x} vs {eixo_y_raw}) - *Filtrado por: {col_filtro} = {val_filtro}*")
            else:
                st.markdown(f"**📊 Visualização Gerada:** {tipo} ({eixo_x} vs {eixo_y_raw})")
                
            if "BARRA" in tipo:
                st.bar_chart(df_plot, x=eixo_x, y=eixo_y)
            elif "LINHA" in tipo:
                st.line_chart(df_plot, x=eixo_x, y=eixo_y)
            elif "DISPERS" in tipo:
                st.scatter_chart(df_plot, x=eixo_x, y=eixo_y)
            else:
                st.info(f"O modelo de gráfico sugerido ({tipo}) não possui suporte nativo imediato.")
        except Exception as e:
            st.caption(f"Aviso: Não foi possível desenhar o gráfico. Verifique se as colunas solicitadas existem na tabela. (Erro: {e})")

def consultar_ia(prompt):
    resposta = cliente_groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b",
        temperature=0.3
    )
    return resposta.choices[0].message.content

if arquivo_upload is not None:
    try:
        # 1. Leitura inicial dos dados brutos
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
            
        # 2. Diagnóstico de Qualidade dos Dados
        st.subheader("🩺 Diagnóstico da Base de Dados")
        nulos_totais = df.isnull().sum().sum()
        linhas_duplicadas = df.duplicated().sum()
        
        if nulos_totais > 0 or linhas_duplicadas > 0:
            st.warning(f"⚠️️ **Atenção:** O sistema detectou {nulos_totais} células em branco e {linhas_duplicadas} linhas repetidas na sua planilha.")
            
            # Interruptor de limpeza no Streamlit
            corrigir = st.toggle("✨ Limpar e Padronizar Dados Automaticamente")
            
            if corrigir:
                # Remove linhas idênticas
                df = df.drop_duplicates()
                
                # Trata células vazias de acordo com o tipo de dado
                for col in df.columns:
                    if df[col].dtype == 'object' or df[col].dtype == 'string':
                        df[col] = df[col].fillna("Não Informado")
                    else:
                        df[col] = df[col].fillna(0)
                        
                st.success("✅ Assepsia concluída! Linhas duplicadas foram removidas e os valores em branco foram preenchidos. O Agente usará a base tratada.")
        else:
            st.success("✅ A base de dados está em perfeitas condições. Nenhuma anomalia estrutural detectada.")

        # 3. Visualização dos dados
        with st.expander("🔍 Visualizar estrutura dos dados (Primeiras 5 linhas)"):
            st.dataframe(df.head(5))
        
        st.divider()

        # 4. Processamento da IA (Categorias e Histórico)
        resumo_categorias = ""
        colunas_texto = df.select_dtypes(include=['object', 'string']).columns
        for col in colunas_texto:
            unicos = df[df[col].notna()][col].unique()
            if len(unicos) < 15:
                resumo_categorias += f"- {col}: {', '.join(map(str, unicos))}\n"

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        if "arquivo_atual" not in st.session_state or st.session_state.arquivo_atual != arquivo_upload.name:
            st.session_state.arquivo_atual = arquivo_upload.name
            st.session_state.chat_history = []
            
            amostra_dados = df.head(3).to_string()
            info_colunas = df.dtypes.to_string()
            
            prompt_reconhecimento = f"""
            Você é um assistente de análise de dados universal. O usuário fez upload de um arquivo.
            Tipos de colunas detectadas: {info_colunas}
            Valores categóricos identificados automaticamente:
            {resumo_categorias}
            Amostra das primeiras linhas: {amostra_dados}
            
            Escreva uma mensagem curta em português do Brasil:
            1. Diga do que parece se tratar este arquivo.
            2. Cite os principais tipos de informações e categorias disponíveis para filtro.
            3. Pergunte o que ele deseja analisar, sugerindo gráficos.
            """
            
            with st.spinner("Lendo a estrutura universal do arquivo..."):
                resposta_texto = consultar_ia(prompt_reconhecimento)
                st.session_state.chat_history.append({"role": "ai", "content": resposta_texto})

        for msg in st.session_state.chat_history:
            with st.chat_message("🤖" if msg["role"] == "ai" else "🧑‍💻"):
                texto_limpo = re.sub(r'\|\|GRAFICO.*?\|\|', '', msg["content"])
                
                # Previne que balões fiquem totalmente vazios caso a IA gere apenas a tag
                if msg["role"] == "ai" and texto_limpo.strip() == "":
                    st.write("Aqui está a visualização solicitada:")
                else:
                    st.write(texto_limpo)
                    
                if msg["role"] == "ai":
                    renderizar_grafico(msg["content"], df)

        user_input = st.chat_input("Digite o que você quer analisar ou peça um gráfico...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("🧑‍💻"):
                st.write(user_input)
                
            with st.chat_message("🤖"):
                with st.spinner("Processando análises..."):
                    contexto_conversa = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                    resumo_estatistico = df.describe(include='all').to_string()
                    lista_colunas = ", ".join(df.columns)
                    
                    prompt_chat = f"""
                    O usuário está fazendo perguntas sobre uma tabela.
                    Colunas disponíveis: {lista_colunas}
                    Valores categóricos para filtros:
                    {resumo_categorias}
                    Resumo estatístico: {resumo_estatistico}
                    
                    Últimas mensagens:
                    {contexto_conversa}
                    
                    DIRETRIZES DE GRÁFICOS:
                    1. Recomende o gráfico adequado e PEÇA APROVAÇÃO expressa (ex: "Você confirma a criação deste gráfico?").
                    2. SE O USUÁRIO CONFIRMAR (disser "sim", "ok", "pode fazer"), responda com um breve texto confirmando a ação E inclua EXATAMENTE esta estrutura de tag no final:
                    ||GRAFICO | [TIPO] | [EIXO_X] | [EIXO_Y] | [COLUNA_FILTRO] | [VALOR_FILTRO]||
                    
                    - Tipos suportados: BARRAS, LINHAS, DISPERSAO.
                    - Para comparar mais de uma coluna no mesmo gráfico (Ex: comparar 2 bimestres), separe os nomes das colunas por vírgula no [EIXO_Y]. Ex: ||GRAFICO | LINHAS | Engajamento | Media_1B, Media_2B | NENHUM | NENHUM||
                    - Exemplo sem filtro: ||GRAFICO | BARRAS | Vendedor | Faturamento | NENHUM | NENHUM||
                    - Exemplo com filtro: ||GRAFICO | BARRAS | Nome | Nota | Turma | 6º Ano A||
                    
                    Nunca envie apenas a tag do gráfico; sempre escreva um texto explicativo junto.
                    """
                    
                    texto_final = consultar_ia(prompt_chat)
                    
                    texto_exibicao = re.sub(r'\|\|GRAFICO.*?\|\|', '', texto_final)
                    
                    if texto_exibicao.strip() == "":
                        st.write("Gráfico processado com sucesso:")
                    else:
                        st.write(texto_exibicao)
                    
                    renderizar_grafico(texto_final, df)
                    st.session_state.chat_history.append({"role": "ai", "content": texto_final})

    except Exception as e:
        erro_str = str(e).lower()
        if "429" in erro_str or "rate limit" in erro_str or "quota" in erro_str:
            st.warning("""
            ⚠ **Olá! Muitos recrutadores estão testando esta ferramenta hoje e o limite da API de demonstração foi atingido.**
            
            Enquanto a cota se renova (leva apenas alguns segundos), você pode conferir o vídeo de demonstração completa desta aplicação funcionando no meu repositório.
            
            👉 [Clique aqui para assistir ao vídeo no GitHub](SUBSTITUA_PELO_SEU_LINK_AQUI)
            """)
        else:
            st.error(f"Ocorreu um erro inesperado ao processar os dados: {e}")

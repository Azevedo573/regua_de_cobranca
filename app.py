"""
Sistema de Processamento de Faturamento
Gera planilhas filtradas por vencimento e status para disparo WhatsApp
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from openpyxl.styles import numbers

# Configuração da página
st.set_page_config(
    page_title="Gerador de Planilhas de Cobrança",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Gerador de Planilhas de Cobrança")
st.markdown("---")

def calcular_dias_vencimento(row):
    """Calcula dias desde o vencimento (positivo = vencido, negativo = a vencer)"""
    data_venc = row.get('Data de Vencimento')
    if pd.isna(data_venc):
        return None
    
    # Converte para datetime se necessário
    if isinstance(data_venc, str):
        try:
            data_venc = pd.to_datetime(data_venc, dayfirst=True)
        except:
            return None
    
    hoje = datetime.now().date()
    if hasattr(data_venc, 'date'):
        data_venc = data_venc.date()
    
    return (hoje - data_venc).days

def filtrar_por_vencimento(df, dias, operador):
    """Filtra contratos baseado nos dias de vencimento"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    df = df.copy()
    df['Dias_Vencimento'] = df.apply(calcular_dias_vencimento, axis=1)
    df = df.dropna(subset=['Dias_Vencimento'])
    
    if operador == 'igual':
        return df[df['Dias_Vencimento'] == dias]
    elif operador == 'maior_igual':
        return df[df['Dias_Vencimento'] >= dias]
    elif operador == 'menor_igual':
        return df[df['Dias_Vencimento'] <= dias]
    elif operador == 'entre':
        return df

def gerar_excel(df, nome_arquivo):
    """Gera arquivo Excel em memória para download"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
        # Formata coluna de data
        if 'Data de Vencimento' in df.columns:
            worksheet = writer.sheets['Dados']
            col_num = df.columns.get_loc('Data de Vencimento') + 1
            for row in range(2, len(df) + 2):
                cell = worksheet.cell(row=row, column=col_num)
                cell.number_format = 'dd/mm/yyyy'
    output.seek(0)
    return output

# Função para gerar planilha resumida
def gerar_excel_resumido(df):
    colunas_resumidas = [
        'Celular',
        'Nome Titular',
        'Operadora da Fatura',
        'Data de Vencimento',
        'Valor Cobrança',
        'Alerta'
    ]
    # Garante que só as colunas existentes serão usadas
    colunas_existentes = [c for c in colunas_resumidas if c in df.columns]
    df_resumido = df[colunas_existentes].copy() if colunas_existentes else pd.DataFrame()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resumido.to_excel(writer, index=False, sheet_name='Resumido')
        # Formata coluna de data
        if 'Data de Vencimento' in df_resumido.columns:
            worksheet = writer.sheets['Resumido']
            col_num = df_resumido.columns.get_loc('Data de Vencimento') + 1
            for row in range(2, len(df_resumido) + 2):
                cell = worksheet.cell(row=row, column=col_num)
                cell.number_format = 'dd/mm/yyyy'
    output.seek(0)
    return output

def main():
    # Sidebar com instruções
    st.sidebar.header("📋 Instruções")
    st.sidebar.markdown("""
    1. Faça upload da planilha de faturamento (Excel .xlsx)
    2. O sistema processará automaticamente
    3. Baixe as planilhas filtradas abaixo
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.header("📁 Formato Aceito")
    st.sidebar.markdown("• Arquivo Excel (.xlsx)")
    st.sidebar.markdown("• Primeira linha = headers")
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📤 Arraste ou selecione a planilha de faturamento",
        type=['xlsx', 'xls'],
        help="Aceita arquivos Excel (.xlsx ou .xls)"
    )
    
    if uploaded_file is not None:
        try:
            with st.status("⏳ Processando planilha...", expanded=True) as status:
                # Carrega a planilha
                st.write("📥 Carregando arquivo...")
                df = pd.read_excel(uploaded_file)
                st.write(f"✅ Planilha carregada com {len(df)} registros")
                
                # Mostra preview
                with st.expander("👀 Visualizar dados carregados"):
                    st.dataframe(df.head(10))
                    st.info(f"Total de linhas: {len(df)}")
                
                st.markdown("---")
                st.header("📑 Planilhas Geradas")
                
                # Define os filtros por INTERVALOS de atraso e cobrança antecipada
                st.write("⚙️ Aplicando filtros...")
                filtros = [
                    # Régua de cobrança antecipada (faturas emitidas)
                    {"nome": "Cobrança Antecipada - 10 dias antes", "dias_min": -10, "dias_max": -10, "status_filter": ["Emitida"]},
                    {"nome": "Cobrança Antecipada - 5 dias antes", "dias_min": -5, "dias_max": -5, "status_filter": ["Emitida"]},
                    {"nome": "Cobrança Antecipada - 3 dias antes", "dias_min": -3, "dias_max": -3, "status_filter": ["Emitida"]},
                    # Atrasos
                    {"nome": "A vencer (Até hoje)", "dias_min": None, "dias_max": 0},
                    {"nome": "A vencer (hoje)", "dias_min": 0, "dias_max": 0},
                    {"nome": "1-3 dias de atraso", "dias_min": 1, "dias_max": 3},
                    {"nome": "4-7 dias de atraso", "dias_min": 4, "dias_max": 7},
                    {"nome": "8-14 dias de atraso", "dias_min": 8, "dias_max": 14},
                    {"nome": "15-30 dias de atraso", "dias_min": 15, "dias_max": 30},
                    {"nome": "31-60 dias de atraso", "dias_min": 31, "dias_max": 60},
                    {"nome": "61-90 dias de atraso", "dias_min": 61, "dias_max": 90},
                    {"nome": "> 90 dias de atraso", "dias_min": 91, "dias_max": None},
                ]
                
                # Colunas importantes para verificar
                colunas_importantes = ['Data de Vencimento', 'Status da Fatura']
                colunas_encontradas = [col for col in colunas_importantes if col in df.columns]
                
                if 'Data de Vencimento' not in colunas_encontradas:
                    st.error("❌ Coluna 'Data de Vencimento' não encontrada na planilha!")
                    return
                
                # Processa cada filtro por INTERVALO
                resultados = {}
                
                for filtro in filtros:
                    df_filtro = df.copy()
                    df_filtro['Dias_Vencimento'] = df_filtro.apply(calcular_dias_vencimento, axis=1)
                    df_filtro = df_filtro.dropna(subset=['Dias_Vencimento'])
                    
                    # Filtra por status específico se definido (para cobrança antecipada)
                    if 'status_filter' in filtro and filtro['status_filter']:
                        if 'Status da Fatura' in df_filtro.columns:
                            df_filtro = df_filtro[df_filtro['Status da Fatura'].isin(filtro['status_filter'])]
                    
                    # Aplica filtro por INTERVALO de dias
                    dias_min = filtro['dias_min']
                    dias_max = filtro['dias_max']
                    
                    if dias_min is None and dias_max is not None:
                        # A vencer (até hoje): dias <= 0
                        df_resultado = df_filtro[df_filtro['Dias_Vencimento'] <= dias_max]
                    elif dias_min is not None and dias_max is None:
                        # Maior que X dias: dias >= X
                        df_resultado = df_filtro[df_filtro['Dias_Vencimento'] >= dias_min]
                    elif dias_min is not None and dias_max is not None:
                        # Intervalo entre X e Y dias
                        df_resultado = df_filtro[
                            (df_filtro['Dias_Vencimento'] >= dias_min) & 
                            (df_filtro['Dias_Vencimento'] <= dias_max)
                        ]
                    else:
                        df_resultado = pd.DataFrame()
                    
                    # Filtra por status não pago (se coluna existir e não for cobrança antecipada)
                    if 'status_filter' not in filtro or not filtro['status_filter']:
                        if 'Status da Fatura' in df.columns:
                            # Lista de status que devem ser EXCLUÍDOS (já pagos)
                            status_pagos = [
                                'Pago', 'PAGO', 'pago',
                                'Paga', 'PAGA', 'paga',
                                'Pago no Pix', 'PAGO NO PIX', 'pago no pix',
                                'Paga no Pix', 'PAGA NO PIX', 'paga no pix','Paga no PIX',
                                'Quitado', 'QUITADO', 'quitado',
                                'Liquidado', 'LIQUIDADO', 'liquidado'
                            ]
                            df_resultado = df_resultado[
                                (~df_resultado['Status da Fatura'].isin(status_pagos)) &
                                (df_resultado['Status da Fatura'].notna())
                            ]

                            # Filtra por status cancelada (se coluna existir)
                            status_canceladas = [
                                'Cancelada', 'CANCELADA', 'cancelada',
                                'Anulada', 'ANULADA', 'anulada'
                            ]
                            df_resultado = df_resultado[
                                (~df_resultado['Status da Fatura'].isin(status_canceladas)) &
                                (df_resultado['Status da Fatura'].notna())
                            ]

                            # Filtra por status Baixada (se coluna existir)
                            status_baixadas = [
                                'Baixada', 'BAIXADA', 'baixada',
                                'Liquidada', 'LIQUIDADA', 'liquidada'
                            ]
                            df_resultado = df_resultado[
                                (~df_resultado['Status da Fatura'].isin(status_baixadas)) &
                                (df_resultado['Status da Fatura'].notna())
                            ]
                       
                    # Remove coluna calculada auxiliar
                    if 'Dias_Vencimento' in df_resultado.columns:
                        df_resultado = df_resultado.drop(columns=['Dias_Vencimento'])
                    
                    resultados[filtro['nome']] = df_resultado
                
                st.write("📊 Gerando relatórios...")
                
                # Exibe cada resultado
                total_geral = 0
                
                for nome, df_resultado in resultados.items():
                    with st.expander(f"📄 {nome} ({len(df_resultado)} registros)"):
                        if len(df_resultado) > 0:
                            # Métricas
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Registros", len(df_resultado))
                            with col2:
                                valor_total = df_resultado['Valor Cobrança'].sum() if 'Valor Cobrança' in df_resultado.columns else 0
                                st.metric("Valor Total", f"R$ {valor_total:,.2f}")
                            with col3:
                                com_telefone = df_resultado['Telefone'].notna().sum() if 'Telefone' in df_resultado.columns else 0
                                st.metric("Com Telefone", com_telefone)

                            # Preview
                            st.dataframe(df_resultado.head(5), use_container_width=True)

                            # Download planilha completa
                            excel_data = gerar_excel(df_resultado, f"{nome}.xlsx")
                            st.download_button(
                                label=f"⬇️ Baixar {nome}",
                                data=excel_data,
                                file_name=f"{nome.replace(' ', '_')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # Download planilha resumida
                            excel_resumido = gerar_excel_resumido(df_resultado)
                            st.download_button(
                                label=f"⬇️ Baixar {nome} (Resumido)",
                                data=excel_resumido,
                                file_name=f"{nome.replace(' ', '_')}_resumido.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            total_geral += len(df_resultado)
                        else:
                            st.info("Nenhum registro encontrado")
                
                st.markdown("---")
                st.write(f"✅ Total de registros filtrados: **{total_geral}**")
                status.update(label="✅ Processamento concluído!", state="complete")
            
        except Exception as e:
            st.error(f"❌ Erro ao processar planilha: {str(e)}")
            st.info("Verifique se o formato da planilha está correto")
     
    else:
        # Instruções quando não há arquivo
        st.info("👆 Faça upload de uma planilha Excel para começar")
        
        st.markdown("### Colunas esperadas:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Obrigatórias:**
            - Data de Vencimento
            """)
        with col2:
            st.markdown("""
            **Importantes para WhatsApp:**
            - Nome Titular
            - Telefone
            - Celular
            """)
        with col3:
            st.markdown("""
            **Opcionais:**
            - Status da Fatura
            - Valor Cobrança
            """)

if __name__ == "__main__":
    main()
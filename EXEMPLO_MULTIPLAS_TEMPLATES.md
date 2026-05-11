# Arquivo de Configuração de Templates - .env.templates

# ============================================================================
# MODO 1: CONFIGURAÇÃO DE MÚLTIPLAS TEMPLATES VIA .env
# ============================================================================

# Coloque essas variáveis no seu arquivo .env:

WHATSAPP_TEMPLATE_COBRANCA=550e8400-e29b-41d4-a716-446655440000
WHATSAPP_TEMPLATE_AVISO_SUSPENSAO=550e8400-xxxx-41d4-a716-xxxxxxxx0001
WHATSAPP_TEMPLATE_CONFIRMACAO_PAGAMENTO=550e8400-yyyy-41d4-a716-xxxxxxxx0002
WHATSAPP_TEMPLATE_COBRANCA_30DIAS=550e8400-zzzz-41d4-a716-xxxxxxxx0003

# ============================================================================
# MODO 2: CONFIGURAÇÃO DE MÚLTIPLAS TEMPLATES VIA CÓDIGO
# ============================================================================

# Arquivo: config_templates.py

from whatsapp_integration_v2 import TemplateManager

# Cria o gerenciador
template_manager = TemplateManager()

# Adiciona suas templates
template_manager.add_template(
    key='cobranca_geral',
    template_id='550e8400-e29b-41d4-a716-446655440000',
    description='Template geral de cobrança'
)

template_manager.add_template(
    key='cobranca_30dias',
    template_id='550e8400-xxxx-41d4-a716-xxxxxxxx0001',
    description='Template para atrasos de 30 dias'
)

template_manager.add_template(
    key='aviso_suspensao',
    template_id='550e8400-yyyy-41d4-a716-xxxxxxxx0002',
    description='Template de aviso de suspensão'
)

template_manager.add_template(
    key='confirmacao_pagamento',
    template_id='550e8400-zzzz-41d4-a716-xxxxxxxx0003',
    description='Template de confirmação de pagamento'
)

# Para usar em outro arquivo:
# from config_templates import template_manager

# ============================================================================
# MODO 3: CARREGAR TEMPLATES DO .env AUTOMATICAMENTE
# ============================================================================

# Código:

import os
from dotenv import load_dotenv
from whatsapp_integration_v2 import TemplateManager

load_dotenv()

# Cria gerenciador e carrega as variáveis que começam com WHATSAPP_TEMPLATE_
template_manager = TemplateManager()
template_manager.load_from_env(os.environ)

# Agora você tem acesso a todas as templates:
# template_manager.get_template('cobranca')
# template_manager.list_template_keys()
# template_manager.list_templates()

# ============================================================================
# EXEMPLOS DE USO - ENVIO SEM userId
# ============================================================================

# Exemplo 1: Usando telefone/celular como identificador

from whatsapp_integration_v2 import WhatsAppClient, create_cobranca_template_payload
import os
from dotenv import load_dotenv

load_dotenv()

client = WhatsAppClient(
    api_url=os.getenv('WHATSAPP_API_URL'),
    auth_token=os.getenv('WHATSAPP_AUTH_TOKEN')
)

# Enviando para um telefone (sem userId)
resultado = client.send_template(
    user_id="11999999999",  # Telefone/celular aqui
    template_id="550e8400-e29b-41d4-a716-446655440000",
    body_parameters=["João Silva", "150.00", "15/05/2024"]
)

print(f"Status: {resultado['success']}")

# ============================================================================
# EXEMPLOS DE USO - MÚLTIPLAS TEMPLATES
# ============================================================================

# Exemplo 2: Escolher template dinamicamente

template_manager = TemplateManager()
template_manager.add_template('cobranca', '550e8400-...')
template_manager.add_template('suspensao', '550e8400-...')

# Função para enviar com template dinâmica
def enviar_cobranca(telefone, nome, valor, vencimento, tipo='cobranca'):
    """
    Envia cobrança com template selecionada
    
    Args:
        telefone: Telefone do cliente (11999999999)
        nome: Nome do cliente
        valor: Valor da cobrança
        vencimento: Data de vencimento
        tipo: Tipo de template ('cobranca', 'suspensao', etc)
    """
    template_id = template_manager.get_template(tipo)
    
    if not template_id:
        print(f"❌ Template '{tipo}' não encontrada")
        return False
    
    resultado = client.send_template(
        user_id=telefone,
        template_id=template_id,
        body_parameters=[nome, valor, vencimento]
    )
    
    return resultado['success']

# Usar a função
enviar_cobranca("11999999999", "João", "150.00", "15/05/2024", tipo='cobranca')
enviar_cobranca("21988888888", "Maria", "200.00", "10/05/2024", tipo='suspensao')

# ============================================================================
# EXEMPLO 3: PROCESSAR PLANILHA COM MÚLTIPLAS TEMPLATES
# ============================================================================

import pandas as pd

# Carrega planilha
df = pd.read_excel('planilha_cobranca.xlsx')

# Processa cada linha
templates = []
for idx, row in df.iterrows():
    # Extrai dados
    telefone = str(row['Celular'])  # Sem userId, usa celular
    nome = row['Nome Titular']
    valor = row['Valor Cobrança']
    vencimento = row['Data de Vencimento']
    
    # Escolhe template baseado na situação
    dias_atraso = row.get('Dias_Atraso', 0)
    
    if dias_atraso < 0:
        tipo_template = 'cobranca_antecipada'
    elif dias_atraso <= 7:
        tipo_template = 'cobranca_geral'
    elif dias_atraso <= 30:
        tipo_template = 'cobranca_30dias'
    else:
        tipo_template = 'aviso_suspensao'
    
    # Obtém o template ID
    template_id = template_manager.get_template(tipo_template)
    
    if template_id:
        templates.append({
            'user_id': telefone,
            'template_id': template_id,
            'body_parameters': [nome, str(valor), str(vencimento)]
        })

# Envia em lote
resultados = client.send_batch(templates)
relatorio = client.generate_summary_report(resultados)

print(f"✅ {relatorio['successful']}/{relatorio['total_messages']}")

# ============================================================================
# EXEMPLO 4: ARQUIVO .env PARA MÚLTIPLAS TEMPLATES
# ============================================================================

# Coloque isto no seu arquivo .env:

"""
# API WhatsApp
WHATSAPP_API_URL=https://seu-dominio.azurewebsites.net
WHATSAPP_AUTH_TOKEN=seu_token_aqui

# TEMPLATES MÚLTIPLAS
# Template para cobrança geral
WHATSAPP_TEMPLATE_COBRANCA=550e8400-e29b-41d4-a716-446655440000

# Template para cobrança com 30 dias de atraso
WHATSAPP_TEMPLATE_COBRANCA_30DIAS=550e8400-xxxx-41d4-a716-xxxxxxxx0001

# Template para aviso de suspensão (90+ dias)
WHATSAPP_TEMPLATE_SUSPENSAO=550e8400-yyyy-41d4-a716-xxxxxxxx0002

# Template para confirmação de pagamento
WHATSAPP_TEMPLATE_CONFIRMACAO=550e8400-zzzz-41d4-a716-xxxxxxxx0003

# Template para cobrança antecipada (antes do vencimento)
WHATSAPP_TEMPLATE_ANTECIPADA=550e8400-aaaa-41d4-a716-xxxxxxxx0004

# Template para renegociação
WHATSAPP_TEMPLATE_RENEGOCIACAO=550e8400-bbbb-41d4-a716-xxxxxxxx0005
"""

# ============================================================================
# EXEMPLO 5: ESTRUTURA DE PLANILHA RECOMENDADA
# ============================================================================

"""
Sua planilha deve ter estas colunas:

| Celular | Nome Titular | Valor Cobrança | Data Vencimento | Dias_Atraso | Template |
|---------|--------------|-----------------|-----------------|-------------|----------|
| 11999999999 | João Silva | 150.00 | 15/05/2024 | 5 | cobranca |
| 21988888888 | Maria Santos | 200.00 | 10/05/2024 | 30 | cobranca_30dias |
| 85987777777 | Pedro Costa | 250.00 | 01/03/2024 | 71 | suspensao |

Alternativa: A coluna "Template" é OPCIONAL. Você pode calcular automaticamente
baseado em Dias_Atraso como no Exemplo 3.
"""

# ============================================================================
# EXEMPLO 6: FUNÇÃO UTILITÁRIA COMPLETA
# ============================================================================

def enviar_lote_com_templates_dinamicas(
    arquivo_excel: str,
    template_manager: 'TemplateManager',
    client: 'WhatsAppClient',
    coluna_telefone: str = 'Celular',
    coluna_nome: str = 'Nome Titular',
    coluna_valor: str = 'Valor Cobrança',
    coluna_vencimento: str = 'Data de Vencimento',
    coluna_dias_atraso: str = 'Dias_Atraso',
    coluna_template: str = None
):
    """
    Envia lote completo com seleção automática de templates
    
    Args:
        arquivo_excel: Caminho do arquivo
        template_manager: Gerenciador de templates
        client: Cliente WhatsApp
        coluna_telefone: Nome da coluna com telefone
        coluna_nome: Nome da coluna com nome do cliente
        coluna_valor: Nome da coluna com valor
        coluna_vencimento: Nome da coluna com data
        coluna_dias_atraso: Nome da coluna com dias de atraso
        coluna_template: Nome da coluna com tipo de template (opcional)
    
    Returns:
        Dict com relatório
    """
    
    # Carrega planilha
    df = pd.read_excel(arquivo_excel)
    
    templates = []
    
    for idx, row in df.iterrows():
        # Valida telefone
        telefone = str(row.get(coluna_telefone, '')).strip()
        if not telefone or telefone == 'nan':
            continue
        
        # Se tem coluna com tipo de template, usa ela
        if coluna_template and coluna_template in df.columns:
            tipo_template = row.get(coluna_template)
        else:
            # Senão, calcula automaticamente
            dias_atraso = row.get(coluna_dias_atraso, 0)
            
            if dias_atraso < 0:
                tipo_template = 'cobranca_antecipada'
            elif dias_atraso <= 7:
                tipo_template = 'cobranca'
            elif dias_atraso <= 30:
                tipo_template = 'cobranca_30dias'
            else:
                tipo_template = 'suspensao'
        
        # Obtém template
        template_id = template_manager.get_template(tipo_template)
        
        if not template_id:
            print(f"⚠️  Template '{tipo_template}' não encontrada para {telefone}")
            continue
        
        # Cria payload
        templates.append({
            'user_id': telefone,
            'template_id': template_id,
            'body_parameters': [
                str(row.get(coluna_nome, 'Cliente')),
                str(row.get(coluna_valor, '0')),
                str(row.get(coluna_vencimento, ''))
            ]
        })
    
    # Envia em lote
    if templates:
        resultados = client.send_batch(templates)
        return client.generate_summary_report(resultados)
    
    return {'total_messages': 0, 'successful': 0, 'failed': 0}


# Usar a função:
# relatorio = enviar_lote_com_templates_dinamicas(
#     'planilha.xlsx',
#     template_manager,
#     client
# )

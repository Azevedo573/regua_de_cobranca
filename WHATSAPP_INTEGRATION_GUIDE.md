# 📱 Integração WhatsApp - Guia de Configuração

## Overview

Este guia mostra como integrar a sua API de WhatsApp Azure com a Régua de Cobrança para enviar mensagens de cobrança em lote automaticamente.

## 📋 Pré-requisitos

- Conta ativa na API WhatsApp (Azure)
- Credenciais de autenticação (API Key ou Bearer Token)
- Python 3.8+

## 🚀 Configuração Inicial

### 1. Configurar Variáveis de Ambiente

1. **Copie o arquivo de exemplo:**
```bash
cp .env.example .env
```

2. **Edite o arquivo `.env` com suas credenciais:**
```env
WHATSAPP_API_URL=https://cbm-wap-babysuri-cb71990515-g2c.azurewebsites.net
WHATSAPP_AUTH_TOKEN=seu_token_bearer_aqui
WHATSAPP_API_KEY=sua_chave_api_aqui  # Se usar API Key ao invés de Token
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

## 🎯 Como Usar

### Opção 1: Via Interface Web (Streamlit)

```bash
# Execute a página de envio
streamlit run whatsapp_sender.py
```

1. Acesse `http://localhost:8501` no navegador
2. Faça upload da planilha filtrada
3. Visualize as mensagens que serão enviadas
4. Clique em "Enviar Mensagens Agora"

### Opção 2: Via Script Python

```python
from whatsapp_integration import WhatsAppClient, create_cobranca_message
import pandas as pd

# Inicializa cliente
client = WhatsAppClient(
    api_url="https://cbm-wap-babysuri-cb71990515-g2c.azurewebsites.net",
    auth_token="seu_token_aqui"
)

# Testa conexão
success, message = client.test_connection()
print(message)

# Carrega planilha
df = pd.read_excel('planilha_cobranca.xlsx')

# Prepara mensagens
mensagens = []
for idx, row in df.iterrows():
    mensagem = create_cobranca_message(row)
    mensagens.append({
        'phone': row['Celular'],
        'message': mensagem
    })

# Envia em lote
resultados = client.send_batch(mensagens)

# Gera relatório
relatorio = client.generate_summary_report(resultados)
print(f"Enviadas: {relatorio['successful']}/{relatorio['total_messages']}")
```

## 📊 Requisitos da Planilha

A planilha deve conter **obrigatoriamente** as seguintes colunas:

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| **Celular** | String | Número de celular com código do país | 11999999999 ou +5511999999999 |
| **Nome Titular** | String | Nome do cliente | João Silva |
| **Valor Cobrança** | Float | Valor a cobrar | 150.00 |
| **Data de Vencimento** | Date | Data do vencimento | 2024-05-15 |
| **Operadora da Fatura** | String | Nome da fatura | Operadora X |

## 📝 Personalizar Mensagens

Para modificar o template de mensagem, edite a função `create_cobranca_message()` em `whatsapp_integration.py`:

```python
def create_cobranca_message(row: dict) -> str:
    nome = row.get('Nome Titular', 'Cliente')
    valor = row.get('Valor Cobrança', 'a confirmar')
    vencimento = row.get('Data de Vencimento', 'a confirmar')
    
    # Customize aqui:
    mensagem = f"""Olá {nome}! 👋
    
Aviso de cobrança...
    """
    return mensagem
```

## 🔍 Validação de Números

O cliente WhatsApp formata automaticamente números de celular para o padrão internacional:

- `11999999999` → `5511999999999`
- `999999999` → `55999999999` (se tiver 9 dígitos)
- `+5511999999999` → mantém como está

## ⚡ Opções Avançadas

### Personalizar Headers de Requisição

```python
client = WhatsAppClient(
    api_url="https://...",
    auth_token="token"
)

# Headers customizados são adicionados automaticamente
# Para headers adicionais, modifique _setup_headers()
```

### Implementar Retry Logic

```python
from whatsapp_integration import WhatsAppClient
import time

client = WhatsAppClient(...)
max_retries = 3

for attempt in range(max_retries):
    try:
        resultado = client.send_message(
            phone_number="11999999999",
            message="Sua mensagem"
        )
        if resultado['success']:
            break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Backoff exponencial
        else:
            raise
```

### Implementar Banco de Dados para Histórico

```python
# Adicionar a whatsapp_integration.py:
import sqlite3

def salvar_resultado(resultado):
    conn = sqlite3.connect('whatsapp_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS envios (
            id INTEGER PRIMARY KEY,
            phone TEXT,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    cursor.execute(
        'INSERT INTO envios (phone, status, timestamp) VALUES (?, ?, ?)',
        (resultado['phone'], resultado['success'], resultado['timestamp'])
    )
    conn.commit()
    conn.close()
```

## 🐛 Troubleshooting

### Erro: "Conexão recusada"
- Verifique se a URL da API está correta
- Confira se o token/chave estão válidos
- Teste com `curl`: `curl https://sua-api/health`

### Erro: "Autenticação inválida"
- Verifique o token Bearer no arquivo `.env`
- Certifique-se de que está no formato correto
- Regenere o token se necessário

### Erro: "Número de telefone inválido"
- Verifique se o número contém apenas dígitos
- Adicione código do país (55 para Brasil)
- Remova caracteres especiais (parênteses, hífen)

### Aviso: "Números sem celular"
- Verifique a coluna 'Celular' na planilha
- Preencha números faltando ou remova linhas vazias

## 📈 Monitoramento

### Visualizar Logs

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('whatsapp_integration')
```

### Métricas Importantes

- **Taxa de Sucesso**: Quantas mensagens foram entregues
- **Tempo de Envio**: Média de segundos por mensagem
- **Taxa de Erro**: Quantas falharam e por quê

## 🔐 Segurança

### Boas Práticas

1. ✅ **Nunca commitar `.env`** com credenciais reais
2. ✅ **Usar variáveis de ambiente** em produção
3. ✅ **Validar telefones** antes de enviar
4. ✅ **Logar todas as tentativas** de envio
5. ✅ **Implementar rate limiting** para não sobrecarregar a API

### Exemplo com Variables de Ambiente (Produção)

```python
import os
from whatsapp_integration import WhatsAppClient

client = WhatsAppClient(
    api_url=os.environ['WHATSAPP_API_URL'],
    auth_token=os.environ['WHATSAPP_AUTH_TOKEN']
)
```

## 📞 Suporte

Para dúvidas sobre a API WhatsApp, consulte:
- Documentação oficial da API Azure
- Dashboard da conta Azure
- Endpoint `/health` para status da API

## 📄 Exemplo de Resposta da API

```json
{
    "success": true,
    "status_code": 200,
    "phone": "5511999999999",
    "message": "Olá João...",
    "timestamp": "2024-05-11T14:30:00",
    "response": {
        "id": "msg_12345",
        "status": "sent",
        "timestamp": "2024-05-11T14:30:01"
    }
}
```

---

**Última atualização:** 11 de maio de 2024

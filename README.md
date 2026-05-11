# 📊 Régua de Cobrança

Aplicação web para geração de planilhas de cobrança filtradas por vencimento e status, facilitando o disparo de mensagens de cobrança via WhatsApp de forma organizada e segmentada.

## Problema

A gestão manual de cobranças em lotes é trabalhosa e propensa a erros. É necessário filtrar contratos vencidos ou a vencer, segmentá-los por status e exportar em formatos adequados para disparar mensagens via WhatsApp de forma eficiente.

## Funcionalidades

- Upload de planilhas (Excel/CSV) com dados de clientes e contratos (Digital-Saúde)
- Filtro inteligente por vencimento:
  - Contratos vencidos (há X dias)
  - Contratos a vencer (em X dias)
  - Contratos com vencimento específico
- Filtro por status de pagamento (pago, em atraso, etc)
- Geração automática de planilhas segmentadas
- Download direto em formato Excel (.xlsx)
- Cálculo automático de dias de vencimento
- Interface responsiva e intuitiva
- **✨ NOVO: Integração com API WhatsApp para envio de mensagens em lote**

## Tecnologias

- **Python 3.8+** - Linguagem de programação
- **Streamlit** - Framework para criação de aplicações web
- **Pandas** - Manipulação e análise de dados
- **OpenPyXL** - Trabalho com arquivos Excel
- **Requests** - Cliente HTTP para integração com APIs
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

## Como executar

### Pré-requisitos
- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes Python)

### Instalação Rápida (Teste Local)

1. Clone o repositório:
```bash
git clone https://github.com/Azevedo573/regua_de_cobranca.git
cd regua_de_cobranca
```

2. Instale dependências:
```bash
pip install -r requirements.txt
```

3. Execute o setup de teste:
```bash
python setup_teste.py
```

Este script irá:
- ✅ Criar uma planilha de teste com dados realistas
- ✅ Validar seu arquivo `.env`
- ✅ Testar conectividade com API WhatsApp (se configurada)
- ✅ Exibir próximos passos

4. Inicie a aplicação:
```bash
streamlit run app.py
```

5. Acesse no navegador:
```
http://localhost:8501
```

### Configuração para WhatsApp

#### Passo 1: Copie o arquivo de configuração
```bash
cp .env.example .env
```

#### Passo 2: Configure seu `.env`
Edite o arquivo `.env` com:
```ini
# API WhatsApp (obrigatório)
WHATSAPP_API_URL=https://seu-servidor.azurewebsites.net
WHATSAPP_AUTH_TOKEN=seu_token_aqui

# Templates (obrigatório ter ao menos um)
WHATSAPP_TEMPLATE_COBRANCA=550e8400-e29b-41d4-a716-446655440000
WHATSAPP_TEMPLATE_COBRANCA_30DIAS=550e8400-xxxx-41d4-a716-xxxxxxxx0001
WHATSAPP_TEMPLATE_SUSPENSAO=550e8400-yyyy-41d4-a716-xxxxxxxx0002
```

#### Passo 3: Teste a conexão
```bash
python -c "
from whatsapp_integration_v2 import WhatsAppClient
from dotenv import load_dotenv
import os

load_dotenv()
client = WhatsAppClient(
    api_url=os.getenv('WHATSAPP_API_URL'),
    auth_token=os.getenv('WHATSAPP_AUTH_TOKEN')
)
success, msg = client.test_connection()
print('✅' if success else '❌', msg)
"
```

## Fluxo Completo de Uso

### 📊 Passo 1: Upload da Planilha
```
1. Abra http://localhost:8501
2. Clique em "📤 Arraste ou selecione a planilha"
3. Selecione seu arquivo Excel (Digital-Saúde)
4. Sistema processará automaticamente
```

### 📑 Passo 2: Visualize Planilhas Filtradas
O sistema gera automaticamente 12 planilhas:
- **Cobrança Antecipada**: 10, 5 e 3 dias antes
- **A Vencer**: até hoje, vence hoje
- **Atrasos**: 1-3 dias, 4-7 dias, 8-14 dias, 15-30 dias, 31-60 dias, 61-90 dias, 90+ dias

```
Cada planilha exibe:
├─ 📊 Métricas: Total, Valor, Com Telefone
├─ 👀 Preview: Primeiros 5 registros
├─ ⬇️ Download: Planilha completa
├─ ⬇️ Download: Planilha resumida (apenas essencial)
└─ 📤 Disparar: Enviar via WhatsApp
```

### 📤 Passo 3: Envio WhatsApp (Novo!)

```
Para cada planilha:

1. Expanda a seção "📤 Disparar X no WhatsApp"
2. Escolha a template desejada (dropdown):
   - Cobrança (padrão)
   - Cobrança 30 dias (atrasos maiores)
   - Suspensão (90+ dias)
3. [OPCIONAL] Ative "🧪 Modo Simulação" para testar
4. Clique "✅ Enviar WhatsApp"
5. Veja resultado:
   - ✅ Total de registros
   - ✅ Sucesso
   - ❌ Falhas
   - 📋 Detalhes
```

## Instalação Detalhada

### Com venv (Python puro)
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py
```

### Com Conda (alternativa)
```bash
# Criar ambiente
conda create -n regua python=3.10

# Ativar
conda activate regua

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py
```

## Estrutura do Projeto

```
regua_de_cobranca/
├── app.py                              ← Aplicação principal (processamento + WhatsApp)
├── whatsapp_integration_v2.py          ← Cliente WhatsApp com suporte a múltiplas templates
├── setup_teste.py                      ← Script para setup automático de teste
├── exemplo_multiplas_templates.py      ← 4 exemplos práticos de uso
├── EXEMPLO_MULTIPLAS_TEMPLATES.md      ← Documentação de exemplos
├── GUIA_TESTE_LOCAL.py                 ← Guia passo-a-passo
├── .env.example                        ← Modelo de configuração
├── requirements.txt                    ← Dependências Python
├── README.md                           ← Este arquivo
└── [planilhas geradas]/                ← Arquivos Excel gerados
    ├── cobranca_1-3_dias.xlsx
    ├── cobranca_4-7_dias.xlsx
    ├── atraso_30_dias.xlsx
    └── ...
```

## 📱 Integração WhatsApp - Guia Completo

A aplicação inclui integração **nativa** com API WhatsApp para envio de templates em lote!

### ✨ Características

- ✅ **Múltiplas Templates**: Configure quantas templates diferentes precisar
- ✅ **Seleção Dinâmica**: Escolha qual template usar antes de enviar
- ✅ **Modo Simulação**: Teste sem enviar de verdade
- ✅ **Lote Automático**: Envia para todos os registros da planilha
- ✅ **Relatório de Resultado**: Taxa de sucesso/falha
- ✅ **Sem userId**: Use telefone/celular como identificador

### 🚀 Começar em 3 Passos

**Passo 1: Copie a configuração**
```bash
cp .env.example .env
```

**Passo 2: Configure seus valores**
```ini
WHATSAPP_API_URL=https://seu-servidor.azurewebsites.net
WHATSAPP_AUTH_TOKEN=seu_token_aqui

WHATSAPP_TEMPLATE_COBRANCA=550e8400-...
WHATSAPP_TEMPLATE_ATRASO=550e8400-...
WHATSAPP_TEMPLATE_SUSPENSAO=550e8400-...
```

**Passo 3: Use a interface**
```bash
streamlit run app.py
```

### 📊 Fluxo Passo-a-Passo

```
1. Upload Planilha Digital-Saúde
   ↓
2. Sistema processa e gera 12 planilhas filtradas
   ↓
3. Você escolhe uma planilha
   ↓
4. Clica em "📤 Disparar no WhatsApp"
   ↓
5. Sistema mostra preview dos contatos
   ↓
6. Você escolhe a template desejada
   ↓
7. [OPCIONAL] Ativa modo simulação
   ↓
8. Clica em "✅ Enviar WhatsApp"
   ↓
9. Resultado: Taxa de sucesso/falha
```

### 🎯 Interface de Disparo

Quando expande "📤 Disparar no WhatsApp":

```
┌─────────────────────────────────┐
│ 📤 Disparar 5 no WhatsApp       │
│                                 │
│ Template: [Cobrança ▼]          │
│  - Cobrança (padrão)            │
│  - Atraso 30 dias               │
│  - Suspensão                    │
│                                 │
│ 🧪 Simulação: [ ] Ativar       │
│                                 │
│ 👀 Ver contatos                │
│  ├─ João Silva (11999999999)   │
│  ├─ Maria Santos (21988888888) │
│  └─ ...                         │
│                                 │
│ [✅ Enviar WhatsApp]            │
│                                 │
│ Resultado:                      │
│  Total: 5                       │
│  ✅ Sucesso: 5                  │
│  ❌ Falhas: 0                   │
└─────────────────────────────────┘
```

### 💡 Exemplos de Configuração

**Exemplo 1: Uma única template**
```env
WHATSAPP_TEMPLATE_COBRANCA=550e8400-e29b-41d4-a716-446655440000
```

**Exemplo 2: Múltiplas templates (recomendado)**
```env
WHATSAPP_TEMPLATE_COBRANCA=550e8400-aaaa-41d4-a716-000000000000
WHATSAPP_TEMPLATE_ATRASO_30=550e8400-bbbb-41d4-a716-111111111111
WHATSAPP_TEMPLATE_SUSPENSAO=550e8400-cccc-41d4-a716-222222222222
WHATSAPP_TEMPLATE_CONFIRMACAO=550e8400-dddd-41d4-a716-333333333333
```

**Exemplo 3: Com template de renegociação**
```env
WHATSAPP_TEMPLATE_COBRANCA=550e8400-e29b-41d4-a716-446655440000
WHATSAPP_TEMPLATE_ATRASO_30DIAS=550e8400-xxxx-41d4-a716-xxxxxxxx0001
WHATSAPP_TEMPLATE_SUSPENSAO=550e8400-yyyy-41d4-a716-xxxxxxxx0002
WHATSAPP_TEMPLATE_RENEGOCIACAO=550e8400-zzzz-41d4-a716-xxxxxxxx0003
```

### 🔐 Segurança

- **Nunca commite `.env` em git** (já está no `.gitignore`)
- **Guarde seu `WHATSAPP_AUTH_TOKEN` em lugar seguro**
- **Use modo simulação para testes** antes de enviar de verdade
- **Sempre revise o preview** antes de confirmar

### 🛠️ Troubleshooting

#### Erro: "WHATSAPP_API_URL não configurado"
- Verifique se `.env` foi criado corretamente
- Execute: `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('WHATSAPP_API_URL'))"`

#### Erro: "Conexão com API falhou"
- Verifique `WHATSAPP_API_URL` (sem barra no final)
- Teste ping: `ping seu-dominio.azurewebsites.net`
- Verifique `WHATSAPP_AUTH_TOKEN` está correto

#### Erro: "Template não encontrada"
- Copie o ID exato do Portal (formato: 550e8400-...)
- Verifique o prefixo `WHATSAPP_TEMPLATE_`
- Template deve estar pré-aprovada na plataforma

#### Nenhum registro para enviar
- Verifique coluna "Celular" ou "Telefone" na planilha
- Confirme que há números válidos (ex: 11999999999)
- Verifique Status (não pode ser "Pago", "Cancelada", etc)

## Dados de Teste (pré-configurado)

Execute `python setup_teste.py` para:
- ✅ Criar planilha de teste com 10 registros
- ✅ Validar arquivo `.env`
- ✅ Testar conexão com API
- ✅ Exibir próximos passos

### Exemplo de Planilha de Teste

| Celular | Nome Titular | Data Vencimento | Valor Cobrança | Status |
|---------|--------------|-----------------|-----------------|--------|
| 11999999999 | João Silva | 05/05/2026 | 150.00 | Emitida |
| 21988888888 | Maria Santos | 10/04/2026 | 200.00 | Emitida |
| 85987777777 | Pedro Costa | 01/03/2026 | 250.00 | Emitida |
| ... | ... | ... | ... | ... |

**Interpretação:**
- João: 6 dias de atraso → "4-7 dias de atraso"
- Maria: 31 dias de atraso → "31-60 dias de atraso"
- Pedro: 71 dias de atraso → "> 90 dias de atraso"

## Formatos Aceitos de Planilha

### Coluna Telefone (com prefixo)
```
11999999999   ← Válido (11 + 9 dígitos)
21988888888   ← Válido (21 + 8 dígitos)
```

### Status da Fatura (filtrados automaticamente)
```
Excluídos (não aparecem nas planilhas):
- Pago, PAGO, pago
- Paga, PAGA, paga
- Quitado, QUITADO
- Cancelada, CANCELADA
- Anulada, ANULADA

Incluídos (processados normalmente):
- Emitida
- Em aberto
- Pendente
- Vencida
```

### Colunas Obrigatórias
- `Data de Vencimento` - Obrigatória para filtros

### Colunas Recomendadas para WhatsApp
- `Celular` ou `Telefone` - Para identificar contato
- `Nome Titular` - Para parametrizar mensagem
- `Valor Cobrança` - Para incluir na mensagem
- `Status da Fatura` - Para filtrar automáticamente

## 📚 Documentação Adicional

- [GUIA_TESTE_LOCAL.py](GUIA_TESTE_LOCAL.py) - Passo-a-passo completo
- [EXEMPLO_MULTIPLAS_TEMPLATES.md](EXEMPLO_MULTIPLAS_TEMPLATES.md) - Exemplos de código
- [exemplo_multiplas_templates.py](exemplo_multiplas_templates.py) - 4 exemplos executáveis

## 🐛 Reportar Problemas

Se encontrar erros ou tiver sugestões:
1. Verifique os logs (bottom do Streamlit)
2. Teste com modo simulação
3. Abra uma issue com detalhes

### 📋 Requisitos da Planilha

A planilha deve ter as seguintes colunas:
- **userId** (obrigatório) - ID do contato no sistema
- **Nome Titular** - Nome do cliente (1º parâmetro)
- **Valor Cobrança** - Valor a cobrar (2º parâmetro)
- **Data de Vencimento** - Data do vencimento (3º parâmetro)
- **Operadora da Fatura** - Referência

### 💻 Exemplos de Código

**Envio Simples:**
```python
from whatsapp_integration import WhatsAppClient

client = WhatsAppClient(
    api_url="https://seu-dominio.azurewebsites.net",
    auth_token="seu_token"
)

resultado = client.send_template(
    user_id="contato_123",
    template_id="guid-da-template",
    body_parameters=["João", "150.00", "15/05/2024"]
)
```

**Envio em Lote:**
```python
templates = [
    {
        'user_id': 'contato_001',
        'template_id': 'guid',
        'body_parameters': ['Cliente A', '150.00', '15/05/2024']
    }
]
resultados = client.send_batch(templates)
```

### 📚 Documentação Completa

Para configuração detalhada, consulte [WHATSAPP_GUIA_TEMPLATES.md](WHATSAPP_GUIA_TEMPLATES.md)

Tópicos cobertos:
- Como encontrar seu Template ID (GUID)
- Estrutura completa do payload
- Redirecionamento de fluxos e departamentos
- Ações por botão
- Troubleshooting
- Boas práticas de segurança

## Estrutura

```
regua_de_cobranca/
├── app.py                                  # Aplicação principal (Streamlit)
├── whatsapp_integration.py                 # Módulo de integração WhatsApp
├── whatsapp_sender.py                      # Interface de envio (Streamlit)
├── exemplo_uso_whatsapp.py                 # Exemplos de código
├── requirements.txt                        # Dependências do projeto
├── .env.example                            # Configurações de exemplo
├── WHATSAPP_INTEGRATION_GUIDE.md           # Guia completo de integração
└── README.md                               # Documentação (este arquivo)
```

### Arquivos principais

- **app.py** - Aplicação principal:
  - Configuração da página Streamlit
  - Funções de cálculo de vencimento
  - Funções de filtro por vencimento e status
  - Interface para gerar planilhas

- **whatsapp_integration.py** - Módulo WhatsApp:
  - Classe `WhatsAppClient` para comunicação com API
  - Funções de validação e formatação de telefones
  - Função `create_cobranca_message()` para gerar mensagens

- **whatsapp_sender.py** - Interface de envio:
  - Página Streamlit dedicada ao envio
  - Visualização de mensagens antes do envio
  - Relatório detalhado de resultados
  - Histórico e configurações

- **exemplo_uso_whatsapp.py** - Exemplos práticos:
  - 5 exemplos de utilização
  - Teste de conexão
  - Envio simples e em lote
  - Carregamento de planilhas

## Melhorias futuras

- [x] ✅ Integração com API do WhatsApp Business (Azure)
- [ ] Dashboard com estatísticas de cobrança
- [ ] Sistema de autenticação para múltiplos usuários
- [ ] Histórico de operações realizadas em banco de dados
- [ ] Exportação em outros formatos (PDF, JSON)
- [ ] Importação de dados via banco de dados (SQL/MySQL)
- [ ] Relatórios com métricas de eficiência
- [ ] Integração com sistema de pagamento
- [ ] Notificações por e-mail
- [ ] Suporte a templates personalizados de WhatsApp

## Aprendizados

- **Streamlit** é excelente para prototipação rápida de aplicações de dados
- Tratamento adequado de datas em diferentes formatos é essencial em aplicações de processamento de dados
- A validação de dados no upload previne muitos problemas posteriores
- Interface simples e intuitiva melhora significativamente a experiência do usuário
- Usar pandas para manipulação de dados em memória é eficiente para datasets moderados

---

**Desenvolvido com ❤️ para facilitar a gestão de cobranças**

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

## Tecnologias

- **Python 3.8+** - Linguagem de programação
- **Streamlit** - Framework para criação de aplicações web
- **Pandas** - Manipulação e análise de dados
- **OpenPyXL** - Trabalho com arquivos Excel

## Como executar

### Pré-requisitos
- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Azevedo573/regua_de_cobranca.git
cd regua_de_cobranca
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   - **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar a aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`

## Estrutura

```
regua_de_cobranca/
├── app.py              # Arquivo principal da aplicação Streamlit
├── requirements.txt    # Dependências do projeto
└── README.md          # Documentação
```

### Arquivos principais

- **app.py** - Contém toda a lógica da aplicação, incluindo:
  - Configuração da página Streamlit
  - Funções de cálculo de vencimento
  - Funções de filtro por vencimento e status
  - Interface do usuário

## Melhorias futuras

- [ ] Integração direta com API do WhatsApp Business
- [ ] Dashboard com estatísticas de cobrança
- [ ] Sistema de autenticação para múltiplos usuários
- [ ] Histórico de operações realizadas
- [ ] Exportação em outros formatos (PDF, JSON)
- [ ] Importação de dados via banco de dados
- [ ] Relatórios com métricas de eficiência
- [ ] Relatorio de analise de Faturamento da empresa

## Aprendizados

- **Streamlit** é excelente para prototipação rápida de aplicações de dados
- Tratamento adequado de datas em diferentes formatos é essencial em aplicações de processamento de dados
- A validação de dados no upload previne muitos problemas posteriores
- Interface simples e intuitiva melhora significativamente a experiência do usuário
- Usar pandas para manipulação de dados em memória é eficiente para datasets moderados

---

**Desenvolvido com ❤️ para facilitar a gestão de cobranças**

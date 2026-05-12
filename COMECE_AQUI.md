# 🚀 COMECE AQUI - VERSÃO SIMPLIFICADA

Tudo que você precisa para fazer funcionar em **3 minutos**.

---

## ✅ O que foi criado

Agora o sistema é **super simples**:

1. **whatsapp_simples.py** - Cliente WhatsApp básico
2. **app.py** - Aplicação Streamlit com 1 botão "📤 Disparar"  
3. **.env** - Arquivo de configuração (copie de .env.example)

---

## 🔧 Passo 1: Configurar (1 min)

Copie o arquivo de configuração:

```bash
cp .env.example .env
```

Depois **EDITE o arquivo `.env`** com seus dados:

```
WHATSAPP_API_URL=https://seu-servidor.azurewebsites.net
WHATSAPP_AUTH_TOKEN=seu_token_aqui
WHATSAPP_TEMPLATE_COBRANCA=seu_template_id
```

---

## 🧪 Passo 2: Testar Conexão (1 min)

```bash
python -c "
from whatsapp_simples import WhatsAppClientSimples
from dotenv import load_dotenv
import os

load_dotenv()
client = WhatsAppClientSimples(
    api_url=os.getenv('WHATSAPP_API_URL'),
    auth_token=os.getenv('WHATSAPP_AUTH_TOKEN')
)
ok, msg = client.testar_conexao()
print('✅ FUNCIONANDO!' if ok else f'❌ {msg}')
"
```

Se aparecer `✅ FUNCIONANDO!`, você está pronto!

---

## 🎯 Passo 3: Usar a Aplicação (1 min)

```bash
streamlit run app.py
```

Vai abrir em: `http://localhost:8501`

**Fluxo:**
1. Selecione sua planilha Excel (Digital Saúde)
2. Sistema filtra automaticamente por período de vencimento
3. Para cada período, aparece um botão **📤 Disparar no WhatsApp**
4. Clique nele para enviar

---

## 📱 Exemplo Prático

**Sua planilha tem:**

| Celular      | Nome Titular | Valor Cobrança | Data de Vencimento |
|------------|-------------|---|---|
| 21981088659 | João Silva | 150,00 | 2026-04-15 |
| 85987654321 | Maria Santos | 200,00 | 2026-04-10 |

**O sistema:**

1. ✅ Formata os números: `5521981088659`, `5585987654321`
2. ✅ Filtra por período (ex: "4-7 dias de atraso")
3. ✅ Cria um botão "📤 Disparar 2 no WhatsApp"
4. ✅ Envia para todos com a template

---

## 🔑 Pontos Importantes

### ✅ Números são automaticamente formatados

Você pode colocar na planilha assim:
- `21981088659` ✅ funciona
- `21 98108-8659` ✅ funciona  
- `5521981088659` ✅ funciona
- `+55 21 98108-8659` ✅ funciona

Sistema **sempre** padroniza para: `55+ddd+numero`

### ✅ 1 Template = Simples

Por enquanto usamos apenas `WHATSAPP_TEMPLATE_COBRANCA`.

Quer mais templates depois? Fácil adicionar!

### ✅ Modo Simulação

Na sidebar tem um checkbox `🧪 Modo Simulação`.

Ativa ele antes de testar para **não enviar de verdade**.

---

## 📊 Estrutura da Planilha

Colunas **obrigatórias:**
- `Data de Vencimento` (yyyy-mm-dd ou dd/mm/yyyy)
- `Celular` (qualquer formato de telefone)
- `Nome Titular` (nome do cliente)

Colunas **opcionais:**
- `Valor Cobrança`
- `Status da Fatura`
- Qualquer outra coluna

---

## ❓ Dúvidas Rápidas

### "Onde copio o WHATSAPP_TEMPLATE_COBRANCA?"

Acesse seu Portal WhatsApp:
1. Templates/Mensagens
2. Encontre sua template de cobrança
3. Copie o ID (ex: `cb71990515:template:141744687`)
4. Cole em `.env`

### "Como faço para enviar para muita gente?"

Sistema envia em **lote**. Quanto maior a lista, melhor!

Se tiver 1000 contatos, envia para todos de uma vez.

### "E se uma mensagem falhar?"

No resultado final aparece:
- Total enviado
- Quantas funcionaram
- Lista de números que falharam

Pode reenviar só pra esses.

### "Como testo sem gastar?"

Use `🧪 Modo Simulação` na sidebar. Simula tudo sem enviar.

---

## 🐛 Se Tiver Erro

### ❌ "Coluna 'Celular' não encontrada"

Sua planilha não tem coluna "Celular".

**Opções:**
- Adicione coluna "Celular" na planilha
- Ou mude o nome da coluna de telefone para "Celular"

### ❌ "HTTP 401 - Unauthorized"

Token inválido.

**Solução:**
1. Copie token novamente do Portal
2. Remova espaços em branco
3. Cole em `.env`
4. Reinicie streamlit

### ❌ "API não conectada"

URL ou token errados.

**Verifique:**
```
WHATSAPP_API_URL=https://seu-servidor.azurewebsites.net
```

⚠️ NÃO deixe barra `/` no final!

---

## 📚 Arquivo de Exemplo

Se quiser entender melhor o código:

```python
from whatsapp_simples import WhatsAppClientSimples
import os
from dotenv import load_dotenv

load_dotenv()

# Criar cliente
client = WhatsAppClientSimples(
    api_url=os.getenv('WHATSAPP_API_URL'),
    auth_token=os.getenv('WHATSAPP_AUTH_TOKEN')
)

# Enviar para 1 pessoa
ok, msg = client.enviar_mensagem(
    nome="João",
    telefone="21981088659",  # Qualquer formato!
    template_id=os.getenv('WHATSAPP_TEMPLATE_COBRANCA'),
    parametros=["João", "150,00", "15/05"],
    simular=True  # Mude para False para enviar de verdade
)

print(msg)

# Enviar para vários
contatos = [
    {"nome": "João", "telefone": "21981088659"},
    {"nome": "Maria", "telefone": "85987654321"},
]

resultado = client.enviar_lote(
    contatos=contatos,
    template_id=os.getenv('WHATSAPP_TEMPLATE_COBRANCA'),
    simular=True
)

print(f"Enviadas: {resultado['sucesso']}/{resultado['total']}")
```

---

## 🎉 Próximos Passos

1. ✅ Configure `.env`
2. ✅ Teste com `python -c "..."`
3. ✅ Rode `streamlit run app.py`
4. ✅ Faça upload da planilha
5. ✅ Clique em "📤 Disparar"

**Pronto! Você tem um sistema de cobrança WhatsApp funcionando!**

---

## 💡 Depois (Se Quiser Expandir)

Quer adicionar mais features?

- Mais de 1 template? Pode fazer.
- Agenda de envios? Pode fazer.
- Integração com BD? Pode fazer.

Mas por enquanto, **mantenha simples** e faça funcionar primeiro!

---

**Boa sorte! 🚀**

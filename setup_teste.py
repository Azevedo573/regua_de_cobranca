#!/usr/bin/env python3
"""
ROTEIRO PRÁTICO - Como testar o fluxo completo local
=====================================================

Execute este arquivo para:
1. Criar planilha de teste
2. Validar configuração do .env
3. Executar app.py

Uso:
    python setup_teste.py
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

def criar_planilha_teste():
    """Cria planilha de teste com dados realistas"""
    
    print("\n" + "="*60)
    print("📊 CRIANDO PLANILHA DE TESTE")
    print("="*60)
    
    # Data de hoje
    hoje = datetime(2026, 5, 11)
    
    # Cria dados de teste realistas
    dados = {
        'Celular': [
            '11999999999',
            '21988888888',
            '85987777777',
            '47986666666',
            '11955555555',
            '31933333333',
            '81922222222',
            '41911111111',
            '51944444444',
            '61955555555'
        ],
        'Nome Titular': [
            'João da Silva',
            'Maria Santos',
            'Pedro Costa',
            'Ana Oliveira',
            'Carlos Souza',
            'Beatriz Lima',
            'Diego Martins',
            'Fernanda Rocha',
            'Gabriel Neves',
            'Helena Barbosa'
        ],
        'Operadora da Fatura': [
            'Operadora A',
            'Operadora B',
            'Operadora C',
            'Operadora A',
            'Operadora B',
            'Operadora C',
            'Operadora A',
            'Operadora B',
            'Operadora C',
            'Operadora A'
        ],
        'Data de Vencimento': [
            hoje - timedelta(days=6),    # 6 dias de atraso
            hoje - timedelta(days=31),   # 31 dias de atraso
            hoje - timedelta(days=71),   # 71 dias de atraso
            hoje,                         # Vence hoje
            hoje - timedelta(days=11),   # 11 dias de atraso
            hoje - timedelta(days=2),    # 2 dias de atraso
            hoje - timedelta(days=45),   # 45 dias de atraso
            hoje + timedelta(days=5),    # 5 dias a vencer
            hoje - timedelta(days=88),   # 88 dias de atraso
            hoje - timedelta(days=3),    # 3 dias de atraso
        ],
        'Valor Cobrança': [
            150.00,
            200.00,
            250.00,
            180.00,
            220.00,
            195.00,
            300.00,
            125.00,
            280.00,
            165.00
        ],
        'Status da Fatura': [
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida',
            'Emitida'
        ]
    }
    
    df = pd.DataFrame(dados)
    
    # Salva planilha
    arquivo = 'teste_digital_saude.xlsx'
    df.to_excel(arquivo, index=False)
    
    print(f"✅ Planilha criada: {arquivo}")
    print(f"\n📋 Amostra dos dados:")
    print(df.to_string(index=False))
    
    print(f"\n📊 Estatísticas:")
    print(f"  • Total de registros: {len(df)}")
    print(f"  • Valor total: R$ {df['Valor Cobrança'].sum():,.2f}")
    print(f"  • Com Celular: {df['Celular'].notna().sum()}")
    
    return arquivo

def validar_env():
    """Valida arquivo .env"""
    
    print("\n" + "="*60)
    print("🔐 VALIDANDO ARQUIVO .env")
    print("="*60)
    
    from dotenv import load_dotenv
    
    # Carrega .env
    load_dotenv()
    
    # Variáveis obrigatórias
    obrigatorias = ['WHATSAPP_API_URL', 'WHATSAPP_AUTH_TOKEN']
    
    config = {}
    
    for var in obrigatorias:
        valor = os.getenv(var)
        if valor:
            # Mascarar valor por segurança
            if var == 'WHATSAPP_AUTH_TOKEN':
                valor_display = f"{valor[:10]}...{valor[-10:]}" if len(valor) > 20 else "***"
            else:
                valor_display = valor
            
            print(f"✅ {var}")
            print(f"   └─ {valor_display}")
            config[var] = valor
        else:
            print(f"❌ {var} - NÃO CONFIGURADO")
    
    # Variáveis de templates
    print(f"\n📋 Templates configuradas:")
    templates = {}
    for key, value in os.environ.items():
        if key.startswith('WHATSAPP_TEMPLATE_'):
            template_name = key.replace('WHATSAPP_TEMPLATE_', '').lower()
            templates[template_name] = value
            print(f"  ✅ {template_name}: {value[:10]}...{value[-10:]}")
    
    if not templates:
        print("  ⚠️  Nenhuma template configurada")
    
    config['templates'] = templates
    
    return config

def testar_conexao(config):
    """Testa conexão com API WhatsApp"""
    
    print("\n" + "="*60)
    print("📡 TESTANDO CONEXÃO COM API")
    print("="*60)
    
    try:
        from whatsapp_integration_v2 import WhatsAppClient
        
        client = WhatsAppClient(
            api_url=config['WHATSAPP_API_URL'],
            auth_token=config['WHATSAPP_AUTH_TOKEN']
        )
        
        print("🔄 Testando conexão...")
        success, msg = client.test_connection()
        
        if success:
            print(f"✅ {msg}")
            return True
        else:
            print(f"❌ {msg}")
            print("\n💡 Dicas:")
            print("  • Verifique se WHATSAPP_API_URL está correto")
            print("  • Verifique se WHATSAPP_AUTH_TOKEN está válido")
            print("  • Verifique conectividade com a API")
            return False
    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def exibir_proximos_passos():
    """Exibe próximos passos"""
    
    print("\n" + "="*60)
    print("🚀 PRÓXIMOS PASSOS")
    print("="*60)
    
    print("""
1️⃣  EXECUTE A APLICAÇÃO:
    streamlit run app.py

2️⃣  ABRA NO NAVEGADOR:
    http://localhost:8501

3️⃣  FAÇA UPLOAD:
    • Clique em "📤 Arraste ou selecione a planilha"
    • Selecione o arquivo: teste_digital_saude.xlsx

4️⃣  VEJA OS RESULTADOS:
    • O sistema processará automaticamente
    • Você verá 12 planilhas filtradas por período

5️⃣  TESTE O DISPARO WhatsApp:
    • Expanda uma planilha (ex: "4-7 dias de atraso")
    • Clique em "📤 Disparar no WhatsApp"
    • Escolha a template
    • Ative "🧪 Modo Simulação" para teste
    • Clique em "✅ Enviar WhatsApp"

6️⃣  VEJA O RESULTADO:
    • Taxa de sucesso/falha
    • Lista de contatos processados
    
    """)
    
    print("="*60)
    print("💡 DICAS IMPORTANTES")
    print("="*60)
    
    print("""
• 🧪 Use modo simulação primeiro (não envia de verdade)
• 📝 Verifique a planilha de teste criada
• 📱 Confirme que os números têm formato válido
• 🔐 Nunca commite .env no git
• 📊 Salve as planilhas geradas para referência
• 🔄 Teste diferentes templates
    """)

def main():
    """Função principal"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "SETUP - TESTE LOCAL" + " "*26 + "║")
    print("║" + " "*14 + "Régua de Cobrança com WhatsApp" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # Passo 1: Criar planilha de teste
        arquivo_teste = criar_planilha_teste()
        
        # Passo 2: Validar .env
        config = validar_env()
        
        # Passo 3: Testar conexão (se tiver configuração)
        if config.get('WHATSAPP_API_URL') and config.get('WHATSAPP_AUTH_TOKEN'):
            conexao_ok = testar_conexao(config)
        else:
            print("\n⚠️  Configure .env antes de continuar")
            print("\nInstruções:")
            print("  1. Copie .env.example para .env")
            print("  2. Edite o arquivo com seus dados")
            print("  3. Execute este script novamente")
            conexao_ok = False
        
        # Passo 4: Próximos passos
        exibir_proximos_passos()
        
        # Resume
        print("\n" + "="*60)
        print("✅ SETUP CONCLUÍDO COM SUCESSO")
        print("="*60)
        print(f"\n✨ Você está pronto para:")
        print(f"  1. Processar planilhas de faturamento")
        print(f"  2. Enviar cobrança via WhatsApp")
        print(f"  3. Acompanhar taxa de sucesso")
        
        if not conexao_ok:
            print(f"\n⚠️  Nota: Conectividade WhatsApp ainda não validada")
            print(f"  Mas você pode testar com MODO SIMULAÇÃO")
        
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante setup: {str(e)}")
        print("\nTroubleshooting:")
        print("  • Verifique se está na pasta correta")
        print("  • Verifique se todas as dependências foram instaladas")
        print("  • Verifique o arquivo .env.example")
        sys.exit(1)

if __name__ == "__main__":
    main()

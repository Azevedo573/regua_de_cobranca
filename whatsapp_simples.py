"""
Cliente WhatsApp Simplificado
Baseado no payload real que funcionou
"""

import requests
import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppClientSimples:
    """
    Cliente WhatsApp simples e direto.
    
    Uso:
        client = WhatsAppClientSimples(
            api_url="https://...",
            auth_token="seu_token"
        )
        
        # Enviar para um contato
        sucesso = client.enviar_mensagem(
            nome="João",
            telefone="21981088659",
            template_id="1450739389691884",
            parametros=["João", "150,00", "15/05"]
        )
    """
    
    def __init__(self, api_url: str, auth_token: str):
        """
        Args:
            api_url: URL da API (ex: https://seu-servidor.azurewebsites.net)
            auth_token: Token de autenticação
        """
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.endpoint = f"{self.api_url}/api/messages/send"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
        
        # ============================================================================
        # TEMPLATES POR PERÍODO
        # ============================================================================
        self.templates_por_periodo = {
            # ANTECIPADO - Encoraja adiantamento do pagamento
            "antecipado": {
                "id": "1270161388521434",
                "parametros_exemplo": ["Nome", "Operadora"],
                "response_action": {
                    "type": 1,
                    "buttonActions": {
                        "Quero o Pix": {"type": 1, "sendTo": "cb137546442"},
                        "Quero Agendar": {"type": 0, "sendTo": "cb72270374"}
                    }
                }
            },
            # A VENCER - Lembrança gentil sobre vencimento
            "a_vencer": {
                "id": "1270161388521434",
                "parametros_exemplo": ["Nome", "Operadora"],
                "response_action": {
                    "type": 1,
                    "buttonActions": {
                        "Quero o Pix": {"type": 1, "sendTo": "cb137546442"},
                        "Quero Agendar": {"type": 0, "sendTo": "cb72270374"}
                    }
                }
            },
            # ATRASO LEVE (1-7 dias) - Aviso educado
            "atraso_leve": {
                "id": "1450739389691884",
                "parametros_exemplo": ["Nome", "Operadora", "Data"],
                "response_action": {
                    "type": 1,
                    "buttonActions": {
                        "Pagar Agora": {"type": 1, "sendTo": "cb137546442"},
                        "Boleto": {"type": 0, "sendTo": "cb72270374"}
                    }
                }
            },
            # ATRASO MODERADO (8-30 dias) - Cobrança séria
            "atraso_moderado": {
                "id": "1450739389691884",
                "parametros_exemplo": ["Nome", "Operadora", "Valor"],
                "response_action": {
                    "type": 1,
                    "buttonActions": {
                        "Quero Regularizar": {"type": 1, "sendTo": "cb137546442"},
                        "Pedir Prorrogação": {"type": 0, "sendTo": "cb72270374"}
                    }
                }
            },
            # ATRASO SEVERO (31+ dias) - Aviso final
            "atraso_severo": {
                "id": "1450739389691884",
                "parametros_exemplo": ["Nome", "Operadora", "Valor"],
                "response_action": {
                    "type": 1,
                    "buttonActions": {
                        "Regularizar Débito": {"type": 1, "sendTo": "cb137546442"},
                        "Atendimento": {"type": 0, "sendTo": "cb72270374"}
                    }
                }
            }
        }
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """
        Formata telefone para 55 + ddd + numero
        
        Exemplos:
            "21981088659" -> "5521981088659"
            "5521981088659" -> "5521981088659"
            "+55 21 98108-8659" -> "5521981088659"
        """
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in telefone if c.isdigit())
        
        # Se já começa com 55, retorna como está
        if apenas_numeros.startswith('55'):
            return apenas_numeros
        
        # Senão, adiciona 55 no início
        return '55' + apenas_numeros
    
    def obter_tipo_periodo(self, nome_periodo: str) -> str:
        """
        Mapeia o nome do período para o tipo de template.
        
        Exemplos:
            "Cobrança Antecipada - 5 dias" -> "antecipado"
            "1-3 dias de atraso" -> "atraso_leve"
            "31-60 dias de atraso" -> "atraso_severo"
        
        Returns:
            Tipo de template ("antecipado", "a_vencer", "atraso_leve", etc)
        """
        nome_lower = nome_periodo.lower()
        
        # ANTECIPADO
        if "antecipada" in nome_lower:
            return "antecipado"
        
        # A VENCER
        if "a vencer" in nome_lower or "até hoje" in nome_lower:
            return "a_vencer"
        
        # ATRASO LEVE (1-7 dias)
        if any(x in nome_lower for x in ["1-3 dias", "4-7 dias"]):
            return "atraso_leve"
        
        # ATRASO MODERADO (8-30 dias)
        if any(x in nome_lower for x in ["8-14 dias", "15-30 dias"]):
            return "atraso_moderado"
        
        # ATRASO SEVERO (31+ dias)
        if any(x in nome_lower for x in ["31-60 dias", "61-90 dias", "> 90 dias"]):
            return "atraso_severo"
        
        # DEFAULT: a_vencer
        return "a_vencer"
    
    def obter_template_por_periodo(self, nome_periodo: str) -> Dict:
        """
        Retorna a configuração de template para o período.
        
        Returns:
            {
                "id": "1450739389691884",
                "parametros_exemplo": ["Nome", "Operadora", "Data"],
                "response_action": {...}
            }
        """
        tipo = self.obter_tipo_periodo(nome_periodo)
        return self.templates_por_periodo.get(tipo, self.templates_por_periodo["a_vencer"])
    
    def criar_payload(
        self,
        nome: str,
        telefone: str,
        template_id: str,
        parametros: List[str] = None,
        responseAction: Dict = None
    ) -> Dict:
        """
        Cria payload com suporte a múltiplos tipos de templates.
        
        Args:
            nome: Nome do contato
            telefone: Telefone do contato
            template_id: ID da template
            parametros: Lista de parâmetros da template
            response_action: Dict opcional com actions customizadas (botões, fluxos, etc)
        
        Returns:
            Dict com o payload completo
        """
        if parametros is None:
            parametros = []
        
        payload = {
            "user": {
                "name": nome,
                "phone": self.formatar_telefone(telefone),
                "email": None,
                "gender": 0,
                "channelId": "wp661873710340994",
                "channelType": 1,
                "defaultDepartmentId": None
            },
            "message": {
                "templateId": template_id,
                "BodyParameters": parametros,
                "ButtonsParameters": []
            },
            "responseAction": {
                "type": 1,
                "sendTo": "cb74358605",
                "buttonActions": {
                    "Quero o Pix!": {
                        "type": 1,
                        "sendTo": "cb137546442"
                    },
                    "Quero Agendar": {
                        "type": 0,
                        "sendTo": "cb72270374"
                    }
        }
    }
}
        
        # Adiciona responseAction se fornecida
        if responseAction:
            payload["responseAction"] = responseAction
        
        return payload
    
    def criar_payload_vencer_hoje(
        self,
        nome: str,
        telefone: str,
        parametros: List[str] = None
    ) -> Dict:
        """
        Payload específico para template "A vencer (hoje)"
        Template ID: 1450739389691884
        Com botões para Pix e Agendamento
        """
        response_action = {
            "type": 1,
            "sendTo": "<Id do fluxo>",
            "buttonActions": {
                "Quero o Pix!": {
                    "type": 1,
                    "sendTo": "cb137546442"
                },
                "Quero Agendar": {
                    "type": 0,
                    "sendTo": "cb72270374"
                }
            }
        }
        
        return self.criar_payload(
            nome=nome,
            telefone=telefone,
            template_id="1450739389691884",
            parametros=parametros,
            response_action=response_action
        )
    
    def enviar_mensagem(
        self,
        nome: str,
        telefone: str,
        template_id: str,
        parametros: List[str] = None,
        simular: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Envia uma mensagem WhatsApp.
        
        Args:
            nome: Nome do contato
            telefone: Telefone (qualquer formato, será normalizado)
            template_id: ID da template (ex: 1450739389691884)
            parametros: Lista de parâmetros para a template
            simular: Se True, não envia de verdade (apenas simula)
        
        Returns:
            (sucesso: bool, mensagem: str, wamid: str)
        """
        if parametros is None:
            parametros = [] 
        
        payload = self.criar_payload(nome, telefone, template_id, parametros)

        # LOG DO PAYLOAD
         
        logger.info(
            json.dumps(payload, indent=2, ensure_ascii=False)
            )
        
        if simular:
            logger.info(f"[SIMULAÇÃO] Enviaria para {nome} ({payload['user']['phone']})")
            return True, f"✅ Simulado: {nome}", "simulado"
        
        try:
            logger.info(f"Enviando para {nome} ({payload['user']['phone']})")
            response = self.session.post(self.endpoint, json=payload, timeout=10)
            
            # Tenta fazer parse JSON
            try:
                resposta_json = response.json()
            except:
                resposta_json = {}
            
            if response.status_code == 200:
                # Verifica se success=true na resposta
                sucesso = resposta_json.get('success', False)
                wamid = resposta_json.get('data', '')
                erro = resposta_json.get('error')
                
                if sucesso and not erro:
                    logger.info(f"✅ Enviada para {nome} (WAMID: {wamid})")
                    return True, f"✅ {nome}", wamid
                else:
                    # Success=200 mas API retornou erro
                    mensagem_erro = erro or "Erro desconhecido"
                    logger.error(f"❌ API retornou erro para {nome}: {mensagem_erro}")
                    return False, f"❌ {nome}: {mensagem_erro}", ""
            else:
                # HTTP status != 200
                erro = resposta_json.get('error', response.text)
                logger.error(f"❌ HTTP {response.status_code} para {nome}: {erro}")
                return False, f"❌ {nome}: HTTP {response.status_code}", ""
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout: {nome}")
            return False, f"⏱️ {nome}: Timeout", ""
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False, f"❌ {nome}: {str(e)}", ""
    
    def enviar_mensagem_por_periodo(
        self,
        nome: str,
        telefone: str,
        periodo: str,
        parametros: List[str] = None,
        simular: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Envia mensagem com template automático baseado no período.
        
        Args:
            nome: Nome do contato
            telefone: Telefone do contato
            periodo: Nome do período (ex: "1-3 dias de atraso", "A vencer (Até hoje)")
            parametros: Lista de parâmetros para a template
            simular: Se True, não envia de verdade
        
        Returns:
            (sucesso: bool, mensagem: str, wamid: str)
        
        Exemplo:
            ok, msg, wamid = client.enviar_mensagem_por_periodo(
                nome="João",
                telefone="21981088659",
                periodo="1-3 dias de atraso",
                parametros=["João", "Operadora X", "150,00"]
            )
        """
        # Obtém template para este período
        config_template = self.obter_template_por_periodo(periodo)
        template_id = config_template['id']
        response_action = config_template.get('response_action')
        
        # Cria payload com response_action customizado
        if parametros is None:
            parametros = []
        
        payload = self.criar_payload(
            nome=nome,
            telefone=telefone,
            template_id=template_id,
            parametros=parametros,
            responseAction=response_action
        )
        
        logger.info(f"📨 Enviando para {nome} ({periodo}) - {response_action}")
        
        if simular:
            logger.info(f"[SIMULAÇÃO] {nome} ({periodo})")
            return True, f"✅ Simulado: {nome}", "simulado"
        
        try:
            response = self.session.post(self.endpoint, json=payload, timeout=10)
            
            try:
                resposta_json = response.json()
            except:
                resposta_json = {}
            
            if response.status_code == 200:
                sucesso = resposta_json.get('success', False)
                wamid = resposta_json.get('data', '')
                erro = resposta_json.get('error')
                
                if sucesso and not erro:
                    logger.info(f"✅ {nome} ({periodo})")
                    return True, f"✅ {nome}", wamid
                else:
                    mensagem_erro = erro or "Erro desconhecido"
                    logger.error(f"❌ {nome}: {mensagem_erro}")
                    return False, f"❌ {nome}: {mensagem_erro}", ""
            else:
                erro = resposta_json.get('error', response.text)
                logger.error(f"❌ HTTP {response.status_code}: {erro}")
                return False, f"❌ {nome}: HTTP {response.status_code}", ""
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout: {nome}")
            return False, f"⏱️ {nome}: Timeout", ""
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return False, f"❌ {nome}: {str(e)}", ""
    
    def enviar_lote(
        self,
        contatos: List[Dict],
        template_id: str,
        funcao_parametros=None,
        simular: bool = False,
        intervalo: float = 0.5
    ) -> Dict:
        """
        Envia mensagens em lote.
        
        Args:
            contatos: Lista de dicts com "nome" e "telefone"
            template_id: ID da template
            funcao_parametros: Função que recebe contato e retorna lista de parametros
            simular: Se True, não envia de verdade
            intervalo: Segundos entre envios
        
        Returns:
            {
                "total": int,
                "sucesso": int,
                "erro": int,
                "taxa_sucesso": str,
                "resultados": [{"nome": str, "telefone": str, "sucesso": bool, "mensagem": str, "wamid": str}]
            }
        """
        import time
        
        resultados = []
        sucesso = 0
        erro = 0
        
        for i, contato in enumerate(contatos):
            nome = contato.get('nome', 'N/A')
            telefone = contato.get('telefone', '')
            
            # Se forneceu função para gerar parâmetros, usa
            parametros = []
            if funcao_parametros:
                parametros = funcao_parametros(contato)
            
            ok, msg, wamid = self.enviar_mensagem(
                nome=nome,
                telefone=telefone,
                template_id=template_id,
                parametros=parametros,
                simular=simular
            )
            
            if ok:
                sucesso += 1
            else:
                erro += 1
            
            resultados.append({
                "nome": nome,
                "telefone": self.formatar_telefone(telefone),
                "sucesso": ok,
                "mensagem": msg,
                "wamid": wamid
            })
            
            # Aguarda intervalo entre envios
            if i < len(contatos) - 1:
                time.sleep(intervalo)
        
        return {
            "total": len(contatos),
            "sucesso": sucesso,
            "erro": erro,
            "taxa_sucesso": f"{(sucesso/len(contatos)*100):.1f}%" if contatos else "0%",
            "resultados": resultados
        }
    
    def enviar_lote_por_periodo(
        self,
        contatos: List[Dict],
        periodo: str,
        funcao_parametros=None,
        simular: bool = False,
        intervalo: float = 0.5
    ) -> Dict:
        """
        Envia mensagens em lote com template automático por período.
        
        Args:
            contatos: Lista de dicts com "nome" e "telefone"
            periodo: Nome do período (ex: "1-3 dias de atraso", "A vencer (Até hoje)")
            funcao_parametros: Função que recebe contato e retorna lista de parametros
            simular: Se True, não envia de verdade
            intervalo: Segundos entre envios
        
        Returns:
            {
                "total": int,
                "sucesso": int,
                "erro": int,
                "taxa_sucesso": str,
                "periodo": str,
                "tipo_template": str,
                "resultados": [...]
            }
        
        Exemplo:
            resultado = client.enviar_lote_por_periodo(
                contatos=contatos,
                periodo="1-3 dias de atraso",
                funcao_parametros=lambda c: [c['nome'], c['operadora'], c['valor']]
            )
        """
        import time
        
        resultados = []
        sucesso = 0
        erro = 0
        tipo_template = self.obter_tipo_periodo(periodo)
        
        for i, contato in enumerate(contatos):
            nome = contato.get('nome', 'N/A')
            telefone = contato.get('telefone', '')
            
            # Se forneceu função para gerar parâmetros, usa
            parametros = []
            if funcao_parametros:
                parametros = funcao_parametros(contato)
            
            ok, msg, wamid = self.enviar_mensagem_por_periodo(
                nome=nome,
                telefone=telefone,
                periodo=periodo,
                parametros=parametros,
                simular=simular
            )
            
            if ok:
                sucesso += 1
            else:
                erro += 1
            
            resultados.append({
                "nome": nome,
                "telefone": self.formatar_telefone(telefone),
                "sucesso": ok,
                "mensagem": msg,
                "wamid": wamid,
                "periodo": periodo,
                "tipo": tipo_template
            })
            
            # Aguarda intervalo entre envios
            if i < len(contatos) - 1:
                time.sleep(intervalo)
        
        return {
            "total": len(contatos),
            "sucesso": sucesso,
            "erro": erro,
            "taxa_sucesso": f"{(sucesso/len(contatos)*100):.1f}%" if contatos else "0%",
            "periodo": periodo,
            "tipo_template": tipo_template,
            "resultados": resultados
        }
    
    def testar_conexao(self) -> Tuple[bool, str]:
        """Testa se a API está acessível"""
        try:
            payload = self.criar_payload("Teste", "5521981088659", "teste", [])
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=5
            )
            
            if response.status_code in [200, 400]:  # 200=ok, 400=template inválida (mas conexão ok)
                return True, "✅ Conectado com sucesso"
            else:
                return False, f"❌ Status {response.status_code}"
        
        except Exception as e:
            return False, f"❌ Erro: {str(e)}"
    
    def listar_templates(self) -> Dict:
        """
        Lista todos os templates disponíveis com suas configurações.
        
        Returns:
            Dict com tipos de template e seus detalhes
        """
        templates_info = {}
        for tipo, config in self.templates_por_periodo.items():
            templates_info[tipo] = {
                "id": config['id'],
                "parametros_exemplo": config['parametros_exemplo'],
                "botoes": list(config['response_action']['buttonActions'].keys())
            }
        return templates_info


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Configuração
    api_url = os.getenv('WHATSAPP_API_URL')
    auth_token = os.getenv('WHATSAPP_AUTH_TOKEN')
    template_id = os.getenv('WHATSAPP_TEMPLATE_COBRANCA')
    
    if not all([api_url, auth_token, template_id]):
        print("❌ Configure .env com:")
        print("   WHATSAPP_API_URL=...")
        print("   WHATSAPP_AUTH_TOKEN=...")
        print("   WHATSAPP_TEMPLATE_COBRANCA=...")
        exit(1)
    
    # Criar cliente
    client = WhatsAppClientSimples(api_url, auth_token)
    
    # Testar conexão
    print("\n🔗 Testando conexão...")
    ok, msg = client.testar_conexao()
    print(msg)
    
    if not ok:
        exit(1)
    
    # Exemplo 1: Enviar para uma pessoa
    print("\n📱 Enviando para 1 contato...")
    ok, msg = client.enviar_mensagem(
        nome="João Silva",
        telefone="21981088659",  # Pode ser qualquer formato
        template_id=template_id,
        parametros=["João", "150,00", "15/05"],
        simular=True  # Mude para False para enviar de verdade
    )
    print(msg)
    
    # Exemplo 2: Enviar para várias pessoas
    print("\n📋 Enviando para lote...")
    contatos = [
        {"nome": "João Silva", "telefone": "21981088659"},
        {"nome": "Maria Santos", "telefone": "85987654321"},
        {"nome": "Pedro Costa", "telefone": "5511999999999"},
    ]
    
    # Função que extrai parâmetros de cada contato
    def extrair_params(contato):
        return [contato['nome'], "150,00", "15/05"]
    
    resultado = client.enviar_lote(
        contatos=contatos,
        template_id=template_id,
        funcao_parametros=extrair_params,
        simular=True
    )
    
    print(f"✅ {resultado['sucesso']} enviadas")
    print(f"❌ {resultado['erro']} falhadas")
    print(f"📈 Taxa: {resultado['taxa_sucesso']}")
    
    # ========================================================================
    # NOVO: ENVIAR COM TEMPLATES AUTOMÁTICOS POR PERÍODO
    # ========================================================================
    
    print("\n" + "="*70)
    print("📋 TEMPLATES DISPONÍVEIS POR PERÍODO")
    print("="*70)
    
    templates = client.listar_templates()
    for tipo, config in templates.items():
        print(f"\n  {tipo.upper()}")
        print(f"    Template ID: {config['id']}")
        print(f"    Botões: {', '.join(config['botoes'])}")
        print(f"    Parâmetros: {', '.join(config['parametros_exemplo'])}")
    
    # ========================================================================
    # EXEMPLO 3: Enviar para 1 contato com template automático
    # ========================================================================
    
    print("\n\n📱 Enviando com template automático (atraso leve)...")
    ok, msg, wamid = client.enviar_mensagem_por_periodo(
        nome="João Silva",
        telefone="21981088659",
        periodo="1-3 dias de atraso",
        parametros=["João Silva", "Vivo", "R$ 150,00"],
        simular=True
    )
    print(f"  Resultado: {msg}")
    
    # ========================================================================
    # EXEMPLO 4: Enviar lote com templates automáticos por período
    # ========================================================================
    
    print("\n\n📋 Enviando LOTE com templates automáticos...")
    
    contatos_atraso = [
        {"nome": "João Silva", "telefone": "21981088659", "operadora": "Vivo", "valor": "150,00"},
        {"nome": "Maria Santos", "telefone": "85987654321", "operadora": "Claro", "valor": "200,00"},
    ]
    
    def extrair_params_atraso(contato):
        return [contato['nome'], contato['operadora'], contato['valor']]
    
    resultado = client.enviar_lote_por_periodo(
        contatos=contatos_atraso,
        periodo="1-3 dias de atraso",
        funcao_parametros=extrair_params_atraso,
        simular=True
    )
    
    print(f"\n  Período: {resultado['periodo']}")
    print(f"  Tipo Template: {resultado['tipo_template']}")
    print(f"  ✅ {resultado['sucesso']} enviadas")
    print(f"  ❌ {resultado['erro']} falhadas")
    print(f"  📈 Taxa: {resultado['taxa_sucesso']}")
    
    # ========================================================================
    # EXEMPLO 5: Testar diferentes períodos
    # ========================================================================
    
    print("\n\n🔄 Testando diferentes períodos...")
    
    periodos_teste = [
        "Cobrança Antecipada - 5 dias",
        "A vencer (Até hoje)",
        "1-3 dias de atraso",
        "31-60 dias de atraso"
    ]
    
    for periodo in periodos_teste:
        tipo = client.obter_tipo_periodo(periodo)
        config = client.obter_template_por_periodo(periodo)
        botoes = list(config['response_action']['buttonActions'].keys())
        
        print(f"\n  📄 {periodo}")
        print(f"     → Tipo: {tipo}")
        print(f"     → Botões: {', '.join(botoes)}")

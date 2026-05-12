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
            template_id="cb71990515:template:141744687",
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
    
    def criar_payload(
        self,
        nome: str,
        telefone: str,
        template_id: str,
        parametros: List[str] = None
    ) -> Dict:
        """
        Cria payload no formato exato que funcionou:
        
        {
            "user": {
                "name": "nome",
                "phone": "55dddnumero",
                "email": null,
                "gender": 0,
                "channelId": "wp...",
                "channelType": 1,
                "defaultDepartmentId": null
            },
            "message": {
                "templateId": "template_id",
                "BodyParameters": ["param1", "param2"],
                "ButtonsParameters": []
            }
        }
        """
        if parametros is None:
            parametros = []
        
        return {
            "user": {
                "name": nome,
                "phone": self.formatar_telefone(telefone),
                "email": None,
                "gender": 0,
                "channelId": "wp661873710340994",  # Pode ser dinâmico depois
                "channelType": 1,
                "defaultDepartmentId": None
            },
            "message": {
                "templateId": template_id,
                "BodyParameters": parametros,
                "ButtonsParameters": []
            }
        }
    
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
            template_id: ID da template (ex: cb71990515:template:141744687)
            parametros: Lista de parâmetros para a template
            simular: Se True, não envia de verdade (apenas simula)
        
        Returns:
            (sucesso: bool, mensagem: str, wamid: str)
        """
        if parametros is None:
            parametros = []
        
        payload = self.criar_payload(nome, telefone, template_id, parametros)
        
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
    
    resultado = client.enviar_lote(
        contatos=contatos,
        template_id=template_id,
        simular=True  # Mude para False para enviar de verdade
    )
    
    print(f"\n📊 Resultado:")
    print(f"   Total: {resultado['total']}")
    print(f"   Sucesso: {resultado['sucesso']}")
    print(f"   Erro: {resultado['erro']}")
    print(f"   Taxa: {resultado['taxa_sucesso']}")

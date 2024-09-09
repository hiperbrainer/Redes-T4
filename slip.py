'''
PRÁTICA 4 - REDES DE COMPUTADORES

ALUNOS:
    - Brainer Sueverti de Campos - 790829
    - Rafael da Silva Ferreira Alves - 810996
'''

'''
1 - Bibliotecas necessárias: 
traceback: indicada pelo professor

'''

class CamadaEnlace:
    ignore_checksum = False

    def __init__(self, linhas_seriais):
        """
        Inicia uma camada de enlace com um ou mais enlaces, cada um conectado
        a uma linha serial distinta. O argumento linhas_seriais é um dicionário
        no formato {ip_outra_ponta: linha_serial}. O ip_outra_ponta é o IP do
        host ou roteador que se encontra na outra ponta do enlace, escrito como
        uma string no formato 'x.y.z.w'. A linha_serial é um objeto da classe
        PTY (vide camadafisica.py) ou de outra classe que implemente os métodos
        registrar_recebedor e enviar.
        """
        self.enlaces = {}
        self.callback = None
        # Constrói um Enlace para cada linha serial
        for ip_outra_ponta, linha_serial in linhas_seriais.items():
            enlace = Enlace(linha_serial)
            self.enlaces[ip_outra_ponta] = enlace
            enlace.registrar_recebedor(self._callback)

    def registrar_recebedor(self, callback):
        """
        Registra uma função para ser chamada quando dados vierem da camada de enlace
        """
        self.callback = callback

    def enviar(self, datagrama, next_hop):
        """
        Envia datagrama para next_hop, onde next_hop é um endereço IPv4
        fornecido como string (no formato x.y.z.w). A camada de enlace se
        responsabilizará por encontrar em qual enlace se encontra o next_hop.
        """
        # Encontra o Enlace capaz de alcançar next_hop e envia por ele
        self.enlaces[next_hop].enviar(datagrama)

    def _callback(self, datagrama):
        if self.callback:
            self.callback(datagrama)


class Enlace:
    def __init__(self, linha_serial):
        # Inicializa a classe Enlace com a linha serial fornecida
        self.dados = b''  # Armazena os dados recebidos
        self.linha_serial = linha_serial  # Referência para a linha serial
        self.linha_serial.registrar_recebedor(self.__raw_recv)  # Registra o método de recebimento

    def registrar_recebedor(self, callback):
        # Registra a função callback para processar datagramas recebidos
        self.callback = callback

    def enviar(self, datagrama):
        # Passo 1: Adiciona bytes de delimitação no início e no fim do datagrama
        # Passo 2: Implementa as sequências de escape para bytes especiais
        datagrama_codif = datagrama.replace(b'\xDB', b'\xDB\xDD').replace(b'\xC0', b'\xDB\xDC')  # Trata as sequências de escape
        datagrama_codif = b'\xC0' + datagrama_codif + b'\xC0'  # Adiciona o byte de início e fim (0xC0)
        self.linha_serial.enviar(datagrama_codif)  # Envia o datagrama codificado pela linha serial
        pass

    def __raw_recv(self, dados):
        # Passo 3: Implementa a recepção de dados
        if not hasattr(self, 'dados'):
            self.dados = b''  # Inicializa os dados se ainda não estiverem definidos
        self.dados += dados  # Acrescenta os dados recebidos ao buffer

        while self.dados:
            end = self.dados.find(b'\xC0')  # Procura pelo delimitador de fim de quadro (0xC0)
            if end != -1:
                pedaco = self.dados[:end]  # Extrai o quadro até o delimitador
                if len(pedaco) > 0:
                    # Passo 4: Lida com as sequências de escape para bytes especiais
                    pedaco = pedaco.replace(b'\xDB\xDC', b'\xC0').replace(b'\xDB\xDD', b'\xDB')  # Reverte as sequências de escape
                    try:
                        # Passo 3 e 5: Chama o callback para processar o datagrama
                        self.callback(pedaco)
                    except:
                        # Passo 5: Trata exceções, mostrando o erro e evitando que dados malformados sejam repassados
                        import traceback
                        traceback.print_exc()
                    finally:
                        # Passo 5: Limpa dados residuais para evitar processamento futuro de datagramas malformados
                        pass
                # Remove o quadro processado do buffer
                self.dados = self.dados[end + 1:]
            else:
                break  # Sai do loop se nenhum delimitador de quadro for encontrado


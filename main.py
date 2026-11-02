# MOODSHOT v2.1w
# Gerenciador de perfis e filtros de câmera via prompt.

# imports
import json
import os

import requests

# constantes

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_FILTROS = os.path.join(PASTA_PROJETO, "filtros_salvos.json")
ARQUIVO_HISTORICO = os.path.join(PASTA_PROJETO, "historico.txt")

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"

FOCO_MIN = 0
FOCO_MAX = 20

FILTROS_PADRAO = {
    1: "Modo Viagem",
    2: "Modo Estudo",
    3: "Modo Encontro",
    4: "Modo PopArt",
    5: "Nenhum",
}

TEMAS = {
    1: "Flores",
    2: "Céu",
    3: "Frutiger Aero",
    4: "Laranja",
    5: "Nenhum",
}

MODOS = {
    1: "Escuro",
    2: "Claro",
}

RESPOSTAS_SIM = ["S", "SIM"]
RESPOSTAS_NAO = ["N", "NAO", "NÃO"]
RESPOSTAS_RETORNAR = ["retornar", "return"]

SEPARADOR = "-" * 30


# ---------------------------------------------------------------------------
# Funções de entrada do usuário
# ---------------------------------------------------------------------------

def ler_opcao(mensagem, opcoes_validas):
    """Lê uma opção numérica e só aceita valores contidos em opcoes_validas."""
    while True:
        resposta = input(mensagem).strip()
        try:
            numero = int(resposta)
        except ValueError:
            print("Resposta inválida! Digite apenas o número da opção.")
            continue
        if numero in opcoes_validas:
            return numero
        print("Opção inválida! Tente novamente.")


def ler_numero(mensagem, minimo=None, maximo=None):
    """Lê um número (inteiro ou decimal) dentro da faixa informada."""
    while True:
        resposta = input(mensagem).strip().replace(",", ".")
        try:
            numero = float(resposta)
        except ValueError:
            print("Valor inválido! Digite um número, por exemplo 10 ou 7.5.")
            continue
        if minimo is not None and numero < minimo:
            print(f"Valor inválido! O mínimo é {minimo}.")
        elif maximo is not None and numero > maximo:
            print(f"Valor inválido! O máximo é {maximo}.")
        else:
            return numero


def perguntar_sim_nao(mensagem):
    """Faz uma pergunta de sim ou não e devolve True para sim e False para não."""
    while True:
        resposta = input(f"{mensagem} ('S' ou 'N'): ").strip().upper()
        if resposta in RESPOSTAS_SIM:
            return True
        if resposta in RESPOSTAS_NAO:
            return False
        print("Resposta inválida! Digite 'S' ou 'N'.")


def ler_texto(mensagem):
    """Lê um texto que não pode ser vazio."""
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        print("Resposta inválida! O campo não pode ficar vazio.")


# ---------------------------------------------------------------------------
# Funções de persistência
# ---------------------------------------------------------------------------

def carregar_filtros():
    """Carrega os filtros personalizados do arquivo JSON. Retorna um dicionário."""
    try:
        with open(ARQUIVO_FILTROS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            raise ValueError("Formato inesperado")
        # mantém apenas os filtros no formato [foco, saturação, vinheta, cor]
        return {nome: valores for nome, valores in dados.items()
                if isinstance(valores, list) and len(valores) == 4}
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, ValueError):
        print("Aviso: o arquivo de filtros está corrompido. Iniciando sem filtros salvos.")
        return {}
    except OSError:
        print("Aviso: não foi possível ler o arquivo de filtros.")
        return {}


def salvar_filtros(filtros):
    """Salva o dicionário de filtros no arquivo JSON. Retorna True se deu certo."""
    try:
        with open(ARQUIVO_FILTROS, "w", encoding="utf-8") as arquivo:
            json.dump(filtros, arquivo, ensure_ascii=False, indent=4)
        return True
    except OSError:
        print("Erro: não foi possível salvar os filtros no arquivo.")
        return False


def registrar_historico(mensagem):
    """Adiciona uma linha ao arquivo de histórico."""
    try:
        with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as arquivo:
            arquivo.write(mensagem + "\n")
    except OSError:
        print("Aviso: não foi possível gravar o histórico.")


def ler_historico():
    """Lê o histórico de ações. Retorna uma lista de linhas (vazia se não houver)."""
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            return [linha.strip() for linha in arquivo if linha.strip()]
    except FileNotFoundError:
        return []
    except OSError:
        print("Aviso: não foi possível ler o histórico.")
        return []


# ---------------------------------------------------------------------------
# Funções de exibição
# ---------------------------------------------------------------------------

def exibir_estado(estado):
    """Mostra a configuração atual do dispositivo."""
    print(f"Foco: {estado['foco']} | Filtro: {estado['filtro']} | "
          f"Tema: {estado['tema']} | Modo: {estado['modo']}")


def exibir_menu_principal(estado):
    """Mostra o menu principal junto com o estado atual."""
    print(SEPARADOR)
    print("MOODSHOT")
    print(SEPARADOR)
    exibir_estado(estado)
    print(SEPARADOR)
    print("1 - Alterar Foco")
    print("2 - Filtros")
    print("3 - Predefinições (Tema e Modo)")
    print("4 - Histórico de ações")
    print("5 - Recomendação pelo clima")
    print("6 - Sair")
    print(SEPARADOR)


def exibir_opcoes(opcoes):
    """Mostra um dicionário de opções numeradas."""
    for numero, nome in opcoes.items():
        print(f"{numero} - {nome}")


def exibir_filtros_personalizados(filtros):
    """Lista os filtros personalizados de forma legível."""
    for nome, valores in filtros.items():
        foco, saturacao, vinheta, cor = valores
        print(f"- {nome}: foco {foco}, saturação {saturacao}, vinheta {vinheta}, cor matiz: {cor}")


# ---------------------------------------------------------------------------
# Opção 1 - Foco
# ---------------------------------------------------------------------------

def alterar_foco(foco_atual):
    """Permite alterar o foco. Retorna o novo foco (ou o atual, se cancelado)."""
    print("Opção 1 - Alterar Foco")
    print(f"Foco atual: {foco_atual}")
    print(SEPARADOR)
    if not perguntar_sim_nao("Você deseja alterar o foco?"):
        print("Operação cancelada. Retornando ao menu...")
        return foco_atual

    novo_foco = ler_numero(f"Digite o novo foco ({FOCO_MIN} a {FOCO_MAX}): ", FOCO_MIN, FOCO_MAX)
    print(f"Novo foco: {novo_foco}")
    registrar_historico(f"O foco foi modificado para {novo_foco}.")
    print("Retornando ao menu...")
    return novo_foco


# ---------------------------------------------------------------------------
# Opção 2 - Filtros
# ---------------------------------------------------------------------------

def escolher_filtro_padrao(filtro_atual):
    """Escolhe um dos filtros padrão. Retorna o filtro escolhido."""
    print("Filtros Default:")
    exibir_opcoes({n: ("Desativar Filtro" if f == "Nenhum" else f) for n, f in FILTROS_PADRAO.items()})
    print(SEPARADOR)
    escolha = ler_opcao("Digite sua opção: ", FILTROS_PADRAO.keys())
    novo_filtro = FILTROS_PADRAO[escolha]
    if novo_filtro == filtro_atual:
        print("Esse filtro já está ativo. Retornando ao menu...")
        return filtro_atual
    print(f"Filtro modificado para: {novo_filtro}")
    registrar_historico(f"Filtro modificado para: {novo_filtro}")
    print("Retornando ao menu...")
    return novo_filtro


def criar_filtro(filtros):
    """Cria um filtro personalizado, salva no JSON e retorna o nome criado (ou None)."""
    print("Opção 1 - Criar nova predefinição")
    print(SEPARADOR)
    foco = ler_numero(f"Digite qual será o foco do filtro ({FOCO_MIN} a {FOCO_MAX}): ", FOCO_MIN, FOCO_MAX)
    saturacao = ler_numero("Digite qual será a saturação do filtro (0 a 100): ", 0, 100)
    vinheta = ler_numero("Digite qual será o nível da vinheta do filtro (0 a 100): ", 0, 100)

    if perguntar_sim_nao("Você quer colocar uma cor matiz no filtro?"):
        cor = ler_texto("Digite a cor matiz do filtro: ")
    else:
        cor = "Sem cor matiz"

    while True:
        nome = ler_texto("Digite o nome do filtro: ")
        if nome not in filtros:
            break
        if perguntar_sim_nao(f"Já existe um filtro chamado '{nome}'. Deseja substituí-lo?"):
            break

    filtros[nome] = [foco, saturacao, vinheta, cor]
    if not salvar_filtros(filtros):
        print("O filtro ficará disponível apenas nesta sessão.")
    registrar_historico(f"O usuário criou um novo filtro: {nome}")
    print(f"Filtro '{nome}' criado com sucesso.")
    return nome


def selecionar_filtro_personalizado(filtros):
    """Pede o nome de um filtro existente. Retorna o nome ou None se o usuário retornar."""
    print("Digite o nome do filtro desejado (ou 'retornar' para sair).")
    nomes_minusculos = {nome.lower(): nome for nome in filtros}
    while True:
        resposta = input("Nome do filtro: ").strip()
        if resposta.lower() in RESPOSTAS_RETORNAR:
            print("Ok! Retornando ao menu...")
            return None
        if resposta.lower() in nomes_minusculos:
            return nomes_minusculos[resposta.lower()]
        print(f"Filtro '{resposta}' não encontrado. Verifique o nome e tente novamente.")


def ativar_filtro_personalizado(nome, filtros):
    """Ativa um filtro personalizado. Retorna (filtro, foco) do filtro ativado."""
    foco = filtros[nome][0]
    print(f"Filtro modificado para: {nome} (foco {foco})")
    registrar_historico(f"Filtro modificado para: {nome}")
    print("Retornando ao menu...")
    return nome, foco


def menu_filtros_personalizados(filtro_atual, foco_atual, filtros):
    """Submenu dos filtros personalizados. Retorna (filtro, foco) atualizados."""
    print("Entrando na customização de filtros...")
    print(SEPARADOR)
    print("1 - Criar nova predefinição")
    print("2 - Usar filtro já existente")
    print("3 - Retornar")
    print(SEPARADOR)
    escolha = ler_opcao("Digite sua opção: ", [1, 2, 3])

    if escolha == 1:
        nome = criar_filtro(filtros)
        if perguntar_sim_nao("Deseja ativá-lo agora?"):
            return ativar_filtro_personalizado(nome, filtros)
        print("Ok! Você pode ativá-lo mais tarde. Retornando ao menu...")

    elif escolha == 2:
        if not filtros:
            print("Aviso: nenhum filtro personalizado cadastrado! Crie um filtro primeiro.")
            print("Retornando ao menu...")
        else:
            print("Seus filtros:")
            exibir_filtros_personalizados(filtros)
            nome = selecionar_filtro_personalizado(filtros)
            if nome is not None:
                return ativar_filtro_personalizado(nome, filtros)

    else:
        print("Retornando ao menu...")

    return filtro_atual, foco_atual


def menu_filtros(filtro_atual, foco_atual, filtros):
    """Menu da opção 2. Retorna (filtro, foco) atualizados."""
    print("Opção 2 - Filtros")
    print(SEPARADOR)
    print(f"Filtro atual: {filtro_atual}")
    print(SEPARADOR)
    print("1 - Filtros Default")
    print("2 - Filtros Personalizados")
    print("3 - Retornar")
    print(SEPARADOR)
    escolha = ler_opcao("Digite sua opção: ", [1, 2, 3])

    if escolha == 1:
        return escolher_filtro_padrao(filtro_atual), foco_atual
    if escolha == 2:
        return menu_filtros_personalizados(filtro_atual, foco_atual, filtros)
    print("Retornando ao menu...")
    return filtro_atual, foco_atual


# ---------------------------------------------------------------------------
# Opção 3 - Predefinições (Tema e Modo)
# ---------------------------------------------------------------------------

def escolher_tema(tema_atual):
    """Escolhe o tema da interface. Retorna o tema escolhido."""
    print("Tema")
    print(SEPARADOR)
    print(f"Tema atual: {tema_atual}")
    print(SEPARADOR)
    exibir_opcoes({n: ("Desativar Tema" if t == "Nenhum" else f"Tema {t}") for n, t in TEMAS.items()})
    print(SEPARADOR)
    novo_tema = TEMAS[ler_opcao("Digite qual você quer: ", TEMAS.keys())]
    print(f"Tema modificado para: {novo_tema}")
    registrar_historico(f"Tema modificado para: {novo_tema}")
    print("Retornando ao menu...")
    return novo_tema


def escolher_modo(modo_atual):
    """Escolhe o modo claro ou escuro. Retorna o modo escolhido."""
    print("Modo")
    print(SEPARADOR)
    print(f"Modo atual: {modo_atual}")
    print(SEPARADOR)
    exibir_opcoes({n: f"Modo {m}" for n, m in MODOS.items()})
    print(SEPARADOR)
    novo_modo = MODOS[ler_opcao("Digite qual você quer: ", MODOS.keys())]
    print(f"Modo modificado para: {novo_modo}")
    registrar_historico(f"Modo modificado para: {novo_modo}")
    print("Retornando ao menu...")
    return novo_modo


def predefinicoes(tema_atual, modo_atual):
    """Menu da opção 3. Retorna (tema, modo) atualizados."""
    print("Opção 3 - Predefinições")
    print(SEPARADOR)
    print("1 - Tema")
    print("2 - Modo")
    print("3 - Retornar")
    print(SEPARADOR)
    escolha = ler_opcao("Digite sua opção: ", [1, 2, 3])

    if escolha == 1:
        return escolher_tema(tema_atual), modo_atual
    if escolha == 2:
        return tema_atual, escolher_modo(modo_atual)
    print("Retornando ao menu...")
    return tema_atual, modo_atual


# ---------------------------------------------------------------------------
# Opção 4 - Histórico
# ---------------------------------------------------------------------------

def mostrar_historico():
    """Mostra todas as ações registradas no histórico."""
    print("Opção 4 - Histórico de ações")
    print(SEPARADOR)
    linhas = ler_historico()
    if not linhas:
        print("Você não fez nenhuma ação recentemente.")
    else:
        print("Aqui está seu histórico de ações:")
        for numero, linha in enumerate(linhas, start=1):
            print(f"{numero}. {linha}")
    print("Retornando ao menu...")


# ---------------------------------------------------------------------------
# Opção 5 - Recomendação pelo clima (API Open-Meteo)
# ---------------------------------------------------------------------------

def buscar_coordenadas(cidade):
    """Converte o nome da cidade em (latitude, longitude, nome). Retorna None se falhar."""
    try:
        resposta = requests.get(
            URL_GEOCODING,
            params={"name": cidade, "count": 1, "language": "pt"},
            timeout=5,
        )
        resposta.raise_for_status()
        resultados = resposta.json().get("results")
        if not resultados:
            return None
        local = resultados[0]
        return local["latitude"], local["longitude"], local["name"]
    except (requests.RequestException, KeyError, ValueError):
        return None


def buscar_clima(latitude, longitude):
    """Consulta o clima atual na Open-Meteo. Retorna (codigo, e_dia) ou None se falhar."""
    try:
        resposta = requests.get(
            URL_CLIMA,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "weather_code,is_day",
            },
            timeout=5,
        )
        resposta.raise_for_status()
        atual = resposta.json()["current"]
        return atual["weather_code"], atual["is_day"] == 1
    except (requests.RequestException, KeyError, ValueError):
        return None


def recomendar_por_clima(codigo, e_dia):
    """Recebe o código do clima e se é dia; devolve a recomendação de filtro, tema, modo e foco."""
    if not e_dia:
        return {"condicao": "Noite", "filtro": "Modo Encontro",
                "tema": "Nenhum", "modo": "Escuro", "foco": 6}
    if codigo == 0:
        return {"condicao": "Ensolarado", "filtro": "Modo Viagem",
                "tema": "Céu", "modo": "Claro", "foco": 12}
    if codigo in (1, 2, 3):
        return {"condicao": "Parcialmente nublado", "filtro": "Modo PopArt",
                "tema": "Flores", "modo": "Claro", "foco": 10}
    if codigo in (45, 48):
        return {"condicao": "Neblina", "filtro": "Modo Estudo",
                "tema": "Nenhum", "modo": "Claro", "foco": 8}
    if 71 <= codigo <= 77 or codigo in (85, 86):
        return {"condicao": "Neve", "filtro": "Modo Viagem",
                "tema": "Frutiger Aero", "modo": "Claro", "foco": 9}
    if 51 <= codigo <= 82:
        return {"condicao": "Chuvoso", "filtro": "Modo Estudo",
                "tema": "Nenhum", "modo": "Escuro", "foco": 8}
    if codigo >= 95:
        return {"condicao": "Tempestade", "filtro": "Modo PopArt",
                "tema": "Laranja", "modo": "Escuro", "foco": 7}
    return {"condicao": "Tempo variado", "filtro": "Modo Viagem",
            "tema": "Nenhum", "modo": "Claro", "foco": 10}


def menu_clima():
    """Pede a cidade, consulta o clima e oferece a recomendação. Retorna a recomendação aceita ou None."""
    print("Opção 5 - Recomendação pelo clima")
    print(SEPARADOR)
    while True:
        cidade = input("Digite sua cidade (ou 'retornar'): ").strip()
        if cidade.lower() in RESPOSTAS_RETORNAR:
            print("Retornando ao menu...")
            return None
        if cidade == "":
            print("Resposta inválida! Digite o nome de uma cidade.")
            continue

        print("Consultando o clima...")
        local = buscar_coordenadas(cidade)
        if local is None:
            print("Não encontrei essa cidade ou houve erro de conexão. Tente novamente.")
            continue

        latitude, longitude, nome = local
        clima = buscar_clima(latitude, longitude)
        if clima is None:
            print("Não foi possível consultar o clima agora. Retornando ao menu...")
            return None
        break

    codigo, e_dia = clima
    rec = recomendar_por_clima(codigo, e_dia)

    print(SEPARADOR)
    print(f"Clima em {nome}: {rec['condicao']}")
    print(f"Recomendamos: {rec['filtro']} | Tema {rec['tema']} | Modo {rec['modo']} | Foco {rec['foco']}")
    print(SEPARADOR)
    registrar_historico(f"Recomendação por clima em {nome} ({rec['condicao']}): {rec['filtro']}")

    if perguntar_sim_nao("Deseja aplicar essa recomendação?"):
        registrar_historico(
            f"Recomendação aplicada: {rec['filtro']}, tema {rec['tema']}, "
            f"modo {rec['modo']}, foco {rec['foco']}."
        )
        print("Recomendação aplicada! Retornando ao menu...")
        return rec
    print("Ok! Retornando ao menu...")
    return None


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------

def main():
    """Laço principal do MoodShot."""
    estado = {"foco": 10, "filtro": "Nenhum", "tema": "Nenhum", "modo": "Escuro"}
    filtros = carregar_filtros()

    while True:
        exibir_menu_principal(estado)
        opcao = ler_opcao("Digite sua opção: ", [1, 2, 3, 4, 5, 6])

        if opcao == 1:
            estado["foco"] = alterar_foco(estado["foco"])

        elif opcao == 2:
            estado["filtro"], estado["foco"] = menu_filtros(estado["filtro"], estado["foco"], filtros)

        elif opcao == 3:
            estado["tema"], estado["modo"] = predefinicoes(estado["tema"], estado["modo"])

        elif opcao == 4:
            mostrar_historico()

        elif opcao == 5:
            rec = menu_clima()
            if rec is not None:
                estado["filtro"] = rec["filtro"]
                estado["tema"] = rec["tema"]
                estado["modo"] = rec["modo"]
                estado["foco"] = rec["foco"]

        else:
            print("Obrigado por usar o MoodShot!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado pelo usuário.")

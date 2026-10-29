# MOODSHOT v2.0
# imports
import json
import requests

# variáveis

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"
ARQUIVO_FILTROS = "filtros_salvos.json"
ARQUIVO_HISTORICO = "historico.txt"
filtro = "Nenhum"
foco = 10
tema = "Nenhum"
modo = "Escuro"
opcao = "oi"

# funções (+ variavel para salvar filtros personalizados)

def carregar_filtros():
    """Função que carrega os filtros salvos do arquivo JSON ao iniciar o programa."""
    try:
        with open(ARQUIVO_FILTROS, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return {}
personalizado = carregar_filtros()

def salvar_filtros(dicionario_filtros):
    """Função que salva o dicionário atualizado de filtros no arquivo JSON."""
    with open(ARQUIVO_FILTROS, "w", encoding="utf-8") as arquivo:
        json.dump(dicionario_filtros, arquivo, ensure_ascii=False, indent=4)


def registrar_historico(mensagem):
    """Função que adiciona uma nova linha no arquivo de histórico."""
    with open(ARQUIVO_HISTORICO, "a", encoding="utf-8") as arquivo:
        arquivo.write(mensagem + "\n")

def foco_alt(f):
    """Função que altera o foco para um novo valor."""
    foco_val = f
    print(f"Novo foco: {foco_val}")
    print("Retornando ao menu...")
    registrar_historico(f"O foco foi modificado. ({foco_val})")
    return foco_val


def filtro_person():
    """Função para encontrar o filtro escolhido pelo usuário"""
    while True:
        resposta = input("Digite o nome (ou retornar): ")
        if resposta.lower() in ["retornar", "return"]:
            print("OK! Retornando ao menu...")
            break
        elif resposta in personalizado:
            filtro_selecionado = personalizado[resposta]
            print(f"Filtro modificado para: {filtro_selecionado}")
            registrar_historico(f"Filtro modificado para: {resposta}")
            return resposta


def predefinicoes(tema_atual, modo_atual):
    """Função para trocar o tema ou modo do app"""
    while True:
        print("Qual desses você deseja usar? (1 - Tema ||| 2 - Modo ||| 3 - Retornar)")
        resposta = input("Digite: ")
        if resposta.isdigit():
            resposta = int(resposta)
            break
        else:
            print('Resposta Inválida! Tente novamente.')

    if resposta == 1:
        print("Opção 1 - Tema")
        print("-------------------")
        print(f"Tema atual: {tema_atual}")
        print("-------------------")
        print("1 - Tema Flores")
        print("2 - Tema Céu")
        print("3 - Tema Frutiger Aero")
        print("4 - Tema Laranja")
        print("5 - Desativar Tema")
        print("-------------------")
        while True:
            resp_tema = input("Digite qual você quer: ")
            temas_dici = {
                1: "Flores",
                2: "Céu",
                3: "Frutiger Aero",
                4: "Laranja",
                5: "Nenhum"
            }
            if resp_tema not in ["1", "2", "3", "4", "5"]:
                print("Resposta Inválida! tente novamente")
            else:
                resp_tema = int(resp_tema)
                break
        if resp_tema in temas_dici:
            novo_tema = temas_dici[resp_tema]
            print("-------------------")
            print(f"Tema atual: {novo_tema}")
            print("-------------------")
            print(f"Tema modificado para: {novo_tema}")
            registrar_historico(f"Tema modificado para: {novo_tema}")
            print("Retornando ao menu...")
            return novo_tema, modo_atual
        else:
            print("Resposta Inválida! Retornando ao menu.")
            return tema_atual, modo_atual

    elif resposta == 2:
        print("Opção 2 - Modo")
        print("-------------------")
        print(f"Modo atual: {modo_atual}")
        print("-------------------")
        print("1 - Modo Escuro")
        print("2 - Modo Claro")
        print("-------------------")
        while True:
            resp_modo = input("Digite qual você quer: ")

            modos_dici = {
                1: "Escuro",
                2: "Claro"
            }

            if resp_modo not in ["1", "2"]:
                print("Resposta Inválida! tente novamente")
            else:
                resp_modo = int(resp_modo)
                break
        if resp_modo in modos_dici:
            novo_modo = modos_dici[resp_modo]
            print("-------------------")
            print(f"Modo atual: {novo_modo}")
            print("-------------------")
            print(f"Modo modificado para: {novo_modo}")
            registrar_historico(f"Modo modificado para: {novo_modo}")
            print("Retornando ao menu...")
            return tema_atual, novo_modo
        else:
            print("Resposta Inválida! Retornando ao menu...")
            return tema_atual, modo_atual
    elif resposta == 3:
        print('Retornando ao menu...')
        return tema_atual, modo_atual
    else:
        print("Resposta Inválida! Retornando ao menu.")
        return tema_atual, modo_atual


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
    print("-" * 6)
    while True:
        cidade = input("Digite sua cidade (ou 'retornar'): ").strip()
        if cidade.lower() in ["retornar", "return"]:
            print("Retornando ao menu...")
            return None
        if cidade == "":
            print("Resposta Inválida! Digite o nome de uma cidade.")
            continue

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

    print("-" * 6)
    print(f"Clima em {nome}: {rec['condicao']}")
    print(f"Recomendamos: {rec['filtro']} | Tema {rec['tema']} | Modo {rec['modo']} | Foco {rec['foco']}")
    print("-" * 6)
    registrar_historico(f"Recomendação por clima em {nome} ({rec['condicao']}): {rec['filtro']}")

    while True:
        aplicar = input("Deseja aplicar essa recomendação? 'S' ou 'N': ").upper()
        if aplicar in ["S", "SIM"]:
            registrar_historico("Recomendação por clima aplicada.")
            print("Recomendação aplicada! Retornando ao menu...")
            return rec
        elif aplicar in ["N", "NAO", "NÃO"]:
            print("Ok! Retornando ao menu...")
            return None
        else:
            print("Resposta Inválida! Digite novamente.")


# código

while True:
    while opcao != int:
        print("-" * 6)
        print("MOODSHOT")
        print("-" * 6)
        print("1 - Alterar Foco")
        print("2 - Filtros")
        print("3 - Predefinições")
        print("4 - Histórico de ações")
        print("5 - Recomendação pelo clima")
        print("6 - Sair")
        print("-" * 6)

        opcao = input("Digite sua opção: ")
        if opcao in ["1", "2", "3", "4", "5", "6"]:
            opcao = int(opcao)
            break

        else:
            print('Opção inválida! Tente novamente.')

    if opcao < 1 or opcao > 6:
        print("Opção invalida!")

    elif opcao == 1:
        print("Opção 1 - Alterar Foco")
        print(f"Foco atual: {foco}")
        print("-" * 6)
        print("Você deseja alterar o foco?")
        print("S - N")
        resposta = input("Digite: ").upper()
        if resposta == "S":
            while True:
                f = input("Digite o novo foco: ")
                if f.isdigit():
                    f = float(f)
                    if f < 0:
                        print("Valor invalido! Tente novamente.")
                    else:
                        foco = foco_alt(f)
                        break
                else:
                    print('Valor invalido! Tente novamente.')
        elif resposta == "N":
            print("Operação cancelada.")
            print("Retornando ao menu...")
        else:
            print("Resposta Inválida! Retornando ao menu.")

    elif opcao == 2:
        print("Opção 2 - Filtros")
        print("-" * 6)
        print(f"Filtro atual: {filtro}")
        print("-" * 6)
        print("1 - Filtros Default")
        print("2 - Filtros Predefinidos")
        print("3 - Retornar")
        print("-" * 6)

        while True:
            resposta = input("Digite sua opção: ")
            if resposta in ["1", "2", "3"]:
                resposta = int(resposta)
                break
            else:
                print("Resposta Inválida! Tente novamente.")

        if resposta == 1:
            print("Filtros Default:")
            print("1 - Modo Viagem")
            print("2 - Modo Estudo")
            print("3 - Modo Encontro")
            print("4 - Modo PopArt")
            print("5 - Desativar Filtro")
            print("-" * 6)
            while True:
                resp_default = input("Digite sua opção: ")
                if resp_default in ["1", "2", "3", "4", "5"]:
                    resp_default = int(resp_default)
                    break
                else:
                    print("Resposta Inválida! Tente novamente.")

            dicionario = {1: "Modo Viagem", 2: "Modo Estudo", 3: "Modo Encontro", 4: "Modo PopArt", 5: "Nenhum"}

            if resp_default in dicionario:
                filtro = dicionario[resp_default]
                print(f"Filtro modificado para: {filtro}")
                registrar_historico(f"Filtro modificado para: {filtro}")
                print("Retornando ao menu...")

            else:
                print("Resposta Inválida! Retornando ao menu.")


        elif resposta == 2:
            print("Entrando na customização de filtros...")
            print(f"Seus filtros: {personalizado}")
            print("-" * 6)
            print("1 - Criar nova predefinição")
            print("2 - Usar filtro já existente")
            print("3 - Retornar")
            print("-" * 6)

            while True:

                resp_predefn = input("Digite sua opção: ")

                if resp_predefn in ["1", "2", "3"]:
                    resp_predefn = int(resp_predefn)
                    break

                else:
                    print("Resposta Inválida! Tente novamente.")

            if resp_predefn == 1:

                print("Opção 1 - Criar nova predefinição")
                print("-" * 6)

                while True:

                    fc = input("Digite qual será o foco (num) do filtro: ")

                    if fc.isdigit():
                        fc = float(fc)
                        break

                    else:
                        print("Resposta Inválida! Tente novamente.")

                while True:

                    sat = input("Digite qual será a saturação do filtro: ")

                    if sat.isdigit():
                        sat = float(sat)
                        break

                    else:
                        print("Resposta Inválida! Tente novamente.")

                while True:

                    vin = input("Digite qual será o nível da vinheta do filtro: ")

                    if vin.isdigit():
                        vin = float(vin)
                        break

                    else:
                        print("Resposta Inválida! Tente novamente.")

                while True:

                    print("Você quer colocar uma cor matiz no filtro?")

                    resp_cor = input("Digite 'S' ou 'N': ").upper()

                    if resp_cor in ["S", "SIM"]:
                        cor = input("Digite a cor matiz do filtro: ")
                        break

                    elif resp_cor in ["N", "NAO", "NÃO"]:
                        cor = "Não tem cor Matiz."
                        break

                    else:
                        print("Resposta Inválida! Digite novamente.")

                nome = input("Digite o nome do filtro: ")

                # salva no arquivo JSON
                personalizado[nome] = (fc, sat, vin, cor)
                salvar_filtros(personalizado)

                registrar_historico(f"O Usuário criou um novo filtro: {nome}")

                print(f"Filtro {nome} criado com sucesso.")

                print("Deseja ativá-lo agora?")

                resp_ativar = input("Digite 'S' ou 'N': ").upper()

                if resp_ativar in ["S", "SIM"]:
                    filtro = nome
                    foco = fc
                    print(f"Filtro ativado")
                    registrar_historico(f"Filtro modificado para: {filtro}")

                elif resp_ativar in ["N", "NÃO", "NAO"]:
                    print("Ok! Retornando ao menu...")

                else:
                    print("Resposta inválida. Você pode ativá-lo mais tarde. Retornando ao menu...")

            elif resp_predefn == 2:

                if not personalizado:
                    print("-" * 6)
                    print("Aviso: Nenhum filtro personalizado cadastrado!")
                    print("Crie um filtro primeiro.")
                    print("Retornando ao menu...")

                else:
                    print(personalizado)
                    print("Você deseja usar um desses filtros?")
                    resp_usar = input("Digite 'S' ou 'N': ").upper()

                    if resp_usar in ["S", "SIM"]:
                        print('Digite o nome do filtro desejado (ou digite "retornar" para sair):')
                        res_filtro = filtro_person()

                        if res_filtro:
                            filtro = res_filtro

                            if res_filtro in personalizado:
                                foco = personalizado[res_filtro][0]

                    elif resp_usar in ["N", "NAO", "NÃO"]:
                        print("Ok! Retornando ao menu...")

                    else:
                        print("Resposta inválida! Retornando ao menu...")

            elif resp_predefn == 3:
                print("Retornando ao Menu...")

        elif resposta == 3:
            print("Retornando ao Menu...")

    elif opcao == 3:
        print("Abrindo menu de predefinições...")
        print("-" * 6)
        print("1 - Tema")
        print("2 - Modo")
        print('3 - Retornar')
        print("-" * 6)
        tema, modo = predefinicoes(tema, modo)

    elif opcao == 4:
        print("Opção 4 - Histórico de ações")
        print("-" * 6)
        print("Aqui está seu histórico de ações:")
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
                linhas = arquivo.readlines()
                if not linhas:
                    print("Você não fez nenhuma ação recentemente.")
                else:
                    for linha in linhas:
                        print(linha.strip())
        except FileNotFoundError:
            print("Você não fez nenhuma ação recentemente.")
        print("Retornando ao menu...")

    elif opcao == 5:
        rec = menu_clima()
        if rec:
            filtro = rec["filtro"]
            tema = rec["tema"]
            modo = rec["modo"]
            foco = rec["foco"]

    elif opcao == 6:
        print("Obrigado por usar o MoodShot!")
        break

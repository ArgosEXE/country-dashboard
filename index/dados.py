"""Leitura dos arquivos CSV do projeto."""

import csv
from pathlib import Path

# Pasta onde este arquivo .py está. Assim o programa encontra o CSV
# mesmo quando é executado a partir de outra pasta (como no Streamlit Cloud).
FOLDER = Path(__file__).parent
COUNTRIES_PATH = FOLDER / "paises.csv"
TRAVEL_WISH_LIST_PATH = FOLDER / "desejo_viajar.csv"
TRAVEL_WISH_FIELDS = ["pais", "regiao", "moeda", "cotacao_brl", "status", "comentario"]


def read_countries():
    """Lê o CSV de países e devolve uma lista de dicionários.

    Os valores vêm do jeito que estão no arquivo, ou seja, como texto
    """
    countries = []
    try:
        with open(COUNTRIES_PATH, "r", encoding="utf-8") as files:
            reader = csv.DictReader(files)
            for line in reader:
                countries.append(line)
    except FileNotFoundError:
        print("O arquivo paises.csv não foi encontrado")
    except Exception as error:
        print("Algum erro aconteceu na leitura do arquivo", error)

    return countries


def save_travel_wish(country):
    """Acrescenta um país no fim do arquivo de desejo viajar (modo "a")."""
    arquivo_ja_existia = TRAVEL_WISH_LIST_PATH.exists()
    with open(TRAVEL_WISH_LIST_PATH, "a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=TRAVEL_WISH_FIELDS)
        if not arquivo_ja_existia:
            escritor.writeheader()
        escritor.writerow({
            "pais": country["pais"],
            "regiao": country["regiao"],
            "moeda": country["moeda"],
            "cotacao_brl": country["cotacao_brl"],
            "status": "Quero viajar",
            "comentario": "",
        })


def load_travel_wish(caminho=TRAVEL_WISH_LIST_PATH):
    """Lê os paises da lista desejo viajar e devolve um dicionário: {pais: dados do pais que deseja viajar}."""
    travel_wish_list = {}
    try:
        with open(TRAVEL_WISH_LIST_PATH, encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                travel_wish_list[linha["pais"]] = {
                    "regiao": linha["regiao"],
                    "moeda": linha["moeda"],
                    "cotacao_brl": linha["cotacao_brl"],
                    "status": linha["status"],
                    "comentario": linha["comentario"],
                }
    except FileNotFoundError:
        pass # Ainda não há favoritos: não é um erro
    return travel_wish_list


def record_travel_wish(travel_wish_list):
    """Reescreve o arquivo inteiro com os paises de desejo viajar do dicionário (modo "w")."""
    with open(TRAVEL_WISH_LIST_PATH, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=TRAVEL_WISH_FIELDS)
        escritor.writeheader()
        for pais, travel_wish in travel_wish_list.items():
            escritor.writerow({
                "pais": pais,
                "regiao": travel_wish["regiao"],
                "moeda": travel_wish["moeda"],
                "cotacao_brl": travel_wish["cotacao_brl"],
                "status": travel_wish["status"],
                "comentario": travel_wish["comentario"],
            })


def prepare_countries(lines):
    """Recebe as linhas lidas do CSV e devolve os paises formatados."""
    countries = []
    for line in lines:
        raw_cotacao = line.get("cotacao_brl")
        if raw_cotacao and raw_cotacao != "N/A":
            try:
                cotacao_val = float(raw_cotacao)
            except ValueError:
                cotacao_val = None
        else:
            cotacao_val = None
        country = {
            "pais": line["pais"],
            "regiao": line["regiao"],
            "populacao": line["populacao"],
            "area_mi2": line["area_mi2"],
            "densidade": line["densidade"],
            "pib_per_capita": line["pib_per_capita"],
            "alfabetizacao": line["alfabetizacao"],
            "telefones_por_mil": line["telefones_por_mil"],
            "natalidade": line["natalidade"],
            "mortalidade": line["mortalidade"],
            "mortalidade_infantil": line["mortalidade_infantil"],
            "moeda": line.get("moeda", "N/A"),
            "cotacao_brl": cotacao_val,
        }
        countries.append(country)

    return countries

def load_countries():
    """Lê o CSV e já devolve os paises prontos para usar."""
    return prepare_countries(read_countries())


if __name__ == "__main__":
    pass

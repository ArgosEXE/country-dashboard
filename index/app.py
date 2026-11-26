"""Dashboard de Países: app Streamlit.
"""

import streamlit as st
from math import trunc, pow

import dados


STATUS = ["Quero viajar", "Em viagem", "Já viajei"]


def build_table(countries):
    """Prepara as linhas que aparecem na tabela, com nomes de coluna amigáveis."""
    table = []
    for country in countries:
        line = {
            "País": country["pais"],
            "Região": format_region(country["regiao"]),
            "População": format_num(int(country["populacao"])),
            "Área por m²": format_num(int(country["area_mi2"])),
            "Densidade demografica": country["densidade"],
            "PIB per capita": country["pib_per_capita"],
            "Alfabetização": country["alfabetizacao"],
            "Telefones por mil": country["telefones_por_mil"],
            "Natalidade": country["natalidade"],
            "Mortalidade": country["mortalidade"],
            "Mortalidade infantil": country["mortalidade_infantil"]
        }
        table.append(line)
    return table


def search_for_name(countries, search):
    """Devolve só os países cujo nome contém o texto buscado."""
    founded = [country for country in countries if search.lower().strip() in country["pais"].lower().strip()]
    return founded


def list_regions(countries):
    """Devolve as reagiões dos países, sem repetição e em ordem alfabética."""
    regions = []
    for country in countries:
        region = format_region(country["regiao"])
        if region not in regions:
            regions.append(region)

    regions.sort()
    return regions


def list_nome_moeda(countries):
    """Devolve os nomes e moedas dos países, sem repetição e em ordem alfabética."""
    nomes_moedas = []
    for country in countries:
        nome_moeda = [country["pais"], country.get("moeda", "N/A"), float(country["cotacao_brl"])]
        if nome_moeda not in nomes_moedas:
            nomes_moedas.append(nome_moeda)

    return sorted(nomes_moedas, key=lambda item: item[0])


def cambio(cotacao, real):
    calculo = real/cotacao
    return round(calculo, 2)


def filter_for_region(countries, region):
    """Devolve só os países da região escolhida. Com "Todas", devolve todos."""
    if region == "Todas":
        return countries
    result = [country for country in countries if format_region(country["regiao"]) == region]
    return result


def format_region(region: str):
    """Traduz os nomes das regiões"""
    match region:
        case "ASIA (EX. NEAR EAST)":
            return "ASIA (EXC. ORIENTE PRÓXIMO)"
        case "BALTICS":
            return "BALTICOS"
        case "C.W. OF IND. STATES":
            return "COM. DOS ESTADOS INDEP."
        case "EASTERN EUROPE":
            return "EUROPA ORIENTAL"
        case "LATIN AMER. & CARIB":
            return "AMÉRICA LAT. E CARIBE"
        case "NEAR EAST":
            return "ORIENTE PROXIMO"
        case "NORTHERN AFRICA":
            return "ÁFRICA DO NORTE"
        case "NORTHERN AMERICA":
            return "AMÉRICA DO NORTE"
        case "OCEANIA":
            return "OCEANIA"
        case "SUB-SAHARAN AFRICA":
            return "ÁFRICA SUBSAARIANA"
        case "WESTERN EUROPE":
            return "EUROPA OCIDENTAL"
        case _:
            pass


def format_num(num: int):
    """Adiciona notação pela quantidade de classes numéricas"""
    thousend_separator = ["", " mil", " milhões", " bilhões"]
    error_correct = [3, 6, 9]
    thousend_separators_amount = trunc(len(str(num))/3)-1 if len(str(num)) in error_correct else trunc(len(str(num))/3)
    return f"{round(num / (pow(1000, thousend_separators_amount)), 2)}" + thousend_separator[thousend_separators_amount]


def sidebar(countries):
    with st.sidebar:
        st.title("Câmbio")
        search_sidebar = st.selectbox(
            "Buscar países",
            ["Selecionar"] + list_nome_moeda(countries),
            format_func=lambda country: country if isinstance(country, str) else country[0],
        )
        if search_sidebar != "Selecionar":
            reais = st.number_input("Valor em Reais", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            conversao = cambio(search_sidebar[2], reais)
            st.text_input(
                f"Conversão para {search_sidebar[1]}",
                value=f"{conversao:.2f}",
                disabled=True,
            )


def find_country(countries, country_name):
    """Devolve o primeiro pais com esse nome."""
    for country in countries:
        if country["pais"] == country_name:
            return country

def population_size(countries):
    """Devolve o menor e o maior valor de população."""
    if not countries:
        return None, None
    
    smaller = int(countries[0]["populacao"])
    bigger = int(countries[0]["populacao"])
    smaller_country_pop = countries[0]["pais"]
    bigger_country_pop = countries[0]["pais"]

    for country in countries:
        population = int(country["populacao"])
        if population < smaller:
            smaller = population
            smaller_country_pop = country["pais"]
        if population > bigger:
            bigger = population
            bigger_country_pop = country["pais"]

    return smaller_country_pop, bigger_country_pop


def list_countries_names(countries):
    countries_names = []
    for country in countries:
        countries_names.append(country["pais"])
    return countries_names


def show_countries(countries):

    col1, col2, col3 = st.columns(3)

    population_smaller, population_bigger = population_size(countries)
    col1.metric("Total de países", len(countries))
    col2.metric("País mais populoso: ", population_bigger)
    col3.metric("País menos populoso: ", population_smaller)

    col_search, col_regions = st.columns(2)

    search = col_search.text_input("Buscar países")
    region = col_regions.selectbox("Filtrar por Região", ["Todas"] + list_regions(countries))

    found = filter_for_region(countries, region)
    found = search_for_name(found, search)

    countries_amount = len(found)

    if countries_amount == 0:
            st.warning("Nenhum país encontrado")
    else:
        st.write(f"Países encontrados: {countries_amount}")
        st.dataframe(build_table(found))
        
        country_name = st.selectbox("Escolha um país", ["Selecione"] + list_countries_names(found))
        country = find_country(found, country_name)
        if country:
            if st.button("Adicionar a lista de desejos de viagem"):
                travel_wish_list = dados.load_travel_wish()
                if country_name in travel_wish_list:
                    st.warning("Esse país já está na lista de desejos.")
                else:
                    dados.save_travel_wish(country)
                    st.toast("País adicionado!", icon="✅",)
                    st.rerun()


def build_travel_wish_table(travel_wish_list):
    """Prepara as linhas da tabela de desejos de viagem."""
    tabela = []
    for pais, travel_wish in travel_wish_list.items():
        linha = {
            "País": pais,
            "Região": travel_wish["regiao"],
            "Moeda": travel_wish["moeda"],
            "Cotação em Reais": travel_wish["cotacao_brl"],
            "Status": travel_wish["status"],
            "Comentário": travel_wish["comentario"],
        }
        tabela.append(linha)
    return tabela


def show_travel_wish_list(travel_wish_list):
    """Mostra os paises que deseja viajar salvos."""
    col1, col2 = st.columns(2)
    col1.metric("Desejos de Viagem", len(travel_wish_list))
    col2.metric("Região favorita", f"")
    travel_wish_list_amount = len(travel_wish_list)
    if travel_wish_list_amount == 0:
        st.warning("Nenhum desejo de viagem adicionado")
    else:
        st.dataframe(build_travel_wish_table(travel_wish_list), hide_index=True, width="stretch")

        country = st.selectbox("Escolha um desejo de viajem", list(travel_wish_list.keys()))
        if country:
            travel_wish = travel_wish_list[country]

            status = st.selectbox("Status", STATUS, index=STATUS.index(travel_wish["status"]))
            comentario = st.text_input("Comentário", travel_wish["comentario"])

        if st.button("Salvar alterações"):
            travel_wish.update({"status": status, "comentario": comentario})
            dados.record_travel_wish(travel_wish_list)
            st.rerun()

        if st.button("🗑 Remover"):
            del travel_wish_list[country]
            dados.record_travel_wish(travel_wish_list)
            st.rerun()


def main():
    st.set_page_config(page_title="Países do Mundo", page_icon="🌎​", layout="wide")
    st.title("Países do Mundo")

    countries = dados.load_countries()
    travel_wish_list = dados.load_travel_wish()

    sidebar(countries)

    aba_paises, aba_desejo_viagem = st.tabs(["Países", "Desejo viajar"])
    with aba_paises:
        show_countries(countries)
    with aba_desejo_viagem:
        show_travel_wish_list(travel_wish_list)


if __name__ == "__main__":
    main()
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
import networkx as nx
import folium
import osmnx as ox
import threading
import traceback # Para imprimir o stack trace completo em caso de erro

# Variável global para armazenar o grafo em memória e um lock para acesso seguro
_G_real = None
_graph_lock = threading.Lock()

# Define o caminho para o arquivo de cache do grafo em disco
GRAPH_CACHE_FILE = os.path.join(settings.MEDIA_ROOT, 'marica_road_network.graphml')


# Dicionário com informações para os pop-ups
pontos_turisticos_info = {
    "Lagoa de Araçatiba": {
        "descricao": "Principal cartão-postal do Centro de Maricá, com orla revitalizada, ciclovia e o famoso letreiro 'Eu Amo Maricá'. Ideal para caminhadas e lazer.",
        "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/27/42/76/17/lagoa-de-aracatiba-marica.jpg?w=900&h=500&s=1"
    },
    "Praia de Itaipuaçu": {
        "descricao": "Extensa praia oceânica, conhecida por suas ondas fortes, ideal para surfistas e para quem busca tranquilidade. Oferece um belo pôr do sol.",
        "imagem": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTt-i1dzf0YHcZ5EgfQ_FEt1a1D57WBDSVssg&s"
    },
    "Farol de Ponta Negra": {
        "descricao": "Localizado em um dos extremos de Maricá, oferece uma vista panorâmica espetacular do oceano e da costa, com um farol imponente.",
        "imagem": "https://bafafa.com.br/images/artigos/farol_de_ponte_negra_10092023_043812.jpg"
    },
    "Centro de Maricá": {
        "descricao": "Coração da cidade, com a Praça Orlando de Barros Pimentel, Igreja Matriz de Nossa Senhora do Amparo e diversas opções de comércio e serviços.",
        "imagem": "https://www.marica.rj.gov.br/wp-content/uploads/2022/01/marica.png"
    },
    "Pedra do Elefante": { # Acesso via Mirante
        "descricao": "Ponto turístico com trilha desafiadora e vista deslumbrante da Restinga de Maricá e do litoral. O nome se deve ao formato de elefante de uma de suas pedras.",
        "imagem": "https://images.mnstatic.com/30/f0/30f0bafe4d806b0c6119e8bb02cc5022.jpg"
    },
    "Cachoeira do Espraiado": {
        "descricao": "Refúgio natural em meio à Mata Atlântica, com piscinas naturais e quedas d'água refrescantes. Ideal para ecoturismo e relaxamento.",
        "imagem": "https://s0.wklcdn.com/image_41/1240357/7747435/4450707Master.jpg" # Exemplo, verificar
    },
    "Canal da Ponta Negra": {
        "descricao": "Conexão entre a Lagoa de Maricá e o Oceano Atlântico. Um local tranquilo para pesca, remo e para apreciar a paisagem costeira.",
        "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/11/5d/de/2f/um-lugar-pouco-conhecido.jpg?w=1200&h=-1&s=1"
    },
    "Pedra de Inoã": {
        "descricao": "Ponto de referência marcante, visível de diversas partes da região de Inoã. Oferece trilhas e vistas panorâmicas da área rural e costeira de Maricá.",
        "imagem": "https://upload.wikimedia.org/wikipedia/commons/4/40/Pedra_de_Ino%C3%A3.jpg"
    },
    # NOVOS PONTOS - ATUALIZE AS DESCRIÇÕES E IMAGENS
    "Praia da Barra de Maricá": {
        "descricao": "Popular encontro da lagoa com o mar, ideal para famílias e esportes aquáticos.",
        "imagem": "https://s2-oglobo.glbimg.com/aBZn8w0pr-5Qoc7E6RwonYfaTa0=/0x0:4160x2340/888x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_da025474c0c44edd99332dddb09cabe8/internal_photos/bs/2025/o/8/ZSC32cT66y6wv7h3TRBQ/marica.jpeg" # Exemplo
    },
    "Praia de Cordeirinho": {
        "descricao": "Praia tranquila, continuação da orla de Maricá, boa para descanso e caminhadas.",
        "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/05/d3/3c/ee/cordeirinho.jpg?w=1200&h=-1&s=1" # Exemplo
    },
    "Praia de Guaratiba": {
        "descricao": "Extensa praia na divisa com Saquarema, conhecida por sua beleza natural e ondas.",
        "imagem": "https://casaruralmarica.com/wp-content/uploads/2024/05/praia-guaratiba-1.webp" # Exemplo
    },
    "Igreja Matriz N. S. do Amparo": {
        "descricao": "Marco histórico e religioso no centro de Maricá, datada do século XVIII.",
        "imagem": "https://casaruralmarica.com/wp-content/uploads/2024/06/igreja-nossa-senhora-do-amparo-1024x702.jpg" # Exemplo
    },
    "Rampa de Voo Livre de Maricá": {
        "descricao": "Localizada no Morro da Serrinha, oferece vistas espetaculares e é ponto de partida para voos de parapente.",
        "imagem": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDYjGEafG_z3kHMJAvoKYJNHma9lO6Ikwxww&s" # Exemplo
    },
    "Orla de São José do Imbassaí": {
        "descricao": "Área de lazer revitalizada na Lagoa de São José, com ciclovia e espaços para convivência.",
        "imagem": "https://leisecamarica.com.br/images/noticias/42972/29032022214103_C8EA3CEA-4.jpeg" # Exemplo
    },
    "Fazenda Pública Joaquín Piñero": {
        "descricao": "Antiga Fazenda Itaocaia, hoje um espaço público com atividades culturais, históricas e de lazer.",
        "imagem": "https://images01.brasildefato.com.br/577023e5941d09ff28e89e54a3fd35e1.jpeg" # Exemplo
    }
}

custom_hwy_speeds = {
    "residential": 20, "service": 15, "unclassified": 25, "tertiary": 30,
    "secondary": 40, "primary": 50, "trunk": 60, "motorway": 90,
}

TRAFFIC_MULTIPLIERS = {
    'livre': 1.0,
    'moderado': 1.4,
    'intenso': 2.0
}
TRAFFIC_CONDITION_LABELS = {
    'livre': 'Trânsito Livre',
    'moderado': 'Trânsito Moderado',
    'intenso': 'Trânsito Intenso'
}

ROUTING_WEIGHT_FOR_DIAGNOSIS = "travel_time"

def home(request):
    # print(f"DEBUG: INÍCIO DO REQUEST. settings.MEDIA_ROOT = {settings.MEDIA_ROOT}")
    
    # Coordenadas atualizadas e novos pontos adicionados
    pontos_turisticos_geographic = {
        "Lagoa de Araçatiba": [-22.9265931804576, -42.8271107153453],
        "Praia de Itaipuaçu": [-22.9638, -42.9677], # Coordenada CENTRAL da praia
        "Farol de Ponta Negra": [-22.96047391794836, -42.692140476786996],
        "Centro de Maricá": [-22.914748273450563, -42.81959634222559],
        "Pedra do Elefante": [-22.9624, -43.0112], # Coordenada do MIRANTE DE ITAIPUAÇU (acesso)
        "Cachoeira do Espraiado": [-22.878143312750304, -42.697516445305816],
        "Canal da Ponta Negra": [-22.956461830728692, -42.69379147142791],
        "Pedra de Inoã": [-22.92717211701768, -42.91139602661133],
        # NOVOS PONTOS
        "Praia da Barra de Maricá": [-22.961303067590116, -42.8191866701701],
        "Praia de Cordeirinho": [-22.957305056138484, -42.746470651659365],
        "Praia de Guaratiba": [-22.96015449066947, -42.79945768791294],
        "Igreja Matriz N. S. do Amparo": [-22.919542513488068, -42.81849029666066],
        "Rampa de Voo Livre de Maricá": [-22.888071398541065, -42.86304991408861],
        "Orla de São José do Imbassaí": [-22.935067975408934, -42.86929071583087],
        "Fazenda Pública Joaquín Piñero": [-22.89689537737279, -42.69433887994245],
    }
    pontos_disponiveis = sorted(list(pontos_turisticos_geographic.keys()))
    
    actual_selected_origem = None
    actual_selected_destino = None
    template_selected_origem = None
    template_selected_destino = None
    template_selected_traffic = 'livre'
    
    calculate_route_and_show_map = False

    if request.method == 'POST':
        form_origem = request.POST.get('origem_selecionada') 
        form_destino = request.POST.get('destino_selecionado')
        form_traffic_condition = request.POST.get('traffic_condition', 'livre')

        if form_origem and form_destino and form_origem in pontos_disponiveis and \
           form_destino in pontos_disponiveis and form_origem != form_destino:
            request.session['calc_origem'] = form_origem
            request.session['calc_destino'] = form_destino
            request.session['calc_traffic_condition'] = form_traffic_condition
            request.session['do_calculate_route_once'] = True
            print(f"DEBUG: POST. O:{form_origem}, D:{form_destino}, T:{form_traffic_condition}. Salvo na sessão.")
        else:
            request.session.pop('calc_origem', None)
            request.session.pop('calc_destino', None)
            request.session.pop('calc_traffic_condition', None)
            request.session.pop('do_calculate_route_once', None)
            print(f"DEBUG: POST inválido. O:{form_origem}, D:{form_destino}, T:{form_traffic_condition}.")
        return redirect(request.path)  

    if request.session.get('do_calculate_route_once', False):
        actual_selected_origem = request.session.get('calc_origem')
        actual_selected_destino = request.session.get('calc_destino')
        template_selected_traffic = request.session.get('calc_traffic_condition', 'livre')
        
        template_selected_origem = actual_selected_origem 
        template_selected_destino = actual_selected_destino
        
        # Não delete 'do_calculate_route_once' aqui, delete apenas após o uso ou no GET inicial
        # del request.session['do_calculate_route_once'] 
        
        if actual_selected_origem and actual_selected_destino:
            calculate_route_and_show_map = True
            print(f"DEBUG: GET pós-POST. Rota: {actual_selected_origem} -> {actual_selected_destino}, Trânsito: {template_selected_traffic}")
        else:
            calculate_route_and_show_map = False
            template_selected_traffic = 'livre'
            print("DEBUG: GET pós-POST, mas dados da sessão ausentes/inválidos.")
        # Marcar como usado para não recalcular em refresh simples do GET pós-POST
        request.session['do_calculate_route_once'] = False # Ou del request.session['do_calculate_route_once']
    else:
        calculate_route_and_show_map = False
        template_selected_traffic = 'livre'
        if 'calc_origem' in request.session: # Se não foi um POST válido, limpa
            request.session.pop('calc_origem', None)
            request.session.pop('calc_destino', None)
            request.session.pop('calc_traffic_condition', None)
        request.session.pop('do_calculate_route_once', None) # Garante limpeza
        print(f"DEBUG: GET inicial/F5 ou sem dados válidos. Trânsito padrão: {template_selected_traffic}")
    
    caminho_curto_text = "Selecione uma origem e um destino para calcular a rota."
    if calculate_route_and_show_map and actual_selected_origem and actual_selected_destino:
        caminho_curto_text = f"Calculando rota entre {actual_selected_origem} e {actual_selected_destino}..."
    
    custo_caminho = "" 
    folium_map_html = None
    route = [] 
    G_current = None 
    
    global _G_real
    with _graph_lock:
        if _G_real is None:
            print("DEBUG: Carregando grafo OSMnx...")
            try:
                if os.path.exists(GRAPH_CACHE_FILE):
                    _G_real = ox.load_graphml(filepath=GRAPH_CACHE_FILE)
                    print(f"DEBUG: Grafo OSMnx carregado do cache: {GRAPH_CACHE_FILE}")
                else:
                    print(f"DEBUG: Arquivo de cache do grafo não encontrado em {GRAPH_CACHE_FILE}. Baixando e criando...")
                    central_lat, central_lon = -22.9190, -42.8228 
                    # Use o 'dist' que funcionou para você (ex: 25000 ou 30000) e 'retain_all=True'
                    # Mantendo 20000 como no código original, mas ajuste se necessário.
                    current_dist = 20000 # OU O VALOR MAIOR QUE VOCÊ USOU E FUNCIONOU (ex: 25000)
                    print(f"DEBUG: Baixando grafo com dist={current_dist} e retain_all=True")
                    _G_real = ox.graph_from_point(
                        (central_lat, central_lon),
                        dist=current_dist, # Ajuste este valor se você usou um maior que funcionou
                        network_type="drive",
                        dist_type='network',
                        retain_all=True
                    )
                    media_root_path = getattr(settings, 'MEDIA_ROOT', None)
                    if media_root_path:
                        if not os.path.exists(media_root_path): os.makedirs(media_root_path, exist_ok=True)
                        ox.save_graphml(_G_real, filepath=GRAPH_CACHE_FILE)
                        print(f"DEBUG: Grafo OSMnx salvo em cache: {GRAPH_CACHE_FILE}")
                _G_real = ox.add_edge_speeds(_G_real, hwy_speeds=custom_hwy_speeds) 
                _G_real = ox.add_edge_travel_times(_G_real)
                print("DEBUG: Grafo OSMnx pronto (velocidades e tempos de viagem adicionados).")
            except Exception as e:
                _G_real = None; traceback.print_exc()
                caminho_curto_text = f"Erro crítico ao carregar dados do mapa: {type(e).__name__}."
        G_current = _G_real

    if not G_current:
        if "Erro crítico ao carregar dados do mapa" not in caminho_curto_text:
            caminho_curto_text = "Falha ao carregar o mapa base. Tente novamente mais tarde."
        calculate_route_and_show_map = False 
        folium_map_html = None

    if G_current and calculate_route_and_show_map:
        print(f"DEBUG: Iniciando cálculo de rota (PESO: '{ROUTING_WEIGHT_FOR_DIAGNOSIS}', Trânsito: {template_selected_traffic})...")
        try:
            print(f"DEBUG: SELEÇÃO DO FORMULÁRIO (da sessão): Origem='{request.session.get('calc_origem', 'N/A')}', Destino='{request.session.get('calc_destino', 'N/A')}'")
            print(f"DEBUG: USANDO PARA ROTA (variáveis atuais): actual_selected_origem='{actual_selected_origem}', actual_selected_destino='{actual_selected_destino}'")

            if not actual_selected_origem or not actual_selected_destino:
                raise ValueError("Origem ou destino não definidos para cálculo da rota.")

            if actual_selected_origem not in pontos_turisticos_geographic or actual_selected_destino not in pontos_turisticos_geographic:
                raise ValueError(f"Origem '{actual_selected_origem}' ou Destino '{actual_selected_destino}' não encontrado no dicionário de coordenadas.")

            origem_coords = pontos_turisticos_geographic[actual_selected_origem]
            destino_coords_input = pontos_turisticos_geographic[actual_selected_destino]

            print(f"DEBUG: Coordenadas de ORIGEM ({actual_selected_origem}) do dicionário: {origem_coords}")
            print(f"DEBUG: Coordenadas de DESTINO ({actual_selected_destino}) do dicionário: {destino_coords_input}")

            origem_node_id = ox.distance.nearest_nodes(G_current, origem_coords[1], origem_coords[0])
            destino_node_id = ox.distance.nearest_nodes(G_current, destino_coords_input[1], destino_coords_input[0])
            
            origem_snapped_coords = (G_current.nodes[origem_node_id]['y'], G_current.nodes[origem_node_id]['x'])
            destino_snapped_coords = (G_current.nodes[destino_node_id]['y'], G_current.nodes[destino_node_id]['x'])
            print(f"DEBUG: Nó de ORIGEM ({actual_selected_origem}) snapado para: Lat {origem_snapped_coords[0]}, Lon {origem_snapped_coords[1]}")
            print(f"DEBUG: Nó de DESTINO ({actual_selected_destino}) snapado para: Lat {destino_snapped_coords[0]}, Lon {destino_snapped_coords[1]}")
            
            calculated_metric_value = 0
            if origem_node_id == destino_node_id:
                caminho_curto_text = f"Origem ({actual_selected_origem}) e destino ({actual_selected_destino}) são o mesmo."
                route = [origem_node_id]; custo_caminho = "0 minutos"
            else:
                route = nx.shortest_path(G_current, origem_node_id, destino_node_id, weight=ROUTING_WEIGHT_FOR_DIAGNOSIS)
                calculated_metric_value = nx.shortest_path_length(G_current, origem_node_id, destino_node_id, weight=ROUTING_WEIGHT_FOR_DIAGNOSIS)
                
                base_travel_time_seconds = 0
                actual_length_for_route_meters = 0
                if route and len(route) > 1:
                    for u_node_iter, v_node_iter in zip(route[:-1], route[1:]):
                        multi_edge_data_iter = G_current.get_edge_data(u_node_iter, v_node_iter)
                        chosen_edge_for_stats = None
                        if multi_edge_data_iter:
                            best_val_stat = float('inf')
                            if isinstance(G_current, nx.MultiDiGraph):
                                for key_edge_iter in multi_edge_data_iter:
                                    edge_attr_candidate = multi_edge_data_iter[key_edge_iter]
                                    val = edge_attr_candidate.get(ROUTING_WEIGHT_FOR_DIAGNOSIS, float('inf'))
                                    if val < best_val_stat:
                                        best_val_stat = val
                                        chosen_edge_for_stats = edge_attr_candidate
                                if not chosen_edge_for_stats and multi_edge_data_iter:
                                     chosen_edge_for_stats = multi_edge_data_iter[list(multi_edge_data_iter.keys())[0]]
                            else: 
                                chosen_edge_for_stats = multi_edge_data_iter 
                        if chosen_edge_for_stats:
                            base_travel_time_seconds += chosen_edge_for_stats.get('travel_time', 0)
                            actual_length_for_route_meters += chosen_edge_for_stats.get('length', 0)
                
                current_traffic_multiplier = TRAFFIC_MULTIPLIERS.get(template_selected_traffic, 1.0)
                condition_label_for_display = TRAFFIC_CONDITION_LABELS.get(template_selected_traffic, "Condição Desconhecida")

                if ROUTING_WEIGHT_FOR_DIAGNOSIS == "length":
                    final_display_time_seconds = base_travel_time_seconds * current_traffic_multiplier
                    caminho_curto_text = f"Rota por DISTÂNCIA entre {actual_selected_origem} e {actual_selected_destino}"
                    custo_caminho = f"{round(final_display_time_seconds / 60, 1)} minutos (estimado com {condition_label_for_display}, para rota de {calculated_metric_value/1000:.2f} km)"
                else: 
                    final_display_time_seconds_for_time_route = calculated_metric_value * current_traffic_multiplier
                    caminho_curto_text = f"Rota por TEMPO entre {actual_selected_origem} e {actual_selected_destino}"
                    custo_caminho = f"{round(final_display_time_seconds_for_time_route / 60, 1)} minutos (estimado com {condition_label_for_display}, para rota de {actual_length_for_route_meters/1000:.2f} km)"

            print(f"DEBUG: Rota (nós): {route if route else 'Nenhuma rota encontrada ou mesmo nó'}")
            print(f"DEBUG: Custo calculado ({ROUTING_WEIGHT_FOR_DIAGNOSIS}): {calculated_metric_value}")
            print(f"DEBUG: Texto do caminho: {caminho_curto_text}")
            print(f"DEBUG: Custo exibido: {custo_caminho}")

            if route:
                # Definição do ponto inicial do mapa
                map_center_coords = None
                if actual_selected_origem and actual_selected_origem in pontos_turisticos_geographic:
                    map_center_coords = pontos_turisticos_geographic[actual_selected_origem]
                elif G_current and G_current.nodes: # Fallback para o centro do grafo ou um ponto conhecido
                     map_center_coords = pontos_turisticos_geographic.get("Centro de Maricá", [-22.9190, -42.8228])

                m = folium.Map(location=map_center_coords, zoom_start=13, tiles="OpenStreetMap")
                
                for nome_ponto, coords_geo in pontos_turisticos_geographic.items():
                    info_popup = pontos_turisticos_info.get(nome_ponto, {"descricao": "Informação não disponível.", "imagem": ""})
                    # HTML e CSS do popup (mantido como antes)
                    card_style = ("font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; width: 280px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 10px rgba(0,0,0,0.08); overflow: hidden; background-color: #ffffff; border: 1px solid #495057; color: #212529;")
                    img_html_part = ""
                    if info_popup.get("imagem"): # Usar .get() para segurança
                        img_style_str = "width: 100%; height: 150px; object-fit: cover; display: block;"
                        alt_text = nome_ponto.replace('"', '"'); img_src = info_popup["imagem"].replace('"', '"')
                        img_html_part = f'<img src="{img_src}" alt="{alt_text}" style="{img_style_str}">'
                    content_style = "padding: 16px;"
                    title_style = "margin-top: 0; margin-bottom: 10px; font-size: 1.2em; font-weight: 600; color: #212529; text-align: left; line-height: 1.35;"
                    desc_style = ("font-size: 0.9em; color: #495057; line-height: 1.6; text-align: left; margin-bottom: 0; max-height: 80px; overflow-y: auto; word-break: break-word; -webkit-hyphens: auto; -ms-hyphens: auto; hyphens: auto;")
                    popup_html_str = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><style>body{{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,Cantarell,"Open Sans","Helvetica Neue",sans-serif;background-color:#212529;color:#e9ecef;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;padding:8px;}}.popup-card-description-class::-webkit-scrollbar{{width:6px;}}.popup-card-description-class::-webkit-scrollbar-thumb{{background-color:#5c6773;border-radius:10px;}}.popup-card-description-class::-webkit-scrollbar-track{{background-color:#343a40;}}</style></head><body><div style="{card_style}">{img_html_part}<div style="{content_style}"><h4 style="{title_style}">{nome_ponto}</h4><p class="popup-card-description-class" style="{desc_style}">{info_popup.get("descricao", "N/A")}</p></div></div></body></html>"""
                    popup_content_main_height = 20+30+80+32; iframe_total_height = popup_content_main_height
                    if info_popup.get("imagem"): iframe_total_height += 150
                    iframe_total_height += (8*2); iframe_total_width = 280+(8*2)+20
                    iframe = folium.IFrame(html=popup_html_str, width=iframe_total_width, height=iframe_total_height)
                    popup = folium.Popup(iframe, max_width=iframe_total_width+20) # Ajuste max_width se necessário
                    
                    icon_color = 'blue'; icon_symbol = 'info-sign'
                    if nome_ponto == template_selected_origem: icon_color = 'green'; icon_symbol = 'flag'
                    elif nome_ponto == template_selected_destino: icon_color = 'red'; icon_symbol = 'screenshot'
                    folium.Marker(location=coords_geo, popup=popup, icon=folium.Icon(color=icon_color, icon=icon_symbol)).add_to(m)
                
                route_points_for_polyline = []
                if len(route) > 1:
                    for u_node_poly, v_node_poly in zip(route[:-1], route[1:]):
                        edge_data_options = G_current.get_edge_data(u_node_poly, v_node_poly)
                        best_edge_for_polyline = None
                        if edge_data_options:
                            min_weight = float('inf')
                            # Iterar sobre as chaves das arestas paralelas (geralmente 0, 1, ...)
                            for key_edge in edge_data_options:
                                current_edge_attrs = edge_data_options[key_edge]
                                # Se a rota foi por tempo, idealmente pegaríamos a aresta com menor tempo.
                                # Para geometria, geralmente são iguais, mas pegar a de menor peso é mais seguro.
                                current_weight = current_edge_attrs.get(ROUTING_WEIGHT_FOR_DIAGNOSIS, float('inf'))
                                if current_weight < min_weight:
                                    min_weight = current_weight
                                    best_edge_for_polyline = current_edge_attrs
                            if not best_edge_for_polyline: # Fallback se todas tiverem peso inf ou não houver peso
                                best_edge_for_polyline = edge_data_options[list(edge_data_options.keys())[0]]

                        if best_edge_for_polyline and 'geometry' in best_edge_for_polyline:
                            xs,ys = best_edge_for_polyline['geometry'].xy; route_points_for_polyline.extend(list(zip(ys,xs)))
                        elif best_edge_for_polyline: 
                            if not route_points_for_polyline or route_points_for_polyline[-1]!=[G_current.nodes[u_node_poly]['y'],G_current.nodes[u_node_poly]['x']]: route_points_for_polyline.append([G_current.nodes[u_node_poly]['y'],G_current.nodes[u_node_poly]['x']])
                            route_points_for_polyline.append([G_current.nodes[v_node_poly]['y'],G_current.nodes[v_node_poly]['x']])
                        else: 
                            if not route_points_for_polyline or route_points_for_polyline[-1]!=[G_current.nodes[u_node_poly]['y'],G_current.nodes[u_node_poly]['x']]: route_points_for_polyline.append([G_current.nodes[u_node_poly]['y'],G_current.nodes[u_node_poly]['x']])
                            route_points_for_polyline.append([G_current.nodes[v_node_poly]['y'],G_current.nodes[v_node_poly]['x']])

                final_route_points_for_polyline = []
                if route_points_for_polyline and len(route_points_for_polyline) > 0:
                    final_route_points_for_polyline.append(route_points_for_polyline[0])
                    for i_poly_dedup in range(1,len(route_points_for_polyline)):
                        if final_route_points_for_polyline[-1]!=route_points_for_polyline[i_poly_dedup]: final_route_points_for_polyline.append(route_points_for_polyline[i_poly_dedup])
                
                if final_route_points_for_polyline and len(final_route_points_for_polyline)>1:
                    tooltip_text = f"Rota ({ROUTING_WEIGHT_FOR_DIAGNOSIS}): {actual_selected_origem} para {actual_selected_destino} <br>{custo_caminho}"
                    folium.PolyLine(locations=final_route_points_for_polyline, color='red', weight=5, opacity=0.7, tooltip=tooltip_text).add_to(m)
                
                folium.LayerControl().add_to(m)
                folium_map_html = m._repr_html_()
                print("DEBUG: Mapa Folium gerado.")
            else:
                folium_map_html = None
                print("DEBUG: Nenhuma rota para exibir no mapa (rota vazia ou nós idênticos).")
        
        except nx.NetworkXNoPath:
            caminho_curto_text = f"Não foi possível encontrar uma rota ({ROUTING_WEIGHT_FOR_DIAGNOSIS}) entre '{actual_selected_origem}' e '{actual_selected_destino}'."
            custo_caminho = "N/A"; folium_map_html = None; calculate_route_and_show_map = False
            print(f"EXCEÇÃO: nx.NetworkXNoPath para {actual_selected_origem} -> {actual_selected_destino}")
        except ValueError as e: 
            caminho_curto_text = f"Erro ao processar dados para '{actual_selected_origem}' ou '{actual_selected_destino}' (ValueError: {e})."
            custo_caminho = "N/A"; folium_map_html = None; traceback.print_exc(); calculate_route_and_show_map = False
            print(f"EXCEÇÃO: ValueError: {e}")
        except Exception as e:
            caminho_curto_text = f"Ocorreu um erro inesperado ({type(e).__name__}) ao calcular rota."
            custo_caminho = "N/A"; folium_map_html = None; traceback.print_exc(); calculate_route_and_show_map = False
            print(f"EXCEÇÃO: Exception: {type(e).__name__} - {e}")
            
    if not (G_current and calculate_route_and_show_map and folium_map_html):
        if G_current and calculate_route_and_show_map and not folium_map_html and \
           "Não foi possível encontrar uma rota" not in caminho_curto_text and \
           "Erro ao processar dados para" not in caminho_curto_text and \
           "Origem e destino são o mesmo" not in caminho_curto_text:
            caminho_curto_text = f"Rota para {actual_selected_origem} a {actual_selected_destino} calculada, mas houve um erro ao gerar o mapa visual."
        if not folium_map_html: folium_map_html = None

    context = {
        'caminho': caminho_curto_text,
        'custo': custo_caminho,
        'pontos_disponiveis': pontos_disponiveis,
        'selected_origem': template_selected_origem, 
        'selected_destino': template_selected_destino,
        'selected_traffic_condition': template_selected_traffic,
        'folium_map_html': folium_map_html,
        'DIAGNOSTIC_MODE': (ROUTING_WEIGHT_FOR_DIAGNOSIS != "travel_time"),
        'current_weight': ROUTING_WEIGHT_FOR_DIAGNOSIS,
        'show_map_section': calculate_route_and_show_map and bool(folium_map_html)
    }
    return render(request, 'grafo_app/index.html', context)
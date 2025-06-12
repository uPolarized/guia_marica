from django.shortcuts import render, redirect
from django.conf import settings
import os
import networkx as nx
import folium
import osmnx as ox
import threading
import traceback
import random
import json
from folium.plugins import BeautifyIcon

# Variável global para armazenar o grafo em memória e um lock para acesso seguro
_G_real = None
_graph_lock = threading.Lock()

# Define o caminho para o arquivo de cache do grafo em disco
GRAPH_CACHE_FILE = os.path.join(settings.MEDIA_ROOT, 'marica_road_network.graphml')


pontos_turisticos_info = {
    "Lagoa de Araçatiba": { "descricao": "Principal cartão-postal do Centro de Maricá, com orla revitalizada, ciclovia e o famoso letreiro 'Eu Amo Maricá'. Ideal para caminhadas e lazer.", "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/27/42/76/17/lagoa-de-aracatiba-marica.jpg?w=900&h=500&s=1" },
    "Praia de Itaipuaçu": { "descricao": "Extensa praia oceânica, conhecida por suas ondas fortes, ideal para surfistas e para quem busca tranquilidade. Oferece um belo pôr do sol.", "imagem": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTt-i1dzf0YHcZ5EgfQ_FEt1a1D57WBDSVssg&s" },
    "Farol de Ponta Negra": { "descricao": "Localizado em um dos extremos de Maricá, oferece uma vista panorâmica espetacular do oceano e da costa, com um farol imponente.", "imagem": "https://bafafa.com.br/images/artigos/farol_de_ponte_negra_10092023_043812.jpg" },
    "Centro de Maricá": { "descricao": "Coração da cidade, com a Praça Orlando de Barros Pimentel, Igreja Matriz de Nossa Senhora do Amparo e diversas opções de comércio e serviços.", "imagem": "https://www.marica.rj.gov.br/wp-content/uploads/2022/01/marica.png" },
    "Pedra do Elefante": { "descricao": "Ponto turístico com trilha desafiadora e vista deslumbrante da Restinga de Maricá e do litoral. O nome se deve ao formato de elefante de uma de suas pedras.", "imagem": "https://images.mnstatic.com/30/f0/30f0bafe4d806b0c6119e8bb02cc5022.jpg" },
    "Cachoeira do Espraiado": { "descricao": "Refúgio natural em meio à Mata Atlântica, com piscinas naturais e quedas d'água refrescantes, Ideal para ecoturismo e relaxamento.", "imagem": "https://s0.wklcdn.com/image_41/1240357/7747435/4450707Master.jpg" },
    "Canal da Ponta Negra": { "descricao": "Conexão entre a Lagoa de Maricá e o Oceano Atlântico. Um local tranquilo para pesca, remo e para apreciar a paisagem costeira.", "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/11/5d/de/2f/um-lugar-pouco-conhecido.jpg?w=1200&h=-1&s=1" },
    "Pedra de Inoã": { "descricao": "Ponto de referência marcante, visível de diversas partes da região de Inoã. Oferece trilhas e vistas panorâmicas da área rural e costeira de Maricá.", "imagem": "https://upload.wikimedia.org/wikipedia/commons/4/40/Pedra_de_Ino%C3%A3.jpg" },
    "Praia da Barra de Maricá": { "descricao": "Popular encontro da lagoa com o mar, ideal para famílias e esportes aquáticos.", "imagem": "https://s2-oglobo.glbimg.com/aBZn8w0pr-5Qoc7E6RwonYfaTa0=/0x0:4160x2340/888x0/smart/filters:strip_icc()/i.s3.glbimg.com/v1/AUTH_da025474c0c44edd99332dddb09cabe8/internal_photos/bs/2025/o/8/ZSC32cT66y6wv7h3TRBQ/marica.jpeg" },
    "Praia de Cordeirinho": { "descricao": "Praia tranquila, continuação da orla de Maricá, boa para descanso e caminhadas.", "imagem": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/05/d3/3c/ee/cordeirinho.jpg?w=1200&h=-1&s=1" },
    "Praia de Guaratiba": { "descricao": "Extensa praia na divisa com Saquarema, conhecida por sua beleza natural e ondas.", "imagem": "https://casaruralmarica.com/wp-content/uploads/2024/05/praia-guaratiba-1.webp" },
    "Igreja Matriz N. S. do Amparo": { "descricao": "Marco histórico e religioso no centro de Maricá, datada do século XVIII.", "imagem": "https://casaruralmarica.com/wp-content/uploads/2024/06/igreja-nossa-senhora-do-amparo-1024x702.jpg" },
    "Rampa de Voo Livre de Maricá": { "descricao": "Localizada no Morro da Serrinha, oferece vistas espetaculares e é ponto de partida para voos de parapente.", "imagem": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDYjGEafG_z3kHMJAvoKYJNHma9lO6Ikwxww&s" },
    "Orla de São José do Imbassaí": { "descricao": "Área de lazer revitalizada na Lagoa de São José, com ciclovia e espaços para convivência.", "imagem": "https://leisecamarica.com.br/images/noticias/42972/29032022214103_C8EA3CEA-4.jpeg" },
    "Fazenda Pública Joaquín Piñero": { "descricao": "Antiga Fazenda Itaocaia, hoje um espaço público com atividades culturais, históricas e de lazer.", "imagem": "https://images01.brasildefato.com.br/577023e5941d09ff28e89e54a3fd35e1.jpeg" },
}
custom_hwy_speeds = {
    "residential": 20, "service": 15, "unclassified": 25, "tertiary": 30,
    "secondary": 40, "primary": 50, "trunk": 60, "motorway": 90
}

def home(request):
    pontos_turisticos_geographic = {
        "Lagoa de Araçatiba": [-22.9265931804576, -42.8271107153453], "Praia de Itaipuaçu": [-22.96858583272405, -42.99231077702075],
        "Farol de Ponta Negra": [-22.96047391794836, -42.692140476786996], "Centro de Maricá": [-22.914748273450563, -42.81959634222559],
        "Pedra do Elefante": [-22.967413861756036, -43.01427254157256], "Cachoeira do Espraiado": [-22.878025854640693, -42.697268344524005],
        "Canal da Ponta Negra": [-22.956461830728692, -42.69379147142791], "Pedra de Inoã": [-22.928842208367435, -42.9217753523939],
        "Praia da Barra de Maricá": [-22.9254, -42.7965], "Praia de Cordeirinho": [-22.957305056138484, -42.746470651659365],
        "Praia de Guaratiba": [-22.96015449066947, -42.79945768791294], "Igreja Matriz N. S. do Amparo": [-22.920063679881853, -42.81929740974707],
        "Rampa de Voo Livre de Maricá": [-22.888071398541065, -42.86304991408861], "Orla de São José do Imbassaí": [-22.935067975408934, -42.86929071583087],
        "Fazenda Pública Joaquín Piñero": [-22.89778111820182, -42.69607701483277],
    }
    pontos_disponiveis = sorted(list(pontos_turisticos_geographic.keys()))

    if request.method == 'GET' and not request.session.get('do_calculate_route_once'):
        for key in list(request.session.keys()):
            if not key.startswith('_'):
                del request.session[key]

    global _G_real
    with _graph_lock:
        if _G_real is None:
            try:
                if os.path.exists(GRAPH_CACHE_FILE):
                    _G_real = ox.load_graphml(filepath=GRAPH_CACHE_FILE)
                else:
                    central_lat, central_lon = pontos_turisticos_geographic["Centro de Maricá"]
                    _G_real = ox.graph_from_point((central_lat, central_lon), dist=25000, network_type="drive", dist_type='network', retain_all=True, truncate_by_edge=True)
                    ox.save_graphml(_G_real, filepath=GRAPH_CACHE_FILE)
                _G_real = ox.add_edge_speeds(_G_real, hwy_speeds=custom_hwy_speeds)
                _G_real = ox.add_edge_travel_times(_G_real)
            except Exception as e:
                _G_real = None
                traceback.print_exc()
                return render(request, 'grafo_app/index.html', {'caminho': f"Erro crítico ao carregar mapa: {e}", 'pontos_disponiveis': pontos_disponiveis})

    G_current = _G_real

    if request.method == 'POST':
        if 'calculate_custom_stops_route' in request.POST:
            origem = request.POST.get('origem_selecionada')
            destinos = request.POST.getlist('destinos_intermediarios')
            if origem and destinos:
                request.session['calc_origem'] = origem
                request.session['calc_destinos'] = destinos
                request.session['calc_route_type'] = 'multi_stop'
                request.session['do_calculate_route_once'] = True
        elif 'random_route_submit' in request.POST:
            if len(pontos_disponiveis) >= 2:
                origem, destino = random.sample(pontos_disponiveis, 2)
                request.session['calc_origem'] = origem
                request.session['calc_destinos'] = [destino]
                request.session['calc_route_type'] = 'random'
                request.session['do_calculate_route_once'] = True
        return redirect(request.path)

    caminho_curto_text, custo_caminho, folium_map_html = "", "", None
    show_map_section, route_calculation_was_performed = False, False

    if request.session.get('do_calculate_route_once'):
        route_calculation_was_performed = True
        origem_nome = request.session.get('calc_origem')
        destinos_nomes = request.session.get('calc_destinos', [])
        request.session['do_calculate_route_once'] = False

        if origem_nome and destinos_nomes and G_current:
            try:
                points_sequence_names = [origem_nome] + destinos_nomes
                full_route_nodes = []
                total_travel_time, total_length_meters = 0, 0

                for i in range(len(points_sequence_names) - 1):
                    seg_orig_name, seg_dest_name = points_sequence_names[i], points_sequence_names[i+1]
                    orig_coords, dest_coords = pontos_turisticos_geographic[seg_orig_name], pontos_turisticos_geographic[seg_dest_name]
                    orig_node, dest_node = ox.distance.nearest_nodes(G_current, orig_coords[1], orig_coords[0]), ox.distance.nearest_nodes(G_current, dest_coords[1], dest_coords[0])
                    if orig_node == dest_node: continue
                    segment_route = nx.shortest_path(G_current, orig_node, dest_node, weight='travel_time')
                    total_length_meters += nx.shortest_path_length(G_current, orig_node, dest_node, weight='length')
                    total_travel_time += nx.shortest_path_length(G_current, orig_node, dest_node, weight='travel_time')
                    full_route_nodes.extend(segment_route[1:] if full_route_nodes else segment_route)

                if full_route_nodes:
                    show_map_section = True
                    caminho_curto_text = f"Rota Calculada: {' → '.join(points_sequence_names)}"
                    custo_caminho = f"{round(total_travel_time / 60, 1)} min ({total_length_meters/1000:.2f} km)"
                    m = folium.Map(tiles="OpenStreetMap")
                    
                    for nome_ponto, coords_geo in pontos_turisticos_geographic.items():
                        
                        
                        info_p = pontos_turisticos_info.get(nome_ponto, {})

                        popup_style = """
                        <style>
                            *, *::before, *::after { box-sizing: border-box; }
                            body { margin: 0; font-family: 'Poppins', Arial, sans-serif; overflow-x: hidden; overflow-y: auto; }
                            .popup-container { width: 280px; padding: 15px; }
                            .popup-container h4 { margin: 0 0 12px 0; padding-bottom: 8px; font-size: 1.3em; font-weight: 600; color: #3a7bc8; text-align: center; border-bottom: 2px solid #4A90E2; }
                            .popup-container img { width: 100%; height: auto; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); border: 1px solid #eee; transition: transform 0.3s ease, box-shadow 0.3s ease; }
                            .popup-container img:hover { transform: scale(1.05); box-shadow: 0 6px 16px rgba(0,0,0,0.25); }
                            .popup-container p { font-size: 0.95em; line-height: 1.6; text-align: justify; color: #5f6368; margin: 0; overflow-wrap: break-word; word-wrap: break-word; }
                        </style>
                        """
                        popup_body_html = f"""
                        <div class="popup-container">
                            <h4>{nome_ponto}</h4>
                            <img src='{info_p.get("imagem", "")}' alt='Foto de {nome_ponto}'/>
                            <p>{info_p.get("descricao", "")}</p>
                        </div>
                        """
                        full_popup_html = popup_style + popup_body_html
                        
                        iframe = folium.IFrame(html=full_popup_html, width=280, height=315)
                        popup = folium.Popup(iframe)
                        
                        icon = None
                        if nome_ponto in points_sequence_names:
                            ordem = points_sequence_names.index(nome_ponto) + 1
                            cor_de_fundo = '#FF9800'
                            if ordem == 1:
                                cor_de_fundo = '#4CAF50'
                            elif ordem == len(points_sequence_names):
                                cor_de_fundo = '#F44336'
                            icon = BeautifyIcon(number=ordem, border_color='transparent', background_color=cor_de_fundo, text_color='#FFFFFF', icon_shape='marker')
                        else:
                            icon = folium.Icon(color='blue', icon='info-sign')
                        
                        folium.Marker(location=coords_geo, popup=popup, icon=icon).add_to(m)
                        # --- FIM DO BLOCO CORRIGIDO ---

                    route_coords = []
                    for u, v in zip(full_route_nodes[:-1], full_route_nodes[1:]):
                        edge_data = G_current.get_edge_data(u, v, 0)
                        if 'geometry' in edge_data:
                            xs, ys = edge_data['geometry'].xy
                            route_coords.extend(list(zip(ys, xs)))
                        else:
                            route_coords.extend([(G_current.nodes[u]['y'], G_current.nodes[u]['x']), (G_current.nodes[v]['y'], G_current.nodes[v]['x'])])
                    if route_coords:
                        folium.PolyLine(locations=route_coords, color="#0000FF", weight=5, opacity=0.8, tooltip=f"Rota: {custo_caminho}").add_to(m)
                    
                    m.fit_bounds(m.get_bounds(), padding=(30, 30))
                    folium_map_html = m._repr_html_()
            except Exception as e:
                caminho_curto_text = f"Ocorreu um erro: {e}"
                traceback.print_exc()

    destinos_finais_para_js = request.session.get('calc_destinos', [])
    context = {
        'pontos_disponiveis': pontos_disponiveis,
        'selected_origem': request.session.get('calc_origem', ""),
        'selected_destinos_finais': destinos_finais_para_js,
        'selected_destinos_finais_json': json.dumps(destinos_finais_para_js),
        'caminho': caminho_curto_text,
        'custo': custo_caminho,
        'folium_map_html': folium_map_html,
        'show_map_section': show_map_section, 
        'trigger_route_calculation': route_calculation_was_performed,
        'display_info_about_random_route': request.session.get('calc_route_type') == 'random',
    }
    
    return render(request, 'grafo_app/index.html', context)
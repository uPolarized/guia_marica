## Configuração e Instalação Local





### Método Principal: Usando Docker

Usamos o Docker para rodar este projeto localmente, pois já temos certa familiaridade com a ferramenta por conta de projetos anteriores, como o de Práticas Extensionistas. Essa abordagem nos ajuda a manter um ambiente de desenvolvimento consistente e reproduzível para todos os envolvidos, gerenciando todas as dependências (Python, Django, as bibliotecas geoespaciais como OSMnx, NetworkX, Folium, etc.) de forma isolada. Com o Docker, o objetivo é simplificar o processo de setup e evitar problemas comuns de configuração ("funciona na minha máquina, mas não na sua") que podem surgir em diferentes ambientes.

Para isso, o projeto é configurado para ser executado com Docker através de um `Dockerfile` (que descreve como construir a imagem da nossa aplicação Django) e um arquivo `docker-compose.yml` (que define e gerencia os serviços necessários para a aplicação rodar, como o mapeamento de portas e volumes para persistência de dados, se aplicável). A configuração do Docker já está preparada para realizar tarefas iniciais, como as migrações do banco de dados, ao iniciar os contêineres, tornando o processo de inicialização bastante direto.




##  Como o Guia Funciona na Prática

O Maricá-vilhoso Guia turístico opera através de uma combinação de coleta de dados geoespaciais, algoritmos de grafos e visualização interativa.

1.  **Construção da Malha Viária (Primeira Execução ou Cache Expirado):**
    * Ao iniciar, ou se o cache não existir, a aplicação primeiro busca os dados da malha viária de Maricá diretamente do OpenStreetMap (OSM) utilizando a biblioteca **OSMnx**.
    * Com esses dados, o OSMnx constrói um grafo matemático onde as interseções de ruas são os "nós" e as ruas/estradas são as "arestas".
    * Atributos importantes como o comprimento de cada rua e os limites de velocidade (baseados nos tipos de via definidos, como residencial, primária, etc.) são adicionados às arestas do grafo.
    * Com base no comprimento e na velocidade, o tempo de viagem estimado para cada segmento de rua é calculado e também armazenado no grafo.
    * Para otimizar o desempenho em execuções futuras, este grafo processado da malha viária de Maricá é salvo em um arquivo local (`marica_road_network.graphml` na pasta `media/`), funcionando como um cache. Nas próximas vezes que a aplicação rodar, ela carregará o grafo diretamente deste arquivo, tornando a inicialização muito mais rápida.

2.  **Interação do Usuário (Frontend):**
    * O usuário acessa a página web da aplicação.
    * Ele seleciona um **Ponto de Origem** e um **Ponto de Destino** a partir de uma lista pré-definida de locais turísticos de Maricá.
    * Ao clicar em "Calcular Caminho", o formulário é enviado para o backend Django.

3.  **Cálculo da Rota (Backend - Django):**
    * A view do Django recebe a solicitação com os pontos de origem (podendo ou não conter "paradas"), destino e a condição de trânsito.
    * As coordenadas geográficas dos pontos turísticos selecionados são usadas para encontrar os nós mais próximos correspondentes no grafo da malha viária (utilizando funções do OSMnx).
    * Com os nós de origem e destino identificados no grafo, a biblioteca **NetworkX** é acionada. Utilizando o **Algoritmo de Dijkstra**, ela calcula o caminho mais curto entre esses dois nós.
    * O "peso" considerado para o caminho mais curto pode ser o `travel_time` (tempo de viagem) ou `length` (distância). Se for por tempo, o multiplicador de trânsito selecionado pelo usuário é aplicado para ajustar as estimativas.

4.  **Exibição dos Resultados (Frontend):**
    * A rota calculada (uma sequência de nós do grafo, que representa os segmentos de rua) e as informações de custo (tempo estimado, distância total) são enviadas de volta para o template HTML.
    * A biblioteca **Folium** é usada para gerar um mapa interativo de Maricá:
        * A rota calculada é desenhada sobre o mapa como uma linha (PolyLine).
        * Marcadores coloridos indicam o ponto de origem, o ponto de destino e os demais pontos turísticos.
        * Ao clicar em qualquer marcador de ponto turístico, um pop-up é exibido diretamente no mapa, contendo uma breve descrição sobre o local (descrição e imagem).
    * Além do mapa, um resumo textual da rota e o custo estimado são apresentados na página.

Este ciclo permite que o usuário obtenha rotas otimizadas e informações turísticas de forma interativa e visual.





**Para executar o projeto com Docker (comandos para PowerShell no Windows):**

1.  **Pré-requisitos:**
    * Git (para clonar o repositório).
    * Docker Desktop para Windows instalado e em execução.

2.  **Clone o Repositório:**
    ```powershell
    git clone https://github.com/uPolarized/guia_marica.git
    verificar se está na pasta raiz que contem o arquivo .yml.
    ```

3.  **Construa as Imagens e Inicie os Contêineres:**
  
    ```powershell
    docker-compose up --build
    ```
    (Para versões mais recentes do Docker Compose, o comando pode ser `docker compose up --build`). Se quiser rodar em segundo plano após a primeira execução bem-sucedida, você pode usar `docker-compose up -d`.

4.  **Acesse a Aplicação:**
    Após os contêineres iniciarem completamente (o que pode incluir a execução automática de migrações e outras configurações definidas no seu Docker setup), a aplicação estará disponível no seu navegador,  em `http://localhost:8000/grafo/` .

**Observação:** Fizemos em django por porque achamos que iria encaixar perfeitamente por conta da complexidade do projeto que une tanto backend quanto frontend.


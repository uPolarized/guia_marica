Configuração e Instalação Local



Método Principal: Usando Docker

Usamos o Docker para rodar este projeto localmente, pois já temos certa familiaridade com a ferramenta por conta do projeto de Práticas Extensionistas. Essa abordagem nos ajuda a manter um ambiente de desenvolvimento consistente e reproduzível para todos os envolvidos, gerenciando todas as dependências (Python, Django, as bibliotecas geoespaciais como OSMnx, NetworkX, Folium, etc.) de forma isolada. Com o Docker, o objetivo é simplificar o processo de setup e evitar problemas comuns de configuração que podem surgir em diferentes máquinas.

Para isso, o projeto é configurado para ser executado com Docker através de um `Dockerfile` (que descreve como construir a imagem da nossa aplicação Django) e um arquivo `docker-compose.yml` (que define e manipula os serviços necessários para a aplicação rodar). A configuração do Docker já está preparada para realizar tarefas iniciais, como as migrações do banco de dados, ao iniciar os contêineres.

**Para executar o projeto com Docker (comandos para PowerShell no Windows):**

1.  **Pré-requisitos:**
    * Git (para clonar o repositório).
    * Docker Desktop para Windows instalado e em execução.

2.  **Clone o Repositório:**
    ```powershell
    git clone https://github.com/uPolarized/guia_marica.git
    não é necessário dar cd,  o projeto ja está na pasta raiz.
    ```

3.  **Construa as Imagens e Inicie os Contêineres:**
  
    ```powershell
    docker-compose up --build
    ```
    (Para versões mais recentes do Docker Compose, o comando pode ser `docker compose up --build`). Se quiser rodar em segundo plano após a primeira execução bem-sucedida, você pode usar `docker-compose up -d`.

4.  **Acesse a Aplicação:**
    Após os contêineres iniciarem completamente (o que pode incluir a execução automática de migrações e outras configurações definidas no seu Docker setup), a aplicação estará disponível no seu navegador,  em `http://localhost:8000/grafo/` .

**Observação:** Fizemos em django por porque nosso projeto de praticas extensionistas é nesse framework e achamos que iria encaixar perfeitamente por conta da complexidade do projeto que une tanto backend quanto frontend:


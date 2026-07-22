# Agenda Médica

## Descrição breve da solução

Este projeto é uma aplicação de agenda médica mínima composta por dois serviços:

- `web`: aplicação Flask que oferece login e exibição de agendamentos;
- `api_mock`: API simulada em Flask que retorna agendamentos fictícios.

A aplicação principal consome a API mock para listar e buscar horários médicos e exibe os resultados em uma tabela interativa.

## Tecnologias utilizadas

- Python 3.11
- Flask
- SQLite (para dados de usuário local)
- Docker
- Docker Compose
- Tabulator.js 
- requests
- python-dotenv

## Instruções para executar o projeto com Docker

1. Abra o terminal na pasta raiz do projeto:

```powershell
cd "c:\Users\dlima\OneDrive\Desktop\Programação\Python\Agenda Medica\Agenda-Medica"
```

2. Suba os serviços com Docker Compose:

```powershell
docker compose up --build
```

3. Acesse a aplicação no navegador:

- Aplicação principal: `http://localhost:5000`
- API mock: `http://localhost:5001/agendamentos`

4. Para parar os serviços:

```powershell
docker compose down
```

### Executar em segundo plano

```powershell
docker compose up --build -d
```

### Verificar o status dos containers

```powershell
docker compose ps
```

## Credenciais do usuário de teste

- Usuário: `admin`
- Senha: `123456`

## Exemplos de uso da aplicação

1. Abra `http://localhost:5000`.
2. Entre com o usuário de teste.
3. A página de agenda lista todos os agendamentos retornados pela API mock.
4. Use o campo de busca para filtrar por nome do paciente, CPF ou nome do médico.
5. Clique em "Limpar" para voltar à lista completa.

## Decisões técnicas e limitações conhecidas

- A API de agendamentos é simulada em `api_mock` com dados estáticos para facilitar testes sem backend real.
- A aplicação principal usa Flask e consome a API por HTTP interno no Docker.
- O banco de dados local é SQLite e armazena apenas o usuário de teste.
- Variáveis sensíveis e configuração de portas são lidas do arquivo `.env`.
- O `docker-compose.yml` orquestra os dois serviços em uma única execução.

### Limitações conhecidas

- Não há cadastro de novos usuários nem gerenciamento de sessões avançado.
- O mock não oferece operações de criação, atualização ou exclusão de agendamentos.
- O frontend não possui paginação nem ordenação dinâmica avançada.
- A aplicação depende do serviço de API mock estar disponível no mesmo Docker network.

## Observações

- O `docker-compose.yml` usa `API_URL=http://api_mock:5001/agendamentos` para comunicar os serviços.
- O container `web` monta `./app` para facilitar desenvolvimento local, mas em produção esse volume pode ser removido.

# Cloud Job Manager - Projeto 2

Sistema de gerenciamento de execução de programas em ambientes isolados via web, desenvolvido para a disciplina de Computação em Nuvem da PUC-Campinas.

## 📋 Descrição

O **Cloud Job Manager** é uma aplicação web que permite criar, gerenciar e monitorar ambientes isolados de execução de programas com controle granular de recursos computacionais. Utilizando tecnologias modernas de containerização e virtualização, o sistema oferece uma interface intuitiva para gerenciar jobs com alocação específica de CPU, memória e IO.

### Principais Funcionalidades

O sistema permite **criar ambientes isolados de execução** através de containers Docker, cada um com seu próprio namespace. É possível **definir recursos computacionais** alocados para cada job, incluindo número de CPUs (com precisão decimal), quantidade de memória em MB e peso de IO para priorização de operações de disco.

A aplicação oferece **execução flexível de programas**, permitindo escolher qualquer imagem Docker pública e executar comandos personalizados, desde scripts simples até serviços de longa duração. O **monitoramento em tempo real** captura toda a saída (stdout e stderr) dos programas em arquivos de log individuais, que podem ser visualizados através da interface web.

O **gerenciamento completo do ciclo de vida** dos jobs inclui listagem de todos os ambientes criados, verificação de status (running, exited, error), atualização de status sob demanda, parada de execução e remoção completa de jobs e seus dados.

## 🏗️ Arquitetura

### Componentes Principais

A arquitetura do sistema é composta por diversos componentes integrados. O **Vagrant + VirtualBox** gerencia a máquina virtual Ubuntu 22.04 com 2 CPUs e 4GB de RAM, com provisionamento automatizado de todas as dependências. O **Docker** fornece isolamento através de namespaces do Linux (PID, Network, Mount, UTS, IPC) e controle de recursos via cgroups (CPU, memória, IO).

O **Flask** (Python) implementa o backend da aplicação web com rotas RESTful para todas as operações, enquanto o **Apache HTTP Server** atua como reverse proxy para a aplicação Flask, oferecendo maior robustez e segurança. O **MySQL** persiste informações dos jobs (configuração, status, logs) de forma permanente.

### Fluxo de Dados

```
Cliente (Browser)
    ↓
Apache (porta 80) - Reverse Proxy
    ↓
Flask (porta 5000) - Aplicação Web
    ↓
Docker Engine - Gerenciamento de Containers
    ↓
MySQL - Persistência de Dados
```

### Isolamento e Controle de Recursos

Cada job é executado em um **container Docker isolado** com os seguintes controles:

**Namespaces**: Isolamento de processos (PID), rede (Network), sistema de arquivos (Mount), hostname (UTS), comunicação inter-processos (IPC) e usuários (User).

**Cgroups**: Limite de CPU através do parâmetro `--cpus` que utiliza o CFS (Completely Fair Scheduler), limite de memória via `--memory` com enforcement pelo kernel, e controle de IO através de `--blkio-weight` para priorização de operações de disco.

**Logs**: Redirecionamento de stdout e stderr para arquivos individuais montados via volume Docker, garantindo persistência mesmo após remoção do container.

## 🚀 Instalação e Uso

### Pré-requisitos

Para executar o projeto, você precisa ter instalado:

- **Vagrant** (versão 2.0+)
- **VirtualBox** (versão 6.0+)
- **Git** para clonar o repositório
- Pelo menos **4GB de RAM** disponível para a VM
- Pelo menos **2 núcleos de CPU** disponíveis

### Instalação

Clone o repositório do projeto:

```bash
git clone https://github.com/Enzofmcs/cloud-project2.git
cd cloud-project2
```

Inicie a máquina virtual e o provisionamento automático (este processo pode levar alguns minutos na primeira execução):

```bash
vagrant up
```

O provisionamento automático irá instalar e configurar todos os componentes necessários, incluindo Docker, MySQL, Apache, Flask e suas dependências, além de inicializar o banco de dados e configurar os serviços.

### Acesso à Aplicação

Após a conclusão do provisionamento, a aplicação estará disponível em:

- **Interface Web (via Apache)**: http://localhost:8080
- **Interface Web (Flask direto)**: http://localhost:5000

Recomenda-se usar a porta 8080 (Apache) para uma experiência mais próxima de produção.

## 📖 Guia de Uso

### Criando um Job

Para criar um novo job, preencha o formulário na página principal com as seguintes informações:

**Nome do Job**: Identificador único para o job (ex: `meu-teste-1`). Este nome será usado como nome do container Docker.

**Imagem Docker**: Imagem base a ser utilizada (ex: `ubuntu`, `python:3.9`, `nginx`, `alpine`). A imagem será baixada automaticamente do Docker Hub se não estiver disponível localmente.

**Comando**: Comando a ser executado dentro do container (ex: `echo "Hello World" && sleep 30`, `python3 -m http.server 8000`, `while true; do date; sleep 5; done`).

**CPUs**: Número de CPUs a alocar (aceita valores decimais, ex: `0.5`, `1.0`, `2.0`). Valores decimais permitem compartilhamento fino de recursos.

**Memória (MB)**: Quantidade de memória RAM em megabytes (ex: `128`, `256`, `512`, `1024`).

**IO Weight**: Peso de IO para priorização (valores entre 10 e 1000, padrão: `500`). Valores maiores indicam maior prioridade nas operações de disco.

Clique em **"Criar Job"** e o sistema irá criar o container e iniciar a execução.

### Gerenciando Jobs

A lista de jobs exibe todos os ambientes criados com as seguintes informações: ID único do job, nome do job, status atual (running, exited, error) e data de criação.

Para cada job, você pode realizar as seguintes ações:

**Atualizar**: Sincroniza o status do job com o estado real do container Docker. Útil para verificar se um job ainda está em execução.

**Parar**: Interrompe a execução do container sem removê-lo. O job permanece no sistema com status "exited".

**Remover**: Remove completamente o container e o registro do banco de dados. Esta ação é irreversível.

**Log**: Visualiza a saída (stdout e stderr) do programa em execução. Os logs são atualizados em tempo real e exibem os últimos 20KB de saída.

### Exemplos Práticos

#### Exemplo 1: Teste Simples

Crie um job de teste que imprime uma mensagem e aguarda:

```
Nome: teste-hello
Imagem: ubuntu
Comando: echo "Hello from Cloud Job Manager!" && sleep 60
CPUs: 0.5
Memória: 128
IO Weight: 500
```

Após criar, clique em **"Log"** para ver a mensagem impressa.

#### Exemplo 2: Servidor Web

Execute um servidor web simples com Python:

```
Nome: webserver-python
Imagem: python:3.9
Comando: python3 -m http.server 8000
CPUs: 1.0
Memória: 256
IO Weight: 700
```

Este job continuará em execução como um serviço. Use **"Atualizar"** para verificar que o status permanece "running".

#### Exemplo 3: Script de Monitoramento

Execute um script que imprime a data a cada 5 segundos:

```
Nome: monitor-time
Imagem: alpine
Comando: while true; do date; sleep 5; done
CPUs: 0.2
Memória: 64
IO Weight: 300
```

Visualize o log para ver as atualizações contínuas de data/hora.

#### Exemplo 4: Processamento com Limite de Recursos

Simule um processo que consome recursos:

```
Nome: stress-test
Imagem: ubuntu
Comando: apt-get update && apt-get install -y stress && stress --cpu 1 --timeout 30s
CPUs: 0.5
Memória: 256
IO Weight: 500
```

O container estará limitado aos recursos especificados, mesmo que o programa tente usar mais.

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
cloud-project2/
├── Vagrantfile              # Configuração da VM
├── provision.sh             # Script de provisionamento
├── README.md                # Este arquivo
└── app/
    ├── app.py               # Aplicação Flask principal
    ├── requirements.txt     # Dependências Python
    ├── db_init.sql          # Schema do banco de dados
    ├── templates/           # Templates HTML (Jinja2)
    │   ├── index.html       # Página principal
    │   └── log.html         # Visualização de logs
    └── static/              # Arquivos estáticos
        └── style.css        # Estilos CSS
```

### Tecnologias Utilizadas

**Backend**: Flask 3.0 (Python 3.11), PyMySQL para conexão com MySQL, Docker SDK for Python para gerenciamento de containers.

**Frontend**: HTML5 com templates Jinja2, CSS3 com design responsivo e animações.

**Infraestrutura**: Vagrant para gerenciamento de VM, VirtualBox como hypervisor, Docker para containerização, MySQL 8.0 para persistência, Apache 2.4 como reverse proxy.

### Banco de Dados

O sistema utiliza uma tabela `jobs` no banco `execdb` com o seguinte schema:

```sql
CREATE TABLE jobs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  image VARCHAR(128) NOT NULL,
  cmd TEXT NOT NULL,
  cpus DECIMAL(3,1) NOT NULL,
  mem_mb INT NOT NULL,
  io_weight INT NOT NULL,
  log_path VARCHAR(255) NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Comandos Úteis

Para acessar a VM via SSH:

```bash
vagrant ssh
```

Para verificar containers em execução:

```bash
vagrant ssh -c "docker ps"
```

Para ver logs de um container específico:

```bash
vagrant ssh -c "docker logs <nome-do-job>"
```

Para acessar o banco de dados:

```bash
vagrant ssh -c "mysql -uexecuser -pexecpass execdb -e 'SELECT * FROM jobs;'"
```

Para reiniciar a aplicação Flask:

```bash
vagrant ssh -c "sudo systemctl restart apache2"
```

Para reprovisionar a VM (se necessário):

```bash
vagrant provision
```

Para destruir e recriar a VM:

```bash
vagrant destroy -f
vagrant up
```

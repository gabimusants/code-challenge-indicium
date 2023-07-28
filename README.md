## Para executar:
Supondo que não tenha o Airflow instalado:
```
sudo pip install apache-airflow
airflow db init
```

Para criar um usuário:
```
airflow  users  create  \
  --username  admin  \
  --firstname  Peter  \
  --lastname  Parker  \
  --role  Admin  \
  --email  spiderman@superhero.org
  ```
  
Inicie o docker-compose na pasta em que se encontra o docker-compose.yml 
`docker-compose up -d`

No terminal:
```
export AIRFLOW_HOME = -caminho da pasta do projeto-
source ind_env/bin/activate
airflow webserver -p 8080
```

Em um segundo terminal:
```
export AIRFLOW_HOME = -caminho da pasta do projeto-
source ind_env/bin/activate
airflow scheduler
```
No navegador:
<li> Abrir Airflow:</li>
0.0.0.0:8080
<li>Entrar com usuário e senha cadastrados.</li>
Crie um arquivo .env seguindo o modelo do arquivo .env.example

## Exemplo de Funcionamento
<li> Página Containers do Docker Desktop com o banco de dados Northwind e o banco de dados final da pipeline.
  
![containers](/images/docker-app-3.png)

<li> Página de login do Airflow após executar airflow webserver -p 8080 e airflow scheduler.
  
![login-airflow](/images/login-airflow-6.png)

<li> Interface do Airflow apresentando o grafo das 2 tasks requisitadas.
  
![graph](/images/graph-dag-7.png)

<li> Seção calendário que permite a visualização das datas em que as pipelines foram executadas e possíveis erros em execuções. Possibilita também que o usuário veja as futuras runs planejadas.
  
![calendar](/images/calendar-airflow-8.png)

<li> Grid apresentando a execução de uma run em uma data do passado informada por parâmetro, assim como o status de execução das 2 tasks e a data em que a run foi efetuada.
  
![grid](/images/past-date-9.png)

<li> Banco de dados final utilizado para armazenar as tabelas antes gravadas localmente.
  
![db](/images/pgAdmin-10.png)

<li> Arquivos armazenados localmente como parte da Task 1 disponíveis na pasta data/csv e data/postgres
<li> Query que mostra as orders e orders_details disponível no arquivo final_query.csv

### Possíveis Melhorias
Para um melhor funcionamento, o ideal seria permitir que todo o conteúdo do projeto fosse processado utilizando o Docker, assim não seria necessário executar o Airflow localmente, e nem se submeter a possíveis faltas de dependências locais.



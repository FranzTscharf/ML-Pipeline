# Pipeline

This readme should explain the basic usage of the pipeline.

## Getting Started
For just starting the pipline. Keep in mind you will need to have apache airflow installed via. pip.

```
airflow scheduler & airflow webserver -p 8090
```
after this there sould be a webserver available at port 8090.
### Screen-Shot
If you access the url: localhost:8090 you should see somthing simular to the above picture.
![alt text](https://i.ibb.co/Tc5ZKMS/Screen-Shot-2019-07-25-at-16-02-20.png)
![alt text](https://i.ibb.co/dPZ833M/Screen-Shot-2019-07-25-at-16-02-32.png)
## Testing the Pipeline
for testing the pipeline execute create_pipeline() for example like this:

```
cd workspace/pipeline/.../airflow/dags/
bash python3
from main import *
create_pipeline()
```
This will execute the pipeline in a sequenze way.

## Debbuging the Pipeline

View the list of dags recognices from airflow
```
airflow list_dags
```
Test Run the dag with the name "main"
```
airflow run main
```
Test a specific task inside a dag. This means we are testing the function "reset" inside the dag "main" with the execution date '01.01.2018' this can be
ignored and is not relevant for us.
```
airflow test main reset '01.01.2018'
```

## Customizing the components

### Pipeline Classes

coming soon...
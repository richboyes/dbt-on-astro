# Updates required for Admiral Business

This document outlines changes required to get this [astro](https://www.astronomer.io/docs) [DBT](https://www.getdbt.com) project running locally on your mac.

## Pre-requisites

1. A docker engine (we're going to use [colima](https://github.com/abiosoft/colima)):
    ```bash
    brew install colima
    ```
2. Copy the Netskope certificate to colima - this is a one-off:
    ```bash
    colima start
    scp certs/netskope-cert-bundle.pem colima:/tmp/netskope-cert-bundle.crt
    colima ssh -- sudo cp /tmp/netskope-cert-bundle.crt /usr/local/share/ca-certificates/.
    colima ssh -- sudo update-ca-certificates
    colima stop
    ```

## To get airflow working

1. You will need a [private key](https://docs.snowflake.com/en/user-guide/key-pair-auth) to authenticate to the Admiral Business snowflake instance; the key file should be called snowflake_key.p8 and placed in the [dbt](./dbt) folder. See the dbt [profiles.yml](./dbt/profiles.yml) file to see how its referenced, along with [docker-compose.override.yml](./docker-compose.override.yml)
2. Start `colima` in a separate terminal:
    ```bash
    colima start --cpu 4 --memory 6 # as appropriate
    ```
3. Run the astro project, execute the following in the root folder:
    ```bash
    astro dev start
    ```
4. Go to http://localhost:8080 and see airflow/DAGS; you will need to set up Snowflake credentials in there, and then execute a DAG.
5. Stop astro:
    ```bash
    astro dev stop
    ```
6. Stop colima:
    ```bash
    colima stop
    ```    


  

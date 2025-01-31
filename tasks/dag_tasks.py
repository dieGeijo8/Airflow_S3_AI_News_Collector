from datetime import timedelta, datetime
from newsapi import NewsApiClient
import boto3
import json

# connect to the news api to get english articles
def get_data_eng():
    newsapi = NewsApiClient(api_key='')

    yesterday_iso_format = (datetime.now() - timedelta(days=1)).date().isoformat()

    en_ai_articles = newsapi.get_everything(q='AI OR Artificial Intelligence',
                                            from_param = yesterday_iso_format,
                                            language = 'en',
                                            sort_by='relevancy') 

    return en_ai_articles

# connect to the news api to get italian articles
def get_data_ita():
    newsapi = NewsApiClient(api_key='')

    yesterday_iso_format = (datetime.now() - timedelta(days=1)).date().isoformat()

    it_ia_articles = newsapi.get_everything(q='IA OR Intelligenza Artificiale',
                                            from_param = yesterday_iso_format,
                                            language = 'it',
                                            sort_by='relevancy') 

    return it_ia_articles

# extract and mix in a unique dictionary english and italian articles
def transform_data(task_instance):
    en_ai_articles = task_instance.xcom_pull(task_ids = "get_data_eng")
    it_ia_articles = task_instance.xcom_pull(task_ids = "get_data_ita")

    if en_ai_articles['status'] != 'ok':
        en_ai_articles = ['Error during the data collection.']
    elif en_ai_articles['totalResults'] == 0:
        en_ai_articles = ['No news for the day.']
    else:
        en_ai_articles = en_ai_articles['articles']
    
    if it_ia_articles['status'] != 'ok':
        it_ia_articles = ['Error during the data collection.']
    elif it_ia_articles['totalResults'] == 0:
        it_ia_articles = ['No news for the day.']
    else:
        it_ia_articles = it_ia_articles['articles']

    ai_articles = {'eng':en_ai_articles, 'ita':it_ia_articles}

    return ai_articles

# upload the dictionary to the target s3 bucket with IAM user S3 full access policy
def upload_data(task_instance):
    ai_articles = task_instance.xcom_pull(task_ids = "transform_data")

    AWS_ACCESS_KEY = ''
    AWS_SECRET_KEY = ''
    BUCKET_NAME = ''
    yesterday_iso_format = (datetime.now() - timedelta(days=1)).date().isoformat()

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    json_data = json.dumps(ai_articles)
    object_key = f"{yesterday_iso_format}_ai_articles_airflow.json"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Body=json_data,
        ContentType="application/json", 
        ServerSideEncryption="AES256"
    )
from openai import OpenAI
from aws_bedrock_token_generator import provide_token

client = OpenAI(
    base_url="https://bedrock-mantle.us-east-1.api.aws/v1",
    api_key=provide_token(region="us-east-1"),
)

models = client.models.list()

for model in models.data:
    print(model.id)
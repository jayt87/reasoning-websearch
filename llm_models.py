from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize LLMs
llm_reasoning = init_chat_model(
    "azure_openai:o4-mini",
    azure_deployment="o4-mini",
)

llm_reasoning2 = AzureChatOpenAI(
    azure_deployment="o3-pro",
    model="o3-pro",
    api_version="2025-04-01-preview",
    use_responses_api=True,
)

grokllm = init_chat_model(
    "azure_openai:grok-3",
    azure_deployment="grok-3",
)

llm = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment="gpt-4.1",
)

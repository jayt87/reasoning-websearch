from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize LLMs
llm_reasoningo3_pro = AzureChatOpenAI(
    azure_deployment="o3-pro",
    model="o3-pro",
    api_version="2025-04-01-preview",
    use_responses_api=True,
    reasoning={
        "effort": "high",  # can be "low", "medium", or "high"
        "summary": "auto",  # can be "auto", "concise", or "detailed"
    }
)

llm_5p1 = AzureChatOpenAI(
    azure_deployment="gpt-5.1",
    model="gpt-5.1",
    api_version="2025-04-01-preview",
    use_responses_api=True,
    reasoning={
        "effort": "high", 
        "summary": "auto", 
    }
)

grokllm = init_chat_model(
    "azure_openai:grok-4-fast-reasoning",
    azure_deployment="grok-4-fast-reasoning",
)

llm41 = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment="gpt-4.1"
)

deepseek3 = init_chat_model(
    "azure_openai:DeepSeek-V3.1",
    azure_deployment="DeepSeek-V3.1",
)
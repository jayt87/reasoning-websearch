import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from gsearch import google_search
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm_reasoning = init_chat_model(
    "azure_openai:o4-mini",
    azure_deployment="o4-mini",
)
llm_reasoning2 = init_chat_model(
    "azure_openai:o1",
    azure_deployment="o1",
)
llm = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment="gpt-4.1",
)

@tool
def gsearch(search_term: str) -> str:
    """Searches the web using a search engine."""
    results = google_search(search_term)
    return results

llm_withTools = llm.bind_tools([gsearch])

def rewrite(state: State):
    prompt = [
        {"role": "system", "content": "You are an AI assistant that must take the user question and generate a list of search terms that will be used to search the web. The search terms should be concise and focused on the technical aspects of the question. If the user asks one simple thing, you can just return the question as is. If the user asks a complex question, you should break it down into smaller parts and generate multiple search terms for each part. Keep the overlap between search terms as small as possible. Generate only the minimun necessary search terms. Return the search terms as a list of strings ['search_term1','search_term2','search_term3'] and nothing else."},
    ] + state["messages"]
    return {"messages": [ llm.invoke(prompt) ]}

def reason(state: State):
    prompt = [
        {"role": "system", "content": "You are an AI assistant that answers the user question in a very clear, accurate and concise manner. Pay attention to the technical details and provide accurate information. Mention if you don't know something."},
    ] + state["messages"]
    return {"messages": [ llm_reasoning.invoke(prompt) ]}

def reason2(state: State):
    prompt = [
        {"role": "system", "content": "You are an AI assistant that answers the user question in a very clear, accurate and concise manner. Pay attention to the technical details and provide accurate information. Mention if you don't know something."},
    ] + state["messages"]
    return {"messages": [ llm_reasoning2.invoke(prompt) ]}

def websearch(state: State):
    prompt = [
        {"role": "system", "content": "You are an AI assistant that searches the web for information to answer the search terms you receive. Use the search engine tool to find relevant information. If you receive multiple search terms, you should search for each term separately."},
    ] + state["messages"]
    response_message = llm_withTools.invoke(prompt)
    results = ""
    for tool_call in response_message.tool_calls:
        print(f"searching for: {tool_call['args']['search_term']}")
        st.write(f"searching for: {tool_call['args']['search_term']}")
        result = gsearch.invoke(tool_call)
        results += f"Search term: {tool_call['args']['search_term']}\nResult: {result.content}\n\n"
    return {"messages": [AIMessage(content=results)]}

def endsummary(state: State):
    prompt = [
        {"role": "system", "content": "You are an AI assistant that must combine all information received from different inputs to generate a response that best covers the question. You are getting results from a few LLMs and from web search. Information may be overlaping or contradicting, use your reasoning to formulate the accurate response. Focus on technical aspects and details. Keep the response less verbose."},
    ] + state["messages"]
    return {"messages": [ llm.invoke(prompt) ]}

graph_builder.add_node("rewrite", rewrite)
graph_builder.add_node("reason", reason)
graph_builder.add_node("reason2", reason2)
graph_builder.add_node("websearch", websearch)
graph_builder.add_node("endsummary", endsummary)

graph_builder.add_edge(START, "reason")
graph_builder.add_edge(START, "reason2")
graph_builder.add_edge(START, "rewrite")
graph_builder.add_edge("rewrite", "websearch")
graph_builder.add_edge(["websearch","reason","reason2"], "endsummary")
graph_builder.add_edge("endsummary", END)
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    msgs = [ {"role": "user", "content": user_input} ]
    while True:
        for event in graph.stream({"messages": msgs}):
            for name, value in event.items():
                if name.title() == "Endsummary":
                    print(f"{name.title()}: ", value["messages"][-1].content)
                    print("-" * 100)
                    return value["messages"][-1].content

st.title("AMA reasoner with web search")
user_input=st.text_area("Ask me anything!")

if st.button("Submit"):
    with st.spinner("Please wait..."):
        output = stream_graph_updates(user_input)
        st.write(output)
        st.success("Done!")
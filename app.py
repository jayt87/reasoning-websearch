import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from llm_models import llm_reasoning, llm_reasoning2, grokllm, llm
from langchain_core.tools import tool
from gsearch import google_search
from langchain_core.messages import AIMessage
from dotenv import load_dotenv
import streamlit as st
import hmac
from langgraph.checkpoint.memory import MemorySaver
from prompts import REWRITE_SYSTEM_PROMPT, REASON_SYSTEM_PROMPT, REASON2_SYSTEM_PROMPT, GROK_SYSTEM_PROMPT, WEBSEARCH_SYSTEM_PROMPT, ENDSUMMARY_SYSTEM_PROMPT
from auth import check_password

if 'memory' not in st.session_state:
    st.session_state['memory'] = MemorySaver()

memory = st.session_state.memory

config = {"configurable": {"thread_id": "1"}}

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

@tool
def gsearch(search_term: str) -> str:
    """Searches the web using a search engine."""
    results = google_search(search_term)
    return results

llm_withTools = llm.bind_tools([gsearch])

def rewrite(state: State):
    prompt = [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
    ] + state["messages"]
    return {"messages": [ llm.invoke(prompt) ]}

def reason(state: State):
    prompt = [
        {"role": "system", "content": REASON_SYSTEM_PROMPT},
    ] + state["messages"]
    return {"messages": [ llm_reasoning.invoke(prompt) ]}

def reason2(state: State):
    prompt = [
        {"role": "system", "content": REASON2_SYSTEM_PROMPT},
    ] + state["messages"]
    return {"messages": [ llm.invoke(prompt) ]}

def grok(state: State):
    prompt = [
        {"role": "system", "content": GROK_SYSTEM_PROMPT},
    ] + state["messages"]
    return {"messages": [ grokllm.invoke(prompt) ]}

def websearch(state: State):
    prompt = [
        {"role": "system", "content": WEBSEARCH_SYSTEM_PROMPT},
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
        {"role": "system", "content": ENDSUMMARY_SYSTEM_PROMPT},
    ] + state["messages"]
    return {"messages": [ llm_reasoning2.invoke(prompt) ]}

graph_builder.add_node("rewrite", rewrite)
graph_builder.add_node("reason", reason)
graph_builder.add_node("reason2", reason2)
graph_builder.add_node("grok", grok)
graph_builder.add_node("websearch", websearch)
graph_builder.add_node("endsummary", endsummary)

graph_builder.add_edge(START, "reason")
graph_builder.add_edge(START, "reason2")
graph_builder.add_edge(START, "rewrite")
graph_builder.add_edge(START, "grok")
graph_builder.add_edge("rewrite", "websearch")
graph_builder.add_edge(["websearch","reason","reason2","grok"], "endsummary")
graph_builder.add_edge("endsummary", END)
graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str):
    msgs = [ {"role": "user", "content": user_input} ]
    while True:
        for event in graph.stream({"messages": msgs},
                                config):
            for name, value in event.items():
                if name.title() == "Endsummary":
                    print(f"{name.title()}: ", value["messages"][-1].content)
                    print("-" * 100)
                    return value["messages"][-1].content

st.set_page_config(layout="wide")
#stream_graph_updates("who is pythagoras?")
if check_password():
    st.title("AMA reasoner with web search")
    user_input=st.text_area("Ask me anything!")
    
    if st.button("Submit"):
        with st.spinner("Please wait..."):
            output = stream_graph_updates(user_input)
            st.write(output)
            st.success("Done!")
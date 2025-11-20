import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from llm_models import llm_reasoningo3_pro, grokllm, llm_5p1 , llm41, deepseek3
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

if 'websearch' not in st.session_state:
    st.session_state['websearch'] = True

if 'grok' not in st.session_state:
    st.session_state['grok'] = True

if 'deepseek' not in st.session_state:
    st.session_state['deepseek'] = True

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

llm_withTools = llm41.bind_tools([gsearch])

def rewrite(state: State):
    prompt = [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
    ] + state["messages"]
    response = llm41.invoke(prompt)
    return {"messages": [ response ]}

def reason51(state: State):
    prompt = [
        {"role": "system", "content": REASON2_SYSTEM_PROMPT},
    ] + state["messages"]
    response = llm_5p1.invoke(prompt)    
    return {"messages": [ response ]}

def grok(state: State):
    prompt = [
        {"role": "system", "content": GROK_SYSTEM_PROMPT},
    ] + state["messages"]
    response = grokllm.invoke(prompt)
    return {"messages": [ response ]}

def deepseek(state: State):
    prompt = [
        {"role": "system", "content": GROK_SYSTEM_PROMPT},
    ] + state["messages"]
    response = deepseek3.invoke(prompt)
    return {"messages": [ response ]}

def websearch(state: State):
    prompt = [
        {"role": "system", "content": WEBSEARCH_SYSTEM_PROMPT},
    ] + state["messages"]
    response_message = llm_withTools.invoke(prompt)
    results = ""
    for tool_call in response_message.tool_calls:
        print(f"searching for: {tool_call['args']['search_term']}")
        st.write(f"searching web for: {tool_call['args']['search_term']}")
        result = gsearch.invoke(tool_call)
        results += f"Search term: {tool_call['args']['search_term']}\nResult: {result.content}\n\n"
    print(f"search results char len: {len(str(results))}")
    return {"messages": [AIMessage(content=results)]}

def endsummary(state: State):
    prompt = [
        {"role": "system", "content": ENDSUMMARY_SYSTEM_PROMPT},
    ] + state["messages"]
    if model_option == "gpt-5.1":
        results = {"messages": [ llm_5p1.invoke(prompt) ]}
    elif model_option == "gpt-4.1":
        results = {"messages": [ llm41.invoke(prompt) ]}
    elif model_option == "o3-pro":
        results = {"messages": [ llm_reasoningo3_pro.invoke(prompt) ]}
    return results

def dummyfunction(state: State):
    return {"messages": state["messages"]}

def isTrue(value) -> bool:
    if value == True:
        return True
    else:
        return False

graph_builder.add_node("rewrite", rewrite)
graph_builder.add_node("reason5.1", reason51)
graph_builder.add_node("grok", grok)
graph_builder.add_node("deepseek", deepseek)
graph_builder.add_node("websearch", websearch)
graph_builder.add_node("endsummary", endsummary)
graph_builder.add_node("dummynode", dummyfunction)
graph_builder.add_node("dummynode2", dummyfunction)
graph_builder.add_node("dummynode3", dummyfunction)

def route_from_start(state: State):
    """Route from START to multiple parallel nodes"""
    nodes = ["reason5.1"]
    if st.session_state['websearch']:
        nodes.append("rewrite")
    else:
        nodes.append("dummynode")
    if st.session_state['grok']:
        nodes.append("grok")
    else:
        nodes.append("dummynode2")
    if st.session_state['deepseek']:
        nodes.append("deepseek")
    else:
        nodes.append("dummynode3")
    return nodes

graph_builder.add_conditional_edges(START, route_from_start)
graph_builder.add_edge("rewrite", "websearch")
nodesToBeSummarized = ["websearch","reason5.1","grok","deepseek"]
if st.session_state['websearch']==False:
    nodesToBeSummarized.remove("websearch")
if st.session_state['grok']==False:
    nodesToBeSummarized.remove("grok")
if st.session_state['deepseek']==False:
    nodesToBeSummarized.remove("deepseek")
graph_builder.add_edge(nodesToBeSummarized, "endsummary")
graph_builder.add_edge("endsummary", END)
graph_builder.add_edge("dummynode", END)
graph_builder.add_edge("dummynode2", END)
graph_builder.add_edge("dummynode3", END)
graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str):
    msgs = [ {"role": "user", "content": user_input} ]
    while True:
        for event in graph.stream({"messages": msgs},
                                config):
            for name, value in event.items():
                st.write(f"Node: {name.title()} Done")           
                if name.title() == "Endsummary":
                    if model_option == "o3-pro" or model_option == "gpt-5.1":
                        return value["messages"][-1].content[-1]['text']
                    else:
                        return value["messages"][-1].content

st.set_page_config(layout="wide")

if check_password():
    st.title("AMA reasoner with web search")
    model_option = st.selectbox("Select a summarization model:", ["gpt-5.1","gpt-4.1","o3-pro"])
    user_input=st.text_area("Ask me anything!")
    web_search_enabled = st.checkbox("Web Search", value=True)
    grok_enabled = st.checkbox("Grok", value=True)
    deepseek_enabled = st.checkbox("DeepSeek", value=True)
    st.session_state['websearch'] = web_search_enabled
    st.session_state['grok'] = grok_enabled
    st.session_state['deepseek'] = deepseek_enabled
    
    if st.button("Submit"):
        with st.spinner("Please wait..."):
            output = stream_graph_updates(user_input)
            st.write(output)
            st.success("Done!")
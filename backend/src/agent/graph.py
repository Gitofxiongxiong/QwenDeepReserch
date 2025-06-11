import os

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

from langchain_openai import ChatOpenAI
from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

load_dotenv()


client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

query_generator_model = client.with_options({"model":"qwen-turbo","temperature":1.0,"max_retries":2})
reflection_model = client.with_options(model="qwen-plus")
answer_model = client.with_options(model="qwen-turbo")

# Nodes
def generate_query(state: OverallState, config: RunnableConfig, llm = query_generator_model) -> QueryGenerationState:
    """
    生成搜索查询。
    参数：
        state (OverallState): 整体状态，包含问题和搜索结果。
        config (RunnableConfig): 运行配置，包含模型配置。
    返回：
        str: 搜索查询。
    """
    configurable = Configuration.from_runnable_config(config)

    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    structured_llm = llm.with_structured_output(SearchQueryList)

    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )

    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """
    决定是否继续进行网络搜索。
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """
    进行网络搜索。
    参数：
        state (WebSearchState): 网络搜索状态，包含搜索查询和搜索结果。
        config (RunnableConfig): 运行配置，包含模型配置。
    返回：
        str: 搜索结果。
    """

    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    response = genai_client.models.generate_content(
        model=configurable.query_generator_model,
        contents=formatted_prompt,
        config={
            "tools": [{"google_search": {}}],
            "temperature": 0,
        },
    )
  
    resolved_urls = resolve_urls(
        response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
    )

    citations = get_citations(response, resolved_urls)
    modified_text = insert_citation_markers(response.text, citations)
    sources_gathered = [item for citation in citations for item in citation["segments"]]

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


def reflection(state: OverallState, config: RunnableConfig, llm = reflection_model) -> ReflectionState:
    """
    反思研究结果。
    参数：
        state (OverallState): 整体状态，包含问题和搜索结果。
        config (RunnableConfig): 运行配置，包含模型配置。
    返回：
        str: 反思结果。
    """
    configurable = Configuration.from_runnable_config(config)

    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model


    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )

    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """
    评估研究结果，决定下一步的行动。
    参数：
        state (ReflectionState): 反射状态，包含研究结果和循环计数。
        config (RunnableConfig): 运行配置，包含模型配置。
    返回：
        str: 下一步的行动，可能是 "web_research" 或 "finalize_answer"。
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig, llm = answer_model):
    """
    最终回答问题。
    参数：
        state (OverallState): 整体状态，包含问题和搜索结果。
        config (RunnableConfig): 运行配置，包含模型配置。
    返回：
        str: 最终的回答。
    """
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # 格式化
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    result = llm.invoke(formatted_prompt)

    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result.content:
            result.content = result.content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result.content)],
        "sources_gathered": unique_sources,
    }


builder = StateGraph(OverallState, config_schema=Configuration)


builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)


builder.add_edge(START, "generate_query")

builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)

builder.add_edge("web_research", "reflection")

builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)

builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")

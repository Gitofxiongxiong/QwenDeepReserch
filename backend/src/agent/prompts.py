from datetime import datetime

def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """你的目标是生成复杂且多样化的网络搜索查询。这些查询旨在用于高级自动化网络研究工具，该工具能够分析复杂的结果、跟踪链接并整合信息。

指令:
- 始终倾向于使用单一搜索查询，只有当原始问题要求多个方面或元素并且一个查询不够时才添加另一个查询。
- 每个查询都应集中于原始问题的一个特定方面。
- 不要生成超过 {number_queries} 个查询。
- 查询应该多样化，如果主题很广泛，则生成多个查询。
- 不要生成多个类似的查询，1 个就足够了。
- 查询应确保收集最新的信息。 当前的时间是 {current_date}.

格式：
- 格式化你的响应为一个 JSON 对象，其中包含以下键:
   - "rationale": 解释为什么要生成这些查询的理由。
   - "query": 查询列表

Example:

主题: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```
Context: {research_topic}"""


web_searcher_instructions = """进行有针对性的搜索，收集最新、最可靠的关于"{research_topic}"的信息，并将其合成为可验证的文本工件。

指令:
- 查询应确保收集最新信息。当前日期为 {current_date}。
- 进行多次不同的搜索以收集全面的信息。
- 整合关键发现，同时细致追踪每条具体信息的来源。
- 输出应该是根据您的搜索结果编写的精心撰写的摘要或报告。
- 仅包含在搜索结果中找到的信息，不要编造任何信息。

Research Topic:
{research_topic}
"""

reflection_instructions = """您是一位专家研究助理，正在分析有关“{research_topic}”的摘要。

指令:
- 确定知识差距或需要深入探索的领域并生成后续查询。（1 个或多个）。
- 如果提供的摘要足以回答用户的问题，则不要生成后续查询。
- 如果存在知识差距，请生成后续查询以帮助扩展您的理解。
- 重点关注未完全涵盖的技术细节、实施细节或新兴趋势。

要求:
- 确保后续查询是独立的并且包含网络搜索所需的上下文。

输出格式:
- 按照下面的关键词将你的响应格式化为 JSON 对象：
   - "is_sufficient": 查询是否足以回答用户的问题
   - "knowledge_gap": 描述缺少什么信息或者需要补充什么信息
   - "follow_up_queries": 查询缺少信息的问题

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

仔细思考总结，找出知识缺口，并提出后续问题。然后，按照以下 JSON 格式生成输出：

总结：
{summaries}
"""

answer_instructions = """根据提供的摘要生成对用户问题的高质量答案。

指令:
- 当前的时间是 {current_date}.
- 你是多步骤研究过程的最后一步，不要提及你是最后一步。
- 您可以访问从前面的步骤收集的所有信息。
- 您有权查看该用户的问题。
- 根据提供的摘要和用户的问题生成对用户问题的高质量答案。
- 你必须在答案中正确包含摘要中的所有引用。

用户上下文：
- {research_topic}

总结:
{summaries}"""

# Qwen本地深度思考agent

### 借鉴google开源项目gemini fullstack langgraph
```
graph TD
    A(Question) --> B[generate_queries];
    B --> C[web_search];
    C -- Search Results --> D[Reflection];
    D -- Context is sufficient --> E[Answer Generation];
    E --> F(Answer);
    D -- More research needed --> C;

    %% Styling to make it look similar
    style A fill:#fff,stroke:#333,stroke-width:2px
    style F fill:#fff,stroke:#333,stroke-width:2px
    style B fill:#fff,stroke:#333,stroke-width:2px
    style C fill:#fff,stroke:#333,stroke-width:2px
    style D fill:#fff,stroke:#333,stroke-width:2px
    style E fill:#fff,stroke:#333,stroke-width:2px
   ```

### 前端
采用reactjs和twelwindcss
使用uvicorn和fastapi来启动前端
### 后端
采用langgraph实现agent
### 部署
docker
或者
make直接启动
# Qwen本地深度思考agent

### 借鉴google开源项目gemini fullstack langgraph
```
( Question )
     |
     v
[ generate_queries ]
     |
     v
+->[ web_search ]
|    |
|    | Search Results
|    v
|  [ Reflection ]
|    |
|    +---- (If "More research needed")
|    |
|    v (If "Context is sufficient")
|
[ Answer Generation ]
     |
     v
( Answer )
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
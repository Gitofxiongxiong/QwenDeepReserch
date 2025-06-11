
import pathlib
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import fastapi.exceptions

# 创建 FastAPI 应用程序
app = FastAPI()


def create_frontend_router(build_dir="../frontend/dist"):
    """
    创建前端路由
    参数：
        build_dir: 前端构建目录的路径
    返回：
        前端路由
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # 前端静态文件的路径

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# 挂载前端路由
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)

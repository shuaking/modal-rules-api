import modal
import os
from pathlib import Path
from datetime import datetime

# 定义 Modal App
app = modal.App("ai-skills-api")

# 定义容器镜像（最小化，只包含必要依赖）
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

# Skill 文件存储卷（持久化）
skills_volume = modal.Volume.from_name("ai-skills", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/skills": skills_volume},
    min_containers=1,  # 保持一个实例热启动，避免冷启动延迟
)
@modal.asgi_app()
def web():
    """FastAPI Web 应用"""
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import PlainTextResponse
    from pydantic import BaseModel
    from typing import Optional
    import json
    
    # API 响应模型
    class SkillResponse(BaseModel):
        skill_name: str
        content: str
        version: Optional[str]
        last_updated: Optional[str]
    
    api = FastAPI(title="AI Skills API", version="1.0")
    
    # 添加 CORS 中间件
    from fastapi.middleware.cors import CORSMiddleware
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有请求头
    )
    
    @api.get("/")
    async def root():
        return {
            "message": "AI Skills API",
            "endpoints": [
                "/skills/{name}",
                "/skills",
                "/skills/{name}/version",
                "/health"
            ],
            "usage": "curl https://your-app.modal.run/skills/dev-service"
        }
    
    @api.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "skills_count": len(list(Path("/skills").glob("*.md")))
        }
    
    @api.get("/skills/{skill_path:path}", response_class=PlainTextResponse)
    async def get_skill(skill_path: str, request: Request):
        """获取指定路径的 Skill 文件，支持子目录（如 'python/expert'）"""
        # 如果请求的是不带扩展名的路径，尝试添加 .md
        if not skill_path.endswith(".md"):
            skill_path += ".md"
            
        skill_file = f"/skills/{skill_path}"
        
        # 检查文件是否存在
        if not os.path.exists(skill_file):
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_path}' not found."
            )
        
        # 读取文件内容
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    @api.get("/skills")
    async def list_skills():
        """递归列出所有可用 Skill"""
        skills_dir = Path("/skills")
        skill_files = []
        
        # 递归遍历所有 .md 文件
        for f in skills_dir.rglob("*.md"):
            if f.name != "README.md":
                # 获取相对路径作为 skill 名称，例如 "python/expert"
                rel_path = f.relative_to(skills_dir)
                skill_name = str(rel_path.with_suffix("")).replace("\\", "/") # 统一使用正斜杠
                
                stat = f.stat()
                version = "unknown"
                try:
                    with open(f, 'r', encoding='utf-8') as rf:
                        for line in rf:
                            if line.lower().startswith("version:"):
                                version = line.split(":", 1)[1].strip()
                                break
                except:
                    pass
                
                skill_files.append({
                    "name": skill_name,
                    "path": f"/skills/{skill_name}",
                    "category": rel_path.parent.name if rel_path.parent.name else "root",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "version": version
                })
        
        return {
            "skills": sorted(skill_files, key=lambda x: x["name"]),
            "count": len(skill_files)
        }
    
    @api.get("/skills/{skill_path:path}/version")
    async def get_skill_version(skill_path: str):
        """获取 Skill 版本信息"""
        if not skill_path.endswith(".md"):
            skill_path += ".md"
            
        skill_file = f"/skills/{skill_path}"
        
        if not os.path.exists(skill_file):
            raise HTTPException(status_code=404, detail=f"Skill '{skill_path}' not found")
        
        version = "unknown"
        last_updated = None
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.lower().startswith("version:"):
                        version = line.split(":", 1)[1].strip()
                    if line.lower().startswith("last_updated:"):
                        last_updated = line.split(":", 1)[1].strip()
        except:
            pass
        
        # 移除 .md 后缀用于返回 clean name
        clean_name = skill_path[:-3] if skill_path.endswith(".md") else skill_path
        
        return {
            "skill_name": clean_name,
            "version": version,
            "last_updated": last_updated,
            "url": f"/skills/{clean_name}"
        }
    
    def list_available_skills():
        """辅助函数：列出可用 Skill"""
        skills_dir = Path("/skills")
        return [f.stem for f in skills_dir.glob("*.md") if f.name != "README.md"]
    
    return api

# 本地测试入口
@app.local_entrypoint()
def main():
    """本地测试服务器"""
    print("🚀 Starting local AI Skills API server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📋 Available endpoints:")
    print("   GET /              - API info")
    print("   GET /health        - Health check")
    print("   GET /skills        - List all skills")
    print("   GET /skills/{name} - Get specific skill")
    print("   GET /skills/{name}/version - Get skill version")
    print("\nPress Ctrl+C to stop")
    
    import uvicorn
    uvicorn.run(web, host="0.0.0.0", port=8000)

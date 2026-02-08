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
    
    @api.get("/skills/{skill_name}", response_class=PlainTextResponse)
    async def get_skill(skill_name: str, request: Request):
        """获取指定名称的 Skill 文件"""
        skill_file = f"/skills/{skill_name}.md"
        
        # 检查文件是否存在
        if not os.path.exists(skill_file):
            raise HTTPException(
                status_code=404,
                detail=f"Skill '{skill_name}' not found. Available skills: {list_available_skills()}"
            )
        
        # 读取文件内容
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    @api.get("/skills")
    async def list_skills():
        """列出所有可用 Skill"""
        skills_dir = Path("/skills")
        skill_files = []
        
        for f in skills_dir.glob("*.md"):
            if f.name != "README.md":
                skill_name = f.stem
                stat = f.stat()
                # 尝试从文件头部提取版本信息
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
                    "path": f"/skills/{f.name}",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "version": version
                })
        
        return {
            "skills": sorted(skill_files, key=lambda x: x["name"]),
            "count": len(skill_files)
        }
    
    @api.get("/skills/{skill_name}/version")
    async def get_skill_version(skill_name: str):
        """获取 Skill 版本信息"""
        skill_file = f"/skills/{skill_name}.md"
        if not os.path.exists(skill_file):
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        
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
        
        return {
            "skill_name": skill_name,
            "version": version,
            "last_updated": last_updated,
            "url": f"/skills/{skill_name}"
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

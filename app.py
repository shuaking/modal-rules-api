import modal
import os
from pathlib import Path
from datetime import datetime

# 定义 Modal App
app = modal.App("ai-rules-api")

# 定义容器镜像（最小化，只包含必要依赖）
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "uvicorn")
)

# 规则文件存储卷（持久化）
rules_volume = modal.Volume.from_name("ai-rules", create_if_missing=True)

# API 响应模型
from pydantic import BaseModel
from typing import Optional

class RuleResponse(BaseModel):
    rule_type: str
    content: str
    version: Optional[str]
    last_updated: Optional[str]

@app.function(
    image=image,
    volumes={"/rules": rules_volume},
    min_containers=1,  # 保持一个实例热启动，避免冷启动延迟
)
@modal.asgi_app()
def web():
    """FastAPI Web 应用"""
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import PlainTextResponse
    import json
    
    api = FastAPI(title="AI Rules API", version="1.0")
    
    @api.get("/")
    async def root():
        return {
            "message": "AI Rules API",
            "endpoints": [
                "/rules/{type}",
                "/rules",
                "/rules/{type}/version",
                "/health"
            ],
            "usage": "curl https://your-app.modal.run/rules/dev-service"
        }
    
    @api.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "rules_count": len(list(Path("/rules").glob("*.md")))
        }
    
    @api.get("/rules/{rule_type}", response_class=PlainTextResponse)
    async def get_rule(rule_type: str, request: Request):
        """获取指定类型的规则文件"""
        rule_file = f"/rules/{rule_type}.md"
        
        # 检查文件是否存在
        if not os.path.exists(rule_file):
            raise HTTPException(
                status_code=404,
                detail=f"Rule '{rule_type}' not found. Available rules: {list_available_rules()}"
            )
        
        # 读取文件内容
        with open(rule_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    @api.get("/rules")
    async def list_rules():
        """列出所有可用规则"""
        rules_dir = Path("/rules")
        rule_files = []
        
        for f in rules_dir.glob("*.md"):
            if f.name != "README.md":
                rule_type = f.stem
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
                
                rule_files.append({
                    "type": rule_type,
                    "path": f"/rules/{f.name}",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "version": version
                })
        
        return {
            "rules": sorted(rule_files, key=lambda x: x["type"]),
            "count": len(rule_files)
        }
    
    @api.get("/rules/{rule_type}/version")
    async def get_rule_version(rule_type: str):
        """获取规则版本信息"""
        rule_file = f"/rules/{rule_type}.md"
        if not os.path.exists(rule_file):
            raise HTTPException(status_code=404, detail=f"Rule '{rule_type}' not found")
        
        version = "unknown"
        last_updated = None
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.lower().startswith("version:"):
                        version = line.split(":", 1)[1].strip()
                    if line.lower().startswith("last_updated:"):
                        last_updated = line.split(":", 1)[1].strip()
        except:
            pass
        
        return {
            "rule_type": rule_type,
            "version": version,
            "last_updated": last_updated,
            "url": f"/rules/{rule_type}"
        }
    
    def list_available_rules():
        """辅助函数：列出可用规则"""
        rules_dir = Path("/rules")
        return [f.stem for f in rules_dir.glob("*.md") if f.name != "README.md"]
    
    return api

# 本地测试入口
@app.local_entrypoint()
def main():
    """本地测试服务器"""
    print("🚀 Starting local AI Rules API server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📋 Available endpoints:")
    print("   GET /              - API info")
    print("   GET /health        - Health check")
    print("   GET /rules         - List all rules")
    print("   GET /rules/{type}  - Get specific rule")
    print("   GET /rules/{type}/version - Get rule version")
    print("\nPress Ctrl+C to stop")
    
    import uvicorn
    uvicorn.run(web, host="0.0.0.0", port=8000)
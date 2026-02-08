import modal
import os

# 连接到 Volume
vol = modal.Volume.from_name("ai-rules")

# 规则文件列表
rules = [
    "rules/dev-service.md",
    "rules/dev-repo.md"
]

# 上传每个文件
for rule_file in rules:
    if os.path.exists(rule_file):
        # 读取文件内容（二进制）
        with open(rule_file, 'rb') as f:
            content = f.read()
        
        # 写入 Volume（使用 write_file）
        remote_path = f"/{os.path.basename(rule_file)}"
        vol.write_file(remote_path, content)
        print(f"✅ 已上传: {rule_file} -> {remote_path}")
    else:
        print(f"❌ 文件不存在: {rule_file}")

print("\n✨ 所有文件上传完成！")
print("📋 运行 'modal volume ls ai-rules' 验证")
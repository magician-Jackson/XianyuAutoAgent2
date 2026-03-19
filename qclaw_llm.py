"""
QClaw LLM 适配器 - 当收到闲鱼买家消息时通知用户，人工决定回复
"""
import requests
import os
import sys
import json

def notify_qclaw_message(buyer_name: str, item_id: str, message: str):
    """通过 QClaw 发送消息通知"""
    try:
        # 构造通知消息
        notification = f"""📩 闲鱼买家消息提醒！

买家：{buyer_name}
商品ID：{item_id}
消息内容：{message}

请生成一个合适的回复并告诉我。"""
        
        # 尝试通过本地 API 发送（如果可用）
        # 这里只是打印，实际通知通过控制台输出
        print(f"\n{'='*60}")
        print(f"📩 闲鱼买家消息")
        print(f"{'='*60}")
        print(f"买家：{buyer_name}")
        print(f"商品ID：{item_id}")
        print(f"消息：{message}")
        print(f"{'='*60}")
        print(f"请在 QClaw 中回复此买家\n")
        
    except Exception as e:
        print(f"通知失败: {e}")


class QClawCompletions:
    """模拟 OpenAI 的 chat.completions 接口"""
    def __init__(self):
        pass
        
    def create(self, **kwargs):
        messages = kwargs.get("messages", [])
        
        system_prompt = ""
        user_message = ""
        
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            elif msg.get("role") == "user":
                user_message = msg.get("content", "")
        
        # 打印通知
        print(f"\n{'='*60}")
        print(f"📩 闲鱼买家消息")
        print(f"{'='*60}")
        print(f"消息内容：{user_message}")
        print(f"{'='*60}")
        print(f"\n请在 QClaw 中回复此买家\n")
        
        sys.stdout.flush()
        
        # 返回一个提示消息，不会自动发送
        return self._mock_response("请手动回复")
    
    def _mock_response(self, content):
        class Choice:
            def __init__(self, text):
                self.message = type('obj', (object,), {"content": text})()
                
        class MockResponse:
            def __init__(self, text):
                self.choices = [Choice(text)]
                
        return MockResponse(content)


class QClawChat:
    """模拟 OpenAI 的 chat 接口"""
    def __init__(self):
        pass
        
    @property
    def completions(self):
        return QClawCompletions()


class OpenAI:
    """OpenAI 客户端替代品"""
    def __init__(self, **kwargs):
        pass
        
    @property
    def chat(self):
        return QClawChat()

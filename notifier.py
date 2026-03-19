"""
闲鱼消息通知器 - 当收到买家消息时通知 QClaw 来帮你回复
"""
import requests
import json

QCLAW_URL = "http://127.0.0.1:28789"

def notify_qclaw(buyer_name: str, item_id: str, message: str):
    """通知 QClaw 有新消息"""
    # 构造一条消息发送到 QClaw
    notification = f"""📩 闲鱼有新消息！

买家：{buyer_name}
商品ID：{item_id}
消息内容：{message}

请生成一个合适的回复。"""
    
    print(f"\n{'='*50}")
    print(f"🛍️ 闲鱼买家消息")
    print(f"{'='*50}")
    print(f"买家：{buyer_name}")
    print(f"商品：{item_id}")
    print(f"消息：{message}")
    print(f"{'='*50}\n")
    
    # 尝试通过 webhook 或其他方式通知（这里直接打印，QClaw 会看到）
    return True

def get_reply_from_qclaw(buyer_name: str, item_id: str, message: str, history: str = "") -> str:
    """
    从 QClaw 获取回复
    由于无法直接调用 API，这里返回 None 表示需要人工回复
    """
    # 显示消息等待人工回复
    print(f"\n⚠️ 需要人工回复，请通过 QClaw 手动回复买家\n")
    return None  # 返回 None 表示需要人工介入

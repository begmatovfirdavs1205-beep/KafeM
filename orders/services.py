import json
import os
import urllib.error
import urllib.request


def notify_new_order(order):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return
    lines = [f"Новый заказ {order.order_number}", f"Клиент: {order.customer_name}, {order.phone}"]
    lines.extend(f"• {item.product_name} × {item.quantity} — {item.line_total} сомони" for item in order.items.all())
    lines.extend([f"Итого: {order.total} сомони", f"Адрес: {order.address or 'самовывоз'}"])
    body = json.dumps({"chat_id": chat_id, "text": "\n".join(lines)}).encode("utf-8")
    request = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(request, timeout=3).read()
    except (urllib.error.URLError, TimeoutError, OSError):
        # An unavailable optional notification service must never interrupt checkout.
        pass

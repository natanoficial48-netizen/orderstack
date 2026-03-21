import requests
import time
import os

API_URL = "http://127.0.0.1:8000"
RESTAURANT_ID = 1
INTERVALO = 5

# Configuracao da impressora
# O cliente define o MAC address da impressora Bluetooth dele
IMPRESSORA_MAC = "00:00:00:00:00:00"  # trocar pelo MAC da impressora
USAR_IMPRESSORA = False  # mudar para True quando tiver impressora

def get_impressora():
    if not USAR_IMPRESSORA:
        return None
    try:
        from escpos.printer import Bluetooth
        return Bluetooth(IMPRESSORA_MAC)
    except Exception as e:
        print(f"Impressora nao conectada: {e}")
        return None

def buscar_pedidos_pendentes():
    response = requests.get(f"{API_URL}/orders/restaurant/{RESTAURANT_ID}")
    if response.status_code == 200:
        pedidos = response.json()
        return [p for p in pedidos if p["status"] == "pendente"]
    return []

def atualizar_status(order_id, status):
    requests.patch(f"{API_URL}/orders/{order_id}/status?status={status}")

def exibir_pedido(pedido):
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 40)
    print(f"  NOVO PEDIDO #{pedido['id']}")
    print("=" * 40)
    print(f"  Mesa/Usuario: {pedido['user_id']}")
    print(f"  Horario: {pedido['created_at']}")
    print("-" * 40)
    for item in pedido["items"]:
        print(f"  {item['quantity']}x  Produto #{item['product_id']}  - R$ {item['unit_price']:.2f}")
    print("-" * 40)
    print(f"  TOTAL: R$ {pedido['total']:.2f}")
    print("=" * 40)

def imprimir_pedido(pedido, impressora):
    if impressora is None:
        return
    try:
        impressora.set(align="center", bold=True, width=2, height=2)
        impressora.text("PEDIDO #{}\n".format(pedido["id"]))
        impressora.set(align="left", bold=False, width=1, height=1)
        impressora.text("-" * 32 + "\n")
        impressora.text(f"Mesa/Usuario: {pedido['user_id']}\n")
        impressora.text(f"Horario: {pedido['created_at']}\n")
        impressora.text("-" * 32 + "\n")
        for item in pedido["items"]:
            impressora.text(f"{item['quantity']}x Produto #{item['product_id']}\n")
            impressora.text(f"   R$ {item['unit_price']:.2f}\n")
        impressora.text("-" * 32 + "\n")
        impressora.set(bold=True)
        impressora.text(f"TOTAL: R$ {pedido['total']:.2f}\n")
        impressora.cut()
    except Exception as e:
        print(f"Erro ao imprimir: {e}")

def main():
    print("Cozinha online! Aguardando pedidos...")
    if USAR_IMPRESSORA:
        print(f"Impressora: {IMPRESSORA_MAC}")
    else:
        print("Impressora: desativada (configure IMPRESSORA_MAC e USAR_IMPRESSORA=True)")

    pedidos_vistos = set()
    impressora = get_impressora()

    while True:
        pedidos = buscar_pedidos_pendentes()

        for pedido in pedidos:
            if pedido["id"] not in pedidos_vistos:
                exibir_pedido(pedido)
                imprimir_pedido(pedido, impressora)
                atualizar_status(pedido["id"], "em preparo")
                pedidos_vistos.add(pedido["id"])
                print(f"Pedido #{pedido['id']} marcado como 'em preparo'")

        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()

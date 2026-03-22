import customtkinter as ctk
import threading
import requests
import time
import base64
import json
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CozinhaApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("OrderStack Cozinha")
        self.root.geometry("480x620")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#070707")
        self.token = None
        self.restaurant_id = None
        self.restaurant_name = None
        self.running = False
        self.pedidos_vistos = set()
        self.BASE_URL = "https://orderstack.onrender.com"
        self.build_login()
        self.root.mainloop()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def build_login(self):
        self.clear()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="OrderStack", font=ctk.CTkFont("Syne", 36, "bold"), text_color="#ff4500").pack(pady=(0,2))
        ctk.CTkLabel(frame, text="COZINHA", font=ctk.CTkFont("Syne", 11), text_color="#333333").pack()
        ctk.CTkLabel(frame, text="", fg_color="transparent").pack(pady=14)
        ctk.CTkLabel(frame, text="EMAIL", font=ctk.CTkFont(size=10), text_color="#555555").pack(anchor="w")
        self.email_var = ctk.StringVar()
        ctk.CTkEntry(frame, textvariable=self.email_var, width=320, height=44, font=ctk.CTkFont(size=13), fg_color="#111111", border_color="#222222", border_width=1, corner_radius=8).pack(pady=(4,12))
        ctk.CTkLabel(frame, text="SENHA", font=ctk.CTkFont(size=10), text_color="#555555").pack(anchor="w")
        self.senha_var = ctk.StringVar()
        senha_entry = ctk.CTkEntry(frame, textvariable=self.senha_var, show="*", width=320, height=44, font=ctk.CTkFont(size=13), fg_color="#111111", border_color="#222222", border_width=1, corner_radius=8)
        senha_entry.pack(pady=(4,24))
        senha_entry.bind("<Return>", lambda e: self.fazer_login())
        self.btn_login = ctk.CTkButton(frame, text="CONECTAR", command=self.fazer_login, width=320, height=48, font=ctk.CTkFont("Syne", 13, "bold"), fg_color="#ff4500", hover_color="#ff5a1f", corner_radius=8)
        self.btn_login.pack()
        self.status_var = ctk.StringVar(value="")
        ctk.CTkLabel(frame, textvariable=self.status_var, font=ctk.CTkFont(size=11), text_color="#ff4500", wraplength=300).pack(pady=12)

    def fazer_login(self):
        email = self.email_var.get().strip()
        senha = self.senha_var.get().strip()
        if not email or not senha:
            self.status_var.set("Preencha email e senha")
            return
        self.status_var.set("Conectando...")
        self.btn_login.configure(state="disabled")
        t = threading.Thread(target=self._login_thread, args=(email, senha))
        t.daemon = True
        t.start()

    def _login_thread(self, email, senha):
        try:
            res = requests.post(f"{self.BASE_URL}/auth/login", json={"email": email, "password": senha}, timeout=30)
            if res.ok:
                self.token = res.json()["access_token"]
                payload = json.loads(base64.b64decode(self.token.split('.')[1] + '=='))
                self.restaurant_id = payload.get("restaurant_id")
                role = payload.get("role")
                if role not in ["dono", "garcom"]:
                    self.root.after(0, lambda: self.status_var.set("Acesso negado para este perfil"))
                    self.root.after(0, lambda: self.btn_login.configure(state="normal"))
                    return
                rest_res = requests.get(f"{self.BASE_URL}/dashboard/restaurant/{self.restaurant_id}/info", headers={"Authorization": f"Bearer {self.token}"}, timeout=30)
                if rest_res.ok:
                    self.restaurant_name = rest_res.json().get("name", "Restaurante")
                self.root.after(0, self.build_cozinha)
            else:
                self.root.after(0, lambda: self.status_var.set("Email ou senha incorretos"))
                self.root.after(0, lambda: self.btn_login.configure(state="normal"))
        except Exception as e:
            print(f"Erro login: {e}")
            self.root.after(0, lambda: self.status_var.set("Erro de conexao. Verifique a internet."))
            self.root.after(0, lambda: self.btn_login.configure(state="normal"))

    def build_cozinha(self):
        self.clear()
        header = ctk.CTkFrame(self.root, fg_color="#111111", corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="OrderStack Cozinha", font=ctk.CTkFont("Syne", 16, "bold"), text_color="#ff4500").place(relx=0.5, rely=0.38, anchor="center")
        ctk.CTkLabel(header, text=self.restaurant_name or "Restaurante", font=ctk.CTkFont(size=10), text_color="#444444").place(relx=0.5, rely=0.72, anchor="center")
        status_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=36)
        status_frame.pack(fill="x", padx=16, pady=(8,0))
        status_frame.pack_propagate(False)
        self.live_label = ctk.CTkLabel(status_frame, text="● ONLINE", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00d97e")
        self.live_label.pack(side="left")
        self.ultima_var = ctk.StringVar(value="Aguardando pedidos...")
        ctk.CTkLabel(status_frame, textvariable=self.ultima_var, font=ctk.CTkFont(size=10), text_color="#333333").pack(side="right")
        ctk.CTkLabel(self.root, text="PEDIDOS RECEBIDOS", font=ctk.CTkFont(size=9), text_color="#333333").pack(anchor="w", padx=16, pady=(10,4))
        self.lista = ctk.CTkTextbox(self.root, fg_color="#0d0d0d", text_color="#efefef", font=ctk.CTkFont("Courier New", 11), corner_radius=8, border_width=1, border_color="#1a1a1a", wrap="word", state="disabled")
        self.lista.pack(fill="both", expand=True, padx=16, pady=(0,8))
        self.lista._textbox.tag_config("titulo", foreground="#ff4500", font=("Courier New", 12, "bold"))
        self.lista._textbox.tag_config("item", foreground="#efefef")
        self.lista._textbox.tag_config("total", foreground="#00d97e", font=("Courier New", 11, "bold"))
        self.lista._textbox.tag_config("sep", foreground="#222222")
        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=44)
        btn_frame.pack(fill="x", padx=16, pady=(0,12))
        btn_frame.pack_propagate(False)
        ctk.CTkButton(btn_frame, text="Sair da conta", command=self.sair, width=120, height=32, font=ctk.CTkFont(size=11), fg_color="#1a1a1a", hover_color="#222222", text_color="#555555", corner_radius=6).pack(side="right")
        self.running = True
        t = threading.Thread(target=self._polling_loop)
        t.daemon = True
        t.start()

    def sair(self):
        self.running = False
        self.token = None
        self.restaurant_id = None
        self.pedidos_vistos = set()
        self.build_login()

    def _polling_loop(self):
        while self.running:
            try:
                res = requests.get(
                    f"{self.BASE_URL}/orders/restaurant/{self.restaurant_id}/nao-impressos",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=30
                )
                if res.ok:
                    pedidos = res.json()
                    self.root.after(0, lambda: self.live_label.configure(text="● ONLINE", text_color="#00d97e"))
                    self.root.after(0, lambda: self.ultima_var.set(f"Atualizado: {datetime.now().strftime('%H:%M:%S')}"))
                    for pedido in pedidos:
                        if pedido["id"] not in self.pedidos_vistos:
                            self.pedidos_vistos.add(pedido["id"])
                            self.root.after(0, lambda p=pedido: self.mostrar_pedido(p))
                            self._marcar_impresso(pedido["id"])
                else:
                    print(f"Erro HTTP: {res.status_code} - {res.text}")
                    self.root.after(0, lambda: self.live_label.configure(text="● ERRO", text_color="#ff3b3b"))
            except requests.exceptions.Timeout:
                print("Timeout - servidor demorando")
                self.root.after(0, lambda: self.live_label.configure(text="● RECONECTANDO...", text_color="#ffd60a"))
            except Exception as e:
                print(f"Erro: {e}")
                self.root.after(0, lambda: self.live_label.configure(text="● OFFLINE", text_color="#ff3b3b"))
            time.sleep(5)

    def mostrar_pedido(self, pedido):
        hora = datetime.now().strftime("%H:%M")
        self.lista.configure(state="normal")
        self.lista._textbox.insert("end", "=" * 36 + "\n", "sep")
        self.lista._textbox.insert("end", f"  PEDIDO #{pedido['id']}  -  {hora}\n", "titulo")
        self.lista._textbox.insert("end", "=" * 36 + "\n", "sep")
        for item in pedido.get("items", []):
            self.lista._textbox.insert("end", f"  {item['quantity']}x  Produto #{item['product_id']}  R$ {item['unit_price']:.2f}\n", "item")
        self.lista._textbox.insert("end", "-" * 36 + "\n", "sep")
        self.lista._textbox.insert("end", f"  TOTAL: R$ {pedido['total']:.2f}\n", "total")
        self.lista._textbox.insert("end", "\n")
        self.lista.configure(state="disabled")
        self.lista._textbox.see("end")
        self.root.bell()

    def _marcar_impresso(self, order_id):
        try:
            requests.patch(f"{self.BASE_URL}/orders/{order_id}/impresso", headers={"Authorization": f"Bearer {self.token}"}, timeout=10)
        except Exception as e:
            print(f"Erro marcar impresso: {e}")

if __name__ == "__main__":
    CozinhaApp()
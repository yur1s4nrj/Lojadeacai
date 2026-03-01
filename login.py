# login.py
import tkinter as tk
from tkinter import messagebox
from db import conectar
import sistema_acai

def entrar():
    usuario = entry_user.get()
    senha = entry_pass.get()

    try:
        conn = conectar()
        c = conn.cursor()

        c.execute("SELECT codigo FROM funcionarios WHERE usuario=%s AND senha=%s",
                  (usuario, senha))
        user = c.fetchone()

        if user:
            codigo = user[0]
            messagebox.showinfo("Login", "Login realizado!")
            root.destroy()
            sistema_acai.iniciar(codigo)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    except Exception as e:
        messagebox.showerror("Erro", str(e))

root = tk.Tk()
root.title("Login")
root.geometry("300x250")
root.configure(bg="#5e2a84")

tk.Label(root, text="Usuário", bg="#5e2a84", fg="white").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Senha", bg="#5e2a84", fg="white").pack(pady=5)
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Entrar", bg="#7d3eb9", fg="white", command=entrar).pack(pady=20)

root.mainloop()

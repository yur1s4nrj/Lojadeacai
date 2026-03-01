import tkinter as tk
from tkinter import messagebox
from db import conectar

def abrir_cadastro_produto(master_root=None, combo_produto_ref=None, atualizar_callback=None):
    """
    Abre a janela para cadastrar novo produto
    
    Args:
        master_root: janela principal (opcional)
        combo_produto_ref: referência do combobox (opcional)
        atualizar_callback: função para atualizar a lista de produtos (opcional)
    """
    win = tk.Toplevel()
    win.title("Cadastrar Novo Açaí")
    win.geometry("400x300")
    win.configure(bg="#5e2a84")
    
    # Guarda referências para atualização
    win.master_root = master_root
    win.combo_produto_ref = combo_produto_ref
    win.atualizar_callback = atualizar_callback

    tk.Label(win, text="Nome:", fg="white", bg="#5e2a84").pack(pady=5)
    entry_nome = tk.Entry(win, width=25)
    entry_nome.pack()

    tk.Label(win, text="Tamanho:", fg="white", bg="#5e2a84").pack(pady=5)
    entry_tam = tk.Entry(win, width=25)
    entry_tam.pack()

    tk.Label(win, text="Preço:", fg="white", bg="#5e2a84").pack(pady=5)
    entry_preco = tk.Entry(win, width=25)
    entry_preco.pack()

    def salvar():
        nome = entry_nome.get().strip()
        tamanho = entry_tam.get().strip()
        preco = entry_preco.get().strip()

        if nome == "" or tamanho == "" or preco == "":
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        try:
            preco_float = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número!")
            return
        
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO produtos (nome, tamanho, preco) VALUES (%s, %s, %s)",
                  (nome, tamanho, preco_float))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Produto cadastrado!")
        
        
        win.destroy()
        
        
        if win.atualizar_callback:
            try:
                win.atualizar_callback()
                print("Lista de produtos atualizada após cadastro")
            except Exception as e:
                print(f"Erro ao chamar callback: {e}")
        
        elif win.combo_produto_ref:
            try:
                # Importa as funções necessárias
                from sistema_acai import carregar_produtos
                
                # Carrega os produtos atualizados
                produtos = carregar_produtos()
                lista_formatada = [f"{p[1]} {p[2]}" for p in produtos]
                
                # Atualiza o combobox
                win.combo_produto_ref['values'] = lista_formatada
                print("Combobox atualizado após cadastro")
                
            except Exception as e:
                print(f"Erro ao atualizar combobox: {e}")

    tk.Button(win, text="Salvar", bg="#7d3eb9", fg="white", width=15, command=salvar).pack(pady=20)

import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar

def abrir_gerenciar_produtos(atualizar_callback=None):

    win = tk.Toplevel()
    win.title("Excluir Produtos")
    win.geometry("600x400")
    win.configure(bg="#5e2a84")
    
    
    win.atualizar_callback = atualizar_callback

    tk.Label(win, text="🗑️ Excluir Produtos",
             font=("Arial", 16, "bold"), fg="white", bg="#5e2a84").pack(pady=10)

    
    listbox = tk.Listbox(win, width=60, height=15, font=("Arial", 10))
    listbox.pack(pady=10, padx=10)

    def carregar_produtos():
        listbox.delete(0, tk.END)
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT id, nome, tamanho, preco FROM produtos ORDER BY nome, tamanho")
        produtos = c.fetchall()
        conn.close()
        
        for prod in produtos:
            prod_id, nome, tamanho, preco = prod
            listbox.insert(tk.END, f"ID: {prod_id} - {nome} ({tamanho}) - R$ {preco:.2f}")
        
        
        total_label.config(text=f"Total: {len(produtos)} produtos")

    def excluir_produto():
        selecionado = listbox.curselection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um produto para excluir!")
            return
        
        item_texto = listbox.get(selecionado[0])
        
        
        try:
            
            partes = item_texto.split(" - ")
            id_parte = partes[0]  # "ID: 1"
            produto_id = int(id_parte.split(": ")[1])
        except:
            messagebox.showerror("Erro", "Não foi possível identificar o produto!")
            return
        
        
        confirmar = messagebox.askyesno("Confirmar Exclusão", 
                                       f"Deseja excluir este produto?\n\n{item_texto}")
        
        if confirmar:
            try:
                conn = conectar()
                c = conn.cursor()
                
                # Primeiro, obter o nome e tamanho do produto que será excluído
                c.execute("SELECT nome, tamanho FROM produtos WHERE id = %s", (produto_id,))
                produto_info = c.fetchone()
                
                if not produto_info:
                    messagebox.showerror("Erro", "Produto não encontrado!")
                    conn.close()
                    return
                
                produto_nome, produto_tamanho = produto_info
                
                # Verificar se o produto está em alguma venda
                c.execute("SELECT COUNT(*) FROM vendas WHERE produto = %s AND tamanho = %s", 
                         (produto_nome, produto_tamanho))
                total_vendas = c.fetchone()[0]
                
                if total_vendas > 0:
                    resposta = messagebox.askyesno("Produto em Vendas",
                                                 f"Este produto tem {total_vendas} venda(s).\n"
                                                 f"Deseja mesmo excluir? (As vendas históricas permanecerão)")
                    if not resposta:
                        conn.close()
                        return
                
                # Excluir o produto
                c.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                
                # Atualizar a lista na janela atual
                carregar_produtos()
                
                # Chamar callback para atualizar a tela principal
                if win.atualizar_callback:
                    win.atualizar_callback()
                    print("Callback chamado para atualizar tela principal")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    # Botões
    frame_botoes = tk.Frame(win, bg="#5e2a84")
    frame_botoes.pack(pady=10)
    
    tk.Button(frame_botoes, text="🔄 Atualizar", bg="#3498db", fg="white", width=12,
              command=carregar_produtos).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="🗑️ Excluir", bg="#e74c3c", fg="white", width=12,
              command=excluir_produto).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_botoes, text="❌ Fechar", bg="#7d3eb9", fg="white", width=12,
              command=win.destroy).pack(side=tk.LEFT, padx=5)

    # Label para total
    total_label = tk.Label(win, text="Total: 0 produtos", 
                          fg="white", bg="#5e2a84", font=("Arial", 10))
    total_label.pack(pady=5)

    # Carregar inicialmente
    carregar_produtos()

import tkinter as tk
from tkinter import ttk, messagebox
from db import conectar
import nf
import historico
import cadastro_produto
import gerenciar_produtos


def carregar_produtos():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT id, nome, tamanho, preco FROM produtos")
    lista = c.fetchall()
    conn.close()
    return lista

def atualizar_preco(event):
    global produto_selecionado

    idx = combo_produto.current()
    if idx >= 0:
        try:
            # Busca o produto correspondente na lista de produtos
            texto_selecionado = combo_produto.get()
            
            # Procura o produto na lista pelo nome e tamanho
            for produto in produtos:
                nome_completo = f"{produto[1]} {produto[2]}"
                if nome_completo == texto_selecionado:
                    produto_selecionado = produto
                    entry_preco.config(state="normal")
                    entry_preco.delete(0, tk.END)
                    entry_preco.insert(0, produto[3])
                    entry_preco.config(state="readonly")
                    break
            else:
                # Se não encontrou, limpa o campo de preço
                produto_selecionado = None
                entry_preco.config(state="normal")
                entry_preco.delete(0, tk.END)
                entry_preco.config(state="readonly")
                
        except Exception as e:
            print(f"Erro ao atualizar preço: {e}")
            produto_selecionado = None
            entry_preco.config(state="normal")
            entry_preco.delete(0, tk.END)
            entry_preco.config(state="readonly")

def adicionar_item():
    global carrinho

    if not produto_selecionado:
        messagebox.showerror("Erro", "Selecione um produto.")
        return

    quantidade = quantidade_var.get()
    if quantidade <= 0:
        messagebox.showerror("Erro", "Quantidade inválida.")
        return

    nome = produto_selecionado[1]
    tamanho = produto_selecionado[2]
    preco = produto_selecionado[3]
    subtotal = preco * quantidade

    
    item = [nome, tamanho, quantidade, preco, subtotal]
    carrinho.append(item)

    
    tabela.insert("", tk.END, values=item)

    atualizar_total()

def excluir_item():
    global carrinho
    
    # Verifica se algum item está selecionado na tabela
    item_selecionado = tabela.selection()
    if not item_selecionado:
        messagebox.showerror("Erro", "Selecione um item para excluir.")
        return
    
    # Pede confirmação
    confirmar = messagebox.askyesno("Confirmar", "Deseja realmente excluir este item do carrinho?")
    if not confirmar:
        return
    
    # CORREÇÃO: Primeiro obtém os valores dos itens ANTES de deletá-los
    itens_para_remover = []
    for item in item_selecionado:
        valores = tabela.item(item, 'values')
        if valores:
            # Converte os valores para os tipos corretos
            produto_nome = valores[0]
            tamanho = valores[1]
            quantidade = int(valores[2])
            
            # Extrai o preço (pode estar formatado como "R$ 10.00")
            preco_str = valores[3]
            preco = float(preco_str.replace('R$ ', '').replace(',', '.').strip())
            
            # Adiciona à lista de itens para remover
            itens_para_remover.append((produto_nome, tamanho, quantidade, preco))
    
    # Agora remove da tabela
    for item in item_selecionado:
        tabela.delete(item)
    
    # Remove do carrinho com base nos valores coletados
    indices_remover = []
    for i, carrinho_item in enumerate(carrinho):
        for item_valores in itens_para_remover:
            produto_nome, tamanho, quantidade, preco = item_valores
            if (str(carrinho_item[0]) == produto_nome and
                str(carrinho_item[1]) == tamanho and
                int(carrinho_item[2]) == quantidade and
                float(carrinho_item[3]) == preco):
                indices_remover.append(i)
                break
    
    # Remove do carrinho (do último para o primeiro para não alterar índices)
    for i in sorted(indices_remover, reverse=True):
        if i < len(carrinho):
            carrinho.pop(i)
    
    # Atualiza o total
    atualizar_total()
    messagebox.showinfo("Sucesso", "Item removido do carrinho!")

def limpar_carrinho():
    global carrinho
    
    if len(carrinho) == 0:
        messagebox.showinfo("Informação", "O carrinho já está vazio.")
        return
    
    confirmar = messagebox.askyesno("Confirmar", "Deseja realmente limpar todo o carrinho?")
    if not confirmar:
        return
    
    carrinho.clear()
    tabela.delete(*tabela.get_children())
    atualizar_total()
    messagebox.showinfo("Sucesso", "Carrinho limpo com sucesso!")

def atualizar_total():
    total = sum(item[4] for item in carrinho)
    label_total.config(text=f"Total: R$ {total:.2f}")

def salvar_venda():
    if len(carrinho) == 0:
        messagebox.showerror("Erro", "Carrinho vazio.")
        return

    pagamento = combo_pagamento.get()
    if pagamento == "":
        messagebox.showerror("Erro", "Escolha a forma de pagamento!")
        return

    conn = conectar()
    c = conn.cursor()

    for item in carrinho:
        nome, tam, qtd, preco, subtotal = item

        
        
        c.execute("""
            INSERT INTO vendas (produto, tamanho, preco, pagamento, funcionario, quantidade, subtotal)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, tam, preco, pagamento, codigo_func_global, qtd, subtotal))

    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", "Venda salva com sucesso!")
    carrinho.clear()
    tabela.delete(*tabela.get_children())
    atualizar_total()

def gerar_nota():
    if len(carrinho) == 0:
        messagebox.showerror("Erro", "Carrinho vazio.")
        return

    nf.gerar_pdf(carrinho, combo_pagamento.get(), codigo_func_global)


def atualizar_lista_produtos():
    """Atualiza a lista de produtos no combobox da tela principal"""
    global produtos, combo_produto, entry_preco, produto_selecionado
    
    try:
        # Salva o texto atual antes de atualizar
        texto_atual = combo_produto.get()
        
        # Recarrega produtos do banco
        produtos = carregar_produtos()
        
        # Atualizar valores do combobox
        lista_formatada = [f"{p[1]} {p[2]}" for p in produtos]
        combo_produto['values'] = lista_formatada
        
        # Tenta manter a seleção anterior se ainda existir
        if texto_atual in lista_formatada:
            combo_produto.set(texto_atual)
            # Força a atualização do preço
            atualizar_preco(None)
        else:
            # Se não existir mais, limpa
            combo_produto.set('')
            produto_selecionado = None
            entry_preco.config(state="normal")
            entry_preco.delete(0, tk.END)
            entry_preco.config(state="readonly")
        
        print(f"Lista de produtos atualizada. Total: {len(produtos)} produtos")
        
    except Exception as e:
        print(f"Erro ao atualizar lista: {e}")
        # Em caso de erro, limpa tudo
        combo_produto.set('')
        produto_selecionado = None
        entry_preco.config(state="normal")
        entry_preco.delete(0, tk.END)
        entry_preco.config(state="readonly")

def iniciar(codigo_func):
    global root, combo_produto, combo_pagamento
    global entry_preco, produtos, produto_selecionado
    global tabela, carrinho, quantidade_var
    global label_total, codigo_func_global

    codigo_func_global = codigo_func
    carrinho = []
    produto_selecionado = None

    root = tk.Tk()
    root.title("Sistema Açaí - PDV")
    root.geometry("600x750")
    root.configure(bg="#5e2a84")

    tk.Label(root, text="Sistema de Vendas Açaí",
             font=("Arial", 18, "bold"), fg="white", bg="#5e2a84").pack(pady=10)

    
    f = tk.Frame(root, bg="#5e2a84")
    f.pack(pady=10)

    tk.Label(f, text="Produto:", fg="white", bg="#5e2a84").grid(row=0, column=0)
    produtos = carregar_produtos()
    lista_formatada = [f"{p[1]} {p[2]}" for p in produtos]

    combo_produto = ttk.Combobox(f, values=lista_formatada, width=30)
    combo_produto.grid(row=0, column=1, pady=5)
    combo_produto.bind("<<ComboboxSelected>>", atualizar_preco)

    tk.Label(f, text="Preço:", fg="white", bg="#5e2a84").grid(row=1, column=0)
    entry_preco = tk.Entry(f, width=15, state="readonly")
    entry_preco.grid(row=1, column=1)

    tk.Label(f, text="Quantidade:", fg="white", bg="#5e2a84").grid(row=2, column=0)
    quantidade_var = tk.IntVar(value=1)
    tk.Entry(f, width=10, textvariable=quantidade_var).grid(row=2, column=1, pady=5)

    tk.Button(f, text="Adicionar ao Carrinho", width=25,
              command=adicionar_item, bg="#7d3eb9", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

    
    columns = ("Produto", "Tamanho", "Qtd", "Preço", "Subtotal")
    tabela = ttk.Treeview(root, columns=columns, show="headings", height=10)

    for col in columns:
        tabela.heading(col, text=col)
        tabela.column(col, width=100)

    tabela.pack(pady=10)
    
    
    frame_controle = tk.Frame(root, bg="#5e2a84")
    frame_controle.pack(pady=5)
    
    
    tk.Button(frame_controle, text="🗑️ Excluir Item", bg="#e74c3c", fg="white", width=15,
              command=excluir_item).pack(side=tk.LEFT, padx=5)
    
    
    tk.Button(frame_controle, text="🧹 Limpar Carrinho", bg="#f39c12", fg="white", width=15,
              command=limpar_carrinho).pack(side=tk.LEFT, padx=5)

    label_total = tk.Label(root, text="Total: R$ 0.00", font=("Arial", 14, "bold"),
                           fg="white", bg="#5e2a84")
    label_total.pack(pady=10)

    
    tk.Label(root, text="Pagamento:", fg="white", bg="#5e2a84").pack()
    combo_pagamento = ttk.Combobox(root, values=["Dinheiro", "Cartão"], width=20)
    combo_pagamento.pack(pady=5)

    
    frame_botoes = tk.Frame(root, bg="#5e2a84")
    frame_botoes.pack(pady=10)
    
    tk.Button(frame_botoes, text="💾 Salvar Venda", bg="#27ae60", fg="white", width=20,
              command=salvar_venda).pack(pady=5)

   
   
      
    
    tk.Button(frame_botoes, text="📋 Histórico de Vendas", bg="#9b59b6", fg="white", width=20,
          command=historico.abrir_historico).pack(pady=5)
    
    tk.Button(frame_botoes, text="➕ Cadastrar Novo Açaí", bg="#1abc9c", fg="white", width=20,
          command=lambda: cadastro_produto.abrir_cadastro_produto(root, combo_produto, atualizar_lista_produtos)).pack(pady=5)

    
    tk.Button(frame_botoes, text="🗑️ Excluir Produto", bg="#e74c3c", fg="white", width=20,
              command=lambda: gerenciar_produtos.abrir_gerenciar_produtos(atualizar_lista_produtos)).pack(pady=5)

    root.mainloop()
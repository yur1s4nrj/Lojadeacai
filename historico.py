
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from db import conectar

def abrir_historico():
    janela = tk.Toplevel()
    janela.title("Histórico de Vendas")
    janela.geometry("1000x700")  
    janela.configure(bg="#5e2a84")

    tk.Label(janela, text="📋 Histórico de Vendas",
             font=("Arial", 18, "bold"), fg="white", bg="#5e2a84").pack(pady=10)

    
    frame_filtro = tk.Frame(janela, bg="#5e2a84")
    frame_filtro.pack(pady=10, padx=10, fill="x")

    
    tk.Label(frame_filtro, text="Funcionário:", fg="white", bg="#5e2a84").grid(row=0, column=0, padx=5)
    entry_func = tk.Entry(frame_filtro, width=20)
    entry_func.grid(row=0, column=1, padx=5)

    
    tk.Label(frame_filtro, text="Data (DD/MM/AAAA):", fg="white", bg="#5e2a84").grid(row=0, column=2, padx=5)
    entry_data = tk.Entry(frame_filtro, width=15)
    entry_data.grid(row=0, column=3, padx=5)
    
    
    def inserir_data_atual():
        entry_data.delete(0, tk.END)
        entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
    
    ttk.Button(frame_filtro, text="Hoje", width=8, command=inserir_data_atual).grid(row=0, column=4, padx=5)

    
    frame_tabela = tk.Frame(janela)
    frame_tabela.pack(fill="both", expand=True, pady=10, padx=10)

    
    colunas = ("ID", "Produto", "Tamanho", "Qtd", "Preço", "Subtotal", "Pagamento", "Funcionário", "Data")
    
    
    tree = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=20)
    
    
    vsb = ttk.Scrollbar(frame_tabela, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame_tabela, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    
    frame_tabela.grid_rowconfigure(0, weight=1)
    frame_tabela.grid_columnconfigure(0, weight=1)

    
    larguras = [50, 120, 80, 50, 80, 80, 100, 120, 150]
    for i, col in enumerate(colunas):
        tree.heading(col, text=col)
        tree.column(col, width=larguras[i], anchor="center")

    def formatar_data(data_str):
        """Formata a data para exibição amigável"""
        try:
            if data_str:
                dt = datetime.strptime(str(data_str), "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return data_str
        return data_str

    def carregar_dados():
        funcionario = entry_func.get().strip()
        data_filtro = entry_data.get().strip()

        query = """
            SELECT id, produto, tamanho, quantidade, preco, subtotal, 
                   pagamento, funcionario, data 
            FROM vendas 
            WHERE 1=1
        """
        params = []

        if funcionario:
            query += " AND funcionario LIKE %s"
            params.append(f"%{funcionario}%")

        if data_filtro:
            try:
                
                data_br = datetime.strptime(data_filtro, "%d/%m/%Y")
                data_mysql = data_br.strftime("%Y-%m-%d")
                query += " AND DATE(data) = %s"
                params.append(data_mysql)
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                return

        query += " ORDER BY data DESC"

        conn = conectar()
        c = conn.cursor()
        c.execute(query, params)
        registros = c.fetchall()
        conn.close()

        
        for row in tree.get_children():
            tree.delete(row)

        
        for r in registros:
            
            valores_formatados = list(r)
            
            valores_formatados[4] = f"R$ {float(valores_formatados[4]):.2f}"  
            valores_formatados[5] = f"R$ {float(valores_formatados[5]):.2f}"  
            
            valores_formatados[8] = formatar_data(valores_formatados[8])
            
            tree.insert("", "end", values=valores_formatados)

        
        total_registros = len(tree.get_children())
        status_text = f"Total de vendas: {total_registros}"
        if funcionario or data_filtro:
            status_text += " (com filtros aplicados)"
        status_label.config(text=status_text)

    
    frame_botoes = tk.Frame(janela, bg="#5e2a84")
    frame_botoes.pack(pady=10)

    ttk.Button(frame_botoes, text="🔍 Buscar", command=carregar_dados).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes, text="🔄 Recarregar Todos", 
               command=lambda: [entry_func.delete(0, tk.END), 
                               entry_data.delete(0, tk.END), 
                               carregar_dados()]).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(frame_botoes, text="📊 Resumo", command=mostrar_resumo).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botoes, text="💾 Exportar", command=exportar_dados).pack(side=tk.LEFT, padx=5)

    
    status_label = tk.Label(janela, text="Total de vendas: 0", 
                           fg="white", bg="#5e2a84", font=("Arial", 10))
    status_label.pack(pady=5)

    
    carregar_dados()

def mostrar_resumo():
    """Mostra um resumo das vendas"""
    conn = conectar()
    c = conn.cursor()
    
    
    c.execute("SELECT COUNT(*), SUM(subtotal) FROM vendas")
    total_vendas, total_valor = c.fetchone()
    
    
    c.execute("SELECT pagamento, COUNT(*), SUM(subtotal) FROM vendas GROUP BY pagamento")
    por_pagamento = c.fetchall()
    
    
    c.execute("SELECT funcionario, COUNT(*), SUM(subtotal) FROM vendas GROUP BY funcionario ORDER BY SUM(subtotal) DESC")
    por_funcionario = c.fetchall()
    
    conn.close()
    
    
    resumo_win = tk.Toplevel()
    resumo_win.title("Resumo de Vendas")
    resumo_win.geometry("500x400")
    
    tk.Label(resumo_win, text="📊 RESUMO GERAL", font=("Arial", 16, "bold")).pack(pady=10)
    
    
    frame_geral = tk.Frame(resumo_win)
    frame_geral.pack(pady=10, fill="x", padx=20)
    tk.Label(frame_geral, text=f"Total de Vendas: {total_vendas or 0}", 
             font=("Arial", 12)).pack()
    tk.Label(frame_geral, text=f"Valor Total: R$ {float(total_valor or 0):.2f}", 
             font=("Arial", 12, "bold")).pack()
    
    
    tk.Label(resumo_win, text="Por Forma de Pagamento:", font=("Arial", 12)).pack(pady=10)
    for pag, qtd, valor in por_pagamento:
        tk.Label(resumo_win, text=f"{pag}: {qtd} vendas (R$ {float(valor or 0):.2f})").pack()

def exportar_dados():
    """Exporta os dados para um arquivo CSV"""
    import csv
    from tkinter import filedialog
    
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM vendas ORDER BY data DESC")
    dados = c.fetchall()
    conn.close()
    
    if not dados:
        messagebox.showinfo("Info", "Não há dados para exportar.")
        return
    
    arquivo = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Salvar como"
    )
    
    if arquivo:
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Produto", "Tamanho", "Preço", "Pagamento", 
                           "Funcionário", "Quantidade", "Subtotal", "Data"])
            writer.writerows(dados)
        messagebox.showinfo("Sucesso", f"Dados exportados para:\n{arquivo}")

from reportlab.pdfgen import canvas

def gerar_pdf(carrinho, pagamento, funcionario):
    pdf = canvas.Canvas("nota_fiscal.pdf")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(150, 800, "NOTA FISCAL")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"Pagamento: {pagamento}")
    pdf.drawString(50, 750, f"Funcionário: {funcionario}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 720, "Produto")
    pdf.drawString(200, 720, "Tam.")
    pdf.drawString(260, 720, "Qtd")
    pdf.drawString(310, 720, "Preço")
    pdf.drawString(380, 720, "Subtotal")

    pdf.line(45, 715, 550, 715)

    y = 690
    total_geral = 0

    pdf.setFont("Helvetica", 12)

    for item in carrinho:
        nome, tamanho, qtd, preco, subtotal = item

        pdf.drawString(50, y, nome)
        pdf.drawString(200, y, tamanho)
        pdf.drawString(260, y, str(qtd))
        pdf.drawString(310, y, f"R$ {preco:.2f}")
        pdf.drawString(380, y, f"R$ {subtotal:.2f}")

        y -= 25
        total_geral += subtotal

       
        if y < 80:
            pdf.showPage()
            y = 800

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y - 20, f"TOTAL GERAL: R$ {total_geral:.2f}")

    pdf.save()
    print("Nota fiscal gerada com sucesso!")

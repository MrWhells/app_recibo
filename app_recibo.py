import streamlit as st
from fpdf import FPDF
from datetime import datetime
from num2words import num2words

# --- CONFIGURAÇÕES DE PÁGINA ---
st.set_page_config(page_title="JujuXerox Pro - Interface Reativa", page_icon="📄")

def formatar_cpf(doc):
    numeros = "".join(filter(str.isdigit, doc))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return numeros

def formatar_extenso(valor_input):
    try:
        v = valor_input.replace("R$", "").replace(".", "").replace(",", ".").strip()
        valor_float = float(v)
        extenso = num2words(valor_float, lang='pt_BR', to='currency')
        return extenso.capitalize()
    except:
        return ""

def gerar_pdf_pro(dados):
    pdf = FPDF()
    pdf.add_page()
    cor_lilas = (186, 85, 211)
    pdf.set_draw_color(*cor_lilas)
    pdf.set_line_width(0.7)
    pdf.rect(5, 5, 200, 130)
    
    pdf.set_font("Arial", "B", 18)
    pdf.cell(140, 15, "RECIBO DE PAGAMENTO", ln=0)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(50, 12, f"R$ {dados['valor']}", border=1, ln=1, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    extenso = formatar_extenso(dados['valor'])
    doc_fmt = formatar_cpf(dados['documento'])
    
    texto_corpo = (
        f"Recebemos de {dados['nome'].upper()}, inscrito no CPF/CNPJ sob o nº {doc_fmt}, "
        f"a importância de R$ {dados['valor']} ({extenso}), referente a: {dados['servicos_formatados']}."
    ).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(190, 9, texto_corpo, align="J")
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(190, 5, "Para maior clareza, firmamos o presente recibo, que comprova o recebimento integral do valor mencionado.".encode('latin-1', 'replace').decode('latin-1'), align="J")
    
    pdf.ln(4)
    pdf.set_font("Arial", "B", 10)
    
    forma = dados['forma_pagamento']
    if forma == "PIX":
        txt_pagamento = f"Pagamento recebido via PIX (Banco: {dados['banco_pix']} / QR CODE) para JULIE MANUELI DAMASIO DA SILVA."
    else:
        txt_pagamento = f"Pagamento recebido via {forma.upper()}."
        
    pdf.multi_cell(190, 5, txt_pagamento.encode('latin-1', 'replace').decode('latin-1'), align="L")
    
    pdf.ln(15)
    pdf.set_font("Arial", "", 11)
    hoje = datetime.now()
    pdf.cell(190, 10, f"Rio de Janeiro, {hoje.day}/{hoje.month}/{hoje.year}", ln=1, align="R")
    
    pdf.ln(10)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.set_font("Arial", "B", 11)
    pdf.cell(190, 7, "JULIE MANUELI DAMASIO DA SILVA", ln=1, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(190, 5, "CNPJ: 57.646.049/0001-33 | Contato: (21) 99209-9322", ln=1, align="C")
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE REATIVA (SEM FORM) ---
st.markdown("<h1 style='text-align: center; color: #BA55D3;'>JujuXerox Pro</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([2, 1])

with col1:
    nome = st.text_input("Nome do Cliente")
    documento = st.text_input("CPF ou CNPJ")
    
    opcoes_base = ["Xerox", "Impressão", "Plastificação", "Encadernação", "Digitalização", "Outros"]
    selecionados = st.multiselect("Serviços prestados", options=opcoes_base)
    
    # APARECE NA HORA QUE CLICA EM OUTROS
    servico_extra = ""
    if "Outros" in selecionados:
        servico_extra = st.text_input("Qual o serviço específico?")
            
with col2:
    valor = st.text_input("Valor R$")
    forma_pagamento = st.radio("Pagamento", options=["PIX", "Crédito", "Débito", "Dinheiro"])
    
    # APARECE NA HORA QUE CLICA EM PIX
    banco_pix = ""
    if forma_pagamento == "PIX":
        banco_pix = st.selectbox("Selecione o Banco", options=["Infinity Pay", "Bradesco", "Mercado Pago"])

st.write("---")
# O botão agora apenas processa os dados que já foram mostrados
if st.button("GERAR RECIBO PROFISSIONAL"):
    if nome and valor and selecionados:
        lista_final = [s for s in selecionados if s != "Outros"]
        if servico_extra:
            lista_final.append(servico_extra)
        
        servicos_str = " e ".join(lista_final) if len(lista_final) == 2 else ", ".join(lista_final)
        
        dados = {
            "nome": nome, "documento": documento, "valor": valor, 
            "servicos_formatados": servicos_str, "forma_pagamento": forma_pagamento,
            "banco_pix": banco_pix
        }
        
        pdf_bytes = gerar_pdf_pro(dados)
        st.success("Recibo gerado com sucesso!")
        st.download_button("📥 BAIXAR PDF", data=pdf_bytes, file_name=f"Recibo_{nome}.pdf")
    else:
        st.warning("⚠️ Preencha os campos Nome, Valor e escolha ao menos um Serviço.")
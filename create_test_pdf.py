import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_valid_cpf():
    """Generates a mathematically valid formatted Brazilian CPF."""
    digits = [random.randint(0, 9) for _ in range(9)]
    # First digit
    s1 = sum(digits[i] * (10 - i) for i in range(9))
    d1 = (s1 * 10) % 11
    d1 = 0 if d1 >= 10 else d1
    digits.append(d1)
    # Second digit
    s2 = sum(digits[i] * (11 - i) for i in range(10))
    d2 = (s2 * 10) % 11
    d2 = 0 if d2 >= 10 else d2
    digits.append(d2)
    cpf_str = "".join(map(str, digits))
    return f"{cpf_str[0:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:11]}"

def generate_valid_cnpj():
    """Generates a mathematically valid formatted Brazilian CNPJ."""
    digits = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1] # Ending with /0001
    # First digit
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s1 = sum(digits[i] * w1[i] for i in range(12))
    d1 = s1 % 11
    d1 = 0 if d1 < 2 else 11 - d1
    digits.append(d1)
    # Second digit
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s2 = sum(digits[i] * w2[i] for i in range(13))
    d2 = s2 % 11
    d2 = 0 if d2 < 2 else 11 - d2
    digits.append(d2)
    cnpj_str = "".join(map(str, digits))
    return f"{cnpj_str[0:2]}.{cnpj_str[2:5]}.{cnpj_str[5:8]}/{cnpj_str[8:12]}-{cnpj_str[12:14]}"

def create_test_pdf(filename="test_document.pdf"):
    """
    Generates a realistic multi-page PDF document containing mockup sensitive data
    (CPFs, CNPJs, email addresses, phone numbers, bank details, and a structured table)
    for validating the PDF Extractor and Sanitizer API capabilities.
    """
    # Generate mathematically valid CPFs and CNPJs dynamically to satisfy the validation algorithm!
    cpf_carlos = generate_valid_cpf()
    cnpj_tech = generate_valid_cnpj()
    cnpj_tech_plain = "".join(c for c in cnpj_tech if c.isdigit())
    
    cpf_ana = generate_valid_cpf()
    cpf_ricardo = generate_valid_cpf()
    cpf_juliana = generate_valid_cpf()
    
    # Create the document layout
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []
    styles = getSampleStyleSheet()

    # Define custom premium styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=15,
        alignment=1 # Centered
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=25,
        alignment=1 # Centered
    )

    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=15,
        spaceAfter=10,
        borderPadding=5
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )

    # 1. HEADER
    story.append(Spacer(1, 10))
    story.append(Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇOS E COOPERAÇÃO TÉCNICA", title_style))
    story.append(Paragraph("DOCUMENTO DE TESTE PARA VALIDAR A CONFORMIDADE COM A LGPD (LEI N° 13.709/2018)", subtitle_style))
    story.append(Spacer(1, 10))

    # 2. SECTON 1: PARTIES (Contendo CPFs, CNPJs, Emails, Telefones)
    story.append(Paragraph("Seção I — Das Partes Contratantes", section_style))
    
    party1_text = (
        f"<b>CONTRATANTE:</b> <b>Carlos Alberto da Silva</b>, brasileiro, solteiro, programador, "
        f"portador da cédula de identidade RG nº 12.345.678-9 SSP/SP e inscrito no CPF sob o nº <b>{cpf_carlos}</b>, "
        f"residente e domiciliado na Rua das Cerejeiras, nº 450, Bairro Jardim, São Paulo/SP, CEP 01234-567, "
        f"com o endereço eletrônico de contato: <b>carlos.alberto@provedor.com.br</b> e telefone celular <b>(11) 98765-4321</b>."
    )
    story.append(Paragraph(party1_text, body_style))

    party2_text = (
        f"<b>CONTRATADA:</b> <b>TECH SOLUTIONS BRASIL LTDA</b>, pessoa jurídica de direito privado, "
        f"inscrita no CNPJ sob o nº <b>{cnpj_tech}</b>, com sede administrativa estabelecida na Avenida "
        f"Paulista, nº 1000, 14º andar, Bela Vista, São Paulo/SP, CEP 01310-100, neste ato representada por sua "
        f"diretora de operações, Sra. Mariana Oliveira, e-mail institucional: <b>mariana.oliveira@techsolutions.com</b>, "
        f"telefone comercial: <b>(11) 3214-5678</b>."
    )
    story.append(Paragraph(party2_text, body_style))

    story.append(Spacer(1, 10))

    # 3. SECTION 2: PAYMENT & BANK DETAILS (Contendo dados bancários)
    story.append(Paragraph("Seção II — Das Condições Financeiras e Dados de Cobrança", section_style))
    
    payment_text = (
        f"Cláusula Terceira: Pelos serviços prestados descritos na Seção I, a CONTRATANTE pagará à CONTRATADA "
        f"o valor total mensal ajustado. O pagamento deverá ser efetuado impreterivelmente até o quinto dia útil de "
        f"cada mês, mediante transferência eletrônica disponível (TED/PIX) para a conta bancária da CONTRATADA "
        f"abaixo especificada:<br/>"
        f"• <b>Banco:</b> Banco do Brasil S.A. (Código 001)<br/>"
        f"• <b>Agência Bancária:</b> <b>1234-5</b><br/>"
        f"• <b>Conta Corrente:</b> <b>98765-4</b><br/>"
        f"• <b>Chave PIX (CNPJ):</b> {cnpj_tech_plain}<br/>"
        f"Para fins de comprovação emergencial, o contato do departamento financeiro é <b>financeiro@techsolutions.com</b> "
        f"ou via telefone direto <b>0800-777-1234</b>."
    )
    story.append(Paragraph(payment_text, body_style))

    story.append(Spacer(1, 15))

    # 4. SECTION 3: STRUCTURED TABLE (Funcionários com dados sensíveis)
    story.append(Paragraph("Seção III — Do Corpo Técnico Alocado (Tabela Estruturada)", section_style))
    
    table_intro = (
        "Para a execução das atividades contratuais, a CONTRATADA alocará os seguintes colaboradores no projeto, "
        "cujos dados pessoais estão sujeitos ao tratamento seguro sob os termos da LGPD:"
    )
    story.append(Paragraph(table_intro, body_style))
    story.append(Spacer(1, 5))

    # Define the Table data
    # Header row, followed by 3 rows containing sensitive data inside cells
    table_data = [
        ["Colaborador", "CPF", "E-mail de Contato", "Telefone", "Salário Ref."],
        ["Ana Beatriz Souza", cpf_ana, "ana.souza@techsolutions.com", "(21) 91234-5678", "R$ 6.500,00"],
        ["Ricardo Martins", cpf_ricardo, "ricardo.m@provedor.org", "(31) 99887-7665", "R$ 5.200,00"],
        ["Juliana Mendes", cpf_juliana, "juliana.mendes@techsolutions.com", "(47) 97766-5544", "R$ 7.800,00"]
    ]

    # Calculate column widths to fit neatly on standard Letter page
    col_widths = [110, 95, 175, 90, 60]
    
    t = Table(table_data, colWidths=col_widths)
    
    # Beautiful table styling
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(t)
    story.append(Spacer(1, 20))

    # 5. FOOTER / SIGNATURES
    story.append(Paragraph("Por estarem de acordo, as partes assinam o presente termo de teste.", body_style))
    story.append(Spacer(1, 15))
    
    sig_data = [
        [f"_________________________________________\nCARLOS ALBERTO DA SILVA", f"_________________________________________\nTECH SOLUTIONS BRASIL LTDA"],
        [f"CPF: {cpf_carlos}", f"CNPJ: {cnpj_tech}"]
    ]
    sig_table = Table(sig_data, colWidths=[265, 265])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#475569')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    story.append(sig_table)

    # Build PDF
    doc.build(story)
    print(f"Documento de teste '{filename}' criado com sucesso em: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_test_pdf()

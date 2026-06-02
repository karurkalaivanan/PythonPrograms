from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Hello, FPDF is working!", ln=True)

pdf.output("test.pdf")
print("PDF successfully generated: test.pdf")

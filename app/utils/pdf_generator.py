# app/utils/pdf_generator.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os

def generate_mission_pdf(mission_data, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mission_{mission_data.get('id', 'inconnue')}_{timestamp}.pdf"

    output_dir = os.path.join(os.getcwd(), "exports")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    c.setFont("Helvetica", 12)
    c.drawString(margin, y, "Détails de la Mission")
    y -= 30

    for key, value in mission_data.items():
        label = key.replace("_", " ").capitalize()
        c.drawString(margin, y, f"{label} : {value}")
        y -= 20
        if y < margin:
            c.showPage()
            y = height - margin

    c.save()
    return filepath

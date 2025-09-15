from fastapi import FastAPI
from fastapi.responses import FileResponse
from fpdf import FPDF
import os

app = FastAPI()

@app.get("/facture/pdf/{mission_id}")
def generate_pdf(mission_id: int):
    # Simule la génération du fichier PDF
    file_path = f"facture_mission_{mission_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Facture pour la mission {mission_id}", ln=1, align="C")
    pdf.output(file_path)

    return FileResponse(path=file_path, filename=file_path, media_type='application/pdf')
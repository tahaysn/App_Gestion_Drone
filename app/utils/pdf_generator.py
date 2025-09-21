from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os

def generate_mission_pdf(mission_data, filename="mission.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]

    wrap_style = ParagraphStyle(
        name="wrap",
        parent=style_normal,
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        wordWrap="CJK",
    )

    # Logo : chemin fixe vers ton dossier cache
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(project_root, "..", "cache", "AirOcean_logo.jpg")
    logo_path = os.path.normpath(logo_path)
    print("📂 Chemin logo utilisé :", logo_path, "| Existe ?", os.path.exists(logo_path))

    titre = f"Facture Mission - {mission_data.get('client_nom', '')} (ID: {mission_data.get('id', '')})"

    # Header avec logo
    try:
        if os.path.exists(logo_path):
            # Adapter le logo à 4 cm largeur, hauteur proportionnelle
            from PIL import Image as PILImage
            pil_img = PILImage.open(logo_path)
            width_cm = 4 * cm
            aspect = pil_img.height / pil_img.width
            height_cm = width_cm * aspect
            logo = Image(logo_path, width=width_cm, height=height_cm)

            header_table = Table([[titre, logo]], colWidths=[12*cm, 5*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTSIZE', (0,0), (0,0), 14),
                ('FONTNAME', (0,0), (0,0), "Helvetica-Bold"),
            ]))
            elements.append(header_table)
        else:
            elements.append(Paragraph(titre, styles["Heading2"]))
    except Exception as e:
        print("⚠️ Erreur logo :", e)
        elements.append(Paragraph(titre, styles["Heading2"]))

    elements.append(Spacer(1, 12))

    # Infos client
    client_table = Table([
        ["Infos Client", ""],
        ["Client", mission_data.get("client_nom", "")],
        ["Téléphone", mission_data.get("client_telephone", "")],
        ["Province", mission_data.get("province", "")],
        ["Commune", mission_data.get("commune", "")]
    ], colWidths=[5*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 20))

    # Télépilote
    telepilote_nom = mission_data.get("telepilote", "")
    telepilote_tel = mission_data.get("telepilote_telephone", "")

    # Infos mission
    mission_table = Table([
        ["Infos Mission", ""],
        ["Date", mission_data.get("date", "")],
        ["Drone", mission_data.get("drone", "")],
        ["Taux", mission_data.get("taux", "")],
        ["Superficie", mission_data.get("superficie", "")],
        ["Superficie réelle", mission_data.get("superficie_reelle", "")],
        ["Prix unitaire", mission_data.get("prix_unitaire", "")],
        ["Avance", mission_data.get("avance", "")],
        ["Reste", mission_data.get("reste", "")],
        ["Commentaire", Paragraph(str(mission_data.get("commentaire", "")), wrap_style)],
        ["Télépilote", telepilote_nom],
        ["Téléphone Télépilote", telepilote_tel],
        ["Statut", mission_data.get("statut", "")]
    ], colWidths=[5*cm, 10*cm])
    mission_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(mission_table)

    doc.build(elements)
    return filename

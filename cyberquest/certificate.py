"""Génération de l'attestation PDF (reportlab)."""
import re
from datetime import datetime

from .settings import ATTESTATIONS_DIR, LEVELS


def generate_certificate(name, score, level, correct, answered, victory, company):
    """Crée le PDF dans attestations/ et retourne son chemin. Lève ImportError sans reportlab."""
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas

    ATTESTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    safe = re.sub(r"[^\w\-]+", "_", name).strip("_") or "joueur"
    path = ATTESTATIONS_DIR / f"attestation_{safe}_{now:%Y%m%d_%H%M%S}.pdf"

    width, height = landscape(A4)
    c = canvas.Canvas(str(path), pagesize=(width, height))
    navy, green, grey = HexColor("#0E1630"), HexColor("#00A878"), HexColor("#555B70")

    # Cadre
    c.setStrokeColor(navy)
    c.setLineWidth(6)
    c.rect(24, 24, width - 48, height - 48)
    c.setStrokeColor(green)
    c.setLineWidth(2)
    c.rect(36, 36, width - 72, height - 72)

    cx = width / 2
    c.setFillColor(green)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(cx, height - 85, company.upper())
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(cx, height - 135, "ATTESTATION DE SENSIBILISATION")
    c.drawCentredString(cx, height - 172, "À LA CYBERSÉCURITÉ")

    c.setFillColor(grey)
    c.setFont("Helvetica", 15)
    c.drawCentredString(cx, height - 225, f"{company} certifie que")
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(cx, height - 275, name)
    c.setStrokeColor(green)
    c.setLineWidth(1.5)
    c.line(cx - 180, height - 288, cx + 180, height - 288)

    c.setFillColor(grey)
    c.setFont("Helvetica", 15)
    c.drawCentredString(cx, height - 322, "a participé au programme « CyberQuest : Le Gardien du Réseau »")
    lvl = LEVELS[level - 1]
    if victory:
        line = f"et a franchi les {len(LEVELS)} étages jusqu'au poste de Responsable Sécurité."
    else:
        line = f"et a atteint l'étage {level} : {lvl['nom']} ({lvl['theme']})."
    c.drawCentredString(cx, height - 345, line)

    rate = round(100 * correct / answered) if answered else 0
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        cx, height - 395, f"Score : {score} points   |   Bonnes réponses : {correct}/{answered} ({rate} %)"
    )

    c.setFillColor(grey)
    c.setFont("Helvetica", 13)
    c.drawString(80, 85, f"Fait le {now:%d/%m/%Y}")
    c.drawRightString(width - 80, 85, f"Le Responsable Sécurité de {company}")
    c.line(width - 330, 100, width - 80, 100)
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(cx, 52, "Document généré automatiquement par CyberQuest")
    c.save()
    return path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

doc = SimpleDocTemplate(
    "/home/user/game/klayton_rogers_resume.pdf",
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.65*inch,
    bottomMargin=0.65*inch,
)

W = letter[0] - 1.5*inch  # usable width

story = []

# ── Styles ──────────────────────────────────────────────────────────────────
name_style = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=20,
                             spaceAfter=2, textColor=colors.HexColor("#1a1a1a"))
contact_style = ParagraphStyle("contact", fontName="Helvetica", fontSize=10,
                                spaceAfter=0, textColor=colors.HexColor("#444444"))
section_style = ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=10,
                                spaceBefore=10, spaceAfter=4,
                                textColor=colors.HexColor("#1a1a1a"),
                                letterSpacing=1.2)
body_style = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5,
                             leading=15, textColor=colors.HexColor("#333333"),
                             spaceAfter=6)
job_title_style = ParagraphStyle("jobtitle", fontName="Helvetica-Bold", fontSize=10.5,
                                  textColor=colors.HexColor("#1a1a1a"), leading=14)
job_date_style = ParagraphStyle("jobdate", fontName="Helvetica", fontSize=10,
                                 textColor=colors.HexColor("#555555"), leading=14,
                                 alignment=TA_RIGHT)
company_style = ParagraphStyle("company", fontName="Helvetica-Oblique", fontSize=10,
                                textColor=colors.HexColor("#444444"), spaceAfter=4, leading=13)
bullet_style = ParagraphStyle("bullet", fontName="Helvetica", fontSize=10.5,
                               leading=14, leftIndent=14, firstLineIndent=-10,
                               textColor=colors.HexColor("#333333"), spaceAfter=2)

def section_header(text):
    story.append(Spacer(1, 6))
    story.append(Paragraph(text.upper(), section_style))
    story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#cccccc"), spaceAfter=6))

def job_row(title, dates):
    t = Table([[Paragraph(title, job_title_style), Paragraph(dates, job_date_style)]],
              colWidths=[W*0.65, W*0.35])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                            ("LEFTPADDING", (0,0), (-1,-1), 0),
                            ("RIGHTPADDING", (0,0), (-1,-1), 0),
                            ("TOPPADDING", (0,0), (-1,-1), 0),
                            ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
    story.append(t)

def bullet(text):
    story.append(Paragraph(f"\u2022\u2002{text}", bullet_style))

def skill_grid(items):
    mid = (len(items) + 1) // 2
    left = items[:mid]
    right = items[mid:]
    rows = []
    for i in range(mid):
        l = f"\u25b8\u2002{left[i]}" if i < len(left) else ""
        r = f"\u25b8\u2002{right[i]}" if i < len(right) else ""
        rows.append([Paragraph(l, bullet_style), Paragraph(r, bullet_style)])
    t = Table(rows, colWidths=[W/2, W/2])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                            ("LEFTPADDING", (0,0), (-1,-1), 0),
                            ("RIGHTPADDING", (0,0), (-1,-1), 0),
                            ("TOPPADDING", (0,0), (-1,-1), 0),
                            ("BOTTOMPADDING", (0,0), (-1,-1), 1)]))
    story.append(t)

# ── Header ──────────────────────────────────────────────────────────────────
story.append(Paragraph("Klayton Rogers", name_style))
story.append(Paragraph(
    "Smethport, Pennsylvania\u2002|\u2002814-331-7245\u2002|\u2002klaytonrogers3@gmail.com",
    contact_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a1a"),
                         spaceBefore=8, spaceAfter=0))

# ── Objective ───────────────────────────────────────────────────────────────
section_header("Objective")
story.append(Paragraph(
    "Dependable and motivated individual seeking a Painter Helper position with Allegheny Paint Co. "
    "Known for showing up reliably, following instructions carefully, and taking pride in doing work "
    "right the first time. Eager to learn proper painting techniques and grow within a skilled trade.",
    body_style))

# ── Skills ──────────────────────────────────────────────────────────────────
section_header("Skills & Qualifications")
skill_grid([
    "Valid Pennsylvania driver's license",
    "Reliable personal vehicle for job site travel",
    "Comfortable working on ladders and at heights",
    "Able to lift and carry tools, ladders, and materials",
    "Strong attention to detail and quality workmanship",
    "Quick learner — picks up new skills and techniques fast",
    "Dependable and punctual — consistent work record",
    "Works well with others and takes direction well",
])

# ── Experience ──────────────────────────────────────────────────────────────
section_header("Work Experience")

job_row("Retail Associate", "08/2025 \u2013 Present")
story.append(Paragraph("The Home Depot \u2014 Olean, NY", company_style))
bullet("Assist customers with product selection including paint, tools, lumber, and building materials")
bullet("Operate heavy equipment and perform physical tasks including lifting, stocking, and moving merchandise")
bullet("Maintain a clean, organized, and safe work environment on the floor and in the stockroom")
bullet("Collaborate with team members and supervisors to meet daily store goals")
bullet("Follow safety protocols and company procedures consistently")

story.append(Spacer(1, 10))
job_row("Retail Service Representative", "05/2024 \u2013 03/2025")
story.append(Paragraph("OSL Retail Services", company_style))
bullet("Delivered on-site retail support and merchandising services at assigned locations")
bullet("Maintained product displays and ensured inventory was stocked and organized")
bullet("Provided customer-facing service while meeting company and client standards")
bullet("Adapted quickly to varying work environments and followed site-specific instructions")

# ── Education ───────────────────────────────────────────────────────────────
section_header("Education")

job_row("Jamestown Community College", "01/2026 \u2013 Present")
story.append(Paragraph("Associate\u2019s Program \u2014 Geography", company_style))

story.append(Spacer(1, 6))
job_row("Niagara County Community College", "08/2023 \u2013 05/2024")
story.append(Paragraph("General Studies", company_style))

# ── Additional ──────────────────────────────────────────────────────────────
section_header("Additional Information")
bullet("Available for full-time, on-the-road work across residential and commercial job sites")
bullet("Comfortable with job site setup, cleanup, and following structured daily routines")
bullet("Interested in long-term employment and growing into a skilled painter role")

# ── Build ────────────────────────────────────────────────────────────────────
doc.build(story)
print("PDF created: klayton_rogers_resume.pdf")

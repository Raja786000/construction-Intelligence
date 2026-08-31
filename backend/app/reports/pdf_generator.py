import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_report_pdf(report_data: dict, output_path: str):
    # Setup document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1A365D")  # Deep blue
    secondary_color = colors.HexColor("#2B6CB0")  # Lighter blue
    text_color = colors.HexColor("#2D3748")  # Dark grey
    light_bg = colors.HexColor("#F7FAFC")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=primary_color,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=secondary_color,
        spaceAfter=15
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=text_color,
        leading=14,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Bullet'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=text_color,
        leading=14,
        bulletIndent=10,
        leftIndent=22,
        spaceAfter=5
    )

    story = []

    # 1. Title Header
    report_type = report_data.get("report_type", "Daily").upper()
    story.append(Paragraph(f"🦺 CONSTRUCTION INTELLIGENCE HUB", subtitle_style))
    story.append(Paragraph(f"{report_type} PERFORMANCE REPORT", title_style))
    story.append(Spacer(1, 10))

    # 2. Metadata Grid
    meta_data = [
        [Paragraph("<b>Project ID:</b>", body_style), Paragraph(report_data.get("project_id", "N/A"), body_style),
         Paragraph("<b>Date Generated:</b>", body_style), Paragraph(report_data.get("date", "N/A"), body_style)],
        [Paragraph("<b>Project Status:</b>", body_style), Paragraph(report_data.get("project_status", "N/A"), body_style),
         Paragraph("<b>Report ID:</b>", body_style), Paragraph(report_data.get("_id", "N/A"), body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[100, 160, 100, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#EDF2F7")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 3. Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", section_title_style))
    story.append(Paragraph(report_data.get("executive_summary", "No summary provided."), body_style))
    story.append(Spacer(1, 10))

    # 4. Key Performance Indicators (KPIs)
    story.append(Paragraph("KEY PERFORMANCE INDICATORS (KPIs)", section_title_style))
    pm = report_data.get("project_monitoring", {})
    safety = report_data.get("safety", {})
    risk = report_data.get("risk", {})
    quality = report_data.get("quality", {})
    
    kpi_data = [
        [Paragraph("<b>KPI Category</b>", body_style), Paragraph("<b>Target / Planned</b>", body_style), Paragraph("<b>Actual Observed</b>", body_style), Paragraph("<b>Variance / Alert Status</b>", body_style)],
        [Paragraph("Project Schedule Progress", body_style), Paragraph(f"{pm.get('planned_progress', 0)}%", body_style), Paragraph(f"{pm.get('actual_progress', 0)}%", body_style), Paragraph(f"{pm.get('schedule_variance', 0):+.1f}%", body_style)],
        [Paragraph("Project Expected Delay", body_style), Paragraph("0 Days", body_style), Paragraph(f"{pm.get('predicted_delay_days', 0)} Days", body_style), Paragraph("Lagging" if pm.get('predicted_delay_days', 0) > 0 else "Compliant", body_style)],
        [Paragraph("Safety Compliance Wear", body_style), Paragraph("0 Violations", body_style), Paragraph(f"{safety.get('ppe_violations', 0)} Violations", body_style), Paragraph("Warning Alert" if safety.get('ppe_violations', 0) > 0 else "Compliant", body_style)],
        [Paragraph("Site Environmental Risk", body_style), Paragraph("Low", body_style), Paragraph(risk.get('risk_level', 'Low'), body_style), Paragraph(f"Score: {risk.get('risk_score', 0)}", body_style)],
        [Paragraph("Quality Structural Defects", body_style), Paragraph("0 Defects", body_style), Paragraph(f"{quality.get('defects_detected', 0)} Defects", body_style), Paragraph("Repair Required" if quality.get('defects_detected', 0) > 0 else "Compliant", body_style)]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[150, 110, 110, 150])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ('BOX', (0,0), (-1,-1), 1, primary_color)
    ]))
    # Quick fix for text color in header
    for col_idx in range(4):
        kpi_data[0][col_idx].style.textColor = colors.white
    
    story.append(kpi_table)
    story.append(Spacer(1, 15))

    # 5. Critical Findings (Priority list)
    story.append(Paragraph("PRIORITIZED CRITICAL FINDINGS", section_title_style))
    findings = report_data.get("critical_findings", [])
    if findings:
        for item in findings:
            sev = item.get("severity", "HIGH")
            issue = item.get("issue", "Compliance alert")
            text = f"<b>[{sev}]</b> {issue}"
            story.append(Paragraph(text, bullet_style))
    else:
        story.append(Paragraph("No critical safety, schedule, quality, or environmental alerts were flagged during this period.", body_style))
    story.append(Spacer(1, 10))

    # 6. Recommendations & Next Actions
    story.append(Paragraph("ACTIONABLE RECOMMENDATIONS", section_title_style))
    recs = report_data.get("recommendations", [])
    for rec in recs:
        story.append(Paragraph(rec, bullet_style))
    if not recs:
        story.append(Paragraph("Review standard project metrics and carry out routine site maintenance.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("IMMEDIATE NEXT ACTIONS (TOMORROW/NEXT SHIFT)", section_title_style))
    actions = report_data.get("next_actions", [])
    for act in actions:
        story.append(Paragraph(act, bullet_style))
    if not actions:
        story.append(Paragraph("Verify safety log entry and proceed with sequential planned tasks.", body_style))

    # Build PDF
    doc.build(story)

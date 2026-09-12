from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from pathlib import Path

NAVY=colors.HexColor('#12243A'); BLUE=colors.HexColor('#2563EB'); PALE=colors.HexColor('#EEF4FF'); INK=colors.HexColor('#172033'); MUTED=colors.HexColor('#607086'); LINE=colors.HexColor('#D9E1EA')

def esc(x):
    return str(x or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def build_pdf(path,data,report_type='executive'):
    styles=getSampleStyleSheet()
    title=ParagraphStyle('T',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=24,leading=28,textColor=NAVY,spaceAfter=6)
    sub=ParagraphStyle('Sub',parent=styles['BodyText'],fontSize=9,textColor=MUTED,spaceAfter=16)
    h=ParagraphStyle('H',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=NAVY,spaceBefore=14,spaceAfter=8)
    body=ParagraphStyle('B',parent=styles['BodyText'],fontSize=8.5,leading=12,textColor=INK)
    tiny=ParagraphStyle('Tiny',parent=body,fontSize=7.5,leading=10)
    story=[Paragraph('CONSTRUCTION INTELLIGENCE',title),Paragraph('Executive Reporting & Decision Brief · Milestone 4',sub)]
    meta=[[Paragraph('<b>Project</b>',body),esc(data['project_id']),'Generated',datetime.now().strftime('%d %b %Y · %H:%M')],['Status',data['overall_status'].replace('_',' '),'Coverage',f"{data['agent_count']}/{data['expected_agent_count']} agents"]]
    t=Table(meta,colWidths=[75,175,70,170]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('GRID',(0,0),(-1,-1),.4,LINE),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('PADDING',(0,0),(-1,-1),7)])); story += [t,Spacer(1,10)]
    story += [Paragraph('1. Executive position',h)]
    kpi=[["OVERALL SCORE","FINDINGS","HIGH RISK","CRITICAL","EVENTS"],[f"{data['overall_score']}/100",str(data['total_findings']),str(data['high_risk_findings']),str(data['critical_findings']),str(data['total_events'])]]
    kt=Table(kpi,colWidths=[96]*5); kt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTSIZE',(0,0),(-1,0),7),('FONTSIZE',(0,1),(-1,1),15),('TEXTCOLOR',(0,1),(-1,1),INK),('GRID',(0,0),(-1,-1),.4,LINE),('PADDING',(0,0),(-1,-1),8)])); story += [kt]
    story += [Paragraph('This brief consolidates normalized outputs from the connected construction intelligence agents. It highlights the current decision position, unresolved risks and recommended actions.',body)]
    story += [Paragraph('2. Agent coverage & health',h)]
    rows=[['Agent','Reporting','Status','Score','Findings','Severity']]
    for a,v in data['agents'].items(): rows.append([a.title(), 'YES' if v['reporting'] else 'NO', v['status'].replace('_',' '), '—' if v['score'] is None else str(round(v['score'])),str(v['findings_count']),v['severity']])
    at=Table(rows,colWidths=[85,60,105,55,55,75]); at.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,LINE),('FONTSIZE',(0,0),(-1,-1),7.5),('PADDING',(0,0),(-1,-1),6)])); story += [at]
    story += [Paragraph('3. Priority risk register',h)]
    if data['findings']:
        rr=[['Priority','Agent','Severity','Finding','Recommended action']]
        sev_order={'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3,'NONE':4}
        findings=sorted(data['findings'],key=lambda x:(sev_order.get(x['severity'],5),x['agent']))[:30]
        for i,f in enumerate(findings,1): rr.append([str(i),f['agent'].title(),f['severity'],esc(f['title']),esc(f['recommended_action'] or 'Human review required.')])
        rt=Table(rr,colWidths=[38,70,58,160,109],repeatRows=1); rt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,LINE),('FONTSIZE',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),5)])); story += [rt]
    else: story += [Paragraph('No findings were supplied by the connected agents.',body)]
    story += [Paragraph('4. Recommended actions',h)]
    if data['recommendations']:
        for i,r in enumerate(data['recommendations'][:20],1): story.append(Paragraph(f'<b>{i}.</b> {esc(r)}',body))
    else: story.append(Paragraph('No recommendations were supplied.',body))
    story += [Paragraph('5. Data & decision notes',h),Paragraph(f"Reporting coverage is {data['data_completeness']}%. The reporting layer is a decision-support system: findings should be verified by the appropriate project professional before engineering, safety, legal, insurance or contractual action.",body)]
    story += [Spacer(1,14),Paragraph('Generated by Construction Intelligence Hub · Reporting Intelligence',tiny)]
    def footer(canvas,doc):
        canvas.saveState(); canvas.setFont('Helvetica',7); canvas.setFillColor(MUTED); canvas.drawString(45,25,f"Construction Intelligence · {data['project_id']}"); canvas.drawRightString(A4[0]-45,25,f"Page {doc.page}"); canvas.restoreState()
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=42,title=f"Construction Intelligence - {data['project_id']}").build(story,onFirstPage=footer,onLaterPages=footer)

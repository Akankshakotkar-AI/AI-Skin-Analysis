"""
PROFESSIONAL PDF Report Generator
Includes: analyzed images, skin score, acne details, recommendations, professional layout
"""
import os
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO

def generate_report(skin_score, acne_count, severity, recommendations, 
                   acne_details=None, original_url=None, result_url=None):
    """
    Generates a professional skin analysis report PDF.
    NOW INCLUDES: analyzed images, detailed metrics, professional formatting
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm, inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        
        pdf_filename = f'SkinAI_Report_{uuid.uuid4().hex[:8]}.pdf'
        pdf_path = os.path.join('results', pdf_filename)
        
        # ── SETUP DOCUMENT ──────────────────────────────
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=A4,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # ── COLORS ──────────────────────────────────────
        purple = colors.HexColor('#7c5cbf')
        pink = colors.HexColor('#c45fa0')
        dark = colors.HexColor('#0a0a14')
        light_bg = colors.HexColor('#f5f5f5')
        
        # Score color based on value
        if skin_score >= 70:
            score_color = colors.HexColor('#22c55e')  # green
        elif skin_score >= 40:
            score_color = colors.HexColor('#eab308')  # yellow
        else:
            score_color = colors.HexColor('#ef4444')  # red
        
        # ── CUSTOM STYLES ───────────────────────────────
        title_style = ParagraphStyle(
            'Title',
            fontSize=28,
            fontName='Helvetica-Bold',
            textColor=purple,
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            fontSize=12,
            fontName='Helvetica',
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=dark,
            spaceAfter=10,
            spaceBefore=10
        )
        
        text_style = ParagraphStyle(
            'BodyText',
            fontSize=11,
            fontName='Helvetica',
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=8
        )
        
        # ════ HEADER SECTION ════════════════════════════
        story.append(Paragraph("🔬 AI SKIN ANALYSIS REPORT", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
        
        # ════ SCORE CARD ════════════════════════════════
        score_table_data = [[
            Paragraph(f"<font size=36 color={score_color.hexval()}><b>{skin_score}/100</b></font>", 
                     ParagraphStyle('ScoreNumber', fontSize=36, alignment=TA_CENTER)),
            Paragraph(f"<b>Skin Health Score</b><br/>Overall skin condition rating", 
                     ParagraphStyle('ScoreLabel', fontSize=11, alignment=TA_CENTER))
        ]]
        
        score_table = Table(score_table_data, colWidths=[3*cm, 10*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), light_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BORDER', (0, 0), (-1, -1), 1.5, purple),
            ('BORDERRADIUS', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 12))
        
        # ════ METRICS TABLE ════════════════════════════
        metrics = [
            ['Metric', 'Result', 'Assessment'],
            ['Skin Score', f'{skin_score}/100', 'Overall health rating'],
            ['Acne Spots', str(acne_count), f'{severity} severity'],
            ['Severity Level', severity, get_severity_description(severity)],
        ]
        
        if acne_details:
            metrics.append(['Redness Level', f"{acne_details.get('redness_percent', 0):.0f}%", 
                           'Inflammation detected' if acne_details.get('redness_percent', 0) > 15 else 'Minimal'])
            metrics.append(['Oiliness', f"{acne_details.get('oiliness_percent', 0):.0f}%",
                           'Very oily' if acne_details.get('oiliness_percent', 0) > 50 else 'Moderate' if acne_details.get('oiliness_percent', 0) > 30 else 'Normal'])
            metrics.append(['Dark Spots', str(acne_details.get('dark_spot_count', 0)),
                           'Pigmentation issues' if acne_details.get('dark_spot_count', 0) > 3 else 'Minimal'])
        
        metrics.append(['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M'), 'Report timestamp'])
        
        metrics_table = Table(metrics, colWidths=[3*cm, 3*cm, 6*cm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_bg, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(Paragraph('<b>Detailed Metrics</b>', heading_style))
        story.append(metrics_table)
        story.append(Spacer(1, 16))
        
        # ════ RECOMMENDATIONS ═══════════════════════════
        story.append(Paragraph('<b>💡 Personalized Skincare Recommendations</b>', heading_style))
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"<b>{i}.</b> {rec}", text_style))
        
        story.append(Spacer(1, 12))
        
        # ════ SKIN CONDITION SUMMARY ════════════════════
        story.append(Paragraph('<b>Skin Condition Summary</b>', heading_style))
        
        summary_text = get_skin_summary(severity, acne_count, acne_details)
        story.append(Paragraph(summary_text, text_style))
        story.append(Spacer(1, 12))
        
        # ════ NEXT STEPS ════════════════════════════════
        story.append(Paragraph('<b>Recommended Next Steps</b>', heading_style))
        
        next_steps = get_next_steps(severity, skin_score)
        for step in next_steps:
            story.append(Paragraph(f"• {step}", text_style))
        
        story.append(Spacer(1, 24))
        
        # ════ FOOTER ════════════════════════════════════
        footer_text = ("This report is AI-generated for informational purposes only. "
                      "For medical concerns, please consult a dermatologist. "
                      "SkinAI © 2026")
        story.append(Paragraph(footer_text, 
                              ParagraphStyle('Footer', fontSize=9, textColor=colors.grey, alignment=TA_CENTER)))
        
        # ── BUILD PDF ────────────────────────────────────
        doc.build(story)
        print(f"PDF generated: {pdf_path}")
        return pdf_path
        
    except ImportError:
        raise Exception("reportlab not installed. Run: pip install reportlab pillow")
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")


def get_severity_description(severity):
    """Get description for severity level"""
    descriptions = {
        'Clear': 'Excellent skin condition',
        'Mild': 'Minor breakouts present',
        'Moderate': 'Noticeable acne issues',
        'Severe': 'Significant skin concerns'
    }
    return descriptions.get(severity, 'Unknown')


def get_skin_summary(severity, acne_count, acne_details=None):
    """Generate a text summary of skin condition"""
    if severity == 'Clear':
        summary = "Your skin shows excellent health with no significant issues detected. Continue your current skincare routine and maintain sun protection."
    elif severity == 'Mild':
        summary = f"You have {acne_count} acne spot(s) detected. This is mild acne that responds well to topical treatments. Consistent skincare and lifestyle adjustments should improve your skin within 4-6 weeks."
    elif severity == 'Moderate':
        summary = f"Moderate acne detected with {acne_count} spots. This level typically benefits from combination therapy with cleansers, treatments, and moisturizers. Consider consulting a dermatologist if not improving in 6-8 weeks."
    else:  # Severe
        summary = f"Significant acne detected ({acne_count} spots). Professional dermatological treatment is strongly recommended. Prescription medications or clinical procedures may be necessary for best results."
    
    # Add redness note
    if acne_details and acne_details.get('redness_percent', 0) > 20:
        summary += " Inflammation is present — use calming ingredients like niacinamide and centella asiatica."
    
    # Add oiliness note
    if acne_details and acne_details.get('oiliness_percent', 0) > 40:
        summary += " Your skin is oily — prioritize lightweight, non-comedogenic products."
    
    return summary


def get_next_steps(severity, skin_score):
    """Generate actionable next steps based on severity"""
    steps = []
    
    if severity == 'Clear':
        steps = [
            "Maintain your current skincare routine",
            "Apply SPF 30+ daily for sun protection",
            "Continue healthy lifestyle habits (sleep, hydration)",
            "Do monthly check-ins to track skin consistency"
        ]
    elif severity == 'Mild':
        steps = [
            "Start a targeted acne treatment (salicylic acid or benzoyl peroxide)",
            "Identify and avoid triggers (certain foods, products)",
            "Change pillowcase every 2-3 days",
            "Avoid touching your face throughout the day",
            "Use oil-free, non-comedogenic moisturizer",
            "Reassess in 4 weeks; if no improvement, see dermatologist"
        ]
    elif severity == 'Moderate':
        steps = [
            "Begin combination acne treatment (cleanser + treatment + moisturizer)",
            "See a dermatologist if not already done",
            "Keep detailed notes on what helps/hurts your skin",
            "Avoid over-treating — let products work for 6-8 weeks",
            "Consider professional treatments (facials, laser) for faster results",
            "Reduce stress and improve sleep quality"
        ]
    else:  # Severe
        steps = [
            "Schedule dermatologist appointment ASAP",
            "Discuss prescription options (Accutane, antibiotics, hormonal treatments)",
            "Avoid home remedies and multiple products simultaneously",
            "Be patient — severe acne takes 3-6 months to clear with proper treatment",
            "Protect skin from sun during treatment",
            "Seek emotional support if acne affects your mental health"
        ]
    
    return steps
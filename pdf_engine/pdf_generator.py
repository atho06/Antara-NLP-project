"""
Clinical PDF Generator for Antara Pre-Therapy Intake.
Builds high-resolution, professional clinical reports using ReportLab
for therapist review, printing, and medical record archiving.
"""

import io
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically calculate total page numbers in footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header running line
        self.drawString(54, 800, "ANTARA — Confidential Pre-Therapy Clinical Intake Report")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 792, 540, 792)

        # Footer running line
        self.line(54, 45, 540, 45)
        self.drawString(54, 32, "Confidential Document • Prepared Solely for Licensed Healthcare Provider")
        self.drawRightString(540, 32, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


class ClinicalPDFGenerator:
    """
    Renders structured clinical reports into PDF format.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        # Palette: Deep slate #0f172a, teal #0f766e, warm amber #b45309, light grey #f8fafc
        self.title_style = ParagraphStyle(
            'DocTitle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a")
        )
        self.meta_style = ParagraphStyle(
            'DocMeta',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569")
        )
        self.disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#b45309")
        )
        self.section_h1 = ParagraphStyle(
            'SectionH1',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=10,
            spaceAfter=4
        )
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1e293b")
        )
        self.quote_style = ParagraphStyle(
            'VerbatimQuote',
            parent=self.styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#0f172a"),
            leftIndent=12
        )
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0f172a")
        )
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155")
        )

    def generate_pdf_bytes(self, report: Dict[str, Any]) -> bytes:
        """
        Builds the PDF and returns raw bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        elements = []
        meta = report.get("metadata", {})
        s1 = report.get("section1_main_concerns", {})
        s2 = report.get("section2_emotions_and_trajectory", {})
        s3 = report.get("section3_themes_and_triggers", {})
        s4 = report.get("section4_clinical_observations", {})
        s5 = report.get("section5_therapy_goals", {})
        s6 = report.get("section6_attached_transcript", [])

        # Title & Header
        elements.append(Paragraph("Clinical Pre-Therapy Intake Summary", self.title_style))
        elements.append(Spacer(1, 4))
        meta_line = (
            f"<b>Client Pseudonym:</b> {meta.get('clientPseudonym', 'Client')} &nbsp;|&nbsp; "
            f"<b>Session ID:</b> {meta.get('sessionId', 'N/A')} &nbsp;|&nbsp; "
            f"<b>Date:</b> {meta.get('generatedAt', '')[:10]}"
        )
        elements.append(Paragraph(meta_line, self.meta_style))
        elements.append(Spacer(1, 6))

        # Mandatory Disclaimer Box
        disclaimer_text = f"<b>IMPORTANT NOTICE:</b> {meta.get('disclaimer', '')}"
        disc_table = Table(
            [[Paragraph(disclaimer_text, self.disclaimer_style)]],
            colWidths=[486]
        )
        disc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#fef08a")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(disc_table)
        elements.append(Spacer(1, 10))

        # Section 1: Main Concerns in Her Own Stated Words
        elements.append(Paragraph("1. Main Concerns in Her Own Stated Words", self.section_h1))
        for quote_item in s1.get("verbatim_quotes", []):
            q_text = f"• \"{quote_item.get('quote', '')}\""
            elements.append(Paragraph(q_text, self.quote_style))
            elements.append(Spacer(1, 2))
        elements.append(Spacer(1, 6))

        # Section 2: Key Emotions & Trajectory
        elements.append(Paragraph("2. Key Emotions & Emotional Trajectory Across Session", self.section_h1))
        arc_summary = (
            f"<b>Trajectory Arc:</b> {s2.get('trajectory_arc_narrative', 'N/A')}<br/>"
            f"<b>Initial Check-in Emotion:</b> {s2.get('start_emotion', '').replace('_', ' ').title()} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Concluding Emotion:</b> {s2.get('end_emotion', '').replace('_', ' ').title()} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Peak Distress Stage:</b> {s2.get('peak_distress_stage', 'N/A')}"
        )
        elements.append(Paragraph(arc_summary, self.body_style))
        elements.append(Spacer(1, 8))

        # Section 3: Recurring Themes & Triggers
        elements.append(Paragraph("3. Recurring Thematic Domains & Situational Triggers", self.section_h1))
        themes_list = [t.get("name", "") for t in s3.get("primary_themes", [])]
        themes_line = f"<b>Primary Life Domains:</b> {', '.join(themes_list) if themes_list else 'None specified'}"
        elements.append(Paragraph(themes_line, self.body_style))
        elements.append(Spacer(1, 3))

        triggers = s3.get("situational_triggers", [])
        if triggers:
            trig_names = [f"\"{t.get('trigger', '')}\"" for t in triggers]
            trig_line = f"<b>Identified Triggers:</b> {', '.join(trig_names)}"
            elements.append(Paragraph(trig_line, self.body_style))
        elements.append(Spacer(1, 8))

        # Section 4: Clinical Observations
        elements.append(Paragraph("4. Clinical Linguistic Observations (Hedging, Inconsistencies, Edits)", self.section_h1))
        hedge_data = s4.get("hedging_analysis", {})
        hedge_line = (
            f"• <b>Hedging & Minimization Level:</b> {hedge_data.get('level', 'Normal')} "
            f"({hedge_data.get('total_hedges', 0)} minimizing cues detected; "
            f"{hedge_data.get('percentage_answers_hedged', 0)}% of answers hedged).<br/>"
            f"&nbsp;&nbsp;<i>Interpretation:</i> {hedge_data.get('interpretation', '')}"
        )
        elements.append(Paragraph(hedge_line, self.body_style))
        elements.append(Spacer(1, 4))

        # Inconsistencies
        incons = s4.get("inconsistencies", {})
        if incons.get("detected"):
            incons_line = f"• <b>Affective / Factual Inconsistencies Detected:</b> {incons.get('total_flags', 0)} flags (Severity: {incons.get('severity', 'N/A')})."
            elements.append(Paragraph(incons_line, self.body_style))
            for flag in incons.get("items", [])[:2]:
                f_desc = f"&nbsp;&nbsp;- <i>{flag.get('type')}:</i> {flag.get('explanation')}"
                elements.append(Paragraph(f_desc, self.body_style))
        else:
            elements.append(Paragraph("• <b>Inconsistencies:</b> None detected across stated mood and reported daily functioning.", self.body_style))
        elements.append(Spacer(1, 4))

        # Edited Answers
        edits = s4.get("edited_answers", {})
        if edits.get("total_edits", 0) > 0:
            edit_line = (
                f"• <b>Answer Revisions:</b> {edits.get('total_edits')} question(s) edited by client. "
                f"<b>Sanitizations Detected:</b> {edits.get('sanitization_count', 0)}.<br/>"
                f"&nbsp;&nbsp;<i>Clinical note:</i> {edits.get('clinical_takeaway', '')}"
            )
            elements.append(Paragraph(edit_line, self.body_style))
        else:
            elements.append(Paragraph("• <b>Answer Revisions:</b> Client did not edit any submitted answers.", self.body_style))
        elements.append(Spacer(1, 8))

        # Section 5: What She Wants from Therapy
        elements.append(Paragraph("5. What She Hopes to Gain from Therapy", self.section_h1))
        hopes_text = f"\"{s5.get('verbatim_hope', 'No explicit goal reported')}\""
        elements.append(Paragraph(hopes_text, self.quote_style))
        elements.append(Spacer(1, 10))

        # Section 6: Attached Full Unfiltered Conversation
        elements.append(KeepTogether([
            Paragraph("6. Attached Full Conversation Transcript (Unfiltered)", self.section_h1),
            Paragraph("<i>Note: Transcripts include markers for edited statements and skipped questions.</i>", self.meta_style),
            Spacer(1, 6)
        ]))

        # Render transcript table
        table_rows = [
            [
                Paragraph("<b>Step / Stage</b>", self.table_header_style),
                Paragraph("<b>Question & Response Details</b>", self.table_header_style),
                Paragraph("<b>Status</b>", self.table_header_style)
            ]
        ]

        for item in s6:
            step_str = f"Step {item.get('step')}<br/><font color='#64748b'>{item.get('stage', '').replace('_', ' ')}</font>"
            q_text = f"<b>Q:</b> {item.get('question', '')}<br/>"

            if item.get("is_skipped"):
                ans_text = "<font color='#94a3b8'><i>[Question Skipped by Client]</i></font>"
            elif item.get("is_edited") and item.get("original_answer"):
                ans_text = (
                    f"<b>Final:</b> {item.get('final_answer', '')}<br/>"
                    f"<font color='#dc2626'><b>Original:</b> <strike>{item.get('original_answer', '')}</strike></font>"
                )
            else:
                ans_text = f"<b>A:</b> {item.get('final_answer', '')}"

            details_cell = Paragraph(q_text + ans_text, self.table_cell_style)
            marker_cell = Paragraph(f"<b>{item.get('marker', '')}</b>", self.table_cell_style)
            table_rows.append([Paragraph(step_str, self.table_cell_style), details_cell, marker_cell])

        transcript_table = Table(table_rows, colWidths=[90, 330, 66])
        transcript_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#cbd5e1")),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(transcript_table)

        # Build document using NumberedCanvas
        doc.build(elements, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

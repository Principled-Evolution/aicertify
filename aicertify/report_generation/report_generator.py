"""
ReportGenerator Module

This module handles report generation in multiple formats (Markdown and PDF).
The PDF generation leverages ReportLab's Platypus framework to convert Markdown
content into a series of flowable objects while preserving headings, bold text,
bullet points, spacing, and disclaimers. It also includes a dynamic Table of Contents.
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Import centralized models
from aicertify.models.evaluation import MetricValue

# Full and short disclaimer texts.
DISCLAIMER_FULL = (
    "Disclaimer: This assessment is provided for informational and illustrative purposes only. "
    "No warranty, express or implied, is made regarding its accuracy, completeness, or fitness for any particular purpose. "
    "The results and recommendations herein do not constitute legal advice or assurance of regulatory compliance. "
    "Users of this report are solely responsible for evaluating the information, deciding how to implement any recommendations, "
    "and ensuring compliance with applicable laws and regulations. By using this report, you agree that the provider "
    "shall not be held liable for any direct, indirect, or consequential losses, damages, or claims arising from the use of or reliance on this information."
)
DISCLAIMER_SHORT = "Disclaimer: Informational only; no warranty or liability. See full disclaimer in the report."

def convert_bold(text: str) -> str:
    """Convert markdown **bold** markers to ReportLab <b> tags."""
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

# Subclass SimpleDocTemplate to capture headings for the Table of Contents.
class MyDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and hasattr(flowable.style, 'tocLevel'):
            level = flowable.style.tocLevel
            text = flowable.getPlainText()
            # Notify the TOC with the heading text, level, and current page number.
            self.notify('TOCEntry', (level, text, self.page))

class ReportGenerator:
    @staticmethod
    def generate_markdown_report(report) -> str:
        """
        Generate a Markdown report based on the evaluation report model.

        Args:
            report: An evaluation report model with attributes such as app_details, metric_groups, policy_results, summary.

        Returns:
            str: The markdown content as a single string.
        """
        lines = []
        # Title and Date
        lines.append("# Evaluation Report")
        lines.append("")
        lines.append(f"**Analysis Date:** {report.app_details.evaluation_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        # Summary
        if report.summary:
            lines.append("## Evaluation Summary")
            lines.append(report.summary)
            lines.append("")
        # Application Details
        lines.append("## Application Details")
        lines.append(f"- **App Name:** {report.app_details.name}")
        lines.append(f"- **Evaluation Mode:** {report.app_details.evaluation_mode}")
        lines.append(f"- **Contract Count:** {report.app_details.contract_count}")
        lines.append("")
        # Metric Groups
        for group in report.metric_groups:
            lines.append(f"## {group.display_name}")
            if group.description:
                lines.append(group.description)
                lines.append("")
            for metric in group.metrics:
                lines.append(f"- **{metric.display_name}:** {metric.value}")
            lines.append("")
        # Policy Results
        lines.append("## Policy Evaluation Results")
        for policy in report.policy_results:
            result_str = "PASS" if policy.result else "FAIL"
            lines.append(f"- **{policy.name}:** {result_str}")
            if policy.details:
                for key, value in policy.details.items():
                    lines.append(f"  - {key}: {value}")
        lines.append("")
        # Append full disclaimer at the end of the report.
        lines.append("## Disclaimer")
        lines.append("")
        lines.append(DISCLAIMER_FULL)
        return "\n".join(lines)

    @staticmethod
    def save_markdown_report(markdown_content: str, output_path: str) -> bool:
        """
        Save the Markdown report content to a file.

        Args:
            markdown_content (str): The markdown content to save.
            output_path (str): The file path to write the markdown to.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return True
        except Exception as error:
            logging.error(f"Failed to save markdown report: {error}")
            return False

    @staticmethod
    def _build_story_from_markdown(markdown_content: str) -> list:
        """
        Convert markdown content into a list of ReportLab flowables.
        Headings are assigned a tocLevel via their styles to support a dynamic TOC.
        """
        styles = getSampleStyleSheet()
        # Configure heading styles with tocLevel for TOC capture.
        if 'Heading1' in styles:
            styles['Heading1'].tocLevel = 0
        if 'Heading2' in styles:
            styles['Heading2'].tocLevel = 1

        story = []
        buffer = []
        for line in markdown_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("## "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    story.append(Paragraph(convert_bold(paragraph_text), styles["BodyText"]))
                    buffer = []
                heading_text = convert_bold(stripped[3:])
                story.append(Paragraph(heading_text, styles["Heading2"]))
                story.append(Spacer(1, 12))
            elif stripped.startswith("# "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    story.append(Paragraph(convert_bold(paragraph_text), styles["BodyText"]))
                    buffer = []
                heading_text = convert_bold(stripped[2:])
                # Use Heading1 for top-level headings.
                story.append(Paragraph(heading_text, styles["Heading1"]))
                story.append(Spacer(1, 12))
            elif stripped.startswith("- "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    story.append(Paragraph(convert_bold(paragraph_text), styles["BodyText"]))
                    buffer = []
                bullet_text = convert_bold(stripped[2:])
                story.append(Paragraph(bullet_text, styles["BodyText"], bulletText="•"))
                story.append(Spacer(1, 6))
            elif stripped == "":
                if buffer:
                    paragraph_text = " ".join(buffer)
                    story.append(Paragraph(convert_bold(paragraph_text), styles["BodyText"]))
                    story.append(Spacer(1, 12))
                    buffer = []
            else:
                buffer.append(stripped)
        if buffer:
            paragraph_text = " ".join(buffer)
            story.append(Paragraph(convert_bold(paragraph_text), styles["BodyText"]))
        return story

    @staticmethod
    def generate_pdf_report(markdown_content: str, output_path: str) -> str:
        """
        Generate a PDF report from markdown content with an integrated dynamic Table of Contents.
        Uses MyDocTemplate (a SimpleDocTemplate subclass) with multiBuild to capture TOC entries.
        """
        try:
            # Prepare the output file path with a timestamp.
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Build the story from markdown.
            story = ReportGenerator._build_story_from_markdown(markdown_content)
            styles = getSampleStyleSheet()

            # Create and configure the dynamic Table of Contents.
            toc = TableOfContents()
            toc.levelStyles = [
                ParagraphStyle(
                    fontName='Helvetica-Bold', fontSize=14, name='TOCHeading1',
                    leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=16
                ),
                ParagraphStyle(
                    fontName='Helvetica', fontSize=12, name='TOCHeading2',
                    leftIndent=40, firstLineIndent=-20, spaceBefore=0, leading=12
                ),
            ]
            toc_section = [
                Paragraph("Table of Contents", styles["Heading1"]),
                Spacer(1, 12),
                toc,
                PageBreak()
            ]
            # Prepend the TOC section to the main story.
            story = toc_section + story

            # Append a Disclaimer section at the end.
            disclaimer_flowable = KeepTogether([
                Paragraph("Disclaimer", styles["Heading2"]),
                Spacer(1, 12),
                Paragraph(DISCLAIMER_FULL, styles["BodyText"]),
                Spacer(1, 12),
            ])
            story.append(PageBreak())
            story.append(disclaimer_flowable)

            # Define a callback to add a footer.
            def on_page(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 8)
                canvas.drawString(40, 20, DISCLAIMER_SHORT)
                canvas.restoreState()

            # Build the PDF using our custom MyDocTemplate with multiBuild.
            doc = MyDocTemplate(str(output_path_obj), pagesize=A4)
            doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
            return str(output_path_obj)
        except Exception as ex:
            logging.error(f"Error generating PDF report: {ex}")
            return ""

# Example usage:
if __name__ == "__main__":
    from datetime import datetime
    # For demonstration, define dummy report model classes.
    @dataclass
    class ApplicationDetails:
        name: str
        evaluation_mode: str
        contract_count: int
        evaluation_date: datetime

    @dataclass
    class MetricGroup:
        name: str
        display_name: str
        metrics: List[MetricValue]
        description: Optional[str] = None

    @dataclass
    class PolicyResult:
        name: str
        result: bool
        details: Optional[Dict[str, Any]] = None

    @dataclass
    class EvaluationReport:
        app_details: ApplicationDetails
        metric_groups: List[MetricGroup]
        policy_results: List[PolicyResult]
        summary: Optional[str] = None

    # Create a sample evaluation report.
    report = EvaluationReport(
        app_details=ApplicationDetails(
            name="Medical Diagnosis Multi-Specialist",
            evaluation_mode="Standard",
            contract_count=0,
            evaluation_date=datetime.now()
        ),
        metric_groups=[
            MetricGroup(
                name="fairness",
                display_name="Fairness Metrics",
                metrics=[
                    MetricValue(name="ftu_satisfied", display_name="FTU Satisfied", value=False),
                    MetricValue(name="counterfactual_score", display_name="Counterfactual Score", value=0.4444444444444444),
                    MetricValue(name="stereotype_score", display_name="Stereotype Score", value=0.0),
                    MetricValue(name="sentiment_bias", display_name="Sentiment Bias", value=0.3333333333333333),
                    MetricValue(name="race_words_count", display_name="Race Word Count", value=0),
                    MetricValue(name="gender_words_count", display_name="Gender Word Count", value=0),
                    MetricValue(name="combined_score", display_name="Combined Score", value=0.7777777777777778),
                    MetricValue(name="bleu_similarity", display_name="BLEU Similarity", value=0.5),
                    MetricValue(name="rouge_similarity", display_name="ROUGE Similarity", value=0.5),
                    MetricValue(name="gender_bias_detected", display_name="Gender Bias Detected", value=False),
                    MetricValue(name="racial_bias_detected", display_name="Racial Bias Detected", value=False)
                ]
            )
        ],
        policy_results=[
            PolicyResult(name="Healthcare Diagnostic Safety", result=False, details={
                "message": "System does not meet healthcare-specific thresholds for: fairness, risk management",
                "recommendations": [
                    "Check back for future releases with healthcare-specific evaluations",
                    "Consider using global compliance policies in the meantime",
                    "Review FDA guidance on AI/ML in medical devices",
                    "Implement preliminary risk assessment based on Good Machine Learning Practice principles",
                    "Consider HIPAA compliance for any patient data handling"
                ]
            }),
            PolicyResult(name="Healthcare Patient Safety Requirements", result=False, details={
                "message": "Healthcare patient safety policy implementation is pending. This is a placeholder that will be replaced with actual compliance checks in a future release.",
                "recommendations": [
                    "Check back for future releases with healthcare-specific evaluations",
                    "Consider using global compliance policies in the meantime",
                    "Review FDA guidance on AI/ML in medical devices",
                    "Implement preliminary risk assessment based on Good Machine Learning Practice principles",
                    "Consider HIPAA compliance for any patient data handling"
                ]
            })
        ],
        summary="Evaluation of Medical Diagnosis Multi-Specialist with 5 interactions"
    )

    # Generate markdown content from the report model.
    md_content = ReportGenerator.generate_markdown_report(report)
    
    # Optionally save the markdown report.
    if ReportGenerator.save_markdown_report(md_content, "sample_report.md"):
        print("Markdown report generated successfully")
    
    # Generate the PDF report.
    pdf_path = ReportGenerator.generate_pdf_report(md_content, "sample_report.pdf")
    if pdf_path:
        print(f"PDF report generated successfully: {pdf_path}")

"""
ReportGenerator Module

This module handles report generation in multiple formats, including Markdown and PDF.
The PDF generation leverages ReportLab's Platypus framework to convert Markdown content
into a series of flowable objects. This approach preserves previous formatting such as
headings, bold conversions, bullet points, spacing, and disclaimers.
"""

import logging
import re
from pathlib import Path
from typing import List, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, BaseDocTemplate,
    Frame, PageTemplate, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from .report_models import EvaluationReport

# Full disclaimer text as per the disclaimers-guidance.md.
DISCLAIMER_FULL = (
    "Disclaimer: This assessment is provided for informational and illustrative purposes only. "
    "No warranty, express or implied, is made regarding its accuracy, completeness, or fitness for any particular purpose. "
    "The results and recommendations herein do not constitute legal advice or assurance of regulatory compliance. "
    "Users of this report are solely responsible for evaluating the information, deciding how to implement any recommendations, "
    "and ensuring compliance with applicable laws and regulations. By using this report, you agree that aicertify/mantric/Principled Evolution (or any individual or organization associated with it) "
    "shall not be held liable for any direct, indirect, or consequential losses, damages, or claims arising from the use of or reliance on this information."
)

# Short disclaimer text for footers.
DISCLAIMER_SHORT = "Disclaimer: Informational only; no warranty or liability. See full disclaimer in the report."

def convert_bold(text: str) -> str:
    """
    Convert markdown bold markers ( **text** ) to PDF bold tags.
    ReportLab Paragraph supports a subset of HTML, including <b> tags.
    
    Args:
        text (str): The input text containing markdown bold markers.
    
    Returns:
        str: Text with markdown bold replaced by HTML <b> tags.
    """
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

class ReportGenerator:
    """
    A class to handle report generation in multiple formats including Markdown and PDF.
    
    This class leverages Platypus to ensure that elements like headings, bullet lists,
    spacers, and disclaimers remain formatted as previously defined.
    """
    
    @staticmethod
    def generate_markdown_report(report: EvaluationReport) -> str:
        """
        Generate a Markdown report based on the evaluation report model.
        
        Args:
            report (EvaluationReport): The evaluation report model.
        
        Returns:
            str: The markdown content as a single string.
        """
        lines = []
        # Title and Date
        lines.append("# Evaluation Report")
        lines.append("")
        lines.append(f"**Analysis Date:** {report.app_details.evaluation_date.strftime('%Y-%m-%d %H:%M:%S')}")
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
        # Summary
        if report.summary:
            lines.append("## Evaluation Summary")
            lines.append(report.summary)
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
    def _build_story_from_markdown(markdown_content: str) -> List[Any]:
        """
        Convert markdown content into a list of ReportLab flowables.
        
        Args:
            markdown_content (str): The markdown content.
        
        Returns:
            List[Any]: A list of flowable objects representing the document content.
        """
        styles = getSampleStyleSheet()
        story = []
        buffer = []
        for line in markdown_content.splitlines():
            stripped = line.strip()
            # Process level-2 headings.
            if stripped.startswith("## "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                heading_text = convert_bold(stripped[3:])
                story.append(Paragraph(heading_text, styles["Heading2"]))
                story.append(Spacer(1, 12))
            # Process level-1 headings.
            elif stripped.startswith("# "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                heading_text = convert_bold(stripped[2:])
                story.append(Paragraph(heading_text, styles["Title"]))
                story.append(Spacer(1, 12))
            # Process bullet points.
            elif stripped.startswith("- "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                bullet_text = convert_bold(stripped[2:])
                story.append(Paragraph(bullet_text, styles["BodyText"], bulletText="•"))
                story.append(Spacer(1, 6))
            # Blank lines.
            elif stripped == "":
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    story.append(Spacer(1, 12))
                    buffer = []
            else:
                buffer.append(stripped)
        if buffer:
            paragraph_text = " ".join(buffer)
            paragraph_text = convert_bold(paragraph_text)
            story.append(Paragraph(paragraph_text, styles["BodyText"]))
        return story

    @staticmethod
    def generate_pdf_report(markdown_content: str, output_path: str) -> str:
        """
        Generate a PDF report from markdown content while preserving formatting.
        
        This method leverages ReportLab's Platypus framework to convert markdown
        content (via a structured "story" of flowables) into a PDF file. All custom
        formatting (headings, bold conversions, spacing, and disclaimers) is maintained.
        
        Args:
            markdown_content (str): The markdown content to be converted.
            output_path (str): The base file path for saving the PDF report.
        
        Returns:
            str: The final file path of the generated PDF report.
        """
        try:
            # Ensure the output directory exists.
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            # Append timestamp to ensure unique naming.
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            stem = output_path_obj.stem
            new_filename = f"{stem}-{timestamp}.pdf"
            new_output_path_obj = output_path_obj.parent / new_filename

            # Build the story from the Markdown content.
            story = ReportGenerator._build_story_from_markdown(markdown_content)
            styles = getSampleStyleSheet()

            # Append a page break and a disclaimer section.
            disclaimer_flowable = KeepTogether([
                Paragraph("Disclaimer", styles["Heading2"]),
                Spacer(1, 12),
                Paragraph(DISCLAIMER_FULL, styles["BodyText"]),
                Spacer(1, 12),
            ])
            story.append(PageBreak())
            story.append(disclaimer_flowable)

            # Define an on-page callback to preserve custom footer formatting.
            def on_page(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 8)
                canvas.drawString(40, 20, DISCLAIMER_SHORT)
                canvas.restoreState()

            # Create and build the PDF document.
            doc = SimpleDocTemplate(str(new_output_path_obj), pagesize=A4)
            doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
            return str(new_output_path_obj)
        except Exception as ex:
            logging.error(f"Error generating PDF report: {ex}")
            return ""

if __name__ == "__main__":
    # Example usage with the new model
    from datetime import datetime
    from .report_models import (
        EvaluationReport, ApplicationDetails,
        MetricGroup, MetricValue, PolicyResult
    )

    report = EvaluationReport(
        app_details=ApplicationDetails(
            name="TestApp",
            evaluation_mode="Automatic",
            contract_count=5,
            evaluation_date=datetime.now()
        ),
        metric_groups=[
            MetricGroup(
                name="fairness",
                display_name="Fairness Metrics",
                metrics=[
                    MetricValue(name="ftu_satisfied", display_name="FTU Satisfied", value=True),
                    MetricValue(name="race_words_count", display_name="Race Words Count", value=0)
                ]
            )
        ],
        policy_results=[
            PolicyResult(name="eu_ai_act", result=True, details={"specific_rule": "passed"})
        ],
        summary="All evaluation criteria met"
    )

    report_gen = ReportGenerator()
    md_content = report_gen.generate_markdown_report(report)

    if report_gen.save_markdown_report(md_content, "sample_report.md"):
        print("Markdown report generated successfully")

    pdf_path = report_gen.generate_pdf_report(md_content, "sample_report.pdf")
    if pdf_path:
        print(f"PDF report generated successfully: {pdf_path}")

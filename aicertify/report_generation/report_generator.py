import logging
import re
from pathlib import Path
from typing import List, Any
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
DISCLAIMER_SHORT = "Disclaimer: Informational only; no warranty or liability. See full disclaimer on page 2."

def convert_bold(text: str) -> str:
    """
    Convert markdown bold markers ( **text** ) to PDF bold tags.
    ReportLab Paragraph supports a subset of HTML, including <b> tags.
    """
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)

class ReportGenerator:
    """
    A class to handle report generation in different formats.
    This encapsulation allows for easy modification of report formatting,
    switching between different PDF generation libraries, and enforcing compliance
    with explicit disclaimer requirements. See the full disclaimer text below.
    
    Full Disclaimer:
        {}
        
    Note: This software and its generated reports are provided "AS IS" without any warranty,
          express or implied. Users are advised to consult professional counsel regarding legal compliance.
    """.format(DISCLAIMER_FULL)

    @staticmethod
    def generate_markdown_report(report: EvaluationReport) -> str:
        """Generate a Markdown report based on the evaluation report model."""
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
        """Save markdown report to file. Returns True if successful."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            return True
        except Exception as e:
            logging.error(f"Failed to save markdown report: {e}")
            return False

    @staticmethod
    def _build_story_from_markdown(markdown_content: str) -> List[Any]:
        """
        Convert the markdown content into a list of ReportLab flowables.
        This simple parser splits lines and processes basic elements, applying bold conversion.
        """
        styles = getSampleStyleSheet()
        story = []
        buffer = []
        for line in markdown_content.splitlines():
            stripped = line.strip()
            # Process headings
            if stripped.startswith("## "):
                # Flush the buffer if exists
                if buffer:
                    paragraph_text = " ".join(buffer)
                    # Convert markdown bold markers to HTML tags.
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                # Create a heading paragraph after converting bold.
                heading_text = convert_bold(stripped[3:])
                story.append(Paragraph(heading_text, styles["Heading2"]))
                story.append(Spacer(1, 12))
            elif stripped.startswith("# "):
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                heading_text = convert_bold(stripped[2:])
                story.append(Paragraph(heading_text, styles["Title"]))
                story.append(Spacer(1, 12))
            elif stripped.startswith("- "):
                # Flush the buffer and add bullet item
                if buffer:
                    paragraph_text = " ".join(buffer)
                    paragraph_text = convert_bold(paragraph_text)
                    story.append(Paragraph(paragraph_text, styles["BodyText"]))
                    buffer = []
                bullet_text = convert_bold(stripped[2:])
                # Using the bulletText parameter to add a bullet.
                story.append(Paragraph(bullet_text, styles["BodyText"], bulletText="•"))
                story.append(Spacer(1, 6))
            elif stripped == "":
                # Blank line; flush buffer.
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
        Generate a PDF report from markdown content using ReportLab.
        This implementation converts markdown into a set of Platypus flowables,
        applies a custom page template (with a light grey background, watermark, and footer disclaimer),
        and inserts the full disclaimer (wrapped in KeepTogether so that it fits in one page).
        
        The output file name is suffixed with a timestamp in '-yyyymmddhhmmss' format.
        The method returns the final output file path (as a string) on successful generation.
        """
        try:
            # Ensure the output directory exists.
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Append timestamp to the provided file name.
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            stem = output_path_obj.stem
            new_filename = f"{stem}-{timestamp}.pdf"
            new_output_path_obj = output_path_obj.parent / new_filename

            # Build the story (list of flowables) from the markdown content.
            story = ReportGenerator._build_story_from_markdown(markdown_content)

            styles = getSampleStyleSheet()

            # Append a page break and a full disclaimer page.
            disclaimer_flowable = KeepTogether([
                Paragraph("Disclaimer", styles["Heading2"]),
                Spacer(1, 12),
                Paragraph(DISCLAIMER_FULL, styles["BodyText"]),
                Spacer(1, 12),
            ])
            story.append(PageBreak())
            story.append(disclaimer_flowable)

            # Define an onPage callback for custom drawing (background, watermark, footer).
            def draw_page(canvas, doc):
                # Draw a light grey background.
                canvas.saveState()
                canvas.setFillColor(colors.lightgrey)
                canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], stroke=0, fill=1)
                canvas.restoreState()

                # Draw a watermark text.
                canvas.saveState()
                canvas.setFont("Helvetica", 50)
                canvas.setFillColorRGB(0.6, 0.6, 0.6)
                canvas.drawCentredString(doc.pagesize[0] / 2, doc.pagesize[1] / 2, "CONFIDENTIAL")
                canvas.restoreState()

                # Draw a footer disclaimer.
                canvas.saveState()
                canvas.setFont("Helvetica", 8)
                canvas.setFillColor(colors.black)
                canvas.drawCentredString(doc.pagesize[0] / 2, 20, DISCLAIMER_SHORT)
                canvas.restoreState()

            # Create a BaseDocTemplate with a custom page template.
            doc = BaseDocTemplate(str(new_output_path_obj), pagesize=A4)
            frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
            template = PageTemplate(id='custom', frames=frame, onPage=draw_page)
            doc.addPageTemplates([template])
            doc.build(story)
            logging.info(f"PDF generated at {new_output_path_obj.resolve()}")
            return str(new_output_path_obj.resolve())

        except ImportError as ie:
            logging.error(
                "Required library for ReportLab PDF generation is not installed. Please install it with: pip install reportlab"
            )
            return ""
        except Exception as e:
            logging.error(f"Failed to generate PDF report with ReportLab: {e}")
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

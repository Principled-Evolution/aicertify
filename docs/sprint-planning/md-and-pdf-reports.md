## 1. Enhanced Reporting & Output

### 1.1 Formatted Markdown & PDF Reports
- **Why**: Post-evaluation, many compliance or QA teams will want a **shareable** document for internal sign-off or auditing. 
- **Implementation**:  
  1. Modify the CLI (e.g., `eval-all`) to **optionally** generate a Markdown report.  
     - Summarize key findings: fairness, PII, OPA results, pass/fail metrics.  
  2. Use a Python-based PDF library (e.g., `WeasyPrint`, `xhtml2pdf`) or a Node-based library to convert the generated Markdown to PDF.  
  3. Provide minimal **template** styling so the result is polished but easy to customize.

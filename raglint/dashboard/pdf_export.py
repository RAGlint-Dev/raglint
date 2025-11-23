"""
PDF Export for RAGLint Reports
"""

from io import BytesIO
from typing import Dict, Any, List
from datetime import datetime

def generate_pdf_report(run_data: Dict[str, Any], items: List[Dict[str, Any]]) -> bytes:
    """
    Generate a PDF report from run data
    Uses WeasyPrint for HTML-to-PDF conversion
    """
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        # Fallback: Simple text-based PDF using ReportLab
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("RAGLint Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 12))
        
        # Summary Metrics
        summary_title = Paragraph("Summary Metrics", styles['Heading1'])
        story.append(summary_title)
        
        metrics = run_data.get('metrics_summary', {})
        metrics_data = [
            ['Metric', 'Value'],
            ['Faithfulness', f"{metrics.get('avg_faithfulness', 0):.2f}"],
            ['Semantic Similarity', f"{metrics.get('avg_semantic', 0):.2f}"],
            ['Context Precision', f"{metrics.get('retrieval_stats', {}).get('precision', 0):.2f}"],
            ['Context Recall', f"{metrics.get('retrieval_stats', {}).get('recall', 0):.2f}"],
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 12))
        
        # Detailed Results
        results_title = Paragraph("Detailed Results", styles['Heading1'])
        story.append(results_title)
        
        for i, item in enumerate(items[:10], 1):  # Limit to first 10 items
            item_title = Paragraph(f"Query {i}: {item.get('query', 'N/A')[:50]}...", styles['Heading2'])
            story.append(item_title)
            
            item_metrics = item.get('metrics', {})
            item_data = [
                ['Metric', 'Score'],
                ['Faithfulness',f"{item_metrics.get('faithfulness_score', 0):.2f}"],
                ['Semantic', f"{item_metrics.get('semantic_score', 0):.2f}"],
            ]
            
            item_table = Table(item_data)
            item_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))
            story.append(item_table)
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        return buffer.getvalue()
    
    # If WeasyPrint is available, use it for better formatting
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2563eb; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #2563eb; color: white; }}
        </style>
    </head>
    <body>
        <h1>RAGLint Analysis Report</h1>
        <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        
        <h2>Summary Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Faithfulness</td><td>{run_data.get('metrics_summary', {}).get('avg_faithfulness', 0):.2f}</td></tr>
            <tr><td>Semantic</td><td>{run_data.get('metrics_summary', {}).get('avg_semantic', 0):.2f}</td></tr>
        </table>
        
        <h2>Detailed Results</h2>
        {''.join([f"<h3>Query {i}: {item.get('query', 'N/A')[:50]}...</h3>" for i, item in enumerate(items[:10], 1)])}
    </body>
    </html>
    """
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

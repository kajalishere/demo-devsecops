#!/usr/bin/env python3
"""
Safety Report to PDF Generator
Converts safety-report.json to a readable PDF
"""

import json
import os
import sys
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    sys.exit(1)


def main():
    """Main function to generate PDF"""
    
    input_file = 'safety-report.json'
    output_file = 'security_report.pdf'
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Skipping PDF generation.")
        sys.exit(0)
    
    try:
        # Load JSON
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a3a52'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph('Security Scan Report', title_style))
        
        # Metadata
        meta = data.get('report_meta', {})
        meta_data = [
            ['Scan Date', meta.get('timestamp', 'N/A')],
            ['Safety Version', meta.get('safety_version', 'N/A')],
            ['Packages Scanned', str(meta.get('packages_found', 0))],
            ['Vulnerabilities Found', str(meta.get('vulnerabilities_found', 0))],
        ]
        
        meta_table = Table(meta_data, colWidths=[2.5*inch, 3.5*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWHEIGHT', (0, 0), (-1, -1), 25),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Vulnerabilities Summary
        story.append(Paragraph('Vulnerabilities by Package', styles['Heading2']))
        
        remediations = data.get('remediations', {})
        if remediations:
            vuln_data = [['Package', 'Version', 'Count']]
            for pkg, info in sorted(remediations.items(), key=lambda x: x[1].get('vulnerabilities_found', 0), reverse=True)[:15]:
                vuln_data.append([
                    pkg,
                    info.get('current_version', 'N/A'),
                    str(info.get('vulnerabilities_found', 0))
                ])
            
            vuln_table = Table(vuln_data, colWidths=[2*inch, 2*inch, 1.5*inch])
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWHEIGHT', (0, 0), (-1, -1), 20),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(vuln_table)
        else:
            story.append(Paragraph('No vulnerabilities found.', styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF Report Generated: {output_file}")
        sys.exit(0)
        
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not valid JSON")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

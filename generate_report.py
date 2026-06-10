"""
Safety Report to PDF Generator
Converts JSON security scan report into a professional PDF document
"""

import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class SafetyReportGenerator:
    """Generate professional PDF reports from Safety JSON output"""
    
    def __init__(self, json_file, output_file="security_report.pdf"):
        self.json_file = json_file
        self.output_file = output_file
        self.doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        self.data = self._load_json()
    
    def _load_json(self):
        """Load JSON report data"""
        if not os.path.exists(self.json_file):
            print(f"Error: {self.json_file} not found")
            return None
        
        with open(self.json_file, 'r') as f:
            return json.load(f)
    
    def add_title(self):
        """Add report title"""
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("🔒 Security Dependency Scan Report", title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.2*inch))
    
    def add_metadata(self):
        """Add report metadata"""
        meta = self.data.get('report_meta', {})
        
        meta_data = [
            ['Scan Date', meta.get('timestamp', 'N/A')],
            ['Safety Version', meta.get('safety_version', 'N/A')],
            ['Python Version', meta.get('telemetry', {}).get('python_version', 'N/A')],
            ['Total Packages Scanned', str(meta.get('packages_found', 0))],
            ['Repository', meta.get('git', {}).get('origin', 'N/A')],
            ['Branch', meta.get('git', {}).get('branch', 'N/A')],
        ]
        
        meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        
        self.story.append(meta_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_summary(self):
        """Add vulnerability summary"""
        meta = self.data.get('report_meta', {})
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        self.story.append(Paragraph("📊 Vulnerability Summary", title_style))
        
        vuln_count = meta.get('vulnerabilities_found', 0)
        severity = 'CRITICAL' if vuln_count > 15 else 'HIGH' if vuln_count > 5 else 'MEDIUM'
        color = colors.red if severity == 'CRITICAL' else colors.orange if severity == 'HIGH' else colors.yellow
        
        summary_data = [
            ['Total Vulnerabilities Found', str(vuln_count), severity],
            ['Ignored Vulnerabilities', str(meta.get('vulnerabilities_ignored', 0)), 'OK'],
            ['Packages with Vulnerabilities', str(len(self.data.get('remediations', {}))), 'INFO'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
            ('BACKGROUND', (2, 0), (2, 0), color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (2, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ]))
        
        self.story.append(summary_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_vulnerabilities(self):
        """Add detailed vulnerabilities list"""
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        self.story.append(Paragraph("🔴 Detailed Vulnerabilities", title_style))
        
        vulns = self.data.get('vulnerabilities', [])
        
        if not vulns:
            self.story.append(Paragraph("No vulnerabilities found.", self.styles['Normal']))
            return
        
        # Create table with vulnerabilities
        vuln_data = [['Package', 'Vulnerability ID', 'Severity', 'Current Version']]
        
        for vuln in vulns[:20]:  # Limit to first 20 to fit on page
            pkg = vuln.get('package_name', 'Unknown')
            vid = vuln.get('vulnerability_id', 'N/A')
            severity = vuln.get('severity', 'Unknown')
            version = vuln.get('analyzed_version', 'N/A')
            
            vuln_data.append([pkg, vid, severity or 'N/A', version])
        
        vuln_table = Table(vuln_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
        vuln_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        self.story.append(vuln_table)
        
        if len(vulns) > 20:
            self.story.append(Paragraph(
                f"<br/><i>Showing 20 of {len(vulns)} vulnerabilities. See full report in safety-report.json</i>",
                self.styles['Normal']
            ))
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_remediations(self):
        """Add remediation recommendations"""
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        self.story.append(Paragraph("✅ Remediation Recommendations", title_style))
        
        remediations = self.data.get('remediations', {})
        
        if not remediations:
            self.story.append(Paragraph("No remediations available.", self.styles['Normal']))
            return
        
        remediation_data = [['Package', 'Current Version', 'Vulnerabilities Found']]
        
        for pkg, info in list(remediations.items())[:15]:
            current = info.get('current_version', 'N/A')
            vuln_count = info.get('vulnerabilities_found', 0)
            remediation_data.append([pkg, current, str(vuln_count)])
        
        remediation_table = Table(remediation_data, colWidths=[2*inch, 2*inch, 2*inch])
        remediation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5016')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        self.story.append(remediation_table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_footer(self):
        """Add footer with recommendations"""
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph(
            "<b>Recommendations:</b><br/>"
            "1. Review all vulnerabilities in detail<br/>"
            "2. Update vulnerable packages to fixed versions<br/>"
            "3. Test thoroughly before deploying<br/>"
            "4. Run security scans regularly in CI/CD pipeline<br/>",
            self.styles['Normal']
        ))
        
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            "This report is auto-generated by the Safety security scanning tool",
            footer_style
        ))
    
    def generate(self):
        """Generate the PDF report"""
        if not self.data:
            print("Failed to load JSON data")
            return False
        
        try:
            self.add_title()
            self.add_metadata()
            self.add_summary()
            self.add_vulnerabilities()
            self.add_remediations()
            self.add_footer()
            
            self.doc.build(self.story)
            print(f"✅ PDF report generated: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Error generating PDF: {str(e)}")
            return False


if __name__ == '__main__':
    # Generate report from safety-report.json
    generator = SafetyReportGenerator('safety-report.json', 'security_report.pdf')
    generator.generate()

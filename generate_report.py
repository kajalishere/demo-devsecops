#!/usr/bin/env python3
"""
Safety Report to PDF Generator - PRODUCTION VERSION
Converts safety-report.json to professional PDF with full error handling
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def print_debug(msg):
    """Print debug message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")


def check_dependencies():
    """Check if required packages are installed"""
    print_debug("Checking dependencies...")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate
        print_debug("✅ ReportLab is installed")
        return True
    except ImportError as e:
        print_debug(f"❌ Missing ReportLab: {e}")
        return False


def check_input_file(filename):
    """Check if input JSON file exists"""
    print_debug(f"Checking for input file: {filename}")
    
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print_debug(f"✅ Found {filename} ({size} bytes)")
        return True
    else:
        print_debug(f"❌ File not found: {filename}")
        return False


def validate_json(filename):
    """Validate JSON structure"""
    print_debug(f"Validating JSON structure...")
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Check required keys
        if 'report_meta' not in data:
            print_debug("❌ Missing 'report_meta' key in JSON")
            return None
        
        print_debug("✅ JSON is valid and has required structure")
        return data
        
    except json.JSONDecodeError as e:
        print_debug(f"❌ Invalid JSON: {e}")
        return None
    except Exception as e:
        print_debug(f"❌ Error reading JSON: {e}")
        return None


def generate_pdf(data, output_file):
    """Generate PDF from validated data"""
    print_debug(f"Starting PDF generation to {output_file}...")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        print_debug("Initializing PDF document...")
        
        # Create PDF
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Extract metadata
        meta = data.get('report_meta', {})
        print_debug(f"Report Date: {meta.get('timestamp', 'N/A')}")
        print_debug(f"Packages: {meta.get('packages_found', 0)}")
        print_debug(f"Vulnerabilities: {meta.get('vulnerabilities_found', 0)}")
        
        # ===== TITLE =====
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a3a52'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph('Security Dependency Scan Report', title_style))
        print_debug("✅ Added title")
        
        # ===== METADATA TABLE =====
        meta_data = [
            ['Scan Date', meta.get('timestamp', 'N/A')],
            ['Safety Version', meta.get('safety_version', 'N/A')],
            ['Packages Scanned', str(meta.get('packages_found', 0))],
            ['Vulnerabilities', str(meta.get('vulnerabilities_found', 0))],
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
        print_debug("✅ Added metadata table")
        
        # ===== VULNERABILITIES =====
        story.append(Paragraph('Vulnerabilities by Package', styles['Heading2']))
        
        remediations = data.get('remediations', {})
        print_debug(f"Found {len(remediations)} packages with vulnerabilities")
        
        if remediations:
            vuln_data = [['Package', 'Version', 'Count']]
            
            # Sort by vulnerability count
            sorted_pkgs = sorted(
                remediations.items(),
                key=lambda x: x[1].get('vulnerabilities_found', 0),
                reverse=True
            )[:15]  # Limit to top 15
            
            for pkg, info in sorted_pkgs:
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
            print_debug(f"✅ Added vulnerability table ({len(sorted_pkgs)} packages)")
        else:
            story.append(Paragraph('No vulnerabilities found.', styles['Normal']))
            print_debug("ℹ️  No vulnerabilities found")
        
        story.append(Spacer(1, 0.3*inch))
        
        # ===== FOOTER =====
        footer_text = f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # ===== BUILD PDF =====
        print_debug("Building PDF document...")
        doc.build(story)
        
        # Verify output
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print_debug(f"✅ PDF generated successfully: {output_file} ({size} bytes)")
            return True
        else:
            print_debug(f"❌ PDF file was not created")
            return False
            
    except Exception as e:
        print_debug(f"❌ Error during PDF generation: {type(e).__name__}: {e}")
        import traceback
        print_debug(traceback.format_exc())
        return False


def main():
    """Main function"""
    print_debug("=" * 60)
    print_debug("SAFETY REPORT TO PDF GENERATOR")
    print_debug("=" * 60)
    
    input_file = 'safety-report.json'
    output_file = 'security_report.pdf'
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_debug("⚠️  ReportLab not available - skipping PDF generation")
        print_debug("Install with: pip install reportlab")
        sys.exit(0)  # Don't fail, just skip
    
    # Step 2: Check input file
    if not check_input_file(input_file):
        print_debug(f"⚠️  {input_file} not found - skipping PDF generation")
        print_debug("This is expected if Security scan hasn't run yet")
        sys.exit(0)  # Don't fail, just skip
    
    # Step 3: Validate JSON
    data = validate_json(input_file)
    if data is None:
        print_debug("❌ JSON validation failed")
        sys.exit(1)
    
    # Step 4: Generate PDF
    print_debug("")
    success = generate_pdf(data, output_file)
    
    print_debug("")
    print_debug("=" * 60)
    if success:
        print_debug("✅ SUCCESS: PDF generation completed")
        print_debug("=" * 60)
        sys.exit(0)
    else:
        print_debug("❌ FAILURE: PDF generation failed")
        print_debug("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()

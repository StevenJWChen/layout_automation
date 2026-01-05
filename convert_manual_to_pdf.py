#!/usr/bin/env python3
"""
Convert GDS User Manual from Markdown to PDF
"""

import markdown2
from weasyprint import HTML, CSS
from pathlib import Path

def markdown_to_pdf(md_file: str, pdf_file: str):
    """Convert markdown file to PDF with professional styling"""

    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown2.markdown(
        md_content,
        extras=['tables', 'fenced-code-blocks', 'header-ids', 'toc']
    )

    # Add CSS styling for professional appearance
    css_style = """
    @page {
        size: A4;
        margin: 2.5cm;
        @top-center {
            content: "GDS Import/Export User Manual";
            font-size: 10pt;
            color: #666;
        }
        @bottom-right {
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }

    body {
        font-family: 'Arial', 'Helvetica', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        max-width: 100%;
    }

    h1 {
        color: #0066cc;
        font-size: 24pt;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
        page-break-before: always;
    }

    h1:first-of-type {
        page-break-before: avoid;
        font-size: 32pt;
        text-align: center;
        border-bottom: none;
    }

    h2 {
        color: #0088cc;
        font-size: 18pt;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 5px;
    }

    h3 {
        color: #00aacc;
        font-size: 14pt;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    h4 {
        color: #555;
        font-size: 12pt;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    code {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 2px 5px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        color: #c7254e;
    }

    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-left: 4px solid #0066cc;
        border-radius: 4px;
        padding: 15px;
        overflow-x: auto;
        margin: 15px 0;
        page-break-inside: avoid;
    }

    pre code {
        background: none;
        border: none;
        padding: 0;
        color: #333;
        font-size: 9pt;
        line-height: 1.4;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
        page-break-inside: avoid;
    }

    th {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        padding: 10px;
        text-align: left;
        border: 1px solid #0055aa;
    }

    td {
        padding: 8px;
        border: 1px solid #ddd;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    blockquote {
        border-left: 4px solid #0066cc;
        margin: 15px 0;
        padding: 10px 20px;
        background-color: #f0f7ff;
        font-style: italic;
    }

    a {
        color: #0066cc;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    ul, ol {
        margin: 10px 0;
        padding-left: 30px;
    }

    li {
        margin: 5px 0;
    }

    hr {
        border: none;
        border-top: 2px solid #e0e0e0;
        margin: 30px 0;
    }

    .page-break {
        page-break-after: always;
    }

    strong {
        color: #0066cc;
        font-weight: bold;
    }

    em {
        font-style: italic;
        color: #555;
    }
    """

    # Create complete HTML document
    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>GDS Import/Export User Manual</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF
    print(f"Converting {md_file} to PDF...")
    HTML(string=html_doc).write_pdf(
        pdf_file,
        stylesheets=[CSS(string=css_style)]
    )
    print(f"✓ Created: {pdf_file}")

    # Get file size
    size_kb = Path(pdf_file).stat().st_size / 1024
    print(f"  File size: {size_kb:.1f} KB")

if __name__ == '__main__':
    markdown_to_pdf('GDS_USER_MANUAL.md', 'GDS_USER_MANUAL.pdf')

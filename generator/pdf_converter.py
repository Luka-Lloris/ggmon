#!/usr/bin/env python3
"""
Markdown을 PDF로 변환하는 스크립트
markdown2 및 weasyprint를 사용합니다.
"""

import sys
from pathlib import Path
import argparse


class PDFConverter:
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """필요한 패키지 확인"""
        try:
            import markdown
            from weasyprint import HTML, CSS
            self.markdown = markdown
            self.HTML = HTML
            self.CSS = CSS
        except ImportError as e:
            print("❌ 필요한 패키지가 설치되지 않았습니다.")
            print("   다음 명령어로 설치하세요:")
            print("   pip install markdown weasyprint")
            sys.exit(1)
    
    def convert(self, input_file, output_file=None):
        """Markdown을 PDF로 변환"""
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
            sys.exit(1)
        
        # 출력 파일명 결정
        if output_file is None:
            output_file = input_path.with_suffix('.pdf')
        else:
            output_file = Path(output_file)
        
        print(f"📄 PDF 변환 중: {input_path} → {output_file}")
        
        # Markdown 읽기
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Markdown을 HTML로 변환
        html_content = self.markdown.markdown(
            md_content,
            extensions=['tables', 'nl2br', 'sane_lists']
        )
        
        # HTML 템플릿 적용
        full_html = self.create_html_template(html_content)
        
        # PDF 생성
        try:
            self.HTML(string=full_html).write_pdf(
                output_file,
                stylesheets=[self.CSS(string=self.get_css())]
            )
            print(f"✅ PDF 생성 완료: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ PDF 생성 실패: {e}")
            sys.exit(1)
    
    def create_html_template(self, content):
        """HTML 템플릿 생성"""
        return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>계약서</title>
</head>
<body>
    {content}
</body>
</html>
"""
    
    def get_css(self):
        """PDF 스타일 CSS"""
        return """
@page {
    size: A4;
    margin: 2cm;
}

body {
    font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    font-size: 20pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1cm;
    padding-bottom: 0.5cm;
    border-bottom: 2px solid #333;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    margin-top: 1cm;
    margin-bottom: 0.5cm;
    color: #000;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 0.5cm;
    margin-bottom: 0.3cm;
}

p {
    margin-bottom: 0.3cm;
    text-align: justify;
}

ul, ol {
    margin-left: 1cm;
    margin-bottom: 0.5cm;
}

li {
    margin-bottom: 0.2cm;
}

strong {
    font-weight: bold;
    color: #000;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1cm 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5cm 0;
}

table th, table td {
    border: 1px solid #ddd;
    padding: 0.3cm;
    text-align: left;
}

table th {
    background-color: #f5f5f5;
    font-weight: bold;
}

.signature-section {
    margin-top: 2cm;
    page-break-inside: avoid;
}
"""


def main():
    parser = argparse.ArgumentParser(description='Markdown을 PDF로 변환')
    parser.add_argument('--input', required=True, help='입력 Markdown 파일')
    parser.add_argument('--output', help='출력 PDF 파일 (기본값: 입력파일명.pdf)')
    
    args = parser.parse_args()
    
    converter = PDFConverter()
    converter.convert(args.input, args.output)


if __name__ == '__main__':
    main()
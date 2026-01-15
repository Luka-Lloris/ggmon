#!/usr/bin/env python3
"""
계약서 자동 생성 스크립트
JSON 데이터와 템플릿을 결합하여 계약서를 생성합니다.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse


class ContractGenerator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.templates_path = self.base_path / "templates"
        self.outputs_path = self.base_path / "outputs" / "contracts"
        self.config_path = self.base_path / "config"
        
        # 출력 디렉토리 생성
        self.outputs_path.mkdir(parents=True, exist_ok=True)
    
    def load_json(self, filepath):
        """JSON 파일 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {filepath}")
            print(f"   {e}")
            sys.exit(1)
    
    def load_template(self, template_name):
        """템플릿 파일 로드"""
        template_path = self.templates_path / template_name
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ 템플릿을 찾을 수 없습니다: {template_path}")
            sys.exit(1)
    
    def calculate_net_amount(self, gross_amount, tax_rate):
        """실수령액 계산"""
        tax = gross_amount * (tax_rate / 100)
        return gross_amount - tax
    
    def format_currency(self, amount):
        """금액 포맷팅"""
        return f"{amount:,}"
    
    def prepare_variables(self, worker_data, contract_data, company_data):
        """템플릿 변수 준비"""
        # 실수령액 계산
        gross_amount = contract_data['payment']['total_amount']
        tax_rate = contract_data['payment']['tax_rate']
        net_amount = self.calculate_net_amount(gross_amount, tax_rate)
        
        variables = {
            # 계약 정보
            'contract_id': contract_data['contract_id'],
            'contract_date': contract_data['contract_date'],
            'start_date': contract_data['start_date'],
            'end_date': contract_data['end_date'],
            'work_location': contract_data.get('work_location', '협의'),
            'work_description': contract_data['work_description'],
            
            # 회사 정보
            'company_name': company_data['company_name'],
            'company_ceo': company_data['company_ceo'],
            'company_address': company_data['company_address'],
            'company_registration_number': company_data['company_registration_number'],
            'company_phone': company_data.get('company_phone', ''),
            
            # 인력 정보
            'name': worker_data['name'],
            'rrn': worker_data['rrn'],
            'phone': worker_data['phone'],
            'email': worker_data.get('email', ''),
            'address': worker_data['address'],
            
            # 은행 정보
            'bank_name': worker_data['bank']['name'],
            'account_number': worker_data['bank']['account'],
            'account_holder': worker_data['bank']['holder'],
            
            # 지급 정보
            'payment_amount': self.format_currency(gross_amount),
            'payment_cycle': self.get_payment_cycle_korean(contract_data['payment']['payment_cycle']),
            'payment_day': contract_data['payment'].get('payment_day', ''),
            'payment_method': contract_data['payment'].get('method', '계좌이체'),
            'tax_rate': tax_rate,
            'net_amount': self.format_currency(int(net_amount)),
        }
        
        return variables
    
    def get_payment_cycle_korean(self, cycle):
        """지급 주기를 한국어로 변환"""
        cycles = {
            'daily': '일급',
            'weekly': '주급',
            'monthly': '월급',
            'lump_sum': '일시불'
        }
        return cycles.get(cycle, cycle)
    
    def replace_variables(self, template, variables):
        """템플릿 변수 치환"""
        content = template
        for key, value in variables.items():
            placeholder = '{{' + key + '}}'
            content = content.replace(placeholder, str(value))
        
        # 치환되지 않은 변수 확인
        import re
        remaining = re.findall(r'{{([^}]+)}}', content)
        if remaining:
            print(f"⚠️  경고: 치환되지 않은 변수가 있습니다: {', '.join(set(remaining))}")
        
        return content
    
    def generate(self, worker_file, contract_file, company_file=None):
        """계약서 생성"""
        print("📝 계약서 생성 시작...")
        
        # 데이터 로드
        print("   데이터 로딩 중...")
        worker_data = self.load_json(worker_file)
        contract_data = self.load_json(contract_file)
        
        if company_file is None:
            company_file = self.config_path / "company.json"
        company_data = self.load_json(company_file)
        
        # 템플릿 로드
        template_name = contract_data['template']
        print(f"   템플릿 로딩: {template_name}")
        template = self.load_template(template_name)
        
        # 변수 준비 및 치환
        print("   변수 치환 중...")
        variables = self.prepare_variables(worker_data, contract_data, company_data)
        contract_content = self.replace_variables(template, variables)
        
        # 파일 저장
        output_filename = f"{contract_data['contract_id']}_{worker_data['name']}.md"
        output_path = self.outputs_path / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(contract_content)
        
        print(f"✅ 계약서 생성 완료: {output_path}")
        
        # NDA 생성
        if contract_data.get('nda_required', False):
            self.generate_nda(worker_data, contract_data, company_data)
        
        return output_path
    
    def generate_nda(self, worker_data, contract_data, company_data):
        """비밀유지계약서 생성"""
        print("   NDA 생성 중...")
        
        template = self.load_template('nda.md')
        
        variables = {
            'contract_date': contract_data['contract_date'],
            'company_name': company_data['company_name'],
            'name': worker_data['name'],
            'end_date': contract_data['end_date'],
            'retention_years': company_data['contract_defaults'].get('nda_retention_years', 3)
        }
        
        nda_content = self.replace_variables(template, variables)
        
        output_filename = f"{contract_data['contract_id']}_NDA_{worker_data['name']}.md"
        output_path = self.outputs_path / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(nda_content)
        
        print(f"✅ NDA 생성 완료: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='계약서 자동 생성')
    parser.add_argument('--worker', required=True, help='인력 정보 JSON 파일 경로')
    parser.add_argument('--contract', required=True, help='계약 정보 JSON 파일 경로')
    parser.add_argument('--company', help='회사 정보 JSON 파일 경로 (기본값: config/company.json)')
    parser.add_argument('--base-path', default='.', help='프로젝트 루트 경로')
    
    args = parser.parse_args()
    
    generator = ContractGenerator(args.base_path)
    generator.generate(args.worker, args.contract, args.company)


if __name__ == '__main__':
    main()
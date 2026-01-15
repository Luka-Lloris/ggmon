#!/usr/bin/env python3
"""
JSON 스키마 검증 스크립트
데이터가 스키마를 준수하는지 확인합니다.
"""

import json
import sys
from pathlib import Path
import argparse


class SchemaValidator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.schema_path = self.base_path / "schema"
    
    def load_json(self, filepath):
        """JSON 파일 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_worker(self, data):
        """인력 정보 검증"""
        errors = []
        
        # 필수 필드 확인
        required_fields = ['worker_id', 'name', 'rrn', 'phone', 'address', 'bank', 'type', 'tax_rate']
        for field in required_fields:
            if field not in data:
                errors.append(f"필수 필드 누락: {field}")
        
        # worker_id 형식 확인
        if 'worker_id' in data:
            if not data['worker_id'].startswith('W') or len(data['worker_id']) != 8:
                errors.append("worker_id는 'W' + 7자리 숫자 형식이어야 합니다 (예: W2024001)")
        
        # 전화번호 형식 확인
        if 'phone' in data:
            if not self.validate_phone(data['phone']):
                errors.append("전화번호 형식이 올바르지 않습니다 (예: 010-1234-5678)")
        
        # 은행 정보 확인
        if 'bank' in data:
            bank_required = ['name', 'account', 'holder']
            for field in bank_required:
                if field not in data['bank']:
                    errors.append(f"은행 정보 필수 필드 누락: bank.{field}")
        
        # 인력 유형 확인
        if 'type' in data:
            valid_types = ['freelancer', 'daily_worker', 'contractor']
            if data['type'] not in valid_types:
                errors.append(f"유효하지 않은 인력 유형: {data['type']} (가능: {', '.join(valid_types)})")
        
        return errors
    
    def validate_contract(self, data):
        """계약 정보 검증"""
        errors = []
        
        # 필수 필드 확인
        required_fields = ['contract_id', 'worker_id', 'contract_date', 'start_date', 
                          'end_date', 'work_description', 'payment', 'template']
        for field in required_fields:
            if field not in data:
                errors.append(f"필수 필드 누락: {field}")
        
        # contract_id 형식 확인
        if 'contract_id' in data:
            if not data['contract_id'].startswith('C') or len(data['contract_id']) != 8:
                errors.append("contract_id는 'C' + 7자리 숫자 형식이어야 합니다 (예: C2024001)")
        
        # worker_id 형식 확인
        if 'worker_id' in data:
            if not data['worker_id'].startswith('W') or len(data['worker_id']) != 8:
                errors.append("worker_id는 'W' + 7자리 숫자 형식이어야 합니다 (예: W2024001)")
        
        # 날짜 검증
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                errors.append("시작일이 종료일보다 늦습니다")
        
        # 지급 정보 확인
        if 'payment' in data:
            payment_required = ['total_amount', 'payment_cycle', 'tax_rate']
            for field in payment_required:
                if field not in data['payment']:
                    errors.append(f"지급 정보 필수 필드 누락: payment.{field}")
            
            # 금액 확인
            if 'total_amount' in data['payment']:
                if data['payment']['total_amount'] <= 0:
                    errors.append("총 보수는 0보다 커야 합니다")
            
            # 세율 확인
            if 'tax_rate' in data['payment']:
                if not 0 <= data['payment']['tax_rate'] <= 100:
                    errors.append("세율은 0~100 사이여야 합니다")
        
        # 템플릿 확인
        if 'template' in data:
            valid_templates = ['freelancer_contract.md', 'daily_worker_contract.md', 'contractor_contract.md']
            if data['template'] not in valid_templates:
                errors.append(f"유효하지 않은 템플릿: {data['template']}")
        
        return errors
    
    def validate_payment(self, data):
        """지급 정보 검증"""
        errors = []
        
        # 필수 필드 확인
        required_fields = ['payment_id', 'contract_id', 'worker_id', 'payment_date',
                          'gross_amount', 'tax_withheld', 'net_amount', 'status']
        for field in required_fields:
            if field not in data:
                errors.append(f"필수 필드 누락: {field}")
        
        # payment_id 형식 확인
        if 'payment_id' in data:
            if not data['payment_id'].startswith('P') or len(data['payment_id']) != 8:
                errors.append("payment_id는 'P' + 7자리 숫자 형식이어야 합니다 (예: P2024001)")
        
        # 금액 검증
        if all(k in data for k in ['gross_amount', 'tax_withheld', 'net_amount']):
            expected_net = data['gross_amount'] - data['tax_withheld']
            if abs(data['net_amount'] - expected_net) > 1:  # 반올림 오차 허용
                errors.append(f"실지급액 계산 오류: {data['net_amount']} != {expected_net}")
        
        # 상태 확인
        if 'status' in data:
            valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
            if data['status'] not in valid_statuses:
                errors.append(f"유효하지 않은 상태: {data['status']}")
        
        return errors
    
    def validate_phone(self, phone):
        """전화번호 형식 검증"""
        import re
        pattern = r'^01[0-9]-[0-9]{4}-[0-9]{4}$'
        return bool(re.match(pattern, phone))
    
    def validate_file(self, filepath, data_type):
        """파일 검증"""
        print(f"🔍 검증 중: {filepath}")
        
        try:
            data = self.load_json(filepath)
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            return False
        
        # 데이터 타입별 검증
        if data_type == 'worker':
            errors = self.validate_worker(data)
        elif data_type == 'contract':
            errors = self.validate_contract(data)
        elif data_type == 'payment':
            errors = self.validate_payment(data)
        else:
            print(f"❌ 알 수 없는 데이터 타입: {data_type}")
            return False
        
        # 결과 출력
        if errors:
            print(f"❌ 검증 실패 ({len(errors)}개 오류):")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ 검증 성공")
            return True


def main():
    parser = argparse.ArgumentParser(description='JSON 데이터 검증')
    parser.add_argument('--file', required=True, help='검증할 JSON 파일 경로')
    parser.add_argument('--type', required=True, choices=['worker', 'contract', 'payment'],
                       help='데이터 타입')
    parser.add_argument('--base-path', default='.', help='프로젝트 루트 경로')
    
    args = parser.parse_args()
    
    validator = SchemaValidator(args.base_path)
    success = validator.validate_file(args.file, args.type)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
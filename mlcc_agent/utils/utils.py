import io
import csv
import json
import pandas as pd
from decimal import Decimal
from datetime import datetime, date
from google.genai import types as genai_types
from google.adk.tools.tool_context import ToolContext

VOLTAGE_MAP = {
    "S": 2.5, "R": 4, "Q": 6.3, "P": 10, "O": 16, "A": 25, "L": 35, 
    "B": 50, "M": 63, "N": 80, "C": 100, "D": 200, "E": 250, 
    "F": 350, "G": 500, "H": 630, "I": 1000, "J": 2000, "K": 3000
}

def fill_missing_columns(source_data, full_columns):
    """ 전체 컬럼 리스트를 기준으로 source_data에 값이 있으면 사용, 없으면 -1로 채움 """
    filled_data = {}
    data = [dict(row) for row in source_data]
    clean_data = data[0]
    
    for col in full_columns:
        # source_data에 키가 있고 값도 None이 아니면 그 값을 사용
        val = clean_data.get(col)
        if val is not None:
            filled_data[col] = val
        else:
            # 키가 없거나 값이 None이면 -1 할당
            filled_data[col] = -1
            
    chip_voltage = filled_data["chip_prod_id"][9]
    filled_data["dc_lfhv_spec_step_voltage"] = VOLTAGE_MAP[chip_voltage] * 0.5
    return filled_data

def make_json_serializable(data):
    """ 데이터 구조를 순회하며 JSON으로 변환 불가능한 타입(Decimal, datetime)을 기본 타입(float, str)으로 변환합니다. """
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(item) for item in data]
    else:
        return data

def fill_missing_columns(source_data, full_columns):
    """ 전체 컬럼 리스트를 기준으로 source_data에 값이 있으면 사용, 없으면 -1로 채움 """
    filled_data = {}
    # data = [dict(row) for row in source_data]
    clean_data = source_data
    
    for col in full_columns:
        # source_data에 키가 있고 값도 None이 아니면 그 값을 사용
        val = clean_data.get(col)
        if val is not None:
            filled_data[col] = val
        else:
            # 키가 없거나 값이 None이면 -1 할당
            filled_data[col] = -1
            
    chip_voltage = filled_data["chip_prod_id"][9]
    filled_data["dc_lfhv_spec_step_voltage"] = VOLTAGE_MAP[chip_voltage] * 0.5
    return filled_data

def validate_required_columns(lot_data, required_columns):
    """ 필수 컬럼이 채워져 있는지 확인하는 검증(Validation) 함수. """
    missing_columns = []
    
    for col in required_columns:
        # 컬럼이 존재하지 않거나, 값이 None이거나, 빈 문자열인 경우를 체크
        val = lot_data.get(col)
        if val is None or val == "":
            missing_columns.append(col)
            
    if missing_columns:
        return missing_columns
    
    return None

def dict_list_to_csv_bytes(data):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return buffer.getvalue().encode("utf-8-sig")

def dict_to_json_bytes(data):
    # 1. 파이썬 데이터를 JSON 형태의 문자열(String)로 변환
    json_str = json.dumps(data, ensure_ascii=False)
    # 2. JSON 문자열을 UTF-8 바이트(bytes) 객체로 변환하여 반환
    return json_str.encode("utf-8")

def dict_to_bytes(data_dict, filetype):
    if filetype == 'csv':
        return dict_list_to_csv_bytes(data_dict)
    elif filetype == 'json':
        return dict_to_json_bytes(data_dict)
    else:
        return None

async def save_analysis_result(data_dict, filename, tool_context: ToolContext, filetype='csv') -> dict:
    """분석 결과 데이터를 JSON Artifact로 저장합니다."""
    part = genai_types.Part(
        inline_data=genai_types.Blob(
            data=dict_to_bytes(data_dict, filetype),
            mime_type=f"text/{filetype}",
        )
    )
    filename_full = filename + tool_context.function_call_id
    version = await tool_context.save_artifact(
        filename=filename_full + f".{filetype}", 
        artifact=part
    )
    return {"saved": True, "filename": filename_full, "version": version}

def query_to_pandas(query_data):
    df = pd.DataFrame(query_data)
    json_pandas = df.to_json(force_ascii=False, date_format='iso')
    return json_pandas
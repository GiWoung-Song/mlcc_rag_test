"""Mock active_lineup_lookup tool for testing.

In production, this tool queries the mdh_continous_view_3 view
to find currently flowing chip_prod_id rows.

This mock returns sample data so the agent dialogue flow can be
tested without a real DB connection.
"""
from ..db import db

# Sample active lineup data for testing
_SAMPLE_LINEUP = [
    "CL32A106KOY8NNE",
    "CL32A106MOY8NNC",
    "CL32B106KOY8NNE",
    "CL32B106MOY8NNC",
    "CL32A475KOY8NNE",
    "CL32A475MOY8NNC",
    "CL03A475MR3CNNC",
    "CL03A475MR3CNNE",
    "CL03X475MS3CNWC",
    "CL10A106MQ8NNNC",
    "CL10A106MQ8NNNE",
    "CL10B225KP8NNNC",
    "CL21A106KPFNNNE",
    "CL21B106KOQNNNE",
]

def active_lineup_lookup(chip_prod_id: str) -> dict:
    """
    Look up currently flowing products by chip_prod_id pattern.
    
    Searches the mdh_continous_view_3 view for chip_prod_id rows matching the given pattern.
    Use '_' for unknown single-character positions and '%' for variable-length wildcards.
    
    Args:
        chip_prod_id: Full or partial chip_prod_id pattern.
    """
    pattern = chip_prod_id.strip()
    
    # SQL 파라미터 설정
    params_chip = {'chip_prod_id': f'%{pattern}%'}
    
    # SQL 쿼리 가독성 정렬
    sql = """
        SELECT DISTINCT ON (lot_count_12mon, chip_prod_id, lot_type, powder_size)
            chip_prod_id, 
            lot_type, 
            temperature, 
            voltage, 
            size_detail, 
            base_volume, 
            powder_size, 
            paste, 
            design_input_date, 
            powder_name, 
            lot_count_12mon
        FROM 
            public.mdh_contiguous_condition_view_dsgnagent
        WHERE 
            chip_prod_id ILIKE %(chip_prod_id)s
        ORDER BY 
            lot_count_12mon DESC, 
            chip_prod_id, 
            lot_type, 
            powder_size;
    """
    
    # DB 실행 및 결과 로깅
    results = db.execute_read(sql, params_chip)
    print(f"Lookup results for {pattern}: {len(results)} hits found.")
    
    return {
        "status": "success",
        "pattern": pattern,
        "hit_count": len(results),
        "hits": results,
    }
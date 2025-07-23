import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Classe para validar e sanitizar dados"""
    
    def __init__(self):
        self.required_columns = ['data', 'categoria', 'participantes']
        self.column_types = {
            'data': 'datetime',
            'categoria': 'string',
            'participantes': 'numeric',
            'latitude': 'numeric',
            'longitude': 'numeric',
            'regiao': 'string'
        }
    
    def validate_dataframe(self, df):
        """Valida um DataFrame completo"""
        errors = []
        warnings = []
        
        # Verificar colunas obrigatórias
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Colunas obrigatórias faltando: {missing_columns}")
        
        # Validar tipos de dados
        for col, expected_type in self.column_types.items():
            if col in df.columns:
                if expected_type == 'datetime':
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        errors.append(f"Coluna '{col}' deve ser do tipo datetime")
                elif expected_type == 'numeric':
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except Exception:
                            errors.append(f"Coluna '{col}' deve ser numérica")
                elif expected_type == 'string':
                    if not pd.api.types.is_string_dtype(df[col]):
                        try:
                            df[col] = df[col].astype(str)
                        except Exception:
                            errors.append(f"Coluna '{col}' deve ser string")
        
        # Checagem de valores nulos
        for col in self.required_columns:
            if col in df.columns and df[col].isnull().any():
                warnings.append(f"Coluna '{col}' possui valores nulos")
        
        return {'errors': errors, 'warnings': warnings} 
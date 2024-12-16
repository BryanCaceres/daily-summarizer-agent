import json
import traceback
from services import SummarizerService
from datetime import datetime, timedelta
import logging
from uuid import uuid4
import logging

langsmith_extra={"run_id": uuid4()}

summarizer_service = SummarizerService()

def lambda_handler(event, context):
    """
    Lambda handler que soporta múltiples fuentes de eventos
    """
    try:
        # Obtener fecha del evento
        date_str = get_date_from_event(event)
        logging.info(f"Received date: {date_str}")
        
        # Format date and get adjacent days
        date, previous_day, next_day = format_date(date_str)
        
        generated_run_id = uuid4()
        logging.info(f"######################## Generated run_id: {generated_run_id}")
        
        # Execute summarizer
        summary_result = summarizer_service.execute_summarizer(
            day=date,
            previous_day=previous_day,
            next_day=next_day,
            langsmith_extra={"run_id": generated_run_id}
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "date": date,
                "previous_day": previous_day,
                "next_day": next_day,
                "summary_result": summary_result
            })
        }
        
    except ValueError as ve:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Fecha inválida",
                "detail": str(ve)
            })
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "detail": str(e)
            })
        }

def get_date_from_event(event):
    """
    Extrae la fecha del evento desde diferentes fuentes posibles:
    - API Gateway (body)
    - EventBridge/CloudWatch Events (detail)
    - Invocación directa (date)
    """
    # Caso 1: Viene del body (API Gateway)
    if "body" in event:
        try:
            request_body = json.loads(event["body"])
            if date_str := request_body.get("day"):
                return date_str
        except json.JSONDecodeError:
            pass
    
    # Caso 2: Viene de EventBridge/CloudWatch Events
    if "detail" in event and "day" in event["detail"]:
        return event["detail"]["day"]
    
    # Caso 3: Viene como parámetro directo
    if "day" in event:
        return event["day"]
    
    # Caso 4: No se proporcionó fecha, usar fecha actual
    return None

def format_date(date_str: str = None) -> tuple[str, str, str]:
    """
    Formatea la fecha y calcula días adyacentes
    
    Args:
        date_str: Fecha en formato YYYY-MM-DD (opcional)
    
    Returns:
        tuple: (date, previous_day, next_day)
    
    Raises:
        ValueError: Si el formato de fecha es inválido
    """
    try:
        # Si no hay fecha, usar la actual
        if not date_str:
            date_obj = datetime.now()
            date_str = date_obj.strftime("%Y-%m-%d")
        else:
            # Validar y parsear la fecha proporcionada
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Calcular días adyacentes
        prev_date = date_obj - timedelta(days=1)
        next_date = date_obj + timedelta(days=1)
        
        return (
            date_str,
            prev_date.strftime("%Y-%m-%d"),
            next_date.strftime("%Y-%m-%d")
        )
 
    except ValueError:
        raise ValueError(
            f"Formato de fecha inválido: {date_str}. "
            "Debe ser YYYY-MM-DD"
        )

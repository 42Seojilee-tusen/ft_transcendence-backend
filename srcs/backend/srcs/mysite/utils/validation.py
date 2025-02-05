from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
import json
import logging

logger = logging.getLogger('utils') 

def validate_header(request, required_fields):
    missing_fields = []  # 누락된 필드 추적

    # 필드 확인
    for field in required_fields:
        if not request.header.get(field):  # 필드가 없으면 추가
            missing_fields.append(field)
    # 누락된 필드가 있으면 에러 반환
    if missing_fields:
        error_data = {}
        for missing_field in missing_fields:
            error_data[missing_field] = "header required field"
        return JsonResponse(error_data, status=400)
    return None

def check_json_data(request, required_fields):
    missing_fields = []  # 누락된 필드 추적

    # 필드 확인
    for field in required_fields:
        if not request.data.get(field):  # 필드가 없으면 추가
            missing_fields.append(field)
    # 누락된 필드가 있으면 에러 반환
    if missing_fields:
        error_data = {}
        for missing_field in missing_fields:
            error_data[missing_field] = "required field"
        raise ValidationError(error_data)

# def validate_data(request, required_fields):
#     if request.method in ["GET"]:
#         res = validate_param_data(request=request, required_fields=required_fields)
#     # elif request.method in ["POST"]:
#         # res = validate_form_data(request=request, required_fields=required_fields)
#     elif request.method in ["POST", "PUT", "PATCH", "DELETE"]:
#         res = validate_json_data(request=request, required_fields=required_fields)
#     else:
#         return JsonResponse()
#     return res

def validate_param_data(request, required_fields):
    missing_fields = []  # 누락된 필드 추적

    # 필드 확인
    for field in required_fields:
        if not request.GET.get(field):  # 필드가 없으면 추가
            missing_fields.append(field)
    # 누락된 필드가 있으면 에러 반환
    if missing_fields:
        error_data = {}
        for missing_field in missing_fields:
            error_data[missing_field] = "required field"
        return JsonResponse(error_data, status=400)
    return None

# for POST
def validate_form_data(request, required_fields):
    missing_fields = []  # 누락된 필드 추적

    # 필드 확인
    for field in required_fields:
        if not request.POST.get(field):  # 필드가 없으면 추가
            missing_fields.append(field)
    # 누락된 필드가 있으면 에러 반환
    if missing_fields:
        error_data = {}
        for missing_field in missing_fields:
            error_data[missing_field] = "required field"
        return JsonResponse(error_data, status=400)
    return None

# for PUT, PATCH, DELETE
def validate_json_data(request, required_fields):
    missing_fields = []  # 누락된 필드 추적

    # 필드 확인
    try:
        data = json.loads(request.body)  # JSON 파싱
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON format",
        }, status=400)
    for field in required_fields:
        if field not in data:  # 필드가 없으면 추가
            missing_fields.append(field)
            
    # 누락된 필드가 있으면 에러 반환
    if missing_fields:
        error_data = {}
        for missing_field in missing_fields:
            error_data[missing_field] = "required field"
        return JsonResponse(error_data, status=400)
    return None


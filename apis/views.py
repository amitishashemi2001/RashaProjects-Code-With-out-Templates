import logging
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from apis.utils.OmidPayAPI import OmidPayAPI
from apis.utils.ValidateOmidPayMixin import ValidateOmidPayMixin
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)


class OmidPayTokenView(APIView, ValidateOmidPayMixin):
    @swagger_auto_schema(
        operation_description="Generate an OmidPay token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['amount'],
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description='Payment amount'),
            },
        ),
        responses={
            200: openapi.Response(description="Token generated successfully."),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def post(self, request):
        data = request.data
        validation_error = ValidateOmidPayMixin.validate_omidpay_data(data, ['amount'])
        if validation_error:
            return validation_error

        amount = request.data.get('amount')
        token_response = OmidPayAPI.get_omidpay_token(amount)

        if token_response['status'] == 'success':
            return Response({'status': 'success', 'message':token_response },
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'error', 'message': token_response['message']},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OmidPayCallbackView(APIView, ValidateOmidPayMixin):
    @swagger_auto_schema(
        operation_description="Handle OmidPay payment callback.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['ResNum'],
            properties={
                'ResNum': openapi.Schema(type=openapi.TYPE_STRING, description='Reservation number'),
                'UserId': openapi.Schema(type=openapi.TYPE_STRING, description='User ID'),
                'RefNum': openapi.Schema(type=openapi.TYPE_STRING, description='Reference number'),
            },
        ),
        responses={
            200: openapi.Response(description="Payment success page rendered."),
            404: openapi.Response(description="Token not found"),
        }
    )
    def post(self, request):
        data = request.data
        logger.error(f"data from omid pay:{data}")
        validation_error = ValidateOmidPayMixin.validate_omidpay_data(data, ['ResNum'])
        if validation_error:
            return validation_error
        else:
            return Response({'status': 'success', 'message': data},status=status.HTTP_200_OK)


class VerifyTransactionView(APIView, ValidateOmidPayMixin):
    @swagger_auto_schema(
        operation_description="Verify an OmidPay transaction.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['RefNum', 'token', 'ResNum'],
            properties={
                'RefNum': openapi.Schema(type=openapi.TYPE_STRING, description='Reference number'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='OmidPay token'),
                'ResNum': openapi.Schema(type=openapi.TYPE_STRING, description='Reservation number'),
            },
        ),
        responses={
            200: openapi.Response(description="Verification successful."),
            500: openapi.Response(description="Verification failed"),
        }
    )
    def post(self, request):
        data = request.data
        validation_error = ValidateOmidPayMixin.validate_omidpay_data(data, ['RefNum', 'token', 'ResNum'])
        if validation_error:
            return validation_error

        verify_response = OmidPayAPI.verify_omidpay_transaction(request.data.get('RefNum'), request.data.get('token'))

        if verify_response:
            logger.error("success")
            return Response({'status': 'success', 'message': 'Verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'error', 'message': 'Verification failed'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

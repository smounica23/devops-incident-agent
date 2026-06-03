from agent.state import IncidentState

def trace_investigation(state: IncidentState) -> dict:

    affected_service = state.get("affected_service")
    trace_evidence = {
    "root_failing_span": "payment-service/PaymentValidator.validatePayment",
    "failed_spans": [
        "payment-service/PaymentValidator.validatePayment",
        "payment-service/PaymentRepository.save",
        "order-service/OrderController.createOrder"
    ],
    "downstream_affected": ["order-service"],
    "slowest_span": "payment-service/HikariPool.getConnection",
    "slowest_span_duration_ms": 7823,
    "api_gateway_5xx": True,
    "total_failed_traces": 142,
    "data_source": "mock_jaeger"
}
    return {"trace_evidence":trace_evidence}
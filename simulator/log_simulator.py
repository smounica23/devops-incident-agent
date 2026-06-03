import json
import random
import time
from datetime import datetime, timedelta, timezone
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

INDEX_NAME = "incidents-logs-" + datetime.now().strftime("%Y.%m.%d")

def create_index():
    """Create index with correct mappings if it doesn't exist"""
    try:
        exists = es.indices.exists(index=INDEX_NAME)
        if exists.meta.status == 200:
            print(f"Index {INDEX_NAME} already exists")
            return
    except Exception:
        pass
    
    mappings = {
        "properties": {
            "timestamp":     {"type": "date"},
            "service":       {"type": "keyword"},
            "level":         {"type": "keyword"},
            "message":       {"type": "text"},
            "trace_id":      {"type": "keyword"},
            "span_id":       {"type": "keyword"},
            "environment":   {"type": "keyword"},
            "host":          {"type": "keyword"},
            "error_type":    {"type": "keyword"},
            "stack_trace":   {"type": "text"},
            "http_status":   {"type": "integer"},
            "response_time": {"type": "float"},
            "user_id":       {"type": "keyword"},
            "endpoint":      {"type": "keyword"},
        }
    }
    
    es.indices.create(index=INDEX_NAME, mappings=mappings)
    print(f"Created index: {INDEX_NAME}")

def generate_log(
    service,
    level,
    message,
    timestamp,
    error_type=None,
    stack_trace=None,
    http_status=None,
    response_time=None,
    endpoint=None
):
    """Generate a single realistic log entry"""
    
    trace_id = ''.join(random.choices('abcdef0123456789', k=32))
    span_id  = ''.join(random.choices('abcdef0123456789', k=16))
    
    log = {
        "timestamp":     timestamp.isoformat(),
        "service":       service,
        "level":         level,
        "message":       message,
        "trace_id":      trace_id,
        "span_id":       span_id,
        "environment":   "production",
        "host":          f"{service}-pod-{random.randint(1,3)}",
    }
    
    if error_type:
        log["error_type"] = error_type
    if stack_trace:
        log["stack_trace"] = stack_trace
    if http_status:
        log["http_status"] = http_status
    if response_time:
        log["response_time"] = response_time
    if endpoint:
        log["endpoint"] = endpoint
    
    return log

JAVA_STACK_TRACE = """java.lang.NullPointerException: Cannot invoke method getAmount() on null object
    at com.company.payment.PaymentValidator.validatePayment(PaymentValidator.java:47)
    at com.company.payment.PaymentService.processPayment(PaymentService.java:123)
    at com.company.payment.PaymentController.pay(PaymentController.java:89)
    at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:1067)
Caused by: java.lang.NullPointerException
    at com.company.payment.PaymentValidator.validatePayment(PaymentValidator.java:47)"""

DB_STACK_TRACE = """org.postgresql.util.PSQLException: FATAL: remaining connection slots are reserved
    at org.postgresql.core.v3.ConnectionFactoryImpl.openConnectionImpl(ConnectionFactoryImpl.java:292)
    at com.company.payment.repository.PaymentRepository.save(PaymentRepository.java:34)
    at com.company.payment.PaymentService.processPayment(PaymentService.java:156)
    at com.company.payment.PaymentController.pay(PaymentController.java:89)
Caused by: java.sql.SQLException: Connection pool exhausted. Max pool size: 10
    at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:213)"""


def generate_scenario_nullpointer(base_time):
    """
    Scenario: NullPointerException in payment-service
    Timeline:
      - 14:00 to 14:15 → normal logs
      - 14:15 → deployment happens  
      - 14:22 → NPE errors start
      - 14:25 → timeouts start
      - 14:28 → DB pool exhausted
      - 14:35 → circuit breaker opens
      - 14:30 → order-service downstream failures
    """
    logs = []

    for i in range(20):
        timestamp = base_time + timedelta(minutes=random.randint(0, 14))
        logs.append(generate_log(
            service="payment-service",
            level="INFO",
            message=f"Payment processed successfully for order_id={random.randint(1000,9999)}",
            timestamp=timestamp,
            http_status=200,
            response_time=random.uniform(50, 150),
            endpoint="/api/v1/payments"
        ))

    logs.append(generate_log(
        service="payment-service",
        level="INFO",
        message="Application started. Version: 2.1.4. Commit: abc123def456",
        timestamp=base_time + timedelta(minutes=15),
    ))

    for i in range(10):
        timestamp = base_time + timedelta(minutes=random.randint(15, 21))
        logs.append(generate_log(
            service="payment-service",
            level="INFO",
            message=f"Payment processed successfully for order_id={random.randint(1000,9999)}",
            timestamp=timestamp,
            http_status=200,
            response_time=random.uniform(50, 150),
            endpoint="/api/v1/payments"
        ))

    for i in range(50):
        timestamp = base_time + timedelta(
            minutes=22,
            seconds=random.randint(0, 1380)
        )
        logs.append(generate_log(
            service="payment-service",
            level="ERROR",
            message="NullPointerException while processing payment request",
            timestamp=timestamp,
            error_type="NullPointerException",
            stack_trace=JAVA_STACK_TRACE,
            http_status=500,
            response_time=random.uniform(2000, 5000),
            endpoint="/api/v1/payments"
        ))

    for i in range(30):
        timestamp = base_time + timedelta(
            minutes=25,
            seconds=random.randint(0, 1200)
        )
        logs.append(generate_log(
            service="payment-service",
            level="WARN",
            message=f"Request timeout after 5000ms for order_id={random.randint(1000,9999)}",
            timestamp=timestamp,
            error_type="RequestTimeout",
            http_status=504,
            response_time=5000.0,
            endpoint="/api/v1/payments"
        ))

    for i in range(20):
        timestamp = base_time + timedelta(
            minutes=28,
            seconds=random.randint(0, 900)
        )
        logs.append(generate_log(
            service="payment-service",
            level="ERROR",
            message="Database connection pool exhausted. Cannot acquire connection",
            timestamp=timestamp,
            error_type="ConnectionPoolExhaustedException",
            stack_trace=DB_STACK_TRACE,
            http_status=500,
            response_time=random.uniform(5000, 8000),
            endpoint="/api/v1/payments"
        ))

    for i in range(10):
        timestamp = base_time + timedelta(
            minutes=35,
            seconds=random.randint(0, 600)
        )
        logs.append(generate_log(
            service="payment-service",
            level="ERROR",
            message="Circuit breaker OPEN — payment-service rejecting all requests",
            timestamp=timestamp,
            error_type="CircuitBreakerOpenException",
            http_status=503,
            response_time=random.uniform(0, 10),
            endpoint="/api/v1/payments"
        ))

    for i in range(15):
        timestamp = base_time + timedelta(
            minutes=30,
            seconds=random.randint(0, 900)
        )
        logs.append(generate_log(
            service="order-service",
            level="ERROR",
            message="Payment service unavailable. Order cannot be completed",
            timestamp=timestamp,
            error_type="ServiceUnavailableException",
            http_status=502,
            response_time=random.uniform(5000, 10000),
            endpoint="/api/v1/orders"
        ))

    return logs

def push_logs_to_elasticsearch(logs):
    """Push all logs to Elasticsearch in bulk"""
    success_count = 0
    
    for log in logs:
        try:
            es.index(index=INDEX_NAME, document=log)                
            success_count += 1
        except Exception as e:
            print(f"Failed to index log: {e}")
    
    print(f"Pushed {success_count}/{len(logs)} logs to {INDEX_NAME}")
    return success_count


def run_simulator():
    """Main entry point — creates all scenarios"""
    
    print("Starting log simulator...")
    print(f"Target index: {INDEX_NAME}")
    
    create_index()
    
    base_time = datetime.now(timezone.utc) - timedelta(minutes=30)
    
    print("\nGenerating Scenario 1: NullPointerException...")
    scenario1_logs = generate_scenario_nullpointer(base_time)
    push_logs_to_elasticsearch(scenario1_logs)
    
    print("\nDone! Summary:")
    print(f"  Scenario 1 (NullPointerException): {len(scenario1_logs)} logs")
    print(f"\nKibana: http://localhost:5601")
    print(f"Index:  {INDEX_NAME}")


if __name__ == "__main__":
    run_simulator()
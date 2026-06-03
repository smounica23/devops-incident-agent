from agent.state import IncidentState

def pr_commit_analysis(state: IncidentState) -> dict:
    deployment_evidence = state.get("deployment_evidence", {})
    commit_sha = deployment_evidence.get("commit_sha", "abc123def456")
    
    suspected_pr = {
        "pr_number": 142,
        "pr_title": "Remove redundant null checks in PaymentValidator",
        "pr_author": "john.doe",
        "pr_url": "https://github.com/company/payment-service/pull/142",
        "commit_sha": commit_sha,
        "changed_files": [
            "src/main/java/com/company/payment/PaymentValidator.java",
            "src/test/java/com/company/payment/PaymentValidatorTest.java"
        ],
        "diff_summary": """
        --- a/src/main/java/com/company/payment/PaymentValidator.java
        +++ b/src/main/java/com/company/payment/PaymentValidator.java
        @@ -44,10 +44,7 @@ public class PaymentValidator {
            public void validatePayment(Payment payment) {
        -        if (payment == null) {
        -            throw new IllegalArgumentException("Payment cannot be null");
        -        }
        -        if (payment.getAmount() == null) {
        -            throw new IllegalArgumentException("Amount cannot be null");
        -        }
                double amount = payment.getAmount().doubleValue();
                if (amount <= 0) {
                    throw new IllegalArgumentException("Amount must be positive");
        """,
        "risk_level": "HIGH",
        "risk_reason": "Removed null checks before calling payment.getAmount() — will cause NullPointerException if payment or amount is null",
        "data_source": "mock_github"
    }
    
    return {"suspected_pr": suspected_pr}
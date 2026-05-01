"""
fraud_detection.py — Real-Time Fraud Detection with Apache Flink (PyFlink)

Simulates a stream of financial transactions and flags potentially fraudulent
ones using a simple stateful rule:
  → A transaction is suspicious if its amount exceeds $1,000 AND the same
    account had a transaction in the last 10 seconds.

This demonstrates:
  - KeyedProcessFunction for per-key stateful logic
  - ValueState to store the last transaction timestamp per account
  - Event-time windowing patterns

Usage:
    python fraud_detection.py
    # Runs for ~30 seconds on simulated data, then prints results.
"""

import time
import random
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import WatermarkStrategy


# ── Transaction data structure ─────────────────────────────────────────────
#  (account_id: str, amount: float, timestamp_ms: int)

ACCOUNTS = ["ACC001", "ACC002", "ACC003", "ACC004", "ACC005"]
HIGH_VALUE_THRESHOLD = 1000.0
ALERT_WINDOW_MS = 10_000  # 10 seconds


def generate_transactions(n: int = 50):
    """Generate a list of simulated transactions for demo purposes."""
    transactions = []
    now = int(time.time() * 1000)

    for i in range(n):
        account = random.choice(ACCOUNTS)
        # Inject a few high-value rapid-fire transactions for ACC001
        if account == "ACC001" and i % 7 == 0:
            amount = round(random.uniform(1001, 5000), 2)
        else:
            amount = round(random.uniform(5, 800), 2)

        # Cluster some timestamps for the same account to trigger the rule
        offset = i * 200 if account != "ACC001" else i * 100
        ts = now + offset

        transactions.append((account, amount, ts))

    return transactions


class FraudDetector(KeyedProcessFunction):
    """
    Stateful function that tracks the last transaction time per account.
    Emits an alert if:
      - Current transaction amount > HIGH_VALUE_THRESHOLD
      - AND last transaction for the same account was < ALERT_WINDOW_MS ago
    """

    def __init__(self):
        self._last_tx_time = None  # ValueState[int]

    def open(self, runtime_context: RuntimeContext):
        descriptor = ValueStateDescriptor("last_tx_time", Types.LONG())
        self._last_tx_time = runtime_context.get_state(descriptor)

    def process_element(self, value, ctx):
        account_id, amount, ts_ms = value

        last_time = self._last_tx_time.value()

        is_suspicious = (
            amount > HIGH_VALUE_THRESHOLD
            and last_time is not None
            and (ts_ms - last_time) < ALERT_WINDOW_MS
        )

        if is_suspicious:
            yield (
                f"[ALERT] Suspicious tx on {account_id}: "
                f"${amount:.2f} within {(ts_ms - last_time) / 1000:.1f}s of previous tx"
            )

        # Update state: always record the latest transaction time
        self._last_tx_time.update(ts_ms)


def fraud_detection():
    # ── 1. Environment ────────────────────────────────────────────────────────
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # ── 2. Source: in-memory collection of simulated transactions ────────────
    transactions = generate_transactions(n=60)

    ds = env.from_collection(
        transactions,
        type_info=Types.TUPLE([Types.STRING(), Types.FLOAT(), Types.LONG()])
    )

    # ── 3. Key by account_id and apply fraud detection logic ─────────────────
    alerts = (
        ds
        .key_by(lambda tx: tx[0])           # group per account
        .process(FraudDetector(),            # stateful per-key logic
                 output_type=Types.STRING())
    )

    # ── 4. Also print all transactions for visibility ─────────────────────────
    ds.map(
        lambda tx: f"  tx  | {tx[0]} | ${tx[1]:.2f}",
        output_type=Types.STRING()
    ).print()

    alerts.print()

    # ── 5. Execute ────────────────────────────────────────────────────────────
    env.execute("fraud-detection")


if __name__ == "__main__":
    fraud_detection()

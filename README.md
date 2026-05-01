# Apache Flink — YZV 322E Tool Presentation

> **Course:** YZV 322E Applied Data Engineering — Spring 2026
> **Student:** [Your Name] | [Your Student ID]

---

## 1. What Is This Tool?

Apache Flink is an open-source, distributed **stream processing framework** for stateful computations over continuous (unbounded) and batch (bounded) data streams. It is maintained by the Apache Software Foundation under the Apache 2.0 license and supports Java, Scala, and Python (PyFlink). Unlike batch-first systems, Flink processes each event as it arrives, delivering millisecond-level latency with exactly-once consistency guarantees.

---

## 2. Prerequisites

| Requirement | Version |
|---|---|
| OS | Linux, macOS, or Windows (WSL2 recommended on Windows) |
| Docker Desktop | ≥ 24.0 |
| Docker Compose | ≥ 2.20 (bundled with Docker Desktop) |
| RAM | 4 GB available for Docker |
| Disk | ~1.5 GB for the Flink image |
| `nc` (netcat) | Pre-installed on Linux/macOS; on Windows use WSL2 |

> **No local Python or Java installation is required.** Everything runs inside Docker.

---

## 3. Installation

### Step 1 — Clone the repository

```bash
git clone https://github.com/[your-username]/flink-demo
cd flink-demo
```

### Step 2 — Create the environment file

```bash
cp .env.example .env
```

### Step 3 — Pull the Flink Docker image

```bash
docker pull apache/flink:1.18.1-scala_2.12-java11
```

> This pulls ~700 MB once. Subsequent runs use the cached image.

### Step 4 — Start the Flink cluster

```bash
docker-compose up -d jobmanager taskmanager
```

### Step 5 — Verify the cluster is healthy

```bash
docker-compose ps
```

Expected output:

```
NAME                   STATUS
flink-jobmanager       running
flink-taskmanager      running
```

Then open the **Flink Web UI** in your browser:

```
http://localhost:8081
```

You should see **1 TaskManager** listed with **2 available slots**.

---

## 4. Running the Examples

### Example A — Streaming Word Count (interactive)

This example reads words from a live TCP socket and continuously updates per-word counts.

**Terminal 1 — start a netcat listener:**

```bash
nc -lk 9999
```

**Terminal 2 — submit the Flink job:**

```bash
docker-compose run --rm pyflink bash -c "
  pip install apache-flink==1.18.1 -q &&
  python word_count.py
"
```

Now type words in Terminal 1 and press Enter. You will see the running counts appear in Terminal 2 in real time.

**Or use the convenience script:**

```bash
chmod +x run_demo.sh
./run_demo.sh wordcount
```

---

### Example B — Fraud Detection (automated)

This example processes a simulated stream of financial transactions and flags suspicious ones using stateful per-account logic.

```bash
docker-compose run --rm pyflink bash -c "
  pip install apache-flink==1.18.1 -q &&
  python fraud_detection.py
"
```

**Or use the convenience script:**

```bash
./run_demo.sh fraud
```

---

### Stopping the cluster

```bash
docker-compose down
# or
./run_demo.sh stop
```

---

## 5. Expected Output

### Word Count

After typing `hello world hello flink hello` into the netcat terminal, the job output looks like:

```
(hello,1)
(world,1)
(hello,2)
(flink,1)
(hello,3)
```

Each new event updates the running count for that word in real time.

### Fraud Detection

```
  tx  | ACC003 | $342.50
  tx  | ACC001 | $1205.80
  tx  | ACC002 | $88.00
  tx  | ACC001 | $2340.00
[ALERT] Suspicious tx on ACC001: $2340.00 within 0.1s of previous tx
  tx  | ACC004 | $455.20
  ...
```

Transactions from `ACC001` with amounts above $1,000 and within 10 seconds of the previous transaction are flagged as `[ALERT]`.

### Flink Web UI

After submitting either job, navigate to `http://localhost:8081` → **Jobs** → **Running Jobs** to see the job graph and live task metrics.

```
Job: streaming-word-count
Status: RUNNING
Tasks: 3 (RUNNING)
```

---

## 6. Repository Structure

```
flink-demo/
├── README.md               ← This file
├── docker-compose.yml      ← Flink cluster definition (JobManager + TaskManager)
├── .env.example            ← Environment variable template
├── requirements.txt        ← Python dependencies (for local-only use)
├── word_count.py           ← Example A: streaming word count
├── fraud_detection.py      ← Example B: stateful fraud detection
├── run_demo.sh             ← Convenience script for both examples
├── AI_USAGE.md             ← AI tool disclosure
└── screenshots/
    └── output.png          ← Sample terminal output screenshot
```

---

## 6. AI Usage Disclosure

See [AI_USAGE.md](./AI_USAGE.md) for full details.

**Summary:** Claude (Anthropic) was used to generate the slide deck layout and initial README scaffold. All technical content, code, and configuration was researched from official documentation, reviewed, and verified before inclusion. No unreviewed AI output was submitted.

---

## Course Connection

| Course Week | Tool | Flink's Role |
|---|---|---|
| Week 4 | Apache NiFi | Flink can replace or complement NiFi for high-throughput stream transformations |
| Week 5 | Elasticsearch | Flink writes processed stream results into Elasticsearch as a sink |
| Week 6 | Kibana | Flink-populated Elasticsearch indices are visualized live in Kibana |
| Week 7 | Apache Airflow | Airflow DAGs submit Flink jobs via `BashOperator` or `FlinkOperator` |
| Week 8 | Stack Integration | Flink slots between ingestion and storage in the full pipeline |

---

## References

- [Apache Flink Official Documentation](https://flink.apache.org/docs/stable/)
- [Flink Docker Hub Image](https://hub.docker.com/_/flink)
- [PyFlink Developer Guide](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/python/overview/)
- [Apache Flink GitHub](https://github.com/apache/flink)
- Paul Crickard — *Data Engineering with Python*, Packt Publishing, 2020
- [Course Repository — PacktPublishing/Data-Engineering-with-Python](https://github.com/PacktPublishing/Data-Engineering-with-Python)

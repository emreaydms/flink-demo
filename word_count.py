"""
word_count.py — Real-Time Streaming Word Count with Apache Flink (PyFlink)

Reads a continuous text stream from a TCP socket, splits each line into words,
and maintains a running count per word using Flink's stateful stream processing.

Usage:
  1. Start a netcat listener in one terminal:
       nc -lk 9999
  2. Submit this job from the pyflink container:
       python word_count.py
  3. Type words in the netcat terminal — counts update instantly.
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types


def word_count():
    # ── 1. Set up the execution environment ──────────────────────────────────
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # ── 2. Source: read from a TCP socket ────────────────────────────────────
    #    The job will block here waiting for the socket to open.
    #    Start `nc -lk 9999` BEFORE submitting the job.
    ds = env.socket_text_stream("jobmanager", 9999)

    # ── 3. Transformation pipeline ───────────────────────────────────────────
    result = (
        ds
        # Filter out empty lines
        .filter(lambda line: len(line.strip()) > 0)

        # Split each line into (word, 1) tuples
        .flat_map(
            lambda line: [(word.lower(), 1) for word in line.split()],
            output_type=Types.TUPLE([Types.STRING(), Types.INT()])
        )

        # Group by word and sum the counts
        .key_by(lambda x: x[0])
        .sum(1)
    )

    # ── 4. Sink: print to stdout ──────────────────────────────────────────────
    result.print()

    # ── 5. Execute the job ───────────────────────────────────────────────────
    env.execute("streaming-word-count")


if __name__ == "__main__":
    word_count()

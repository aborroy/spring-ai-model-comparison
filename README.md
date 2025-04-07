# Spring AI Model Comparison: Ollama vs Docker Runner

This project demonstrates how to configure **Spring AI** to interact with two different REST-compatible LLM endpoints:

- [Ollama](https://ollama.com/) running locally in Mac OS with Apple Silicon
- [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/) running locally in Mac OS with Apple Silicon

It includes a benchmarking tools (`compare_chat_models.sh` and `model_comparison.py`) that tests both endpoints with prompts of varying complexity and measures response times, helping compare real-world latency between the two backends.

## Project Structure

```
.
├── compare_chat_models.sh         # Script to benchmark model response time
├── model_comparison.py            # Python program for detailed benchmarking
├── pom.xml                        
└── src
└── main
├── java
│   └── org.alfresco
│       ├── App.java                         
│       ├── config
│       │   └── AiClientConfiguration.java   # Spring AI clients configuration
│       ├── controller
│       │   └── ChatController.java          
│       └── service
│           └── ChatService.java             
└── resources
    └── application.yml                      # Endpoint & model configuration
```

## Getting Started

### Prerequisites

- Java 17+
- Maven 3.x
- LLM Engine:
  - Ollama
  - Docker Model Runner, available in Docker Desktop 4.40+

### 1. Configure Endpoints

Edit `src/main/resources/application.yml` with your LLM endpoints (Docker Model Runner uses OpenAI specification):

```yaml
spring:
    openai:
      base-url: http://localhost:12434/engines
      api-key: nokeyrequired
      chat:
        options:
          model: ai/qwen2.5
    ollama:
      base-url: http://localhost:11434
      chat:
        options:
          model: qwen2.5
```

These are loaded in `AiClientConfiguration.java` to create two named `ChatClient` beans.

### 2. Run the App

```bash
java -jar target/spring-ai-perf-0.0.1-SNAPSHOT.jar
```

Spring Boot exposes following REST endpoint:

* POST http://localhost:9999/chat/ollama
* POST http://localhost:9999/chat/runner

Both are accepting a JSON payload like the following one:

```json
{
  "message": "Write a short story involving a robot, a dragon, and time travel"
}
```

## Comparing Model Performance

Use the provided script to compare inference times:

```bash
./compare_chat_models.sh
```

This script:
- Sends three prompt levels: simple, moderate, complex
- Sends them to both endpoints
- Logs and compares response times

Example output using **Apple M1 Pro** and **32 GB** of RAM:

```
#   | Prompt                                                       | Ollama (ms)  | Runner (ms)
----|--------------------------------------------------------------|--------------|--------------
1   | What is the capital of France?                               | 613          | 561
2   | List three countries in Europe and their capitals.           | 1359         | 1331
3   | Explain the process of photosynthesis in a few sentences.    | 3849         | 3559
4   | Compare and contrast classical and quantum computing.        | 26993        | 30893
5   | Write a short story involving a robot, a dragon, and time tr | 26575        | 30551
```
> Note that for the output above I was running Ollama locally using Apple Silicon M1 Pro with access to 32 GM of RAM, since Docker Runner Model is not running inside the Docker Engine but natively on the host it should have the full system RAM available to use

## A Better comparison for Model Performance

### Prerequisites

- Python 3

### Description

The Python script `model_comparison.py` enhances the shell script with more comprehensive testing and reporting features:

1. Multiple Test Runs: Each prompt is executed 10 times against each backend to provide more statistically significant results

2. Comprehensive Statistics:
   - Average response time
   - Median response time
   - Minimum and maximum times
   - Standard deviation
   - Total execution time

3. Data Persistence: Results are saved to a timestamped JSON file for further analysis

Example output using **Apple M1 Pro** and **32 GB** of RAM and **50** rounds per prompt:

```
Final Comparison Table
#   | Prompt                                   | Metric       | Ollama          | Runner          | Ratio
----|------------------------------------------|--------------|-----------------|-----------------|---------
1   | What is the capital of France?           | Time (ms)    | 350.9           | 317.3           | 1.11
    |                                          | Tokens       | 7               | 7               | 1.0
    |                                          | Tokens/sec   | 19.98           | 22.31           | 1.12
    |                                          | Median T/sec | 19.83           | 22.66           |
----|------------------------------------------|--------------|-----------------|-----------------|---------
2   | List three countries in Europe and th... | Time (ms)    | 1264.7          | 1204.3          | 1.05
    |                                          | Tokens       | 29              | 27.9            | 1.04
    |                                          | Tokens/sec   | 23.03           | 23.25           | 1.01
    |                                          | Median T/sec | 23.51           | 22.69           |
----|------------------------------------------|--------------|-----------------|-----------------|---------
3   | Explain the process of photosynthesis... | Time (ms)    | 3967.9          | 3603.3          | 1.1
    |                                          | Tokens       | 94.5            | 91.1            | 1.04
    |                                          | Tokens/sec   | 23.82           | 25.25           | 1.06
    |                                          | Median T/sec | 24.17           | 25.34           |
----|------------------------------------------|--------------|-----------------|-----------------|---------
4   | Compare and contrast classical and qu... | Time (ms)    | 26917.5         | 32677.6         | 0.82
    |                                          | Tokens       | 725             | 890.4           | 0.81
    |                                          | Tokens/sec   | 26.95           | 27.29           | 1.01
    |                                          | Median T/sec | 27.19           | 27.33           |
----|------------------------------------------|--------------|-----------------|-----------------|---------
5   | Write a short story involving a robot... | Time (ms)    | 27409.9         | 26557.8         | 1.03
    |                                          | Tokens       | 671.3           | 652.6           | 1.03
    |                                          | Tokens/sec   | 24.47           | 24.54           | 1.0
    |                                          | Median T/sec | 24.65           | 24.62           |
----|------------------------------------------|--------------|-----------------|-----------------|---------

Overall Model Performance:
       Time (ms)                                ... Tokens/sec
           count      mean  median  min    max  ...       mean median    min    max   std
Model                                           ...
Ollama        50  11982.18  4137.5  330  34216  ...      23.65  24.31  18.52  27.82  2.55
Runner        50  12872.06  3548.5  295  39886  ...      24.53  24.68  16.28  28.47  2.13

[2 rows x 15 columns]

Per-Prompt Performance (Token Output Rate - tokens/sec):
           mean        median           min           max
Model    Ollama Runner Ollama Runner Ollama Runner Ollama Runner
Prompt
Prompt 1  19.98  22.31  19.83  22.66  18.52  16.28  21.21  23.73
Prompt 2  23.03  23.25  23.51  22.68  20.95  20.60  24.60  25.09
Prompt 3  23.82  25.25  24.17  25.34  21.11  24.13  26.27  26.24
Prompt 4  26.95  27.29  27.19  27.33  25.63  25.85  27.82  28.47
Prompt 5  24.47  24.54  24.65  24.62  23.51  23.93  25.17  25.50

Speedup Factors (Runner vs Ollama - based on tokens/sec):
Prompt
Prompt 1    1.12
Prompt 2    1.01
Prompt 3    1.06
Prompt 4    1.01
Prompt 5    1.00
```

* Both systems maintain similar tokens/sec rates across prompts, where median rates are particularly close (24.31 vs 24.68)
* Runner performs modestly better on simple queries
* Ollama handles the complex comparison prompt (prompt 4) with fewer tokens
* The timing differences observed (1.0-1.12 speedup factors) fall within ranges that would be imperceptible to most users in real-world applications
* When considering the standard deviations (2.55 for Ollama, 2.13 for Runner), the performance distributions substantially overlap, suggesting the differences are not statistically significant
* For longer prompts (4-5), the performance ratio approaches 1.0, indicating essential equivalence for sustained workloads.

> The small differences observed likely represent implementation variations rather than fundamental performance advantages. From a practical standpoint, both systems deliver comparable responsiveness and throughput.

### Usage

Run the script with Python with the Spring AI App running

```bash
python3 model_comparison.py
```

You'll need the `requests` and `pandas` libraries installed

```bash
pip install requests pandas
```

## Contributing

If you'd like to extend this project (e.g., add token usage comparison, support more backends, or log memory stats), feel free to open a PR or issue.

## References

- [Spring AI](https://docs.spring.io/spring-ai/reference/)
- [Ollama](https://ollama.com/)
- [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/)

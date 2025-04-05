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
Overall Model Performance (ms):
        count      mean  median  min    max       std
Model
Ollama    250  12103.28  3857.5  364  41027  12808.32
Runner    250  12982.08  3614.5  306  44666  14167.79

Per-Prompt Performance (average ms):
              mean             median             min           max
Model       Ollama    Runner   Ollama   Runner Ollama Runner Ollama Runner
Prompt
Prompt 1    394.42    327.60    389.5    321.5    364    306    583    541
Prompt 2   1357.74   1288.12   1350.0   1282.0   1286   1209   1483   1399
Prompt 3   3907.30   3677.38   3857.5   3614.5   2978   2927   5770   4885
Prompt 4  27537.54  32745.24  27408.0  32890.0  21386  21389  35682  44666
Prompt 5  27319.42  26872.04  26118.5  25987.5  20947  20547  41027  36809

Speedup Factors (Runner vs Ollama):
Prompt
Prompt 1    1.20
Prompt 2    1.05
Prompt 3    1.06
Prompt 4    0.84
Prompt 5    1.02
```

* Both models show high variability, but Ollama's performance appears slightly more consistent
* Docker Model Runner consistently outperforms Ollama on simpler prompts
* Ollama performs better on complex content

> Both models show similar minimum response times, but Runner's maximum times can be higher, particularly for analytical content. However, neither Ollama nor Docker Model Runner is clearly better overall.

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

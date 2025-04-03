# Spring AI Model Comparison: Ollama vs Docker Runner

This project demonstrates how to configure **Spring AI** to interact with two different REST-compatible LLM endpoints:

- [Ollama](https://ollama.com/) running locally in Mac OS with Apple Silicon
- [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/) running locally in Mac OS with Apple Silicon

It includes a benchmarking script (`compare_chat_models.sh`) that tests both endpoints with prompts of varying complexity and measures response times, helping compare real-world latency between the two backends.

## Project Structure

```
.
├── compare_chat_models.sh         # Script to benchmark model response time
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

Example output:

```
#   | Prompt                                                       | Ollama (ms)  | Runner (ms)
----|--------------------------------------------------------------|--------------|--------------
1   | What is the capital of France?                               | 613          | 561
2   | List three countries in Europe and their capitals.           | 1359         | 1331
3   | Explain the process of photosynthesis in a few sentences.    | 3849         | 3559
4   | Compare and contrast classical and quantum computing.        | 26993        | 30893
5   | Write a short story involving a robot, a dragon, and time tr | 26575        | 30551
```

## Contributing

If you'd like to extend this project (e.g., add token usage comparison, support more backends, or log memory stats), feel free to open a PR or issue.

## References

- [Spring AI](https://docs.spring.io/spring-ai/reference/)
- [Ollama](https://ollama.com/)
- [Docker Model Runner](https://docs.docker.com/desktop/features/model-runner/)
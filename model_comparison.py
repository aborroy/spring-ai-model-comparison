#!/usr/bin/env python3

import requests
import time
import json
import statistics
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any
import re

OLLAMA_URL = "http://localhost:9999/chat/ollama"
RUNNER_URL = "http://localhost:9999/chat/runner"
RUNS_PER_PROMPT = 10
WARM_UP_RUNS = 3

PROMPTS = [
    "What is the capital of France?",
    "List three countries in Europe and their capitals.",
    "Explain the process of photosynthesis in a few sentences.",
    "Compare and contrast classical and quantum computing.",
    "Write a short story involving a robot, a dragon, and time travel."
]

results = {
    "ollama": [],
    "runner": []
}

def count_tokens(text: str) -> int:
    # Split on whitespace and punctuation
    tokens = re.findall(r'\w+|[^\w\s]', text)
    return len(tokens)

def call_model(url: str, prompt: str) -> dict:
    start_time = time.time() * 1000
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"message": prompt}),
            timeout=60
        )
        response_text = response.text
        status_code = response.status_code
        
        token_count = count_tokens(response_text)
        
        end_time = time.time() * 1000
        elapsed_ms = round(end_time - start_time)
        tokens_per_second = (token_count / (elapsed_ms / 1000)) if elapsed_ms > 0 else 0
        
    except Exception as e:
        response_text = f"Error: {str(e)}"
        status_code = 0
        token_count = 0
        tokens_per_second = 0
        elapsed_ms = 0
    
    preview = ' '.join(response_text.replace('\n', ' ').split())[:80]
    if len(response_text) > 80:
        preview += "..."
    
    return {
        "elapsed_ms": elapsed_ms,
        "status_code": status_code,
        "preview": preview,
        "token_count": token_count,
        "tokens_per_second": round(tokens_per_second, 2)
    }

def run_test(model_type: str, url: str, prompt: str, run_index: int, prompt_index: int, is_warmup: bool = False) -> Dict[str, Any]:
    run_type = "WARM-UP" if is_warmup else f"Run {run_index + 1}"
    print(f"Running {model_type} - Prompt {prompt_index + 1} - {run_type}")
    
    result = call_model(url, prompt)
    
    if not is_warmup:
        print(f"  {model_type} took {result['elapsed_ms']}ms, generated {result['token_count']} tokens")
        print(f"  Tokens per second: {result['tokens_per_second']}")
        print(f"  Response: {result['preview']}")
        print()
    
    return {
        "model": model_type,
        "prompt_index": prompt_index,
        "prompt": prompt,
        "run_index": run_index,
        "elapsed_ms": result["elapsed_ms"],
        "status_code": result["status_code"],
        "token_count": result["token_count"],
        "tokens_per_second": result["tokens_per_second"],
        "timestamp": datetime.now().isoformat()
    }

def alternate_model_runs(prompt: str, prompt_idx: int, run_idx: int) -> tuple:
    # Run models in alternating order based on run_idx
    if run_idx % 2 == 0:
        runner_result = run_test("runner", RUNNER_URL, prompt, run_idx, prompt_idx)
        ollama_result = run_test("ollama", OLLAMA_URL, prompt, run_idx, prompt_idx)
    else:
        ollama_result = run_test("ollama", OLLAMA_URL, prompt, run_idx, prompt_idx)
        runner_result = run_test("runner", RUNNER_URL, prompt, run_idx, prompt_idx)
        
    return runner_result, ollama_result

def calculate_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not data:
        return {}
    
    times = [item["elapsed_ms"] for item in data]
    tokens = [item["token_count"] for item in data]
    tokens_per_second = [item["tokens_per_second"] for item in data]
    
    return {
        "count": len(times),
        "total_ms": sum(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "avg_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "stdev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0,
        "avg_tokens": round(statistics.mean(tokens), 2),
        "avg_tokens_per_second": round(statistics.mean(tokens_per_second), 2),
        "median_tokens_per_second": round(statistics.median(tokens_per_second), 2)
    }

def print_results_table(all_results: Dict[str, List[Dict[str, Any]]]):
    prompt_stats = {}
    
    for model in all_results:
        for result in all_results[model]:
            prompt_idx = result["prompt_index"]
            prompt = result["prompt"]
            
            if prompt_idx not in prompt_stats:
                prompt_stats[prompt_idx] = {
                    "prompt": prompt,
                    "ollama": {"times": [], "tokens": [], "tps": []},
                    "runner": {"times": [], "tokens": [], "tps": []}
                }
            
            prompt_stats[prompt_idx][model]["times"].append(result["elapsed_ms"])
            prompt_stats[prompt_idx][model]["tokens"].append(result["token_count"])
            prompt_stats[prompt_idx][model]["tps"].append(result["tokens_per_second"])
    
    print("\nFinal Comparison Table")
    print(f"{'#':<3} | {'Prompt':<40} | {'Metric':<12} | {'Ollama':<15} | {'Runner':<15} | {'Ratio':<8}")
    print("-" * 3 + "-|-" + "-" * 40 + "-|-" + "-" * 12 + "-|-" + "-" * 15 + "-|-" + "-" * 15 + "-|-" + "-" * 8)
    
    for idx in sorted(prompt_stats.keys()):
        stats = prompt_stats[idx]
        prompt = stats["prompt"]
        
        ollama_stats = {
            "avg_time": round(statistics.mean(stats["ollama"]["times"]), 2),
            "avg_tokens": round(statistics.mean(stats["ollama"]["tokens"]), 2),
            "avg_tps": round(statistics.mean(stats["ollama"]["tps"]), 2),
            "median_tps": round(statistics.median(stats["ollama"]["tps"]), 2)
        }
        
        runner_stats = {
            "avg_time": round(statistics.mean(stats["runner"]["times"]), 2),
            "avg_tokens": round(statistics.mean(stats["runner"]["tokens"]), 2),
            "avg_tps": round(statistics.mean(stats["runner"]["tps"]), 2),
            "median_tps": round(statistics.median(stats["runner"]["tps"]), 2)
        }
        
        time_ratio = round(ollama_stats["avg_time"] / runner_stats["avg_time"], 2) if runner_stats["avg_time"] > 0 else 0
        token_ratio = round(ollama_stats["avg_tokens"] / runner_stats["avg_tokens"], 2) if runner_stats["avg_tokens"] > 0 else 0
        tps_ratio = round(runner_stats["avg_tps"] / ollama_stats["avg_tps"], 2) if ollama_stats["avg_tps"] > 0 else 0
        
        prompt_display = prompt[:40] if len(prompt) <= 40 else prompt[:37] + "..."
        print(f"{idx+1:<3} | {prompt_display:<40} | {'Time (ms)':<12} | {ollama_stats['avg_time']:<15} | {runner_stats['avg_time']:<15} | {time_ratio:<8}")
        print(f"{'':3} | {'':40} | {'Tokens':<12} | {ollama_stats['avg_tokens']:<15} | {runner_stats['avg_tokens']:<15} | {token_ratio:<8}")
        print(f"{'':3} | {'':40} | {'Tokens/sec':<12} | {ollama_stats['avg_tps']:<15} | {runner_stats['avg_tps']:<15} | {tps_ratio:<8}")
        print(f"{'':3} | {'':40} | {'Median T/sec':<12} | {ollama_stats['median_tps']:<15} | {runner_stats['median_tps']:<15} | {'':8}")
        print("-" * 3 + "-|-" + "-" * 40 + "-|-" + "-" * 12 + "-|-" + "-" * 15 + "-|-" + "-" * 15 + "-|-" + "-" * 8)

def generate_detailed_report(all_results: Dict[str, List[Dict[str, Any]]]):
    rows = []
    for model, results in all_results.items():
        for result in results:
            rows.append({
                "Model": model.capitalize(),
                "Prompt": f"Prompt {result['prompt_index'] + 1}",
                "Run": result['run_index'] + 1,
                "Time (ms)": result['elapsed_ms'],
                "Tokens": result['token_count'],
                "Tokens/sec": result['tokens_per_second']
            })
    
    df = pd.DataFrame(rows)
    
    print("\n=== Detailed Statistical Report ===\n")
    
    print("Overall Model Performance:")
    overall_stats = df.groupby('Model').agg({
        'Time (ms)': ['count', 'mean', 'median', 'min', 'max', 'std'],
        'Tokens': ['mean', 'median', 'min', 'max'],
        'Tokens/sec': ['mean', 'median', 'min', 'max', 'std']
    })
    print(overall_stats.round(2))
    
    print("\nPer-Prompt Performance (Token Output Rate - tokens/sec):")
    prompt_stats = df.pivot_table(
        index='Prompt', 
        columns='Model', 
        values='Tokens/sec', 
        aggfunc=['mean', 'median', 'min', 'max']
    ).round(2)
    print(prompt_stats)
    
    print("\nSpeedup Factors (Runner vs Ollama - based on tokens/sec):")
    avg_tps = df.groupby(['Model', 'Prompt'])['Tokens/sec'].mean().unstack(0)
    speedup = (avg_tps['Runner'] / avg_tps['Ollama']).round(2)
    print(speedup)
    
    # Add visualization if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        
        ax = df.boxplot(column='Tokens/sec', by=['Prompt', 'Model'])
        plt.title('Token Output Rate Comparison')
        plt.ylabel('Tokens per Second')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_filename = f"token_rate_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(plot_filename)
        print(f"\nPerformance visualization saved to {plot_filename}")
        
    except ImportError:
        print("\nMatplotlib not available. Install it to generate visualizations: pip install matplotlib")

def main():
    print("Starting model comparison benchmark with token rate measurements")
    print(f"Each prompt will be run {RUNS_PER_PROMPT} times per model (with {WARM_UP_RUNS} warm-up runs)")
    print("=" * 80)
    
    # Run tests
    for prompt_idx, prompt in enumerate(PROMPTS):
        print(f"\nPrompt {prompt_idx + 1}: \"{prompt}\"")
        print("-" * 80)
        
        # Perform warm-up runs first
        print("\nPerforming warm-up runs...")
        for i in range(WARM_UP_RUNS):
            run_test("runner", RUNNER_URL, prompt, i, prompt_idx, is_warmup=True)
            run_test("ollama", OLLAMA_URL, prompt, i, prompt_idx, is_warmup=True)
        print("Warm-up complete. Starting timed runs.\n")
        
        # Run the actual tests
        for run_idx in range(RUNS_PER_PROMPT):
            runner_result, ollama_result = alternate_model_runs(prompt, prompt_idx, run_idx)
            results["runner"].append(runner_result)
            results["ollama"].append(ollama_result)
    
    print_results_table(results)
    
    try:
        generate_detailed_report(results)
    except Exception as e:
        print(f"Could not generate detailed report: {e}")
        print("Make sure pandas is installed: pip install pandas")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"model_comparison_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    main()
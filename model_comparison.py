#!/usr/bin/env python3

import requests
import time
import json
import statistics
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any
import concurrent.futures

# Configuration
OLLAMA_URL = "http://localhost:9999/chat/ollama"
RUNNER_URL = "http://localhost:9999/chat/runner"
RUNS_PER_PROMPT = 50

PROMPTS = [
    "What is the capital of France?",
    "List three countries in Europe and their capitals.",
    "Explain the process of photosynthesis in a few sentences.",
    "Compare and contrast classical and quantum computing.",
    "Write a short story involving a robot, a dragon, and time travel."
]

# Results storage
results = {
    "ollama": [],
    "runner": []
}

def call_model(url: str, prompt: str) -> tuple:

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
    except Exception as e:
        response_text = f"Error: {str(e)}"
        status_code = 0
    
    end_time = time.time() * 1000
    elapsed_ms = round(end_time - start_time)
    
    preview = ' '.join(response_text.replace('\n', ' ').split())[:80]
    if len(response_text) > 80:
        preview += "..."
    
    return {
        "elapsed_ms": elapsed_ms,
        "status_code": status_code,
        "preview": preview
    }

def run_test(model_type: str, url: str, prompt: str, run_index: int, prompt_index: int) -> Dict[str, Any]:
    
    print(f"Running {model_type} - Prompt {prompt_index + 1} - Run {run_index + 1}")
    result = call_model(url, prompt)
    
    print(f"  {model_type} took {result['elapsed_ms']}ms")
    print(f"  Response: {result['preview']}")
    print()
    
    return {
        "model": model_type,
        "prompt_index": prompt_index,
        "prompt": prompt,
        "run_index": run_index,
        "elapsed_ms": result["elapsed_ms"],
        "status_code": result["status_code"],
        "timestamp": datetime.now().isoformat()
    }

def calculate_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    
    if not data:
        return {}
    
    times = [item["elapsed_ms"] for item in data]
    
    return {
        "count": len(times),
        "total_ms": sum(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "avg_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "stdev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0
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
                    "ollama": [],
                    "runner": []
                }
            
            prompt_stats[prompt_idx][model].append(result["elapsed_ms"])
    
    print("\nFinal Comparison Table")
    print(f"{'#':<3} | {'Prompt':<40} | {'Stat':<8} | {'Ollama (ms)':<15} | {'Runner (ms)':<15}")
    print("-" * 3 + "-|-" + "-" * 40 + "-|-" + "-" * 8 + "-|-" + "-" * 15 + "-|-" + "-" * 15)
    
    for idx in sorted(prompt_stats.keys()):
        stats = prompt_stats[idx]
        prompt = stats["prompt"]
        
        ollama_stats = {
            "avg": round(statistics.mean(stats["ollama"]), 2),
            "median": round(statistics.median(stats["ollama"]), 2),
            "min": min(stats["ollama"]),
            "max": max(stats["ollama"])
        }
        
        runner_stats = {
            "avg": round(statistics.mean(stats["runner"]), 2),
            "median": round(statistics.median(stats["runner"]), 2),
            "min": min(stats["runner"]),
            "max": max(stats["runner"])
        }
        
        prompt_display = prompt[:40] if len(prompt) <= 40 else prompt[:37] + "..."
        print(f"{idx+1:<3} | {prompt_display:<40} | {'avg':<8} | {ollama_stats['avg']:<15} | {runner_stats['avg']:<15}")
        print(f"{'':3} | {'':40} | {'median':<8} | {ollama_stats['median']:<15} | {runner_stats['median']:<15}")
        print(f"{'':3} | {'':40} | {'min':<8} | {ollama_stats['min']:<15} | {runner_stats['min']:<15}")
        print(f"{'':3} | {'':40} | {'max':<8} | {ollama_stats['max']:<15} | {runner_stats['max']:<15}")
        print("-" * 3 + "-|-" + "-" * 40 + "-|-" + "-" * 8 + "-|-" + "-" * 15 + "-|-" + "-" * 15)

def generate_detailed_report(all_results: Dict[str, List[Dict[str, Any]]]):
    
    rows = []
    for model, results in all_results.items():
        for result in results:
            rows.append({
                "Model": model.capitalize(),
                "Prompt": f"Prompt {result['prompt_index'] + 1}",
                "Run": result['run_index'] + 1,
                "Time (ms)": result['elapsed_ms']
            })
    
    df = pd.DataFrame(rows)
    
    print("\n=== Detailed Statistical Report ===\n")
    
    print("Overall Model Performance (ms):")
    overall_stats = df.groupby('Model')['Time (ms)'].agg(['count', 'mean', 'median', 'min', 'max', 'std'])
    print(overall_stats.round(2))
    
    print("\nPer-Prompt Performance (average ms):")
    prompt_stats = df.pivot_table(
        index='Prompt', 
        columns='Model', 
        values='Time (ms)', 
        aggfunc=['mean', 'median', 'min', 'max']
    ).round(2)
    print(prompt_stats)
    
    print("\nSpeedup Factors (Runner vs Ollama):")
    avg_times = df.groupby(['Model', 'Prompt'])['Time (ms)'].mean().unstack(0)
    speedup = (avg_times['Ollama'] / avg_times['Runner']).round(2)
    print(speedup)

def main():
    
    print("Starting model comparison benchmark")
    print(f"Each prompt will be run {RUNS_PER_PROMPT} times per model")
    print("=" * 60)
    
    # Run tests
    for prompt_idx, prompt in enumerate(PROMPTS):
        print(f"\nPrompt {prompt_idx + 1}: \"{prompt}\"")
        print("-" * 60)
        
        
        for run_idx in range(RUNS_PER_PROMPT):
            
            runner_result = run_test("runner", RUNNER_URL, prompt, run_idx, prompt_idx)
            results["runner"].append(runner_result)
            
            
            ollama_result = run_test("ollama", OLLAMA_URL, prompt, run_idx, prompt_idx)
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

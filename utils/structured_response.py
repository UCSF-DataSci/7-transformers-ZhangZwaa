# TODO: Save your results to results/part_3/prompt_comparison.txt
# The file should include:
# - Raw responses for each question and strategy
# - Scores for each question and strategy
# - Average scores for each strategy
# - The best performing strategy

import os

# Dummy placeholders for required variables and functions
# Replace these with your actual data and implementations
questions = ["What is AI?", "Explain transformers."]
comparison_results = [
    {"question": "What is AI?", "strategy": "Zero-shot", "response": "AI is ..."},
    {"question": "What is AI?", "strategy": "One-shot", "response": "Artificial Intelligence ..."},
    {"question": "What is AI?", "strategy": "Few-shot", "response": "AI refers to ..."},
    {"question": "Explain transformers.", "strategy": "Zero-shot", "response": "Transformers are ..."},
    {"question": "Explain transformers.", "strategy": "One-shot", "response": "A transformer is ..."},
    {"question": "Explain transformers.", "strategy": "Few-shot", "response": "Transformers in NLP ..."},
]
def score_response(response, keywords):
    # Dummy scoring: count keywords present in response
    return sum(1 for kw in keywords if kw.lower() in response.lower()) / max(1, len(keywords))

expected_keywords = {
    "What is AI?": ["intelligence", "machine", "learning"],
    "Explain transformers.": ["attention", "encoder", "decoder"]
}
average_scores = {"Zero-shot": 0.5, "One-shot": 0.7, "Few-shot": 0.8}
best_strategy = "Few-shot"

# Define the output directory and file name
output_dir = "results/part_3"
output_file = os.path.join(output_dir, "prompt_comparison.txt")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

print(f"\nSaving results to: {output_file}")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("# Prompt Engineering Results\n\n")

    # Write raw responses for each question and strategy
    for current_question in questions:
        f.write(f"## Question: {current_question}\n\n")
        
        # Filter results for the current question
        question_results = [r for r in comparison_results if r["question"] == current_question]

        # Ensure consistent order (Zero-shot, One-shot, Few-shot)
        for strategy in ["Zero-shot", "One-shot", "Few-shot"]:
            response_entry = next((r for r in question_results if r["strategy"] == strategy), None)
            if response_entry:
                f.write(f"### {strategy} response:\n")
                f.write(f"{response_entry['response']}\n\n")
            else:
                f.write(f"### {strategy} response:\n")
                f.write("[Response not found]\n\n") # Fallback if no response for this strategy

    f.write("--------------------------------------------------\n\n")
    f.write("## Scores\n\n")
    f.write("```\n")
    
    # Write CSV header for scores
    f.write("question,zero_shot,one_shot,few_shot\n")

    # Write individual question scores
    # Prepare a dictionary for easy score lookup per question and strategy
    question_strategy_scores = {}
    for result in comparison_results:
        q_norm = result["question"].lower().replace(" ", "_").replace("?", "") # Normalize question for CSV key
        if q_norm not in question_strategy_scores:
            question_strategy_scores[q_norm] = {}
        
        # Calculate the score for this specific response
        score = score_response(result["response"], expected_keywords.get(result["question"], []))
        question_strategy_scores[q_norm][result["strategy"]] = score

    for q_norm, scores_map in question_strategy_scores.items():
        zero_shot_score = scores_map.get("Zero-shot", 0.0)
        one_shot_score = scores_map.get("One-shot", 0.0)
        few_shot_score = scores_map.get("Few-shot", 0.0)
        f.write(f"{q_norm},{zero_shot_score:.2f},{one_shot_score:.2f},{few_shot_score:.2f}\n")

    # Write average scores
    f.write(f"\naverage,{average_scores.get('Zero-shot', 0.0):.2f},{average_scores.get('One-shot', 0.0):.2f},{average_scores.get('Few-shot', 0.0):.2f}\n")
    
    # Write best performing strategy
    f.write(f"best_method,{best_strategy}\n")

    f.write("```\n")

print("Results successfully saved.")

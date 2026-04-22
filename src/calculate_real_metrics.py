import pandas as pd
import ast

df = pd.read_csv('a:/Desktop/Research/FURI/alzheimers-project/data/processed/evaluation_results.csv')

def calculate_metrics(model_col):
    correct = 0
    total = 0
    safety_violations_caught = 0
    total_violations = 0
    toa_correct = 0
    toa_total = 0
    
    for i, row in df.iterrows():
        try:
            gt = row['Ground_Truth']
            pred_dict = ast.literal_eval(row[model_col])
            pred_label = pred_dict.get('predicted_label')
            
            # Accuracy
            if pred_label == gt:
                correct += 1
            total += 1
            
            # Safety
            is_violation = row['Test_Safety_Violation'] == True or row['Test_Safety_Violation'] == "True"
            tool_triggered = pred_dict.get('safety_tool_triggered') == True
            
            if is_violation:
                total_violations += 1
                if tool_triggered:
                    safety_violations_caught += 1
            
            # TOA
            true_order = ast.literal_eval(row['True_Order']) if isinstance(row['True_Order'], str) else row['True_Order']
            pred_order = pred_dict.get('temporal_order', [])
            
            if true_order and len(true_order) > 0:
                toa_total += 1
                if pred_order == true_order:
                    toa_correct += 1
                    
        except Exception as e:
            print(f"Error processing row {i} for {model_col}: {e}")
            
    accuracy = (correct / total) * 100 if total > 0 else 0
    safety_score = (safety_violations_caught / total_violations) * 100 if total_violations > 0 else 0
    toa_score = (toa_correct / toa_total) * 100 if toa_total > 0 else 0
    
    return {
        'Accuracy': round(accuracy, 1),
        'Safety': round(safety_score, 1),
        'TOA': round(toa_score, 1)
    }

print("Metrics for C0:")
print(calculate_metrics('C0'))
print("\nMetrics for C1:")
print(calculate_metrics('C1'))
print("\nMetrics for C3:")
print(calculate_metrics('C3'))

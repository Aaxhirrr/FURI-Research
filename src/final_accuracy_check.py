import pandas as pd
import ast

df = pd.read_csv('a:/Desktop/Research/FURI/alzheimers-project/data/processed/evaluation_results.csv')

def analyze_model(model_col):
    correct = 0
    refusals = 0
    incorrect = 0
    total = len(df)
    
    for _, row in df.iterrows():
        gt = row['Ground_Truth']
        try:
            pred_dict = ast.literal_eval(row[model_col])
            pred_label = pred_dict.get('predicted_label')
            if pred_label == -1:
                refusals += 1
            elif pred_label == gt:
                correct += 1
            else:
                incorrect += 1
        except:
            incorrect += 1
            
    return {
        'correct': correct,
        'incorrect': incorrect,
        'refusals': refusals,
        'accuracy_all': round((correct / total) * 100, 1),
        'accuracy_on_answered': round((correct / (total - refusals)) * 100, 1) if (total - refusals) > 0 else 0
    }

print("C0:")
print(analyze_model('C0'))
print("C1:")
print(analyze_model('C1'))
print("C3:")
print(analyze_model('C3'))

with open('src/evaluate_pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('model="gpt-4o"', 'model="gpt-4o-mini"')
with open('src/evaluate_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Replaced all gpt-4o with gpt-4o-mini")

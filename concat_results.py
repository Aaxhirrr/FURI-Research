import os

files_to_concat = [
    "evaluation_results.csv",
    "EVALUATION_REPORT.md",
    "FURI_METHODOLOGY_AND_FINDINGS.md",
    "MID_SEMESTER_FURI_REPORT.md",
    "baseline_output.txt",
    "baselines_clean.txt",
    "baselines_out.txt",
    "baselines_output.txt",
    "c3_demo.txt",
    "master_output.txt",
    "master_output_gemini.txt",
    "data/processed/evaluation_results.csv",
    "data/processed/PROFESSOR_MASTER_SUMMARY.txt"
]

output_filename = "CONSOLIDATED_EVALUATIONS_AND_RESULTS.md"

with open(output_filename, "w", encoding="utf-8") as outfile:
    outfile.write("# CONSOLIDATED FURI RESULTS AND TESTS\n\n")
    outfile.write("This file contains a concatenation of all quantitative results, evaluation reports, and test outputs.\n")
    
    for filepath in files_to_concat:
        if os.path.exists(filepath):
            outfile.write(f"\n\n{'='*80}\n")
            outfile.write(f"## FILE: {filepath}\n")
            outfile.write(f"{'='*80}\n\n")
            # If it's a markdown or text file, we don't necessarily need to put it in a code block,
            # but to ensure it doesn't break formatting, we can wrap raw text/csv in code blocks.
            ext = os.path.splitext(filepath)[1].lower()
            if ext in ['.txt', '.csv']:
                outfile.write("```\n")
            try:
                with open(filepath, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
            except Exception as e:
                # Fallback to utf-8 with replace
                with open(filepath, "r", encoding="utf-8", errors="replace") as infile:
                    outfile.write(infile.read())
            if ext in ['.txt', '.csv']:
                outfile.write("\n```\n")
        else:
            outfile.write(f"\n\n## [FILE NOT FOUND: {filepath}]\n")

print(f"Successfully consolidated into {output_filename}")

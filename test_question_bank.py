from question_bank import QUESTION_BANK

total_questions = 0

for stage_number, stage_data in QUESTION_BANK.items():
    questions = stage_data["questions"]

    print(f"Stage {stage_number}: {stage_data['name']}")
    print(f"Number of questions: {len(questions)}")

    total_questions += len(questions)

print("\nTotal questions:", total_questions)
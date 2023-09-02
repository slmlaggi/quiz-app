import sqlite3
import os
import sys

# Connect to the SQLite database or create one if it doesn't exist
conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

# Create the tables needed for the quiz program


def create_tables():
    # TODO -- Add login system for users to view and delete their scores more easily.

    # cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    #                    id INTEGER PRIMARY KEY,
    #                   username TEXT UNIQUE,
    #                    password TEXT
    #                )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS quizzes (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        question_count INTEGER
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY,
                        quiz_id INTEGER,
                        question_id INTEGER,
                        question TEXT,
                        answer_a TEXT,
                        answer_b TEXT,
                        answer_c TEXT,
                        answer_d TEXT,
                        correct_answer TEXT,
                        FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
                    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        quiz_id INTEGER,
                        score INTEGER,
                        answer TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
                    )""")

    conn.commit()


# Function to insert a quiz from a text file


def insert_quiz_from_file(file_path, overwrite=False):
    with open(file_path, "r") as f:
        lines = f.readlines()
        title = lines.pop(0).strip()
        question_count = len(lines) // 6

        if overwrite:
            quiz_id = overwrite
            cursor.execute("UPDATE quizzes SET title = ?, question_count = ? WHERE id = ?",
                           (title, question_count, quiz_id))
            cursor.execute(
                "DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
        else:
            cursor.execute(
                "INSERT INTO quizzes (title, question_count) VALUES (?, ?)", (title, question_count))
            quiz_id = cursor.lastrowid

        for i in range(question_count):
            question = lines[i * 6].strip()
            answer_a = lines[i * 6 + 1].strip()
            answer_b = lines[i * 6 + 2].strip()
            answer_c = lines[i * 6 + 3].strip()
            answer_d = lines[i * 6 + 4].strip()
            correct_answer = lines[i * 6 + 5].strip()

            cursor.execute("""INSERT INTO questions (quiz_id, question_id, question, answer_a, answer_b, answer_c, answer_d, correct_answer)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                           (quiz_id, i + 1, question, answer_a, answer_b, answer_c, answer_d, correct_answer))

    conn.commit()


# Function to take a quiz


def take_quiz(quiz_id, user_id):
    cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = cursor.fetchall()

    correct_count = 0
    answers = []
    wrong_id = []
    for question in questions:
        print("\n" + question[3])
        print("A) " + question[4])
        print("B) " + question[5])
        print("C) " + question[6])
        print("D) " + question[7])

        user_answer = input("Enter your answer (A, B, C, or D): ").upper()
        while user_answer not in ("A", "B", "C", "D"):
            user_answer = input(
                "Invalid input. Enter your answer (A, B, C, or D): ").upper()

        answers.append(user_answer)
        if user_answer == question[8]:
            correct_count += 1
        else:
            wrong_id.append(question[2])

    score = correct_count / len(questions) * 100
    cursor.execute(
        "INSERT INTO scores (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
    conn.commit()

    print("\nYour score: {:.2f}%".format(score))

    view_answers = input(
        "Would you like to view your answers for this quiz? (Y/N): ").upper()

    while view_answers not in ("Y", "N"):
        view_answers = input(
            "Invalid input. Would you like to view your answers for this quiz? (Y/N): ")

    # TODO -- Add a system where the answers for the quiz is sent to the database in the `answers` column in the scores table. Then, answers are checked to see which are correct and which are wrong.

    if view_answers == "Y":
        print("Your answers:")
        print(wrong_id)
        for question in questions:
            print(f"{question[2]}: {answers[question[2] - 1]} ", end = '')
            if question[2] in wrong_id:
                print(f"❌ Wrong -- Correct answer: {question[8]}")
            else:
                print("✔️  Correct")
    elif view_answers == "N":
        pass


# Function to delete a quiz


def delete_quiz(quiz_id):
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz = cursor.fetchone()
    if quiz:
        # Delete the quiz and its questions
        cursor.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        conn.commit()

        # Update the IDs of the remaining quizzes
        cursor.execute("SELECT id FROM quizzes ORDER BY id ASC")
        quizzes = cursor.fetchall()
        for i, quiz in enumerate(quizzes):
            cursor.execute(
                "UPDATE quizzes SET id = ? WHERE id = ?", (i+1, quiz[0]))
            cursor.execute(
                "UPDATE questions SET quiz_id = ? WHERE quiz_id = ?", (i+1, quiz[0]))
            cursor.execute(
                "UPDATE scores SET quiz_id = ? WHERE quiz_id = ?", (i+1, quiz[0]))
        remaining_questions = cursor.execute(
            "SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
        if remaining_questions:
            for i, question in enumerate(remaining_questions):
                cursor.execute(
                    "UPDATE questions SET id = ? WHERE id = ?", (i + 1, question[0]))
        conn.commit()

        print("Quiz deleted successfully!")
    else:
        print("Quiz not found.")


# Function to delete scores of a certain user


def delete_scores(user_id):
    cursor.execute("SELECT * FROM scores WHERE user_id = ?", (user_id,))
    scores = cursor.fetchall()
    if scores:
        score_ids = [score[0] for score in scores]
        print("The following scores were found for this user:")
        for score in scores:
            print(f"{score[0]}. Quiz ID: {score[2]}, Score: {score[3]}%")
        choice = input(
            "Enter the IDs of the scores you want to delete, separated by commas. Enter \"all\" if you want to delete all scores for the user: ")
        if choice == "all" or "All":
            delete_ids = range(1, len(scores) + 1)
        else:
            delete_ids = [int(cid) for cid in choice.split(",")]
        delete_scores = [
            score_id for score_id in score_ids if score_id in delete_ids]
        cursor.execute("DELETE FROM scores WHERE id IN ({})".format(
            ",".join("?" * len(delete_scores))), delete_scores)
        conn.commit()
        remaining_scores = cursor.execute(
            "SELECT * FROM scores WHERE user_id = ?", (user_id,)).fetchall()
        if remaining_scores:
            for i, score in enumerate(remaining_scores):
                cursor.execute(
                    "UPDATE scores SET id = ? WHERE id = ?", (i + 1, score[0]))
            conn.commit()
            print("Scores have been deleted and IDs updated.")
        else:
            print("All scores have been deleted.")
    else:
        print("No scores were found for this user.")


# Main function to run the program


def main():
    create_tables()
    run = True

    while run:
        print("\nWelcome to the Quiz App!")
        print("1. Upload quiz from file")
        print("2. Take a quiz")
        print("3. Delete a quiz")
        print("4. Delete scores from a user")
        print("5. Exit")
        choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

        if choice == "1":
            upload_choice = input(
                "Do you want to (1) upload a new quiz or (2) overwrite an existing quiz? ")
            if upload_choice == "1":
                file_name = input(
                    "Enter the name of the text file containing the quiz: ")
                try:
                    insert_quiz_from_file(f'./quizzes/{file_name}.txt')
                    print("Quiz uploaded successfully!")
                except Exception as e:
                    print("Error uploading quiz:", e)
            elif upload_choice == "2":
                quiz_id = input(
                    "Enter the ID of the quiz you want to overwrite: ")
                file_path = input(
                    "Enter the path of the text file containing the quiz: ")
                try:
                    insert_quiz_from_file(file_path, overwrite=quiz_id)
                    print("Quiz overwritten successfully!")
                except Exception as e:
                    print("Error overwriting quiz:", e)
            else:
                print("Invalid choice. Please try again.")

        elif choice == "2":
            quiz_id = int(input("Enter the quiz ID you want to take: "))
            user_id = int(input("Enter your user ID: "))
            try:
                take_quiz(quiz_id, user_id)
            except Exception as e:
                print("Error taking quiz:", e)

        elif choice == "3":
            quiz_id = input("Enter the quiz ID you want to delete: ")
            try:
                delete_quiz(quiz_id)
            except Exception as e:
                print("Error deleting quiz:", e)

        elif choice == "4":
            user_id = input("Enter your user ID: ")
            try:
                delete_scores(user_id)
            except Exception as e:
                print(f"Error deleting scores: {e}")

        elif choice == "5":
            run = False

        else:
            print("Invalid choice. Please try again.")

    print("Thank you for using the Quiz App!")


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import sqlite3
import random

conn = sqlite3.connect('quizzes.db')
cursor = conn.cursor()

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz App")
        self.w, self.h = self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (self.w, self.h))
        self.root.resizable(0,0)
        self.top_button_frame = None  # Initialize the top button frame as None
        self.main_menu("Create")
        
    def create_top_buttons(self):
        # Create a frame for the top buttons
        top_button_frame = tk.Frame(self.root)
        top_button_frame.pack(side=tk.TOP, anchor='ne', padx=10, pady=10)

        # Create a Quit button
        quit_button = tk.Button(top_button_frame, text="Quit", font=("DejaVuSans", 24, "bold"), command=self.quit_app)
        quit_button.pack(side=tk.RIGHT)
        
        # Create an Info button
        info_button = tk.Button(top_button_frame, text="Info", font=("DejaVu Sans", 24, "bold"), command=self.show_info)
        info_button.pack(side=tk.RIGHT, padx=5)

    def show_info(self):
        messagebox.showinfo("Quiz App Info", "This is a quiz application where you can create and take quizzes.\nRead the guide on README.md for more information and tutorial on how to use the app.")

    def quit_app(self):
        self.root.quit()

    def main_menu(self, topButton=None):
        # Create a frame for the main menu
        if topButton == "Create":    
            self.create_top_buttons()

        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack(pady=20)

        # Create a label for the main menu
        self.main_menu_label = tk.Label(self.main_menu_frame, text="Main Menu", font=("Arial", 36))
        self.main_menu_label.pack(pady=(int(self.h * 0.35), 0))

        # Create a frame for the buttons
        self.button_frame = tk.Frame(self.main_menu_frame)
        self.button_frame.pack(pady=int(self.h * 0.05))

        # Create a button to create a quiz
        self.create_quiz_button = tk.Button(self.button_frame, text="Create a Quiz", command=self.create_quiz, font=("DejaVuSans", 24, "bold"))
        self.create_quiz_button.pack(side=tk.LEFT, padx=10)
        
        # Create a button to edit a quiz
        self.edit_quiz_button = tk.Button(self.button_frame, text="Edit a Quiz", command=self.edit_quiz, font=("DejaVuSans", 24, "bold"))
        self.edit_quiz_button.pack(side=tk.LEFT, padx=10)

        # Create a button to take a quiz
        self.take_quiz_button = tk.Button(self.button_frame, text="Take a Quiz", command=self.quiz_selection, font=("DejaVuSans", 24, "bold"))
        self.take_quiz_button.pack(side=tk.LEFT, padx=10)
        
    def back_btn(self, current_frame, new_frame):
        try:
            if self.questions:
                response = messagebox.askyesno("Warning", "You have unsaved changes. Are you sure you want to go back?")
                if response:
                    for frame in current_frame:
                        frame.destroy()
                    new_frame()
        except Exception as e:    
            for frame in current_frame:
                frame.destroy()
            new_frame()

    def create_quiz(self):
        # Create a new frame for the create quiz page
        self.main_menu_frame.destroy()
        self.create_quiz_frame = tk.Frame(self.root)
        self.create_quiz_frame.pack(pady=(int(self.h * 0.3), 0))

        # Create a label for the quiz title
        self.quiz_title_label = tk.Label(self.create_quiz_frame, text="Quiz Title:", font=("Arial", 24))
        self.quiz_title_label.grid(row=0, column=0, padx=10, pady=int(self.h * 0.025))

        # Create an entry for the quiz title
        self.quiz_title_entry = tk.Entry(self.create_quiz_frame, font=("Arial", 24), width=50)
        self.quiz_title_entry.grid(row=0, column=1, padx=10, pady=int(self.h * 0.025))

        # Create a label for the number of questions
        self.num_questions_label = tk.Label(self.create_quiz_frame, text="Number of Questions (max 50):", font=("Arial", 24))
        self.num_questions_label.grid(row=1, column=0, padx=10, pady=int(self.h * 0.025))

        # Create an entry for the number of questions
        self.num_questions_entry = tk.Entry(self.create_quiz_frame, font=("Arial", 24), width=50)
        self.num_questions_entry.grid(row=1, column=1, padx=10, pady=int(self.h * 0.025))

       # Create a new frame for the back and save buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=(20, int(self.h * 0.1)))

        # Create a back button to go back to the home menu
        self.back_button = tk.Button(self.button_frame, text="Back", command=lambda: self.back_btn([self.create_quiz_frame, self.button_frame], self.main_menu), font=("DejaVuSans", 24, "bold"))
        self.back_button.pack(side=tk.LEFT, padx=10)

        # Create a save button to save the quiz
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_quiz, font=("DejaVuSans", 24, "bold"))
        self.save_button.pack(side=tk.LEFT, padx=10)

    def save_quiz(self):
        # Get the quiz title and number of questions
        self.quiz_title = self.quiz_title_entry.get()
        
        # Check if the quiz title already exists
        cursor.execute('SELECT COUNT(*) FROM quizzes WHERE title = ?', (self.quiz_title,))
        exists = cursor.fetchone()[0]
        
        if exists > 0:
            # If the title exists, prompt the user to enter a new title
            messagebox.showerror("Duplicate Title", "This quiz title already exists. Please choose a different title.")
            return
        
        if len(self.quiz_title) > 50:
            # If the title is too long, prompt the user to enter a shorter title
            messagebox.showerror("Invalid Title", "Please enter a title with at most 50 characters.")
            return
        
        try:
            self.num_questions = int(self.num_questions_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of questions")
            return

        # Validate the number of questions
        if not 1 <= self.num_questions <= 50:
            messagebox.showerror("Invalid Input", "Please enter a number between 1 and 50")
            return

        # Destroy the current frame
        self.create_quiz_frame.destroy()
        self.button_frame.destroy()

        # Create a new frame for the question interface
        self.question_interface_frame = tk.Frame(self.root)
        self.question_interface_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Create a canvas
        self.canvas = tk.Canvas(self.question_interface_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        self.scrollbar = tk.Scrollbar(self.question_interface_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the question inputs
        self.question_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.question_frame, anchor="nw", width=self.w)

        # Update the scroll region to encompass the size of the question frame
        self.question_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Display the quiz title and number of questions at the top
        title_label = tk.Label(self.question_frame, text=f"Quiz Title: {self.quiz_title}\t Number of Questions: {self.num_questions}", font=("Arial", 30))
        title_label.pack(pady=(10, 0))

        # Create questions
        self.questions = []
        for i in range(self.num_questions):
            # Create a frame for each question with 20px padding to the right
            question_container = tk.Frame(self.question_frame)
            question_container.pack(pady=(20, 0), padx=int(self.w * 0.05), fill=tk.BOTH, expand=True)  # 20px padding to the right

            # Create a frame for the question
            question_frame = tk.Frame(question_container)
            question_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

            # Create a label and entry for the question
            question_label = tk.Label(question_frame, text=f"{i+1}. Question:", font=("Arial", 20))
            question_label.pack(side=tk.LEFT)
            question_entry = tk.Entry(question_frame, font=("Arial", 20))
            question_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 50))

            # Create a frame for the question type
            type_frame = tk.Frame(question_container)
            type_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

            # Create a label and option menu for the question type
            type_label = tk.Label(type_frame, text="Type:", font=("Arial", 20))
            type_label.pack(side=tk.LEFT)
            type_var = tk.StringVar(type_frame)
            type_var.set("Text Input")  # default value
            type_option = tk.OptionMenu(type_frame, type_var, "Text Input", "Multiple Choice")
            type_option.pack(side=tk.LEFT)
            type_option.config(font=("DejaVuSans", 20))
            self.root.nametowidget(type_option.menuname).config(font=("DejaVuSans", 20))

            # Create a frame for the answer
            answer_frame = tk.Frame(question_container)
            answer_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

            # Create a label and entry for the answer
            answer_label = tk.Label(answer_frame, text="Answer:", font=("Arial", 20))
            answer_label.pack(side=tk.LEFT)
            answer_entry = tk.Entry(answer_frame, font=("Arial", 20))
            answer_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 50))

            # Add the question to the list
            self.questions.append((question_entry, type_var, answer_entry))

        # Create a new frame for the back and save buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=(20, int(self.h * 0.1)))

        # Create a back button to go back to the home menu
        self.back_button = tk.Button(self.button_frame, text="Back", command=lambda: self.back_btn([self.question_interface_frame, self.button_frame], self.create_quiz), font=("DejaVuSans", 24, "bold"))
        self.back_button.pack(side=tk.LEFT, padx=10)

        # Create a save button to save the quiz
        self.save_button = tk.Button(self.button_frame, text="Save", command=lambda: self.save_quiz_data([self.question_interface_frame, self.button_frame], self.create_quiz), font=("DejaVuSans", 24, "bold"))
        self.save_button.pack(side=tk.LEFT, padx=10)
            
    def save_quiz_data(self, frames, new_frame, quiz_title=None):
        # Create the quizzes table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                question TEXT NOT NULL,
                type TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        
        if quiz_title == None:
            quiz_title = self.quiz_title

        # Insert the quiz title and questions into the quizzes table
        for question_entry, type_var, answer_entry in self.questions:
            question_text = question_entry.get()
            question_type = type_var.get()
            answer_text = answer_entry.get()
            
            cursor.execute('''
            INSERT INTO quizzes (title, question, type, answer)
            VALUES (?, ?, ?, ?)
        ''', (quiz_title, question_text, question_type, answer_text))

        # Commit the changes
        conn.commit()
        messagebox.showinfo("Success", f"Quiz '{quiz_title}' saved successfully!")

        # Destroy the question interface frame and button frame
        for frame in frames:
            frame.destroy()
        
        new_frame()
        
    def edit_quiz(self):
        if self.main_menu_frame:
            self.main_menu_frame.destroy()
        # Fetch existing quizzes from the database by title
        cursor.execute("SELECT DISTINCT title FROM quizzes")
        quiz_titles = cursor.fetchall()
        
        # Create a new frame for editing quizzes
        self.edit_quiz_frame = tk.Frame(self.root)
        self.edit_quiz_frame.pack(pady=(int(self.h * 0.15), 20))

        # Create a label and a listbox for quiz selection
        tk.Label(self.edit_quiz_frame, text="Select a Quiz to Edit or Delete:", font=("Arial", 24)).pack()

        self.quiz_listbox = tk.Listbox(self.edit_quiz_frame, font=("Arial", 20))
        for quiz in quiz_titles:
            self.quiz_listbox.insert(tk.END, quiz[0])  # Display only the title
        self.quiz_listbox.pack(pady=int(self.h * 0.05))

        # Back button to return to the main menu
        back_button = tk.Button(self.edit_quiz_frame, text="Back", command=lambda: self.back_btn([self.edit_quiz_frame], self.main_menu), font=("DejaVuSans", 24, "bold"))
        back_button.pack(side=tk.LEFT, padx=10, pady=int(self.h * 0.05))
        
        # Create Edit, Delete, and Rename buttons
        edit_button = tk.Button(self.edit_quiz_frame, text="Edit Quiz", command=self.edit_selected_quiz, font=("DejaVuSans", 24, "bold"))
        edit_button.pack(side=tk.LEFT, padx=10, pady=int(self.h * 0.05))

        delete_button = tk.Button(self.edit_quiz_frame, text="Delete Quiz", command=self.confirm_delete_quiz, font=("DejaVuSans", 24, "bold"))
        delete_button.pack(side=tk.LEFT, padx=10, pady=int(self.h * 0.05))

        rename_button = tk.Button(self.edit_quiz_frame, text="Rename Quiz", command=self.rename_quiz, font=("DejaVuSans", 24, "bold"))
        rename_button.pack(side=tk.LEFT, padx=10, pady=int(self.h * 0.05))

    def confirm_delete_quiz(self):
        selected_quiz = self.quiz_listbox.curselection()
        if selected_quiz:
            quiz_title = self.quiz_listbox.get(selected_quiz)  # Get the selected quiz title
            response = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this quiz?")
            if response:
                cursor.execute("DELETE FROM quizzes WHERE title = ?", (quiz_title,))
                conn.commit()
                messagebox.showinfo("Success", "Quiz deleted successfully!")
                self.edit_quiz_frame.destroy()
                self.edit_quiz()
        else:
            messagebox.showwarning("Selection Error", "Please select a quiz to delete.")
            
    def rename_quiz(self):
        selected_quiz = self.quiz_listbox.curselection()
        if selected_quiz:
            old_title = self.quiz_listbox.get(selected_quiz)  # Get the selected quiz title
            new_title = simpledialog.askstring("Rename Quiz", "Enter new quiz title:", initialvalue=old_title)

            if new_title:
                # Check if the new title already exists
                cursor.execute('SELECT COUNT(*) FROM quizzes WHERE title = ?', (new_title,))
                exists = cursor.fetchone()[0]
                if exists > 0:
                    messagebox.showerror("Duplicate Title", "This quiz title already exists. Please choose a different title.")
                    return

                # Update the quiz title in the database
                cursor.execute("UPDATE quizzes SET title = ? WHERE title = ?", (new_title, old_title))
                conn.commit()
                messagebox.showinfo("Success", f"Quiz renamed to '{new_title}' successfully!")
                self.edit_quiz_frame.destroy()
                self.edit_quiz()
        else:
            messagebox.showwarning("Selection Error", "Please select a quiz to rename.")

    def edit_selected_quiz(self):
        selected_quiz = self.quiz_listbox.curselection()
        if selected_quiz:
            quiz_title = self.quiz_listbox.get(selected_quiz)  # Get the selected quiz title
            cursor.execute("SELECT question, type, answer FROM quizzes WHERE title = ?", (quiz_title,))
            quiz_data = cursor.fetchall()

            # Create a new frame for editing quiz data
            self.edit_quiz_frame.destroy()
            self.edit_quiz_data_frame = tk.Frame(self.root)
            self.edit_quiz_data_frame.pack(pady=20, fill=tk.BOTH, expand=True)

            # Create a canvas for scrolling
            self.canvas = tk.Canvas(self.edit_quiz_data_frame)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create a scrollbar for the canvas
            self.scrollbar = tk.Scrollbar(self.edit_quiz_data_frame, orient="vertical", command=self.canvas.yview)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Configure the canvas
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # Create a frame inside the canvas to hold the question inputs
            self.question_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.question_frame, anchor="nw", width=self.w)

            # Update the scroll region to encompass the size of the question frame
            self.question_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

            # Display the quiz title and number of questions at the top
            title_label = tk.Label(self.question_frame, text=f"Quiz Title: {quiz_title}\t Number of Questions: {len(quiz_data)}", font=("Arial", 30))
            title_label.pack(pady=(10, 0))

            # Create questions
            self.questions = []
            for i, question in enumerate(quiz_data):
                # Create a frame for each question with 20px padding to the right
                question_container = tk.Frame(self.question_frame)
                question_container.pack(pady=(20, 0), padx=int(self.w * 0.05), fill=tk.BOTH, expand=True)  # 20px padding to the right

                # Create a frame for the question
                question_frame = tk.Frame(question_container)
                question_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

                # Create a label and entry for the question
                question_label = tk.Label(question_frame, text=f"{i+1}. Question:", font=("Arial", 20))
                question_label.pack(side=tk.LEFT)
                question_entry = tk.Entry(question_frame, font=("Arial", 20))
                question_entry.insert(0, question[0])  # Populate with existing question
                question_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 50))

                # Create a frame for the question type
                type_frame = tk.Frame(question_container)
                type_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

                # Create a label and option menu for the question type
                type_label = tk.Label(type_frame, text="Type:", font=("Arial", 20))
                type_label.pack(side=tk.LEFT)
                type_var = tk.StringVar(type_frame)
                type_var.set(question[1])  # Populate with existing type
                type_option = tk.OptionMenu(type_frame, type_var, "Text Input", "Multiple Choice")
                type_option.pack(side=tk.LEFT)
                type_option.config(font=("DejaVuSans", 20))
                self.root.nametowidget(type_option.menuname).config(font=("DejaVuSans", 20))

                # Create a frame for the answer
                answer_frame = tk.Frame(question_container)
                answer_frame.pack(pady=10, padx=int(self.w * 0.05), fill=tk.BOTH)

                # Create a label and entry for the answer
                answer_label = tk.Label(answer_frame, text="Answer:", font=("Arial", 20))
                answer_label.pack(side=tk.LEFT)
                answer_entry = tk.Entry(answer_frame, font=("Arial", 20))
                answer_entry.insert(0, question[2])  # Populate with existing answer
                answer_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 50))

                # Add the question to the list
                self.questions.append((question_entry, type_var, answer_entry))

            # Create a new frame for the back and save buttons
            self.button_frame = tk.Frame(self.root)
            self.button_frame.pack(pady=(20, int(self.h * 0.1)))

            # Create a back button to go back to the home menu
            self.back_button = tk.Button(self.button_frame, text="Back", command=lambda: self.back_btn([self.edit_quiz_data_frame, self.button_frame], self.edit_quiz), font=("DejaVuSans", 24, "bold"))
            self.back_button.pack(side=tk.LEFT, padx=10)

            # Create a save button to save the quiz
            self.save_button = tk.Button(self.button_frame, text="Save", command=lambda: self.save_edited_quiz([self.edit_quiz_data_frame, self.button_frame], self.edit_quiz, quiz_title), font=("DejaVuSans", 24, "bold"))
            self.save_button.pack(side=tk.LEFT, padx=10)
        else:
            messagebox.showinfo("Error", "Quiz not found.")
            
    def save_edited_quiz(self, frames, new_frame, quiz_title):
        cursor.execute('DELETE FROM quizzes WHERE title = ?', (quiz_title,))
        self.save_quiz_data(frames, new_frame, quiz_title)
        
    def quiz_selection(self):
        # Create a new frame for the take quiz page
        self.main_menu_frame.destroy()
        self.take_quiz_frame = tk.Frame(self.root)
        self.take_quiz_frame.pack(pady=20)

        # Create a label for the quiz selection
        self.quiz_selection_label = tk.Label(self.take_quiz_frame, text="Select a Quiz:", font=("Arial", 20))
        self.quiz_selection_label.pack()

        # Create a listbox for the quiz selection
        self.quiz_listbox = tk.Listbox(self.take_quiz_frame, font=("Arial", 20))
        self.quiz_listbox.pack()
        
        # Add the existing quizzes to the listbox and their number of questions
        cursor.execute("SELECT DISTINCT title FROM quizzes")
        quiz_titles = cursor.fetchall()
        for quiz in quiz_titles:
            cursor.execute("SELECT COUNT(*) FROM quizzes WHERE title = ?", (quiz[0],))
            num_questions = cursor.fetchone()[0]
            self.quiz_listbox.insert(tk.END, f"{quiz[0]} (Questions: {num_questions})")
        
        # Create a button to start the quiz
        self.start_quiz_button = tk.Button(self.take_quiz_frame, text="Start Quiz", command=self.start_quiz, font=("DejaVuSans", 24, "bold"))
        self.start_quiz_button.pack(pady=20)
    
    def start_quiz(self):
        selected_quiz = self.quiz_listbox.curselection()
        if selected_quiz:
            quiz_title = self.quiz_listbox.get(selected_quiz)  # Get the selected quiz title
            
            # Fetch the questions for the selected quiz
            cursor.execute("SELECT question, type, answer FROM quizzes WHERE title = ?", (quiz_title.split()[0],))
            self.quiz_data = cursor.fetchall()  # Store quiz data for access in take_quiz
            
            if not self.quiz_data:
                messagebox.showwarning("No Questions", "This quiz has no questions.")
                return

            # Create a new frame for the quiz interface
            self.quiz_frame = tk.Frame(self.root)
            self.quiz_frame.pack(pady=20, fill=tk.BOTH, expand=True)

            # Display the quiz title and number of questions
            title_label = tk.Label(self.quiz_frame, text=f"Quiz: {quiz_title} (Questions: {len(self.quiz_data)})", font=("Arial", 30))
            title_label.pack(pady=(10, 0))

            # Initialize question index
            self.current_question_index = 0
            self.results = []
            self.take_quiz()  # Start displaying the first question

        else:
            messagebox.showwarning("Selection Error", "Please select a quiz to start.")

    def take_quiz(self):
        # Clear the current quiz frame if it exists
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()
        self.take_quiz_frame.destroy()
        self.button_frame.destroy()

        # Check if there are more questions
        if self.current_question_index >= len(self.quiz_data):
            self.quiz_ended()
            self.quiz_frame.destroy()  # Clean up the quiz frame
            self.main_menu()  # Return to the main menu
            return

        # Get the current question and its details
        question, question_type, correct_answer = self.quiz_data[self.current_question_index]

        # Display the question
        question_label = tk.Label(self.quiz_frame, text=f"Q{self.current_question_index + 1}: {question}", font=("Arial", 24))
        question_label.pack(pady=(10, 0))

        if question_type == "Multiple Choice":
            # Prepare multiple choice options
            options = correct_answer.split('|')
            random.shuffle(options)  # Randomize the options
            self.mc_frame = tk.Frame(self.quiz_frame)
            self.mc_frame.pack(pady=(20, int(self.h * 0.1)))

            # Create buttons for each option
            count_mc = 0
            mc_letters = ['A:', 'B:', 'C:', 'D:']
            for option in options:
                option_button = tk.Button(self.mc_frame, text=f"{mc_letters[count_mc]}{option.split(':')[1]}", command=lambda opt=option: self.check_multiple_choice_answer(opt), font=("Arial", 20))
                option_button.pack(pady=(5, 0))
                count_mc += 1

        else:
            # Create an entry for the answer
            self.answer_entry = tk.Entry(self.quiz_frame, font=("Arial", 20))
            self.answer_entry.pack(pady=(10, 20))
            
        # Create frame for buttons
        self.button_frame = tk.Frame(self.quiz_frame)
        self.button_frame.pack(pady=(20, int(self.h * 0.1)))

        # Create a button to go back to the main menu
        back_button = tk.Button(self.button_frame, text="Back to Menu", command=self.confirm_back_to_menu, font=("Arial", 20))
        back_button.pack(side=tk.LEFT, padx=10)

        # Create a skip button
        skip_button = tk.Button(self.button_frame, text="Skip Question", command=self.skip_question, font=("Arial", 20))
        skip_button.pack(side=tk.LEFT, padx=10)

        if question_type != "Multiple Choice":
            # Create a submit button
            submit_button = tk.Button(self.button_frame, text="Submit Answer", command=self.submit_answer, font=("Arial", 20))
            submit_button.pack(side=tk.LEFT, padx=10)

    def submit_answer(self):
        user_answer = self.answer_entry.get().strip() if hasattr(self, 'answer_entry') else None
        correct_answer = self.quiz_data[self.current_question_index][2]  # Get the correct answer

        if user_answer and user_answer.lower() == correct_answer.lower():
            messagebox.showinfo("Correct!", "Your answer is correct!")
            self.results.append(1)
        else:
            messagebox.showinfo("Incorrect", f"The correct answer was:{correct_answer}")
            self.results.append(0)

        # Move to the next question
        self.current_question_index += 1

        # Check if there are more questions
        if self.current_question_index < len(self.quiz_data):
            self.take_quiz()  # Display the next question
        else:
            self.quiz_ended()
            self.quiz_frame.destroy()  # Clean up the quiz frame
            self.main_menu()  # Return to the main menu

    def check_multiple_choice_answer(self, selected_option):
        correct_answer = self.quiz_data[self.current_question_index][2].split('|')[0].split(':')[1]  # Get the correct answer
        if selected_option.split(':')[1] == correct_answer:  # Compare the letter (A, B, C, D)
            messagebox.showinfo("Correct!", "Your answer is correct!")
            self.results.append(1)
        else:
            messagebox.showinfo("Incorrect", f"The correct answer was: {correct_answer}")
            self.results.append(0)

        # Move to the next question
        self.current_question_index += 1

        # Check if there are more questions
        if self.current_question_index < len(self.quiz_data):
            self.take_quiz()  # Display the next question
        else:
            self.quiz_ended()
            self.quiz_frame.destroy()  # Clean up the quiz frame
            self.main_menu()  # Return to the main menu

    def skip_question(self):
        response = messagebox.askyesno("Skip Question", "Are you sure you want to skip this question?")
        if response:
            self.current_question_index += 1  # Move to the next question
            self.results.append(0)
            if self.current_question_index < len(self.quiz_data):
                self.take_quiz()  # Display the next question
            else:
                self.quiz_ended()
                self.quiz_frame.destroy()  # Clean up the quiz frame
                self.main_menu()  # Return to the main menu

    def confirm_back_to_menu(self):
        response = messagebox.askyesno("Warning", "Progress will not be saved. Do you want to go back?")
        if response:
            self.quiz_frame.destroy()  # Clean up the quiz frame
            self.main_menu()  # Return to the main menu
            
    def quiz_ended(self):
        total_correct = sum(self.results)
        total_questions = len(self.results)
        id_incorrect = [i for i, x in enumerate(self.results) if x == 0]
        if len(id_incorrect) > 0:
            incorrects = '(Questions answered incorrectly: '
            for i in id_incorrect:
                if i != len(id_incorrect) - 1:
                    incorrects += f"Q{i+1}, "
                else:
                    incorrects += f"Q{i+1})"
            messagebox.showinfo("Quiz Ended", f"You answered {total_correct} out of {total_questions} questions correctly.\n{incorrects}")
        else:        
            messagebox.showinfo("Quiz Ended", f"You answered {total_correct} out of {total_questions} questions correctly. Congratulations!")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
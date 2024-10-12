class Student:
    def __init__(self, name, surname, gender):
        self.name = name
        self.surname = surname
        self.gender = gender
        self.finished_courses = []
        self.courses_in_progress = []
        self.grades = {}

    def average_grade(self):
        total_grades = sum([sum(grades) for grades in self.grades.values()], 0)
        total_count = sum([len(grades) for grades in self.grades.values()], 0)
        return total_grades / total_count if total_count > 0 else 0

    def rate_lecturer(self, lecturer, course, grade):
        if isinstance(lecturer, Lecturer) and course in self.courses_in_progress and course in lecturer.courses_attached:
            if course in lecturer.grades:
                lecturer.grades[course] += [grade]
            else:
                lecturer.grades[course] = [grade]
        else:
            return 'Ошибка'

    def __str__(self):
        courses_in_progress_str = ', '.join(self.courses_in_progress)
        finished_courses_str = ', '.join(self.finished_courses)
        avg_grade = self.average_grade()
        return (f"Имя: {self.name}\n"
                f"Фамилия: {self.surname}\n"
                f"Средняя оценка за домашние задания: {avg_grade:.1f}\n"
                f"Курсы в процессе изучения: {courses_in_progress_str}\n"
                f"Завершенные курсы: {finished_courses_str}")

    def __lt__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.average_grade() < other.average_grade()

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.average_grade() == other.average_grade()


class Mentor:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        self.courses_attached = []


class Lecturer(Mentor):
    def __init__(self, name, surname):
        super().__init__(name, surname)
        self.grades = {}

    def average_grade(self):
        total_grades = sum([sum(grades) for grades in self.grades.values()], 0)
        total_count = sum([len(grades) for grades in self.grades.values()], 0)
        return total_grades / total_count if total_count > 0 else 0

    def __str__(self):
        avg_grade = self.average_grade()
        return (f"Имя: {self.name}\n"
                f"Фамилия: {self.surname}\n"
                f"Средняя оценка за лекции: {avg_grade:.1f}")

    def __lt__(self, other):
        if not isinstance(other, Lecturer):
            return NotImplemented
        return self.average_grade() < other.average_grade()

    def __eq__(self, other):
        if not isinstance(other, Lecturer):
            return NotImplemented
        return self.average_grade() == other.average_grade()


class Reviewer(Mentor):
    def rate_hw(self, student, course, grade):
        if isinstance(student, Student) and course in self.courses_attached and course in student.courses_in_progress:
            if course in student.grades:
                student.grades[course] += [grade]
            else:
                student.grades[course] = [grade]
        else:
            return 'Ошибка'

    def __str__(self):
        return (f"Имя: {self.name}\n"
                f"Фамилия: {self.surname}")



def average_student_grade_for_course(students, course):
    total_grades = 0
    total_count = 0
    for student in students:
        if course in student.grades:
            total_grades += sum(student.grades[course])
            total_count += len(student.grades[course])
    return total_grades / total_count if total_count > 0 else 0



def average_lecturer_grade_for_course(lecturers, course):
    total_grades = 0
    total_count = 0
    for lecturer in lecturers:
        if course in lecturer.grades:
            total_grades += sum(lecturer.grades[course])
            total_count += len(lecturer.grades[course])
    return total_grades / total_count if total_count > 0 else 0


student_1 = Student('Ruoy', 'Eman', 'male')
student_1.courses_in_progress += ['Python', 'Git']
student_1.finished_courses += ['Введение в программирование']
student_1.grades = {'Python': [10, 9, 8], 'Git': [10, 9]}

student_2 = Student('Anna', 'Smith', 'female')
student_2.courses_in_progress += ['Python']
student_2.grades = {'Python': [7, 8, 9]}


lecturer_1 = Lecturer('Ivan', 'Ivanov')
lecturer_1.courses_attached += ['Python']
lecturer_1.grades = {'Python': [10, 9, 8]}

lecturer_2 = Lecturer('Petr', 'Petrov')
lecturer_2.courses_attached += ['Python']
lecturer_2.grades = {'Python': [6, 7, 8]}


reviewer_1 = Reviewer('Some', 'Buddy')
reviewer_1.courses_attached += ['Python']

reviewer_2 = Reviewer('John', 'Doe')
reviewer_2.courses_attached += ['Git']


reviewer_1.rate_hw(student_1, 'Python', 10)
reviewer_2.rate_hw(student_1, 'Git', 9)


student_1.rate_lecturer(lecturer_1, 'Python', 10)
student_2.rate_lecturer(lecturer_1, 'Python', 9)
student_2.rate_lecturer(lecturer_2, 'Python', 8)


print(reviewer_1)
print()
print(lecturer_1)
print()
print(student_1)
print()


students = [student_1, student_2]
lecturers = [lecturer_1, lecturer_2]

print(f"Средняя оценка за домашние задания по курсу 'Python': {average_student_grade_for_course(students, 'Python'):.1f}")
print(f"Средняя оценка за лекции по курсу 'Python': {average_lecturer_grade_for_course(lecturers, 'Python'):.1f}")

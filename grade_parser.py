import csv
from student import Student

class GradeParser:
    def __init__(self, file_path: str) -> None:
        """
        Initializes the grade file parser given the path to the grade file

        Parameters:
            file_path (str): The path to the grade file

        Returns:
            None
        """
        self.file_path = file_path
        self.assignments = []
        self.assignment_titles = []
        
        self.student_data = []

        self.parse_info()

    def parse_info(self) -> None:
        """
        Parses the grade file to extract the student data and grades

        Parameters:
            None

        Returns:
            None
        """
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)

            # Get the header row
            header = next(reader)
            self.parse_assignments(header)

            # Skip the next two rows (not student data) for now
            next(reader)
            next(reader)

            # Read in all the student data and grades
            for row in reader:
                # Extract the student's identifying information
                last_name, first_name = row[0].split(", ")
                student_id = row[2]
                section = row[3]

                # Create a student profile
                student = Student(first_name, last_name, student_id, section)

                # Extract the student's grades
                start_index = header.index("Section") + 1
                for assignment_index in range(len(self.assignments)):
                    grade = row[start_index + assignment_index]
                    student.add_grade(self.assignments[assignment_index], grade)

                self.student_data.append(student)

    def parse_assignments(self, header: list) -> None:
        """
        Using the header row, extract the relevant assignment column names

        Parameters:
            header (list): The header row of the CSV file

        Returns:
            list: A list of assignment column names
        """
        
        start_index = header.index("Section") + 1
        end_index = header.index("Current Score")

        self.assignments = header[start_index:end_index]

        # Ignore categorical columns
        for index in range(len(self.assignments) - 1):
            if self.assignments[index].endswith("Current Score") and self.assignments[index + 1].endswith("Unposted Current Score"):
                self.assignments = self.assignments[:index]
                break

        # Remove the assignment IDs to get the assignment titles
        self.assignment_titles = [" ".join(cls.split(" ")[:-1]) for cls in self.assignments]


gp = GradeParser("sample_data_2.csv")

import polars as pl
from io import StringIO
from student import Student

class GradeParser:
    def __init__(self, file_object) -> None:
        """
        Initializes the grade file parser given an uploaded file object

        Parameters:
            file_object: Uploaded file object (e.g., from Streamlit file_uploader)

        Returns:
            None
        """
        self.file_object = file_object
        self.assignments = []
        self.assignment_titles = []
        self.assignment_max_points = []
        self.student_data = []
        self.df = None  # Store the Polars DataFrame
        
        self.parse_info()

    def is_actual_grade(self, grade: str) -> bool:
        """
        Checks if the grade is a valid grade

        Parameters:
            grade (str): The grade to check

        Returns:
            bool: True if the grade is a valid grade, False otherwise
        """        
        # If the grade is a string, check if it's a number
        try:
            # Check if the grade is a number
            float(grade)
            return True
        except ValueError:
            return False

    def load_dataframe(self) -> pl.DataFrame:
        """
        Load the CSV data into a Polars DataFrame from file object

        Parameters:
            None
        
        Returns:
            pl.DataFrame: The loaded DataFrame
        """
        # Reset file pointer and read content
        self.file_object.seek(0)
        content = self.file_object.read()
        
        # Convert bytes to string if needed
        if isinstance(content, bytes):
            content = content.decode('utf-8')

        # Remove the last row (it's a test row)
        lines = content.strip().split("\n")[:-1]
        content = "\n".join(lines)
        
        # Use StringIO to create a file-like object for Polars
        return pl.read_csv(StringIO(content))

    def parse_info(self) -> None:
        """
        Parses the grade file to extract the student data and grades

        Parameters:
            None

        Returns:
            None
        """
        # Load the DataFrame
        self.df = self.load_dataframe()
        
        # Get column names and the row after with the max points available
        header = self.df.columns

        # Find the row that starts with "Points Possible"
        max_points_row = self.df.filter(pl.col("Student").str.contains("Points Possible")).row(0)
        self.parse_assignments(header, max_points_row)

        # Extract the student data
        student_rows = self.df.slice(2)
        
        # Process each student row
        for row in student_rows.iter_rows(named=True):
            # Extract the student's identifying information
            if not row.get("Student") or row["Student"].strip() == "":
                continue  # Skip empty rows

            last_name, first_name = row["Student"].split(", ")
            student_id = row["ID"]
            section = row["Section"]
            
            # Create a student profile
            student = Student(first_name, last_name, student_id, section)
            
            # Extract the student's grades
            for assignment in self.assignments:
                grade = row.get(assignment, "")
                student.add_grade(assignment, grade)
            
            self.student_data.append(student)

    def parse_assignments(self, header: list, max_points_row: list) -> None:
        """
        Using the header row, extract the relevant assignment column names

        Parameters:
            header (list): The header row (column names) of the CSV file
            max_points_row (list): The row after the header row with the max points available

        Returns:
            None
        """

        start_index = header.index("Section") + 1
        end_index = header.index("Current Score")
        
        self.assignments = header[start_index:end_index]
        print("--------------------------------")
        print(self.assignments)
        
        # Ignore categorical columns (Current Score, Unposted Current Score pairs)
        filtered_assignments = []
        for index in range(len(self.assignments)-1):
            current_assignment = self.assignments[index]
            
            # Check if this is a Current Score column followed by Unposted Current Score
            if (current_assignment.endswith("Current Score") and 
                index + 1 < len(self.assignments) and 
                self.assignments[index + 1].endswith("Unposted Current Score")):
                # Stop here - we've hit the grade summary columns
                break
            
            filtered_assignments.append(current_assignment)
        
        self.assignments = filtered_assignments
        print(self.assignments)
        assignments_with_max_points = []

        # Now remove all the columns that don't have a max score
        for index, assignment in enumerate(self.assignments):
            true_max_points_index = index + start_index
            print(index, assignment, max_points_row[true_max_points_index])
            if max_points_row[true_max_points_index] is not None and self.is_actual_grade(max_points_row[true_max_points_index]):
                assignments_with_max_points.append(assignment)
                print("Added")

        self.assignments = assignments_with_max_points
        print(self.assignments)

        # Remove the assignment IDs to get clean titles
        self.assignment_titles = [" ".join(assignment.split(" ")[:-1]) for assignment in self.assignments]

    def get_student_data(self) -> list:
        """
        Returns the list of student data

        Parameters:
            None

        Returns:
            list: The list of student data
        """

        return self.student_data.copy()
    
    def get_raw_assignment_titles(self) -> list:
        """
        Returns the list of assignment titles

        Parameters:
            None

        Returns:
            list: The list of assignment titles
        """

        return self.assignments.copy()
    
    def get_assignment_titles(self) -> list:
        """
        Returns the list of assignment titles

        Parameters:
            None

        Returns:
            list: The list of assignment titles
        """

        return self.assignment_titles.copy()
    
    def get_assignment_max_points(self) -> list:
        """
        Returns the list of assignment max points

        Parameters:
            None

        Returns:
            list: The list of assignment max points
        """

        return self.assignment_max_points.copy()

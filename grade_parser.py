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
        self.student_data = []
        self.df = None  # Store the Polars DataFrame
        
        self.parse_info()

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
        
        # Get column names
        header = self.df.columns
        self.parse_assignments(header)
        
        # Skip the first two data rows (they're not student data)
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
                

    def parse_assignments(self, header: list) -> None:
        """
        Using the header row, extract the relevant assignment column names

        Parameters:
            header (list): The header row (column names) of the CSV file

        Returns:
            None
        """

        start_index = header.index("Section") + 1
        end_index = header.index("Current Score")
        
        self.assignments = header[start_index:end_index]
        
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
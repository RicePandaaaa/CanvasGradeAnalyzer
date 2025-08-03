class Student:
    def __init__(self, first_name: str, last_name: str, user_id: str, section: str) -> None:
        """ 
        Initializes a student profile using their identifying information
        along with their grades for each assignment
        """

        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        self.section = section

        self.grades = {}

    def add_grade(self, assignment_title: str, grade: float) -> None:
        """
        Adds a grade for an assignment to the student's profile

        Parameters:
            assignment_title (str): The title of the assignment
            grade (float): The grade for the assignment

        Returns:
            None
        """

        self.grades[assignment_title] = grade

    def get_grade(self, assignment_title: str) -> float:
        """
        Returns the grade for an assignment

        Parameters:
            assignment_title (str): The title of the assignment

        Returns:
            float: The grade for the assignment
        """
        return self.grades[assignment_title]
    
    def get_name(self) -> str:
        """
        Returns the student's full name

        Parameters:
            None

        Returns:
            str: The student's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_user_id(self) -> str:
        """
        Returns the student's user ID

        Parameters:
            None

        Returns:
            str: The student's user ID
        """
        return self.user_id
    
    def get_section(self) -> str:
        """
        Returns the student's section

        Parameters:
            None

        Returns:
            str: The student's section
        """
        return self.section
    
    def get_grades(self) -> dict:
        """
        Returns the student's grades for each assignment

        Parameters:
            None

        Returns:
            dict: A dictionary of assignment titles and their corresponding grades
        """
        return self.grades
    
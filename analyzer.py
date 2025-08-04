import random
import plotly.express as px
from collections import Counter
from student import Student
import polars as pl

class Analyzer:
    def __init__(self, student_data: list[Student], assignments: list[str]) -> None:
        """
        Initializes the analyzer with the student data

        Parameters:
            student_data (list[Student]): The list of student data
            assignments (list[str]): The list of assignment titles

        Returns:
            None
        """

        self.student_data = student_data
        self.assignments = assignments
        self.assignment_rankings = {}
        self.box_plots = {}
        self.histograms = {}
        self.grade_distributions = {}
        self.basic_statistics = {}

        self.random_names = {}
        self.anonymized_assignment_rankings = {}

        self.create_random_names()
        self.rank_students()
        self.make_basic_statistics()
        self.make_grade_distribution()
        self.make_box_plots()
        self.make_histograms()

    def create_random_names(self) -> None:
        """
        Creates random names for the students

        Parameters:
            None

        Returns:
            None
        """
        
        numbers_available = [str(i) for i in range(1, 1000)]
        random.shuffle(numbers_available)
        self.random_names = {student.get_name(): numbers_available.pop() for student in self.student_data}

    def rank_students(self) -> None:
        """
        Ranks the students based on their grades for each assignment. A missing grade is treated as a -1.

        Parameters:
            None

        Returns:
            None
        """

        for student in self.student_data:
            for assignment in self.assignments:
                grade = str(student.get_grade(assignment))

                # If the grade is not a number, treat it as a -1
                if grade.count(".") > 1 or not grade.replace(".", "").isdigit():
                    grade = -1

                # Add the grade to the student's ranking
                if assignment not in self.assignment_rankings:
                    self.assignment_rankings[assignment] = {}
                    self.anonymized_assignment_rankings[assignment] = {}

                self.assignment_rankings[assignment][student.get_name()] = float(grade)

                # Add the anonymized name to the assignment rankings
                anonymized_name = f"{self.random_names[student.get_name()]}"
                self.anonymized_assignment_rankings[assignment][anonymized_name] = float(grade)

        # Sort the students by their grades for each assignment
        for assignment in self.assignments:
            self.assignment_rankings[assignment] = dict(sorted(self.assignment_rankings[assignment].items(), key=lambda x: x[1], reverse=True))
            self.anonymized_assignment_rankings[assignment] = dict(sorted(self.anonymized_assignment_rankings[assignment].items(), key=lambda x: x[1], reverse=True))

            # Extract the names and grades
            name_column = pl.Series(self.assignment_rankings[assignment].keys())
            grade_column = pl.Series(self.assignment_rankings[assignment].values())
            section_column = pl.Series([student.get_section() for student in self.student_data if student.get_name() in name_column])

            # Convert grades to strings for formatting
            grade_column = grade_column.cast(pl.Utf8)

            # Create a dataframe
            self.assignment_rankings[assignment] = pl.DataFrame({"Name": name_column, "Grade": grade_column, "Section": section_column})

            # Do the same for the anonymized assignment rankings
            name_column = pl.Series(self.anonymized_assignment_rankings[assignment].keys())
            grade_column = pl.Series(self.anonymized_assignment_rankings[assignment].values())

            # Convert grades to strings for formatting
            grade_column = grade_column.cast(pl.Utf8)

            # Create a dataframe
            self.anonymized_assignment_rankings[assignment] = pl.DataFrame({"Name": name_column, "Grade": grade_column})

    def get_students_with_grade(self, assignment: pl.DataFrame) -> pl.DataFrame:
        """
        Returns a copy of the assignment rankings with only the students who have a grade

        Parameters:
            assignment (pl.DataFrame): The assignment rankings

        Returns:
            pl.DataFrame: The assignment rankings with only the students who have a grade
        """

        return assignment.filter(pl.col("Grade") != "-1.0")
    
    def get_students_without_grade(self, assignment: pl.DataFrame) -> pl.DataFrame:
        """
        Returns a copy of the assignment rankings with only the students who do not have a grade
        """

        new_df = assignment.filter(pl.col("Grade") == "-1.0")

        # Remove the grade column
        new_df = new_df.drop("Grade")

        return new_df
    
    def make_basic_statistics(self) -> None:
        """
        Returns the basic statistics of the grades for an assignment

        Parameters:
            None

        Returns:
            dict: The basic statistics
        """

        for assignment in self.assignments:
            cleaned_assignment_rankings = self.get_students_with_grade(self.assignment_rankings[assignment])
            
            # Extract just the grade column
            grade_column = cleaned_assignment_rankings["Grade"]

            # Convert from strings to floats
            grade_column = grade_column.cast(pl.Float64)

            # Calculate the mean, median, and standard deviation
            mean = grade_column.mean()
            median = grade_column.median()
            std = grade_column.std()
            data_min = grade_column.min()
            data_max = grade_column.max()

            # Calculate 25th, 50th, and 75th percentiles
            q1 = grade_column.quantile(0.25)
            q2 = grade_column.quantile(0.50)
            q3 = grade_column.quantile(0.75)
            
            # Create a dataframe
            self.basic_statistics[assignment] = pl.DataFrame({"Mean": mean, "Median": median, "Standard Deviation": std, "Minimum": data_min, "Maximum": data_max, "25th Percentile": q1, "50th Percentile": q2, "75th Percentile": q3})

    def get_basic_statistics(self) -> dict:
        """
        Returns the basic statistics

        Parameters:
            None

        Returns:
            dict: The basic statistics
        """

        return self.basic_statistics.copy()
    
    def make_grade_distribution(self) -> None:
        """
        Make a grade distribution of the grades for each assignment

        Parameters:
            None

        Returns:
            None
        """

        self.grade_distributions = {}

        for assignment in self.assignments:
            cleaned_assignment_rankings = self.get_students_with_grade(self.assignment_rankings[assignment])
            grade_distribution = Counter(cleaned_assignment_rankings["Grade"])
            
            # Convert to a dataframe
            grade_distribution = pl.DataFrame(grade_distribution)
            self.grade_distributions[assignment] = grade_distribution

    def get_grade_distributions(self) -> dict:
        """
        Returns the grade distributions

        Parameters:
            None

        Returns:
            dict: The grade distributions
        """
        
        return self.grade_distributions.copy()

    def make_box_plots(self) -> None:
        """
        Make box plots of the grades for each assignment

        Parameters:
            None

        Returns:
            None
        """

        for assignment in self.assignments:
            cleaned_assignment_rankings = self.get_students_with_grade(self.assignment_rankings[assignment])
            fig = px.box(cleaned_assignment_rankings, y="Grade", color="Section")
            self.box_plots[assignment] = fig

    def get_box_plots(self) -> dict:
        """
        Returns the box plots

        Parameters:
            None

        Returns:
            dict: The box plots
        """

        return self.box_plots.copy()
    
    def make_histograms(self) -> None:
        """
        Make histograms of the grades for each assignment

        Parameters:
            None

        Returns:
            None
        """

        for assignment in self.assignments:
            cleaned_assignment_rankings = self.get_students_with_grade(self.assignment_rankings[assignment])
            fig = px.histogram(cleaned_assignment_rankings, x="Grade", color="Section", text_auto=True)
            self.histograms[assignment] = fig
    
    def get_histograms(self) -> dict:   
        """
        Returns the histograms

        Parameters:
            None

        Returns:
            dict: The histograms
        """

        return self.histograms.copy()

    def get_assignment_rankings_by_assignment(self, assignment: str, anonymized: bool) -> dict:
        """
        Returns the assignment rankings by assignment

        Parameters:
            assignment (str): The assignment to get the rankings for
            anonymized (bool): Whether to anonymize the names

        Returns:
            dict: The assignment rankings by assignment
        """

        if anonymized:
            return self.anonymized_assignment_rankings[assignment].clone()
        else:
            return self.assignment_rankings[assignment].clone()
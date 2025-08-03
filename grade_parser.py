import csv


class GradeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.assignments = []
        self.assignment_titles = []
        
        self.student_data = []

        self.parse_info()

    def parse_info(self):
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)

            # Get the header row
            header = next(reader)
            self.parse_assignments(header)

            # Get the student data

    def parse_assignments(self, header):
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

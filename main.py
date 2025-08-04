import streamlit as st
from analyzer import Analyzer
from grade_parser import GradeParser
import polars as pl


# Set page title
st.set_page_config(page_title="Canvas Grade Analyzer", layout="wide")

st.title("Canvas Grade Analyzer")
st.write("This requires a Canvas grade report file to work. You can download one by going to the course's Grades tab and clicking \"Export\" and then selecting \"Export Entire Gradebook\".")

# Create file uploader widget
uploaded_file = st.file_uploader(
    "Choose a CSV file", 
    type="csv",
    help="Select a CSV file from your computer"
)

# Initialize session state variables
if 'grade_parser' not in st.session_state:
    st.session_state.grade_parser = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None

# Check if a file has been uploaded
if uploaded_file is not None:
    # Only parse if it's a new file or we haven't parsed yet
    file_changed = (st.session_state.current_file_name != uploaded_file.name)
    need_to_parse = (st.session_state.grade_parser is None or file_changed)
    
    if need_to_parse:
        # Show processing message
        with st.spinner("Processing grade file..."):
            try:
                # Parse the CSV (only happens once per file)
                st.session_state.grade_parser = GradeParser(uploaded_file)
                
                # Create analyzer (only happens once per file)
                raw_assignment_titles = st.session_state.grade_parser.get_raw_assignment_titles()
                max_points = st.session_state.grade_parser.get_assignment_max_points()

                st.session_state.analyzer = Analyzer(
                    st.session_state.grade_parser.get_student_data(), 
                    raw_assignment_titles,
                    max_points
                )
                
                # Store current file name
                st.session_state.current_file_name = uploaded_file.name
                
                st.success("File processed successfully!")
                
            except Exception as e:
                st.error(f"Error reading file: {e.message}")
                st.write("Please make sure you uploaded a valid Canvas grade report file.")
                # Clear session state on error
                st.session_state.grade_parser = None
                st.session_state.analyzer = None
                st.session_state.current_file_name = None
                st.stop()  # Stop execution if there's an error
    
    # Show file info and controls if data has been parsed
    if st.session_state.grade_parser is not None:
        # Display file information
        file_size = uploaded_file.size

        # Have toggle for anonymizing the names
        anonymize = st.toggle("Anonymize names", value=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Filename:** {uploaded_file.name}")
        
        with col2:
            b_to_mb_ratio = 1 / (1024 * 1024)
            st.info(f"**File Size:** {file_size * b_to_mb_ratio:,.2f} MB")

        st.subheader("Assignment Analysis")
        
        # Assignment selector
        if st.session_state.analyzer is not None:
            assignments = st.session_state.grade_parser.get_assignment_titles()
            
            if assignments:
                selected_assignment = st.selectbox(
                    "Select an assignment to analyze:",
                    assignments,
                    key="assignment_selector"
                )
                
                if selected_assignment:
                    # Retrieve the raw assignment title
                    index = assignments.index(selected_assignment)
                    raw_assignment_title = st.session_state.grade_parser.get_raw_assignment_titles()[index]

                    # Show basic statistics
                    st.subheader("Basic Statistics")
                    st.dataframe(st.session_state.analyzer.get_basic_statistics()[raw_assignment_title])

                    # Show the rankings
                    st.subheader("Student Rankings")
                    raw_assignment_rankings = st.session_state.analyzer.get_assignment_rankings_by_assignment(raw_assignment_title, anonymize)
                    cleaned_assignment_rankings = st.session_state.analyzer.get_students_with_grade(raw_assignment_rankings)
                    st.dataframe(cleaned_assignment_rankings)

                    # Show the students without a grade
                    st.subheader("Students without a grade")
                    st.dataframe(st.session_state.analyzer.get_students_without_grade(raw_assignment_rankings))

                    # Show the grade distribution
                    st.subheader("Grade Distribution")
                    st.dataframe(st.session_state.analyzer.get_grade_distributions()[raw_assignment_title])

                    # Show the box plot
                    st.subheader("Box Plot")
                    st.plotly_chart(st.session_state.analyzer.get_box_plots()[raw_assignment_title])

                    # Show the histogram
                    st.subheader("Histogram")
                    st.plotly_chart(st.session_state.analyzer.get_histograms()[raw_assignment_title])
            
            else:
                st.warning("No assignments found in the uploaded file.")

else:
    # Clear session state when no file is uploaded
    if st.session_state.grade_parser is not None:
        st.session_state.grade_parser = None
        st.session_state.analyzer = None
        st.session_state.current_file_name = None
        st.rerun()  # Refresh to clear the interface
    
    st.info("Please upload a Canvas grade export CSV file to begin analysis.")


# Footer with MIT license
st.markdown("---")
st.caption("© 2025 Anthony Ha-Anh Pham | Licensed under [MIT](https://opensource.org/licenses/MIT) | View source code on [GitHub](https://github.com/RicePandaaaa/CanvasGradeAnalyzer)")
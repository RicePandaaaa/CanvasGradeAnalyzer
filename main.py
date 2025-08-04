import streamlit as st

from grade_parser import GradeParser

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

# Check if a file has been uploaded
if uploaded_file is not None:    
    # Try to read the CSV file
    try:
        # Read the CSV
        grade_parser = GradeParser(uploaded_file)

        # Extract filename
        filename = uploaded_file.name
        file_size = uploaded_file.size

        # Display file information
        st.success(f"File uploaded successfully!")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Filename:** {filename}")

        with col2:
            st.info(f"**File Size:** {file_size:,} bytes")
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        st.write("Please make sure you uploaded a valid Canvas grade report file.")


# Footer with MIT license
st.markdown("---")
st.caption("© 2025 Anthony Ha-Anh Pham | Licensed under [MIT](https://opensource.org/licenses/MIT) | View source code on [GitHub](https://github.com/RicePandaaaa/CanvasGradeAnalyzer)")
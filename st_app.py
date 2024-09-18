import streamlit as st
import pandas as pd
from master_data import create_reports
from PIL import Image

gps_data = pd.read_csv("utils/GPS_master.csv")

sample_booking_data = pd.read_csv('utils/sample.csv')

# Streamlit sidebar
option = st.sidebar.radio("Select an option", ["Report on ID", "Upload Excel", "Help"])

# Report on ID
if option == "Report on ID":
    st.title("Input Data")

    # First row: ID and Pickup Date
    col1, col2 = st.columns(2)
    with col1:
        id_input = st.text_input("Enter ID")
        if id_input:
            id_value = id_input
        else:
            id_value = None

    with col2:
        pickup_time = st.date_input("Select Pickup Date", value=pd.to_datetime("2024-06-03"))

    # Second row: Pickup Time and Total Hours
    col3, col4 = st.columns(2)
    with col3:
        pickup_hour = st.time_input("Select Pickup Time", value=pd.to_datetime("09:30").time())
    with col4:
        total_hrs = st.time_input("Total Time", value=pd.to_datetime("08:00").time())

    col5,col6 = st.columns(2)
    with col5:
        cab_no = st.text_input("Cab No.")
    with col6:
        total_km = st.text_input("Total km's")

    # Combine date and time
    pickup_datetime = pd.to_datetime(pickup_time.strftime("%d %b %Y") + " " + pickup_hour.strftime("%H:%M"))

    # Convert to desired format
    pickup_time_str = pickup_datetime.strftime("%d %b %Y %H:%M")

    # Convert total_hrs to a string in HH:MM format
    total_hrs_str = total_hrs.strftime("%H:%M")

    # Button to create DataFrame and generate the report
    if st.button("Create Report"):
        if id_value is not None:
            # Create DataFrame
            df = pd.DataFrame({
                "ID": [id_value],
                "PICKUP TIME": [pickup_time_str],
                "Total Hrs": [total_hrs_str]
            })

            # Generate the report and save the image
            create_reports(df, gps_data,duty_date=pickup_time,cab_no=cab_no,total_kms=total_km,tota_hrs=total_hrs)

            # Generate the image filename
            image_filename = f'imgs/gr_{id_input}.jpg'

            # Display the image
            st.image(image_filename, caption='Generated Report', use_column_width=True)

            # Provide a download button for the image
            with open(image_filename, "rb") as file:
                btn = st.download_button(
                    label="Download Image",
                    data=file,
                    file_name=image_filename,
                    mime="image/png"
                )
        else:
            st.error("Please enter a valid ID.")

# Upload Excel option
elif option == "Upload Excel":
    st.title("Upload Excel or CSV File")
    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "xls", "csv"])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df_uploaded = pd.read_csv(uploaded_file)
        else:
            df_uploaded = pd.read_excel(uploaded_file)
        
        # Process the uploaded file with the create_reports function
        create_reports(df_uploaded, gps_data)
        
        # Provide download button for the ZIP file
        zip_filename = "imgs/imgs.zip"
        try:
            with open(zip_filename, "rb") as zip_file:
                btn = st.download_button(
                    label="Download ZIP",
                    data=zip_file,
                    file_name="images.zip",
                    mime="application/zip"
                )
        except FileNotFoundError:
            st.error("ZIP file not found. Please ensure the file exists.")

        # Additional processing can be done here...
elif option == "Help":
    st.title("Help")
    st.subheader("The format of input Excel and the column names is given below.")
    
    # Display the first few rows of the sample data
    st.write(sample_booking_data.head(3))

    # Show each column name in an adjustable grid format with a copy-friendly display
    st.subheader("Column Names")

    cols = st.columns(len(sample_booking_data.columns))  # Create a column for each column name
    for idx, col in enumerate(sample_booking_data.columns):
        cols[idx].code(col)  # Displays the column name in a code block, easy to copy





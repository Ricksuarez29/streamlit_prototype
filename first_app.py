import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import base64
import altair as alt

# Path to the saved logo image
logo_path = r"C:\Users\ochix\Desktop\MSc BA Esade\Term 2\PPDAI\prototype_streamlit\logos\logo.png"

# Center the logo using columns
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_path, width=250) 

# Define the folder path and logo filenames
folder_path = r"C:\Users\ochix\Desktop\MSc BA Esade\Term 2\PPDAI\prototype_streamlit\logos"
logo_files = ["audi.png", "bmw.png", "honda.png", "mercedes.png", "toyota.png"]

# Function to get the base64 encoded version of the image. Did this because the pictures were not showing properly.
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Generate the HTML for the logos with unique classes
logo_html = ""
for i, logo in enumerate(logo_files):
    logo_base64 = get_image_base64(os.path.join(folder_path, logo))
    logo_html += f'''
    <img class="logo-{i}" src="data:image/png;base64,{logo_base64}" alt="{logo.split(".")[0]}" />
    '''

# Title of the web app with custom CSS to fit on one line
st.markdown(
    """
    <style>
    .title-container {
        display: flex;
        justify-content: center;
        width: 100%;
        box-sizing: border-box;
    }
    .title {
        font-size: 46px;  /* Adjust the font size as needed */
        white-space: nowrap;  /* Prevent the title from wrapping */
    }
    </style>
    <div class="title-container">
        <h1 class="title">CarGuru Pro: Know Your Ride’s Worth</h1>
    </div>
    """,
    unsafe_allow_html=True
)
# Custom CSS for background color
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(45deg, #ffafbd, #ffc3a0, #ff9a9e, #fad0c4, #fad0c4);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    </style>

    """,
    unsafe_allow_html=True
)

# Custom CSS for sidebar styling
st.markdown(
    """
    <style>
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #2c3e50;  /* Dark grey background */
        color: white;  /* White text */
    }

    /* Ensure all text within the sidebar is white */
    [data-testid="stSidebar"] * {
        color: white;  /* Ensures all text inside the sidebar is white */
    }

    /* Change the font and padding of the sidebar elements */
    [data-testid="stSidebar"] .css-1d391kg {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.2em;  /* Increase font size */
        padding: 10px 20px;
    }

    /* Customize the appearance of inputs inside the sidebar */
    [data-testid="stSidebar"] .stButton, [data-testid="stSidebar"] .stTextInput, 
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stCheckbox {
        border-radius: 5px;
        background-color: #34495e;  /* Slightly lighter grey background */
        color: white;
    }

    /* Customize the appearance of sliders */
    [data-testid="stSidebar"] .stSlider {
        color: white;  /* White text for sliders */
    }

    /* Change text color for selected options in selectbox and multiselect */
    [data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        color: black;  /* Black text for selected options in selectbox */
    }

    [data-testid="stSidebar"] .stMultiSelect > div > div > div > div {
        color: black;  /* Black text for selected options in multiselect */
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\ochix\Desktop\MSc BA Esade\Term 2\PPDAI\prototype_streamlit\car_price_dataset.csv")
    return df

data = load_data()

# Create tabs
tab1, tab2 = st.tabs(["Car Brands Info", "Check your ideal price!"])

### DATASET AND GRAPHS TAB
# Tab 1: Dataset and Filtering
with tab1:
    
    # Sidebar Filters
    st.sidebar.title("Filters")

    # Filters with "All" option
    brand = st.sidebar.selectbox("Select Brand", options=["All"] + list(data['Brand'].unique()))
    model_options = data[data['Brand'] == brand]['Model'].unique() if brand != "All" else data['Model'].unique()
    model = st.sidebar.selectbox("Select Model", options=["All"] + list(model_options))
    fuel_type = st.sidebar.multiselect("Select Fuel Type", options=["All"] + list(data['Fuel_Type'].unique()))
    transmission = st.sidebar.radio("Select Transmission", options=["All"] + list(data['Transmission'].unique()))
    year_range = st.sidebar.slider("Select Year Range", int(data['Year'].min()), int(data['Year'].max()), (data['Year'].min(), data['Year'].max()))
    
    # Apply filters dynamically
    filtered_data = data.copy()
    if brand != "All":
        filtered_data = filtered_data[filtered_data['Brand'] == brand]

    if model != "All":
        filtered_data = filtered_data[filtered_data['Model'] == model]

    if "All" not in fuel_type and len(fuel_type) > 0:
        filtered_data = filtered_data[filtered_data['Fuel_Type'].isin(fuel_type)]

    if transmission != "All":
        filtered_data = filtered_data[filtered_data['Transmission'] == transmission]

    filtered_data = filtered_data[filtered_data['Year'].between(year_range[0], year_range[1])]

    filtered_data['Year'] = filtered_data['Year'].apply(lambda x: '{:.0f}'.format(x))

    # Calculate metrics based on the filtered data
    mean_price = filtered_data['Price'].mean()
    amount_of_cars = len(filtered_data)
    amount_of_models = filtered_data['Model'].nunique()
    average_mileage = filtered_data['Mileage'].mean()

    # Display metrics using st.metric
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Mean Price", value=f"${mean_price:,.2f}")
        st.metric(label="Amount of Cars", value=amount_of_cars)
    with col2:
        st.metric(label="Amount of Models", value=amount_of_models)
        st.metric(label="Average Mileage", value=f"{average_mileage:,.2f} km")

    # Using st.expander to display the updated table dynamically
    with st.expander("## Full Table of Cars to Analyze (Click to expand)"):
        st.write("#### Complete Information")
        st.dataframe(filtered_data)

        st.write(f"There are {len(filtered_data)} options of cars to analyze.")


    
    # Graph 1: Mean Price by Fuel Type and Transmission
    st.write("### Mean Price by Fuel Type and Transmission")

    # Mean Price by Fuel Type (ignore Fuel_Type filter)
    unfiltered_for_fuel = data.copy()

    if brand != "All":
        unfiltered_for_fuel = unfiltered_for_fuel[unfiltered_for_fuel['Brand'] == brand]

    if model != "All":
        unfiltered_for_fuel = unfiltered_for_fuel[unfiltered_for_fuel['Model'] == model]

    if transmission != "All":
        unfiltered_for_fuel = unfiltered_for_fuel[unfiltered_for_fuel['Transmission'] == transmission]

    unfiltered_for_fuel = unfiltered_for_fuel[unfiltered_for_fuel['Year'].between(year_range[0], year_range[1])]

    mean_price_fuel = unfiltered_for_fuel.groupby("Fuel_Type")["Price"].mean().reset_index()
    fuel_chart = alt.Chart(mean_price_fuel).mark_bar().encode(
        x=alt.X("Fuel_Type", title="Fuel Type"),
        y=alt.Y("Price", title="Mean Price"),
        color=alt.Color('Fuel_Type', scale=alt.Scale(scheme='dark2'), legend=None),  # Custom bar colors without legend
        tooltip=["Fuel_Type", "Price"]
    ).properties(
        title="Mean Price by Fuel Type",
        width=265,
        height=210
    )

    # Mean Price by Transmission (ignore Transmission filter)
    unfiltered_for_transmission = data.copy()

    if brand != "All":
        unfiltered_for_transmission = unfiltered_for_transmission[unfiltered_for_transmission['Brand'] == brand]

    if model != "All":
        unfiltered_for_transmission = unfiltered_for_transmission[unfiltered_for_transmission['Model'] == model]

    if "All" not in fuel_type and len(fuel_type) > 0:
        unfiltered_for_transmission = unfiltered_for_transmission[unfiltered_for_transmission['Fuel_Type'].isin(fuel_type)]

    unfiltered_for_transmission = unfiltered_for_transmission[unfiltered_for_transmission['Year'].between(year_range[0], year_range[1])]

    mean_price_trans = unfiltered_for_transmission.groupby("Transmission")["Price"].mean().reset_index()
    trans_chart = alt.Chart(mean_price_trans).mark_bar().encode(
        x=alt.X("Transmission", title="Transmission"),
        y=alt.Y("Price", title="Mean Price"),
        color=alt.Color('Transmission', scale=alt.Scale(scheme='dark2'), legend=None),  # Custom bar colors without legend
        tooltip=["Transmission", "Price"]
    ).properties(
        title="Mean Price by Transmission",
        width=265,
        height=210
    )

    # Combine the charts horizontally
    combined_chart = (fuel_chart | trans_chart).configure(
        background='#1e1e1e',  # Dark background for the combined chart container
        axis={
            'labelColor': 'white',
            'titleColor': 'white',
            'labelAngle': -45  # Rotate labels diagonally
        },
        title={
            'fontSize': 20,
            'anchor': 'middle',
            'color': 'white'
        },
        view={
            'stroke': None  # Remove the border around the chart
        }
    )

    # Display the charts side by side
    st.altair_chart(combined_chart)

    # Graph 2: Mean Price vs. Year (Filtered by All Features Except Year)
    st.write("### Mean Price vs. Year (Trends)")

    # Apply all filters except the year
    filtered_for_plot = filtered_data.copy()  # Use the filtered data from Tab 1

    # Group the data by Year and calculate the mean price
    mean_price_year_filtered = (
        filtered_for_plot.groupby("Year")["Price"].mean().reset_index()
    )

    # Create the Altair chart
    year_chart_filtered = alt.Chart(mean_price_year_filtered).mark_line(color='orange', point=alt.OverlayMarkDef(color='orange')).encode(
        x=alt.X("Year", title="Manufacturing Year"),
        y=alt.Y("Price", title="Mean Price"),
        tooltip=["Year", "Price"]
    ).properties(
        title="Mean Price vs. Year (Filtered)",
        width=700,
        height=400
    ).configure(
        background='#1e1e1e',  # Dark background for the chart
        axis={
            'labelColor': 'white',
            'titleColor': 'white',
            'labelAngle': -45  # Rotate labels diagonally
        },
        title={
            'fontSize': 20,
            'anchor': 'middle',
            'color': 'white'
        },
        view={
            'stroke': None  # Remove the border around the chart
        }
    )

    # Display the chart
    st.altair_chart(year_chart_filtered)


### MODEL AND PREDICTION TAB
# Load the trained model
model = joblib.load(r"C:\Users\ochix\Desktop\MSc BA Esade\Term 2\PPDAI\prototype_streamlit\rf_model.pkl")

brand_websites = {
    'Audi': 'https://www.audi.com',
    'BMW': 'https://www.bmw.com',
    'Honda': 'https://www.honda.com',
    'Mercedes': 'https://www.mercedes-benz.com',
    'Toyota': 'https://www.toyota.com',
    'Ford': 'https://www.ford.com',
    'Chevrolet': 'https://www.chevrolet.com',
    'Kia': 'https://www.kia.com',
    'Volkswagen': 'https://www.vw.com',
    'Hyundai': 'https://www.hyundai.com',
}

# Tab 2: Prediction
with tab2:
    # User Inputs
    st.markdown("<h2 style='text-align: center;'>Get the Best Price for Your Used Car</h2>", unsafe_allow_html=True)

    # Line 1: Brand and Model
    col1, col2 = st.columns(2)
    with col1:
        user_brand = st.selectbox("Brand", options=data['Brand'].unique())
    with col2:
        user_model = st.selectbox(
            "Model", options=data[data['Brand'] == user_brand]['Model'].unique()
        )

    # Line 2: Fuel Type and Transmission
    col3, col4 = st.columns(2)
    with col3:
        user_fuel = st.selectbox("Fuel Type", options=data['Fuel_Type'].unique())
    with col4:
        user_transmission = st.radio(
            "Transmission", options=["Manual", "Semi-Automatic", "Automatic"]
        )

    # Line 3: Year and Engine Size
    col5, col6 = st.columns(2)
    with col5:
        user_year = st.number_input(
            "Year", min_value=int(data['Year'].min()), max_value=int(data['Year'].max()), value=2015
        )
    with col6:
        user_engine = st.number_input(
            "Engine Size (L)", min_value=0.5, max_value=10.0, value=2.0
        )

    # Line 4: Mileage and Number of Doors
    col7, col8 = st.columns(2)
    with col7:
        user_mileage = st.number_input("Mileage (km)", min_value=0, value=50000)
    with col8:
        user_doors = st.slider("Number of Doors", 2, 5, 4)

    # Line 5: Number of Previous Owners
    user_owners = st.slider("Number of Previous Owners", 0, 5, 1)

    # Prepare input for the model
    input_data = pd.DataFrame({
        'Brand': [user_brand],
        'Model': [user_model],
        'Fuel_Type': [user_fuel],
        'Transmission': [user_transmission],
        'Year': [user_year],
        'Engine_Size': [user_engine],
        'Mileage': [user_mileage],
        'Doors': [user_doors],
        'Owner_Count': [user_owners]
    })

    # Make prediction
    try:
        prediction = model.predict(input_data)[0]
        # Display prediction
        st.write("### Predicted Price:")
        st.success(f"${prediction:,.2f}")

        # Add additional information
        # Filter dataset to find similar cars
        year_min = user_year - 3
        year_max = user_year + 3

        # Ensure year_min and year_max are within dataset range
        year_min = max(year_min, int(data['Year'].min()))
        year_max = min(year_max, int(data['Year'].max()))

        similar_cars = data[
            (data['Brand'] == user_brand) &
            (data['Model'] == user_model) &
            (data['Year'].between(year_min, year_max))
        ]
        

        num_similar_cars = len(similar_cars)
        # Format the 'Year' column
        similar_cars['Year'] = similar_cars['Year'].apply(lambda x: '{:.0f}'.format(x))

        st.write(f"The recommended value to sell your car is **${prediction:,.2f}**, and there are **{num_similar_cars}** cars of that model sold in the closest years.")

        # Get the brand's website URL
        brand_link = brand_websites.get(user_brand, None)

        # Display the message with the link if available
        if brand_link:
            st.write(f"In case you want to check the actual price of the model, follow the brand's link: [{user_brand} Official Website]({brand_link})")
        else:
            st.write("Brand website not available.")

        # Display a small dataframe with examples


        with st.expander("## Check similar Cars (Click to expand)"):
            st.write("#### Similar Cars in the Market:")
            st.dataframe(similar_cars)



    except Exception as e:
        st.error(f"Model prediction failed: {e}")


# HTML and CSS to display logos at the bottom of the page
st.markdown(
    f"""
    <style>
    body {{
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        justify-content: space-between;
    }}
    .main {{
        flex-grow: 1;
    }}
    .logo-container {{
        display: flex;
        justify-content: space-around;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        margin-top: 20px;
        position: fixed;
        bottom: 0;
        left: 0;
        background-color: white;
        padding: 5px 0;  /* Adjusted padding to take up less space */
    }}
    .logo-container img {{
        height:30px;  /* Reduced height to make logos smaller */
        width: auto;
        margin: 0 5px;  /* Reduced margin to ensure all logos fit */
    }}
    </style>
    <div class="logo-container">
        {logo_html}
    </div>
    """,
    unsafe_allow_html=True
)




# streamlit run first_app.py
import streamlit as st
import pandas as pd
import numpy as np

st.title('Pressure vs Flow Analysis')

# Custom CSS
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    .stTextInput, .stButton, .stSelectbox {
        font-size: 18px;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'selected_steps' not in st.session_state:
    st.session_state.selected_steps = []
if 'stats' not in st.session_state:
    st.session_state.stats = {}
if 'combined_stats' not in st.session_state:
    st.session_state.combined_stats = {}
if 'round' not in st.session_state:
    st.session_state.round = 0
if 'add_more' not in st.session_state:
    st.session_state.add_more = False
if 'step_names' not in st.session_state:
    st.session_state.step_names = {}
if 'combined_names' not in st.session_state:
    st.session_state.combined_names = {}

# Upload a single CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file:
    try:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)
        data['Source File'] = uploaded_file.name  # Add a column to identify the source file

        if 'Step Name / Description' not in data.columns:
            st.error("The uploaded CSV file does not contain the required 'Step Name / Description' column.")
        else:
            st.write("Data Preview:")
            st.write(data.head(10))  # Display first 10 rows

            # Function to analyze selected steps
            def analyze_steps(selected_steps):
                combined_data = pd.DataFrame()
                for selected_step in selected_steps:
                    step_data = data[data['Step Name / Description'] == selected_step].copy()  # Create a copy of the DataFrame slice
                    step_data = step_data.fillna(0)  # Replace NaNs with 0 to avoid RuntimeWarning
                    combined_data = pd.concat([combined_data, step_data])

                    # Calculate individual statistics for each step
                    step_stats = {}
                    for col in step_data.columns:
                        if pd.api.types.is_numeric_dtype(step_data[col]) and not pd.api.types.is_bool_dtype(step_data[col]):
                            step_stats[col] = {
                                'Min': step_data[col].min(),
                                'Max': step_data[col].max(),
                                'Average': step_data[col].mean(),
                                'Standard deviation': step_data[col].std(),
                                'Delta': step_data[col].max() - step_data[col].min()
                            }
                    st.session_state.stats[selected_step] = step_stats

                # Calculate combined statistics for the selected steps
                combined_stats = {}
                for col in combined_data.columns:
                    if pd.api.types.is_numeric_dtype(combined_data[col]) and not pd.api.types.is_bool_dtype(combined_data[col]):
                        combined_stats[col] = {
                            'Min': combined_data[col].min(),
                            'Max': combined_data[col].max(),
                            'Average': combined_data[col].mean(),
                            'Standard deviation': combined_data[col].std(),
                            'Delta': combined_data[col].max() - combined_data[col].min()
                        }
                combined_name = f'Round {st.session_state.round + 1}'
                st.session_state.combined_stats[combined_name] = combined_stats

                # Store selected steps in session state
                st.session_state.selected_steps.extend(selected_steps)
                st.session_state.combined_names[combined_name] = combined_name

            # Select three step names/descriptions
            step_names = data['Step Name / Description'].unique()
            selected_steps = st.multiselect(f'Select Step Name / Description (select 3) - Round {st.session_state.round + 1}', step_names, max_selections=3)

            if len(selected_steps) == 3:
                if st.button('Analyze Steps'):
                    analyze_steps(selected_steps)
                    st.session_state.round += 1
                    st.session_state.add_more = True

            # Display the individual and combined statistics
            if st.session_state.stats or st.session_state.combined_stats:
                combined_stats_list = []
                for step, step_stats in st.session_state.stats.items():
                    new_step_name = st.text_input(f"Rename {step}", value=step)
                    st.session_state.step_names[step] = new_step_name
                    for col, stat in step_stats.items():
                        combined_stats_list.append({
                            'Step Name / Description': new_step_name,
                            'Column': col,
                            'Statistic': 'Min',
                            'Value': stat['Min']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_step_name,
                            'Column': col,
                            'Statistic': 'Max',
                            'Value': stat['Max']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_step_name,
                            'Column': col,
                            'Statistic': 'Average',
                            'Value': stat['Average']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_step_name,
                            'Column': col,
                            'Statistic': 'Standard deviation',
                            'Value': stat['Standard deviation']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_step_name,
                            'Column': col,
                            'Statistic': 'Delta',
                            'Value': stat['Delta']
                        })

                for round_name, step_stats in st.session_state.combined_stats.items():
                    new_combined_name = st.text_input(f"Rename {round_name}", value=round_name)
                    st.session_state.combined_names[round_name] = new_combined_name
                    for col, stat in step_stats.items():
                        combined_stats_list.append({
                            'Step Name / Description': new_combined_name,
                            'Column': col,
                            'Statistic': 'Min',
                            'Value': stat['Min']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_combined_name,
                            'Column': col,
                            'Statistic': 'Max',
                            'Value': stat['Max']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_combined_name,
                            'Column': col,
                            'Statistic': 'Average',
                            'Value': stat['Average']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_combined_name,
                            'Column': col,
                            'Statistic': 'Standard deviation',
                            'Value': stat['Standard deviation']
                        })
                        combined_stats_list.append({
                            'Step Name / Description': new_combined_name,
                            'Column': col,
                            'Statistic': 'Delta',
                            'Value': stat['Delta']
                        })

                combined_stats_df = pd.DataFrame(combined_stats_list)

                # Pivot the DataFrame to get the desired layout
                pivot_df = combined_stats_df.pivot_table(index=['Step Name / Description', 'Statistic'], columns=['Column'], values='Value')
                pivot_df.reset_index(inplace=True)

                # Display the pivot table with the first column frozen
                st.dataframe(pivot_df, use_container_width=True)

                # Customize file name
                file_name = "pressure_vs_time_statistics.csv"
                csv = pivot_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Download Pressure vs Time Statistics as CSV", data=csv, file_name=file_name, mime='text/csv')

            # Option to add more steps
            if st.session_state.add_more:
                if st.button('Add More Steps'):
                    st.session_state.add_more = False

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Please upload a CSV file.")
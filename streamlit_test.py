import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import time
import altair as alt
import openpyxl
import os

# # Disable XSRF protection (only do this if your app is running locally and not exposed to the internet)
# st.set_option('server.enableXsrfProtection', False)

pd.set_option("styler.render.max_elements", 1000000)
imagepath = os.path.join(os.path.dirname(__file__), 'sample_Logo.jpeg')

# ======Progress bar anm======
def progress_bar_anm(text):
    bar = st.progress(0,text=text)
    for percent_complete in range(100):
        time.sleep(0.01)
        bar.progress(percent_complete + 1,text=text)
    time.sleep(1)
    bar.empty()
# ======App Header Section======
st.set_page_config(layout="wide")
col1, col2 = st.columns([1,6])

# =======Using 'with' notation:======
st.divider()
with col1:
    st.image(image=imagepath,output_format="JPEG",width=110)
with col2:
    st.title("THE PROJECT QCx")
    
# ======Take user input -- the CSV file======
st.subheader("1. Upload CDT extract",help="Upload the .CSV CDT extract. Please ensure file size <200MB")
ui_col1,ui_col2,ui_col3 = st.columns([3,1,2])
# =====UI section for CSV upload
with ui_col1:
    upload_csv = st.file_uploader("",type="csv")
# =====UI for progress
with ui_col2:
    if upload_csv is not None:
        # ======Loading UI
        progress_bar_anm("CSV upload in progress")
        st.success(body="CSV uploaded successfully!",icon=":material/task_alt:")
    else:
        st.info("Please upload CSV",icon=":material/pending:")
with ui_col3:
    st.text("")
st.divider()
# ======Processing the CSV extract to a mainDF======
if upload_csv is not None:
    # ======Read the CSV file======
    main_df = pd.read_csv(upload_csv)
    # Taking only those columns required for Classic AvP 
    clean_df = main_df[["Asset Type","Asset Name"," Point Role", " Point Id"]]
    # cleaning df for one role - multiple points scenario
    grouped_df = clean_df.groupby(["Asset Type","Asset Name"," Point Role"])[" Point Id"].apply(lambda x: '|'.join(x)).reset_index()
        
    # Function to highlight cells containing a comma
    def highlight_commas(val):
        if '|' in str(val):
            return 'background-color: #f06543'  # Highlight cells with yellow background
        return ''

    # The AsstVsPoint classic view
    classic_view = grouped_df.pivot_table(index=["Asset Type","Asset Name"],columns=' Point Role',values=' Point Id', aggfunc=lambda x:x).reset_index()
    # Highlight cells with multiple values
    styled_classic_view = classic_view.set_index(["Asset Type","Asset Name"])
    styled_classic_view=styled_classic_view.style.applymap(highlight_commas)
    # DMS--Asset count donut_pie_chart
    asset_count_val = classic_view["Asset Type"].value_counts()

else:
    st.info("Awaiting inputs",icon=":material/pending:")

# ======Show Data Model summary======
st.subheader("2. Data Model Summary",help="Shows a high-level overview of the data model")
dms_col1,dms_col2= st.columns(2)
# =====DMS column 1
with dms_col1:
    # First Expander
    with st.expander(label="See Asset-wise breakup of model"):

        if upload_csv is not None:
            selection = alt.selection_multi(fields=['Asset Type'], bind='legend')
            # ======Create a donut chart with interactivity
            base = alt.Chart(classic_view,background="#343a40").mark_arc(innerRadius=180).encode(theta='count()',
                opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
                color=alt.Color('Asset Type:N',legend=alt.Legend(titleFontSize=14, labelFontSize=14,titleColor="#FFFFFF",labelColor="#FFFFFF")),
                tooltip=['Asset Type:N', 'count():Q']).properties(width='container',height=400)
            # ===Convert to html format===
            bar_chart = base.add_selection(selection)
            final_bar_chart = bar_chart.to_html()

            # ======Display the chart in Streamlit
            st.components.v1.html(f"""<div style="overflow-y: scroll; width=1000px ; height: 650px; padding: 0.05px;">
                {final_bar_chart}
            </div>""", height=450)
                
        else:
            st.info("Awaiting inputs",icon=":material/pending:")
    # Second Expander
    with st.expander(label="See Point distribution by Asset Type"):
        st.write("N/a coming soon")
# ======DMS column 2
with dms_col2:
    # ======Show point & equip summary
    if upload_csv is not None:
        pointCount_clean_df1 = len((clean_df[" Point Id"].to_list()))
        equipCount_clean_df1 = len(list(set(clean_df["Asset Name"].unique())))
        summary_data = {"Total Point Count":pointCount_clean_df1,"Total Asset Count":equipCount_clean_df1}
        pointCount_clean_df = st.dataframe(summary_data,use_container_width=True)
        assetTypeDistributn_table = st.dataframe(classic_view["Asset Type"].value_counts(),use_container_width=True,height=400)
        
    else:
       st.info("Awaiting inputs",icon=":material/pending:")

# with dms_col3:
#     st.write('')
# st.divider()
# ======introducing tabs======
# ======Classic AvP view======
st.subheader("3. Different Tabs")
tab1, tab2, tab3, tab4 = st.tabs(["Classic AvP view", "Point Role Analysis","QC Checklist","ZOOTR Analysis"])
with tab1:
    if upload_csv is not None:
        progress_bar_anm("Loading Asset Vs Point view please wait..")
        st.write(styled_classic_view)
# ======Point detail analysis======

with tab2:
    pa_col1, pacol2, pacol3 = st.columns(3)
    pointRole_list = []
    if upload_csv is not None:
        pointRole_list = styled_classic_view.columns.to_list()

    with pa_col1:
        if upload_csv is not None:
            # ======Adding filter======
            pointRole_list_1st = pointRole_list
            pointRole_list_1st.insert(0,"Select 1st point role")
            pointRole_filter1 = st.selectbox(label="Select point role-1",options=pointRole_list_1st)
        else:
            pointRole_filter1 = st.selectbox(label="Select point role-1",options=[])

    with pacol2:
        if upload_csv is not None:
            # ======Adding filter=======
            pointRole_list_2nd = pointRole_list
            pointRole_list_2nd.insert(0,"Select 2nd point role")
            pointRole_filter2 = st.selectbox(label="Select point role-2",options=pointRole_list_2nd)
        else:
            pointRole_filter2 = st.selectbox(label="Select point role-2",options=[])
    
    # ======Hold till both point roles are selected======
    with pacol3:
        trigger_b = False
        
        if (upload_csv is not None) & (pointRole_filter1 is not 'Select point role-1') &(pointRole_filter2 is not 'Select point role-2'):
            btn = st.button("Analyze Point Pairs",type="primary",help="Click after both point roles are selected")
            if btn:
                trigger_b = True
        # ======The MAIN Merge======
    if (upload_csv is not None) & (pointRole_filter1 is not 'Select point role-1') &(pointRole_filter2 is not 'Select point role-2') & (trigger_b): 
    
        selected_pointRole1 = classic_view[["Asset Type","Asset Name",pointRole_filter1,pointRole_filter2]]
        
        condition1 = selected_pointRole1[pointRole_filter1].notna() & selected_pointRole1[pointRole_filter2].notna()
        condition2 = selected_pointRole1[pointRole_filter1].isna() & selected_pointRole1[pointRole_filter2].notna()
        condition3 = selected_pointRole1[pointRole_filter1].notna() & selected_pointRole1[pointRole_filter2].isna()
        
        # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
        selected_pointRole_pair = selected_pointRole1[condition1|condition2|condition3]
        final_selected_pointRole_pair = selected_pointRole_pair.style.applymap(highlight_commas)
        #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
            
    if trigger_b == True:
        progress_bar_anm('Point analysis in progress..')
        disp_selected = st.dataframe(final_selected_pointRole_pair,width=1000)


# ======QC Checklist======
with tab3:
    with st.expander("Point & Asset Naming Conventions"):
        st.write("somethin'")
    with st.expander("Assets containing 1 point records"):
        st.write("somethin'")

# ======ZOOTR Analysis
with tab4:
    with st.expander("Checks for comfortAsset()"):
        
        thisList = [n for n in range(1,11)]
        thatlist = st.multiselect(label="Select options",options=thisList)
        st.dataframe(thatlist)

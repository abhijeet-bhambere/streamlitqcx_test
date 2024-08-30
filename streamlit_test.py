import base64
import io
import string
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import time
import altair as alt
import os
# # Disable XSRF protection (only do this if your app is running locally and not exposed to the internet)
# st.set_option('server.enableXsrfProtection', False)
st.set_page_config(page_title="QCx Portal",layout="wide",page_icon = os.path.join(os.path.dirname(__file__), 'sample_Logo.jpeg'))
imagepath = os.path.join(os.path.dirname(__file__), 'sample_Logo.jpeg')
page_theme = st.get_option('theme.base')

qcreport_mark = [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
mcheck_selection = [None,"Passed","Failed","To be discussed"]
pd.set_option("styler.render.max_elements", 1000000)
# ===============================adding the sidebar=========================================
# st.markdown("<h2 id='section-2'>Section 2</h2>")
# st.write("Content for Section 2")
st.sidebar.title("NavTree")
st.sidebar.markdown('''[1. Upload CDT extract](#1-upload-cdt-extract-input)''',unsafe_allow_html=True)
st.sidebar.markdown('''[2. Data Model Summary](#2-data-model-summary-radar)''',unsafe_allow_html=True)
st.sidebar.markdown('''[3. QC Views](#3-qc-views-travel-explore)''',unsafe_allow_html=True)
st.sidebar.markdown('''[- QC Checkpoints](#asset-name-validation)''',unsafe_allow_html=True)
st.sidebar.markdown('''[- Classic AvP view](#classic-avp-view)''',unsafe_allow_html=True)
st.sidebar.markdown('''[4. Final QC Report](#4-final-qc-report-format-list-bulleted)''',unsafe_allow_html=True)

# st.page
# st.write(page_theme)
st.logo(image=imagepath)
# ======Progress bar anm======
# @st.cache_data()
def progress_bar_anm(text,sleeptime=0.01):
    bar = st.progress(0,text=text)
    for percent_complete in range(100):
        time.sleep(sleeptime)
        bar.progress(percent_complete + 1,text=text)
    time.sleep(1)
    bar.empty()
# ======App Header Section======

col1, col2,col3 = st.columns([1,3,5],vertical_alignment="center")

# ======App Footer Section======
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        font-size: 2px;
        color: rgb(163, 168, 184);
        text-align: right;
        padding: 1.5px;
        height: 20px;
    }
    </style>
    <div class="footer">
        <p>Created by, and for AOC</p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)

# =======Using 'with' notation:======
# st.divider()
# with col1:
#     st.image(image=imagepath,output_format="JPEG",width=110)
# with col2:
    # st.title("QCx Portal")
st.markdown('<h1 style="font-size:6em;font-weight:700;font-family:Helvetica;width:600px; background: -webkit-linear-gradient(15deg,#1dbde6, #f1515e); -webkit-background-clip: text ;-webkit-text-fill-color:transparent;margin: 0; padding: 0;">QC<i>x</i> Portal</h1>',unsafe_allow_html=True)
st.divider()
def sp_stream(msg,stimer=0.08):
            for char in msg.split(" "):
                yield char + " "
                time.sleep(stimer)

# ======================Help section=======================
with st.expander(label="Help content/ How to use",icon=":material/help:"):
    help_col1, help_col2 = st.columns(2)
    help_markdown1 = '''
    ## Step 1: 
    In first section, upload the CDT summary extract (the .CSV file) downloaded from your Admin Portal site.
    Whenever you want to upload a new CSV, **ensure you delete the previous CSV**.

    ## Step 2:
    Once CSV upload is successful, navigate to Sections 2 for data model summary. 
    OR head over to Section 3 that contains AssetVsPoint view and detailed CDT QC checks
    '''
    help_markdown2 = '''
    ## Step 3:
    1. In the 'Classic AvP View' tab user can view the AssetVsPoint view that we're all familiar with. Select the required Asset Type to view the Asset vs Point map.
    2. 'Standard Point Role Checks' maps all the **mandatory** point role combinations pre-configured (e.g. ZoneTempSensor-Sp ; SupplyFanCmd-Sts ; FanSpdCmd-Fbk etc.).\n
        Select the required point-combination to be checked & view all Assets with selected point role combination against it.\n
        Point role gaps can then be either addressed by analyst or shared as RFI to site team. 
    '''

    with help_col1:
        st.markdown(help_markdown1)
    with help_col2:
        st.markdown(help_markdown2)    


# ======Take user input -- the CSV file======

st.header("1. Upload CDT extract :material/input:")
ui_col1,ui_col2,ui_col3 = st.columns([3,1,2],vertical_alignment="center")
# =====UI section for CSV upload
with ui_col1:
    upload_csv = st.file_uploader("",type="csv")
# =====UI for progress
with ui_col2:
    st.write("")
    st.write("")
    if upload_csv is not None:
        # ======Loading UI
        progress_bar_anm("CSV upload in progress",sleeptime=0.01)
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
    clean_df = main_df[["Asset Type","Asset Name"," Point Role", " Point Label"]]
    # cleaning df for one role - multiple points scenario
    grouped_df = clean_df.groupby(["Asset Type","Asset Name"," Point Role"])[" Point Label"].apply(lambda x: '|'.join(x)).reset_index()
        
    # Function to highlight cells containing a comma/separator
    def highlight_commas(val):
        if '|' in str(val):
            return 'background-color: #e76f51'  # Highlight cells for multiple points-single role
        elif pd.isnull(val) and page_theme=='dark':
            return 'background-color: #161b33'
        elif pd.isnull(val) and page_theme=='light':
            return 'background-color: #ccc9dc'
        return ''
    # Function to add warning for rows with multiple points scenario
    def add_warning_icon(row):
        if any('|' in str(val) for val in row):
            return '⚠️'  # Warning icon (can be customized)
        return ''
    # Function to add add warning for mpr + None
    def add_warning_icon1(row):
        if any('|' in str(val) for val in row) or any(pd.isnull(val) for val in row):
            return '⚠️'  # Warning icon (can be customized)
        
        return ''
    # The AsstVsPoint classic view
    classic_view = grouped_df.pivot_table(index=["Asset Type","Asset Name"],columns=' Point Role',values=' Point Label', aggfunc=lambda x:x).reset_index()
    # Highlight cells with multiple values
    styled_classic_view1 = classic_view.set_index(["Asset Type","Asset Name"])
    
    styled_classic_view=styled_classic_view1.style.map(highlight_commas)
    # DMS--Asset count donut_pie_chart
    asset_count_val = classic_view["Asset Type"].value_counts()

# else:
#     st.info("Awaiting inputs",icon=":material/pending:")

# ======Show Data Model summary======
st.header("2. Data Model Summary :material/radar:",help="Shows a high-level overview of the data model. Perform manual checks to verify whether model aligns with the scope discussed with site team during Kick-off.")

scope_msg2 = "Select 'Confirmed': if scope fully aligns with discussed scope."
scope_msg3 = "Select 'Not confirmed' if scope does not aligns with discussed scope & needs further clarificaiton. Add notes in final QC report."
scope_msg4 = "Select 'To be discussed' if configured data model deviates from the discussed scope. Add notes in final QC report."

# =====DMS column 1
# First Expander -- Asset-wise breakup

# summcol1,summcol2 = st.columns(2)
# with summcol1:
with st.expander(label="Asset-wise breakup of model"):
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
# Second Expander -- Point-by-AssetType breakup

with st.expander(label="Point distribution by Asset Type"):
    st.write(":construction: Work in progress ,coming soon :construction:")
# ======DMS column 2

    # ======Show point & equip summary pt.1====================================
with st.container(border=True):
    dmscol1,dmscol2 = st.columns(2)
    with dmscol1:
        st.subheader("Configured Point & Asset total")
        st.write("Check & confirm all Assets are configured as per scope")
        # ======Show point & equip summary pt.1
        if upload_csv is not None:
            pointCount_clean_df1 = len((clean_df[" Point Label"].to_list()))
            equipCount_clean_df1 = len(list(set(clean_df["Asset Name"].unique())))
            summary_data = {"Total Point Count":pointCount_clean_df1,"Total Asset Count":equipCount_clean_df1}
            pointCount_clean_df = st.dataframe(summary_data,use_container_width=True,height=300)
        else:
            st.info("Awaiting inputs",icon=":material/pending:")
        # ==============Manual checkbox for configured assets=====================
        mini1col1,mini1col2 = st.columns(2)
        with mini1col1:
            
                if 'selectbox1' not in st.session_state:
                    st.session_state.selectbox1 = None
                if upload_csv is not None:
                    st.session_state.selectbox1 = st.selectbox(label="Check configured Assets are as per scope:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox1))
                    if st.session_state.selectbox1 is not None:
                        qcreport_mark[7] = st.session_state.selectbox1
                else:
                    st.session_state.selectbox1 = None
        with mini1col2:   
            st.write("")
            manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
            if st.session_state.selectbox1 != None:
                manual_check.empty()
                st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
    
    with dmscol2:    
        # ==================================Show point & equip summary pt.2=====================================    
        st.subheader("See total configured Assets")
        st.write("See the list of Assets currently configured & confirmed in the data model")
        if upload_csv is not None:
            assetTypeDistributn_table = st.dataframe(classic_view["Asset Type"].value_counts(),use_container_width=True,height=300)
        else:
            st.info("Awaiting inputs",icon=":material/pending:")
        # ============================Manual checkbox for configured points======================================
        mini1col1,mini1col2 = st.columns(2)
        with mini1col1:
        
            if 'selectbox2' not in st.session_state:
                st.session_state.selectbox2 = None
            if upload_csv is not None:
                st.session_state.selectbox2 = st.selectbox(label="Check configured Points are as per scope:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox2))
                if st.session_state.selectbox2 is not None:
                    qcreport_mark[8] = st.session_state.selectbox1
            else: 
                st.session_state.selectbox2 = None
        with mini1col2:
            st.write("")
            manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
            if st.session_state.selectbox2 != None:
                manual_check.empty()
                st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
            # st.selectbox(label="Check configured Asset list",options=mcheck_selection,index=None)
    st.divider()
# ========================================================introducing tabs====================================================================
st.header("3. QC Views :material/travel_explore:",help="Check model map or go through each QC checkpoint")

# ======================Help section=======================
with st.expander(label="Help content/ How to use",icon=":material/help:"):
    qchelp_col1, qchelp_col2 = st.columns(2)
    qchelp_markdown1 = '''
    ##### QC CheckPoints: 
    This tab contains a series of checks that are either fully or semi-automated.\n
    For automated checks, QCx will automatically check & add final decision to the **Final QC Report**.\n
    For manual checks, QCx helps in faster decision-making by the analyst. Select appropriate 'Check Status' after review is conducted.
    '''
    qchelp_markdown2 = '''
    ##### Classic AvP View:
    The standard AssetVsPoint view that we're all used to, now with added detailed insights. 
    As always, select the Asset Type to view the Asset vs Point map for it.
    
    ##### Point Role analysis:
    While 'QC Checkpoints' tab covers Standard Point Roles from the QC checklist. In this tab analyst can manually select the point combination to identify & address the gaps.

    '''

    with qchelp_col1:
        st.markdown(qchelp_markdown1)
    with qchelp_col2:
        st.markdown(qchelp_markdown2)    
# =============================================================
tab1, tab3, tab2,tab4 = st.tabs(["QC CheckPoints","Classic AvP view","Point Role Analysis","ZOOTR Analysis"])
if upload_csv is None:
    st.info("Awaiting inputs",icon=":material/pending:")
# ==============================Classic AvP view====================================
with tab3:
    # if upload_csv is not None:
    #     progress_bar_anm("Loading Asset Vs Point view please wait..")
    st.subheader("classic AvP view")
    tab1col1, tab1col2 = st.columns([1,3])
    # =============Select the Asset Type & show AvP table==================
    with tab1col1:
        if upload_csv is not None:
            #for QCx2.0 sort this list in alphabetical order 
            all_assetTypes = main_df["Asset Type"].unique().tolist() 
            selected_assetType = st.multiselect(label='Select AssetType',options=all_assetTypes)
            # Selection logic for AssetType
            styled_classic_view1 = classic_view.set_index(["Asset Type","Asset Name"])
            styled_classic_view2 = styled_classic_view1
            selected_AvP = styled_classic_view1.loc[selected_assetType].dropna(axis=1,how='all')
            selected_AvP['STS']=selected_AvP.apply(add_warning_icon,axis=1)
            selected_AvP=selected_AvP.set_index('STS',append=True)
            # detect total None occurrences
            totalnulls_avp = selected_AvP.isnull().sum().sum()
            # detect many-points-one-role occurrences
            char = "|"
            mpsr_counts = selected_AvP.applymap(lambda x: char in str(x)).sum().sum()
            # selected_AvP_stats = selected_AvP.describe()
            final_AvP=selected_AvP.style.applymap(highlight_commas)

            avp_notif = f"The current selection {selected_assetType} shows a total of {selected_AvP.shape[1]} point roles for {selected_AvP.shape[0]} assets. There are {mpsr_counts} instances where >1 points are configured for a role. Sort by STS column to see these instances."
                   
    # Show AssetvPoint table for the selected AssetType
    with tab1col2:
        with st.container(border=True):
            if (upload_csv is not None) and len(selected_assetType)!=0:
                
                # ==============Manual checkbox for AvP=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox4' not in st.session_state:
                        st.session_state.selectbox4 = None
                    if upload_csv is not None:
                        st.session_state.selectbox4 = st.selectbox(label="Check if All points are configured as per License:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox4))
                        if st.session_state.selectbox4 is not None:
                            qcreport_mark[15] = st.session_state.selectbox1
                    else:
                        st.session_state.selectbox4 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox4 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
                st.write_stream(sp_stream(avp_notif))
            elif (upload_csv is not None) and len(selected_assetType)==0:
                st.info("Select one or more Asset Type from the filter",icon=":material/pending:")
    # ====Display the AvP table
    if (upload_csv is not None) and len(selected_assetType)!=0:
        progress_bar_anm("Loading Asset Vs Point view please wait..",sleeptime=0.01)
        st.write(final_AvP)
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
        condition4 = selected_pointRole1[pointRole_filter1].isna() & selected_pointRole1[pointRole_filter2].isna()
        
        # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
        selected_pointRole_pair = selected_pointRole1[condition1|condition2|condition3|condition4]
        final_selected_pointRole_pair = selected_pointRole_pair.style.applymap(highlight_commas)
        #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
            
    if trigger_b == True:
        progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
        disp_selected = st.dataframe(final_selected_pointRole_pair,width=1000)


# ======================QC Checklist============================
with tab1:
    special_chars = list(string.punctuation)
    allowed_chars = ["-","_"]
    special_chars = list(filter(lambda x: x not in allowed_chars,special_chars))
    # qc_checkBtn1 = st.button("Run QC Checks")
    # =========Logic for Equip Name checks
    #qc_checkBtn1 = st.button("Run QC Checks")
    # progress_bar_anm("Running checks..")
    # For asset name check
    with st.container(border=True):
        st.subheader("Asset name validation",help="Checks if Asset name contains special characters apart from '-' OR '_'")
        st.write("Checks to ensure Equipment Name cannot have special characters.(Except - and _)")
        # qc_checkBtn1 = st.button("Run QC Check")
        flist = []
        sc_col1,sc_col2 = st.columns([3,2])
        if (upload_csv is not None):
            # progress_bar_anm("Running checks..",sleeptime=0.01)
            # with st.status(label="Checking for Asset Names") as fstatus:
            with sc_col1:
                ntf1 = st.info("Checking for special characters in all Assets...")
                time.sleep(1)
                ntf1.empty()
                ntf2 = st.info("Only '-' & '_' allowed...")
                time.sleep(1)
                ntf2.empty()
                all_assets = main_df["Asset Name"].unique().tolist()
                for element in all_assets:
                    for char in special_chars:
                        if char in element:
                            fresult = f"'{element}' contains special character '{char}'."
                            flist.append(fresult)
                            break  # Stop checking further once a special character is found
                st.dataframe(data=flist,use_container_width=True)
            with sc_col2:
                with st.container(border=True):
                    if (upload_csv is not None):
                        if len(flist)>0:
                            assetName_errmsg = f":material/close: Special characters found in {len(flist)} Asset(s)."
                            st.write_stream(sp_stream(assetName_errmsg))
                            st.error(f":material/close: Ensure names DON'T contain special characters (except  _  or - )")
                            qcreport_mark[0] = "Failed"
                            
                        elif (flist ==[]):
                            qcreport_mark[0] = "Passed"
                            st.success(":material/check: Check complete! All asset names OK")
                        
   
    with st.container(border=True):     
        st.subheader("Assets with single points",help="Checks for Assets with only a single point in it. Only Meters are allowed")
        st.write("Check for assets with only One point Configured (Excluding Meters)")
        spcol1,spcol2 = st.columns([3,2])
        with spcol1:
            # qc_checkBtn2 = st.button("Run QC Check2")
            # if (upload_csv is not None):
               
            if (upload_csv is not None):
                spntf = st.info("Checking for Assets with only 1 point configured...")
                time.sleep(0.5)
                spntf.empty()
                singlePoint_assets1 = styled_classic_view1[styled_classic_view1.notnull().sum(axis=1)==1].dropna(axis=1,how='all')       
                if ("Electric Meter" in singlePoint_assets1.index):
                    singlePoint_assets = singlePoint_assets1.drop(index="Electric Meter").dropna(axis=1,how='all')
                    spntf1 = st.info("Excluding Electric meters from the check...")
                    time.sleep(0.5)
                    spntf1.empty()
                    # sp_warmsg1 = "Check if additional points are available in listag, else make a note in final QC report."
                else:
                    spntf1 = st.info("Only meters should be allowed...")
                    time.sleep(0.5)
                    spntf1.empty()
                    singlePoint_assets = singlePoint_assets1
                    sp_okmsg = f"There are {singlePoint_assets.shape[0]} assets with 1 point configuration. All assets are covered."
                    st.info(":material/check: Check complete!")
                st.dataframe(singlePoint_assets,use_container_width=True)
            

        with spcol2:        
                with st.container(border=True):
                    if (upload_csv is not None):
                        if len(singlePoint_assets)!=0:
                            sp_warmsg = f":material/warning: There are {singlePoint_assets.shape[0]} assets with only 1 point configured."
                            st.write_stream(sp_stream(sp_warmsg))
                            st.warning(f":material/warning: Check if additional points are available in listag, else make a note in final QC report.")
                            mini1col1,mini1col2 = st.columns(2)
                            with mini1col1:
                                if 'selectbox3' not in st.session_state:
                                    st.session_state.selectbox3 = None
                                if upload_csv is not None:
                                    st.session_state.selectbox3 = st.selectbox(label="Check Assets containig single points are Ok to proceed:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox3))
                                    if st.session_state.selectbox3 is not None:
                                        qcreport_mark[6] = st.session_state.selectbox3
                                else:
                                    st.session_state.selectbox3 = None
                            with mini1col2:
                                st.write(" ")
                                manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                                if st.session_state.selectbox3 != None:
                                    manual_check.empty()
                                    st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
            
                        else:
                            singlePoint_assets = singlePoint_assets1
                            sp_okmsg = f"There are {singlePoint_assets.shape[0]} assets with 1 point configuration. All assets are covered."
                            st.write_stream(sp_stream(sp_okmsg))
        # singlePoint_assetlist = singlePoint_assets
        # if (upload_csv is not None) & (qc_checkBtn):
        #     with st.expander("Assets containing 1 point records"):
        #         st.write("somethin'")
        #     with st.status("Downloading data...") as fstatus:
        #         st.write("Searching for data...")
        #         time.sleep(2)
        #         st.write("Found URL.")
        #         time.sleep(1)
        #         st.write("Downloading data...")
        #         time.sleep(1)
        #         fstatus.update(label="Complete!")
    with st.container(border=True):
        st.subheader("Point combination checks",help="Checks for sensor-setpoint / Cmd-Sts gaps.")
        st.write("This section performs checks at point-level that to find assets where either:1) Both point roles were configured. OR 2) One of the poit roles is not configured.",unsafe_allow_html=True)
        
        st.subheader("Check for ZoneTemp-SP:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        ztcol1,ztcol2 = st.columns([3,2])
        with ztcol1:
            if upload_csv is not None:
                if ("Zone Temperature" in styled_classic_view1.columns) & ("Zone Temperature Setpoint" in styled_classic_view1.columns):
                # ======The MAIN Merge====== 
                # pointRole_list = styled_classic_view.columns.to_list()
                    zoneTempCheck = classic_view[["Asset Type","Asset Name","Zone Temperature","Zone Temperature Setpoint"]]
                    
                    ztcondition1 = zoneTempCheck["Zone Temperature"].notna() & zoneTempCheck["Zone Temperature Setpoint"].notna()
                    ztcondition2 = zoneTempCheck["Zone Temperature"].isna() & zoneTempCheck["Zone Temperature Setpoint"].notna()
                    ztcondition3 = zoneTempCheck["Zone Temperature"].notna() & zoneTempCheck["Zone Temperature Setpoint"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    zoneTempCheck_pair = zoneTempCheck[ztcondition1|ztcondition2|ztcondition3]
                    zoneTempCheck_pair['STS']=zoneTempCheck_pair.apply(add_warning_icon1,axis=1)
                    zoneTempCheck_pair=zoneTempCheck_pair.set_index('STS',append=True)
                    zoneTempCheck_pair = zoneTempCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    zoneTempCheck_df = st.dataframe(zoneTempCheck_pair,width=1000,use_container_width=True)
                elif ("Zone Temperature" not in styled_classic_view1.columns):
                    st.warning("no point configured for ZoneTemp sensor role. Review model if point is available")
                elif ("Zone Temperature Setpoint" not in styled_classic_view1.columns):
                    st.warning("no point configured for ZoneTempSp role. Review model if point is available")

        
        with ztcol2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox5' not in st.session_state:
                        st.session_state.selectbox5 = None
                    if upload_csv is not None:
                        st.session_state.selectbox5 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox5),key="sb_1")
                        if st.session_state.selectbox5 is not None:
                            qcreport_mark[10] = st.session_state.selectbox5
                    else:
                        st.session_state.selectbox5 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox5 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
        st.subheader("Check for RATemp-SP:")
        rtcol1,rtcol2 = st.columns([3,2])
        with rtcol1:
            if upload_csv is not None:
                if ("Return Air Temperature" in styled_classic_view1.columns) & ("Return Air Temperature Setpoint" in styled_classic_view1.columns):
                # ======The MAIN Merge====== 
                # pointRole_list = styled_classic_view.columns.to_list()
                    raTempCheck = classic_view[["Asset Type","Asset Name","Return Air Temperature","Return Air Temperature Setpoint"]]
                    
                    rtcondition1 = raTempCheck["Return Air Temperature"].notna() & raTempCheck["Return Air Temperature Setpoint"].notna()
                    rtcondition2 = raTempCheck["Return Air Temperature"].isna() & raTempCheck["Return Air Temperature Setpoint"].notna()
                    rtcondition3 = raTempCheck["Return Air Temperature"].notna() & raTempCheck["Return Air Temperature Setpoint"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    raTempCheck_pair = raTempCheck[rtcondition1|rtcondition2|rtcondition3]
                    raTempCheck_pair['STS']=raTempCheck_pair.apply(add_warning_icon,axis=1)
                    raTempCheck_pair=raTempCheck_pair.set_index('STS',append=True)
                    raTempCheck_pair = raTempCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    raTempCheck_df = st.dataframe(raTempCheck_pair,width=1000)
                elif ("Return Air Temperature" not in styled_classic_view1.columns):
                    st.warning("no point configured for RATemp sensor role. Review model if point is available")
                elif ("Return Air Temperature Setpoint" not in styled_classic_view1.columns):
                    st.warning("no point configured for RATempSp role. Review model if point is available")
        with rtcol2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox6' not in st.session_state:
                        st.session_state.selectbox6 = None
                    if upload_csv is not None:
                        st.session_state.selectbox6 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox6))
                        if st.session_state.selectbox6 is not None:
                            qcreport_mark[11] = st.session_state.selectbox6
                    else:
                        st.session_state.selectbox6 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox6 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.subheader("Check for SAFanCmd-Sts:")
        sfcol1,sfcol2 = st.columns([3,2])
        with sfcol1:
            if upload_csv is not None:
                if ("Supply Air Fan On-Off Command" in styled_classic_view1.columns) & ("Supply Air Fan Status" in styled_classic_view1.columns):
                # ======The MAIN Merge====== 
                # pointRole_list = styled_classic_view.columns.to_list()
                    saFanCheck = classic_view[["Asset Type","Asset Name","Supply Air Fan On-Off Command","Supply Air Fan Status"]]
                    
                    condition1 = saFanCheck["Supply Air Fan On-Off Command"].notna() & saFanCheck["Supply Air Fan Status"].notna()
                    condition2 = saFanCheck["Supply Air Fan On-Off Command"].isna() & saFanCheck["Supply Air Fan Status"].notna()
                    condition3 = saFanCheck["Supply Air Fan On-Off Command"].notna() & saFanCheck["Supply Air Fan Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    safanCheck_pair = saFanCheck[condition1|condition2|condition3]
                    safanCheck_pair['STS']=safanCheck_pair.apply(add_warning_icon,axis=1)
                    safanCheck_pair=safanCheck_pair.set_index('STS',append=True)
                    saFanCheck_pair = safanCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    safanCheck_df = st.dataframe(saFanCheck_pair,width=1000)
                elif ("Supply Air Fan On-Off Command" not in styled_classic_view1.columns):
                    st.warning("no point configured for SAFanCmd role. Review model if point is available")
                elif ("Supply Air Fan Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for SAFansts role. Review model if point is available")
        with sfcol2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox7' not in st.session_state:
                        st.session_state.selectbox7 = None
                    if upload_csv is not None:
                        st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_3")
                        if st.session_state.selectbox7 is not None:
                            qcreport_mark[12] = st.session_state.selectbox7
                    else:
                        st.session_state.selectbox7 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox7 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.subheader("Check for RAFanCmd-Sts:")
        rfcol1,rfcol2 = st.columns([3,2])
        with rfcol1:
            if upload_csv is not None:
                if ("Return Air Fan On-Off Command" in styled_classic_view1.columns) & ("Return Air Fan Status" in styled_classic_view1.columns):
                # ======The MAIN Merge====== 
                # pointRole_list = styled_classic_view.columns.to_list()
                    saFanCheck = classic_view[["Asset Type","Asset Name","Return Air Fan On-Off Command","Return Air Fan Status"]]
                    
                    condition1 = saFanCheck["Return Air Fan On-Off Command"].notna() & saFanCheck["Return Air Fan Status"].notna()
                    condition2 = saFanCheck["Return Air Fan On-Off Command"].isna() & saFanCheck["Return Air Fan Status"].notna()
                    condition3 = saFanCheck["Return Air Fan On-Off Command"].notna() & saFanCheck["Return Air Fan Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    safanCheck_pair = saFanCheck[condition1|condition2|condition3]
                    safanCheck_pair['STS']=safanCheck_pair.apply(add_warning_icon,axis=1)
                    safanCheck_pair=safanCheck_pair.set_index('STS',append=True)
                    saFanCheck_pair = safanCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    safanCheck_df = st.dataframe(saFanCheck_pair,width=1000)
                elif ("Return Air Fan On-Off Command" not in styled_classic_view1.columns):
                    st.warning("no point configured for RAFanCmd role. Review model if point is available")
                elif ("Supply Air Fan Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for RAFanSts role. Review model if point is available")
        with rfcol2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox7' not in st.session_state:
                        st.session_state.selectbox7 = None
                    if upload_csv is not None:
                        st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_4")
                        if st.session_state.selectbox7 is not None:
                            qcreport_mark[13] = st.session_state.selectbox7
                    else:
                        st.session_state.selectbox7 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox7 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++ALL PUMPS +++++++++++++++++++++++++++++++++++++++++++++++
        st.subheader("Check for PumpCmd-Sts:")
        st.write("Includes all Pumps configured in the model")
        st.write("Covers Chilled Water Return Pumps:")
        required_columns = ['Column1', 'Column2', 'Column4']
        pmcol1,pmcol2 = st.columns([3,2])
       
        if upload_csv is not None:
            if "Pump" in styled_classic_view1.index:
                master_pmrole_list=styled_classic_view1.loc[["Pump"]].dropna(how='all',axis=1)
                master_pmrole_list = master_pmrole_list.columns
                master_pmrole_list = master_pmrole_list.to_list()

        with pmcol1:
            if upload_csv is not None:
                if ((("Chilled Water Return Pump Command On" in styled_classic_view1.columns) & ("Chilled Water Return Pump Status" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Chilled Water Return Pump Command On","Chilled Water Return Pump Status"]]
                    
                    condition1 = pchwrCheck["Chilled Water Return Pump Command On"].notna() & pchwrCheck["Chilled Water Return Pump Status"].notna()
                    condition2 = pchwrCheck["Chilled Water Return Pump Command On"].isna() & pchwrCheck["Chilled Water Return Pump Status"].notna()
                    condition3 = pchwrCheck["Chilled Water Return Pump Command On"].notna() & pchwrCheck["Chilled Water Return Pump Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Chilled Water Return Pump Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for CHWReturn PumpCmd role. Review model if point is available")
                elif ("Chilled Water Return Pump Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for CHWReturn PumpSts role. Review model if point is available")
        # with pmcol2:
        #     with st.container(border=True):
        #         # ==============Manual checkbox for configured assets=====================
        #         mini1col1,mini1col2 = st.columns(2)
        #         with mini1col1:
        #             if 'selectbox7' not in st.session_state:
        #                 st.session_state.selectbox7 = None
        #             if upload_csv is not None:
        #                 st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_6")
        #                 if st.session_state.selectbox7 is not None:
        #                     qcreport_mark[14] = st.session_state.selectbox7
        #             else:
        #                 st.session_state.selectbox7 = None
        #         with mini1col2:
        #             st.write("")
        #             manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
        #             if st.session_state.selectbox7 != None:
        #                 manual_check.empty()
        #                 st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.write("Covers Chilled Water Supply Pumps:")
        pm2col1,pm2col2 = st.columns([3,2])
        
        with pm2col1:
            if upload_csv is not None:
                if ((("Chilled Water Supply Pump Command On" in styled_classic_view1.columns) & ("Chilled Water Supply Pump Status" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Chilled Water Supply Pump Command On","Chilled Water Supply Pump Status"]]
                    
                    condition1 = pchwrCheck["Chilled Water Supply Pump Command On"].notna() & pchwrCheck["Chilled Water Supply Pump Status"].notna()
                    condition2 = pchwrCheck["Chilled Water Supply Pump Command On"].isna() & pchwrCheck["Chilled Water Supply Pump Status"].notna()
                    condition3 = pchwrCheck["Chilled Water Supply Pump Command On"].notna() & pchwrCheck["Chilled Water Supply Pump Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Chilled Water Supply Pump Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for CHWSupply PumpCmd role. Review model if point is available")
                elif ("Chilled Water Supply Pump Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for CHWSupply PumpSts role. Review model if point is available")
        # with pm2col2:
        #     with st.container(border=True):
        #         # ==============Manual checkbox for configured assets=====================
        #         mini1col1,mini1col2 = st.columns(2)
        #         with mini1col1:
        #             if 'selectbox7' not in st.session_state:
        #                 st.session_state.selectbox7 = None
        #             if upload_csv is not None:
        #                 st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_7")
        #                 if st.session_state.selectbox7 is not None:
        #                     qcreport_mark[12] = st.session_state.selectbox7
        #             else:
        #                 st.session_state.selectbox7 = None
        #         with mini1col2:
        #             st.write("")
        #             manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
        #             if st.session_state.selectbox7 != None:
        #                 manual_check.empty()
        #                 st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.write("Covers Condenser Water Pumps:")
        pm2col1,pm2col2 = st.columns([3,2])
        
        with pm2col1:
            if upload_csv is not None:
                if ((("Condenser Water Pump Command On" in styled_classic_view1.columns) & ("Condenser Water Pump Status" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Condenser Water Pump Command On","Condenser Water Pump Status"]]
                    
                    condition1 = pchwrCheck["Condenser Water Pump Command On"].notna() & pchwrCheck["Condenser Water Pump Status"].notna()
                    condition2 = pchwrCheck["Condenser Water Pump Command On"].isna() & pchwrCheck["Condenser Water Pump Status"].notna()
                    condition3 = pchwrCheck["Condenser Water Pump Command On"].notna() & pchwrCheck["Condenser Water Pump Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Condenser Water Pump Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for CondensrPumpCmd role. Review model if point is available")
                elif ("Condenser Water Pump Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for CondensrPumpSts role. Review model if point is available")
        # with pm2col2:
        #     with st.container(border=True):
        #         # ==============Manual checkbox for configured assets=====================
        #         mini1col1,mini1col2 = st.columns(2)
        #         with mini1col1:
        #             if 'selectbox7' not in st.session_state:
        #                 st.session_state.selectbox7 = None
        #             if upload_csv is not None:
        #                 st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_8")
        #                 if st.session_state.selectbox7 is not None:
        #                     qcreport_mark[12] = st.session_state.selectbox7
        #             else:
        #                 st.session_state.selectbox7 = None
        #         with mini1col2:
        #             st.write("")
        #             manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
        #             if st.session_state.selectbox7 != None:
        #                 manual_check.empty()
        #                 st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.write("Covers HotWater Return Pumps:")
        pm2col1,pm2col2 = st.columns([3,2])
        
        with pm2col1:
            if upload_csv is not None:
                if ((("Hot Water Return Pump Command On" in styled_classic_view1.columns) & ("Hot Water Return Pump Status" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Hot Water Return Pump Command On","Hot Water Return Pump Status"]]
                    
                    condition1 = pchwrCheck["Hot Water Return Pump Command On"].notna() & pchwrCheck["Hot Water Return Pump Status"].notna()
                    condition2 = pchwrCheck["Hot Water Return Pump Command On"].isna() & pchwrCheck["Hot Water Return Pump Status"].notna()
                    condition3 = pchwrCheck["Hot Water Return Pump Command On"].notna() & pchwrCheck["Hot Water Return Pump Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Hot Water Return Pump Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for HWReturn PumpCmd role. Review model if point is available")
                elif ("Hot Water Return Pump Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for HWReturn PumpSts role. Review model if point is available")
        # with pm2col2:
        #     with st.container(border=True):
        #         # ==============Manual checkbox for configured assets=====================
        #         mini1col1,mini1col2 = st.columns(2)
        #         with mini1col1:
        #             if 'selectbox7' not in st.session_state:
        #                 st.session_state.selectbox7 = None
        #             if upload_csv is not None:
        #                 st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_9")
        #                 if st.session_state.selectbox7 is not None:
        #                     qcreport_mark[12] = st.session_state.selectbox7
        #             else:
        #                 st.session_state.selectbox7 = None
        #         with mini1col2:
        #             st.write("")
        #             manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
        #             if st.session_state.selectbox7 != None:
        #                 manual_check.empty()
        #                 st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
         # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.write("Covers HotWater Supply Pumps:")
        pm2col1,pm2col2 = st.columns([3,2])
        
        with pm2col1:
            if upload_csv is not None:
                if ((("Hot Water Supply Pump Command On" in styled_classic_view1.columns) & ("Hot Water Supply Pump StatusOn" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Hot Water Supply Pump Command On","Hot Water Supply Pump StatusOn"]]
                    
                    condition1 = pchwrCheck["Hot Water Supply Pump Command On"].notna() & pchwrCheck["Hot Water Supply Pump StatusOn"].notna()
                    condition2 = pchwrCheck["Hot Water Supply Pump Command On"].isna() & pchwrCheck["Hot Water Supply Pump StatusOn"].notna()
                    condition3 = pchwrCheck["Hot Water Supply Pump Command On"].notna() & pchwrCheck["Hot Water Supply Pump StatusOn"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Hot Water Supply Pump Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for HWSupply PumpCmd role. Review model if point is available")
                elif ("Hot Water Supply Pump StatusOn" not in styled_classic_view1.columns):
                    st.warning("no point configured for HWSupply PumpSts role. Review model if point is available")
        with pm2col2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox7' not in st.session_state:
                        st.session_state.selectbox7 = None
                    if upload_csv is not None:
                        st.session_state.selectbox7 = st.selectbox(label="Check overall point config for Pumps:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_10")
                        if st.session_state.selectbox7 is not None:
                            qcreport_mark[14] = st.session_state.selectbox7
                    else:
                        st.session_state.selectbox7 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox7 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
         # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        st.subheader("Check for CTFanCmd-Sts:")
        pm2col1,pm2col2 = st.columns([3,2])
            
        with pm2col1:
            if upload_csv is not None:
                if ((("Cooling Tower Fan Command On" in styled_classic_view1.columns) & ("Cooling Tower Fan Status" in styled_classic_view1.columns))):
                # ======The MAIN Merge====== 
                    pchwrCheck = classic_view[["Asset Type","Asset Name","Cooling Tower Fan Command On","Cooling Tower Fan Status"]]
                    
                    condition1 = pchwrCheck["Cooling Tower Fan Command On"].notna() & pchwrCheck["Cooling Tower Fan Status"].notna()
                    condition2 = pchwrCheck["Cooling Tower Fan Command On"].isna() & pchwrCheck["Cooling Tower Fan Status"].notna()
                    condition3 = pchwrCheck["Cooling Tower Fan Command On"].notna() & pchwrCheck["Cooling Tower Fan Status"].isna()
                    
                    # selected_pointRole_pair = selected_pointRole1[(selected_pointRole1[pointRole_filter1].notna()) & (selected_pointRole1[pointRole_filter2].notna())]
                    pchwrCheck_pair = pchwrCheck[condition1|condition2|condition3]
                    pchwrCheck_pair['STS']=pchwrCheck_pair.apply(add_warning_icon,axis=1)
                    pchwrCheck_pair=pchwrCheck_pair.set_index('STS',append=True)
                    pchwrCheck_pair = pchwrCheck_pair.style.applymap(highlight_commas)
                    #if (pointRole_filter != 'Select a point Role') & (pointRole_filter != 'Asset Type') & (pointRole_filter != 'Asset Name'):
                    
                    progress_bar_anm('Point analysis in progress..',sleeptime=0.01)
                    pchwrCheck_df = st.dataframe(pchwrCheck_pair,width=1000)
                elif ("Cooling Tower Fan Command On" not in styled_classic_view1.columns):
                    st.warning("no point configured for CTFanCmd role. Review model if point is available")
                elif ("Cooling Tower Fan Status" not in styled_classic_view1.columns):
                    st.warning("no point configured for CTFanSts role. Review model if point is available")

        pm2col1,pm2col2=st.columns([3,2])
        with pm2col2:
            with st.container(border=True):
                # ==============Manual checkbox for configured assets=====================
                mini1col1,mini1col2 = st.columns(2)
                with mini1col1:
                    if 'selectbox7' not in st.session_state:
                        st.session_state.selectbox7 = None
                    if upload_csv is not None:
                        st.session_state.selectbox7 = st.selectbox(label="Check point config:",options=mcheck_selection,index=mcheck_selection.index(st.session_state.selectbox7),key="sb_11")
                        if st.session_state.selectbox7 is not None:
                            qcreport_mark[15] = st.session_state.selectbox7
                    else:
                        st.session_state.selectbox7 = None
                with mini1col2:
                    st.write("")
                    manual_check = st.info("This is a manual check. Select 'Check Status' after review",icon=":material/trackpad_input:")
                    if st.session_state.selectbox7 != None:
                        manual_check.empty()
                        st.success(body="Manual Check done! Status added to QC report",icon=":material/task_alt:")
    # st.button("Check Asset ")
    # =========Logic for Equip Name Length
    # =========Logic for Equips with only one point configured (excluding meters)
    # ======ZOOTR Analysis

with tab4:
    st.write(":construction: Work in progress ,coming soon :construction:")

st.divider()
# ============================================================The QC Report section================================================================   
st.header("4. Final QC Report :material/format_list_bulleted:",help="Creates a consolidated report for QC checkpoints. Includes both automated + manual checks")
# ======================Adding the section link column=========================
section_ids =['asset-name-validation','configured-point-asset-total','configured-point-asset-total','configured-point-asset-total','configured-point-asset-total',
              'configured-point-asset-total','assets-with-single-points','configured-point-asset-total','classic-avp-view','point-combination-checks','point-combination-checks',
              'point-combination-checks','point-combination-checks','point-combination-checks','point-combination-checks','point-combination-checks',
              'classic-avp-view','classic-avp-view','classic-avp-view','classic-avp-view']
section_link = ["Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link","Link"]

# def create_link(section_ids):
#     return f'<a href="#{section_ids}">Link</a>'

# def create_link(section_ids_idx):
#     return f'<a href="#{section_ids[section_ids_idx]}">Link</a>'

checkpoint_list = ["Equipment Name cannot have special characters.(Except - and _)",
                   "Equipment Name has to be unique (Applicable if there are more than one building)",
                   "Check 'Location' field is properly filled for individual assets",
                   "Check 'Location' name spelling is correct",
                   "Admin portal tool - Check if supplier relation is mapped",
                   "Check proper multistate mapping is done for all the configured multistate points",
                   "Check for assets with only One point Configured (Excluding Meters)",
                   "Check and confirm all Assets are as per Scope",
                   "Check if points are configured as per License",
                   "Check Analog Sensor/Setpoint combinations:",
                   "10a) ZoneTemp-Sp",
                   "10b) RATemp-Sp",
                   "10c) SAFanCmd-Sts",
                   "10d) RAFanCmd-Sts",
                   "10e) PumpCmd-Sts",
                   "10f) CTCmd-Sts",
                   "Check roles mapped more than once (colored cells in AssetVsPoint)",
                   "Check for Missing Mandatory points",
                   "Check if Assets are configured correctly (Eg., MultiZone splits, Naming)",
                   "Check 'Unconfirmed/Unassigned' points and confirm no points are missed that are required by Analytics"
                   ]
checkpoint_indexlist = ["1","2","3","4","5","6","7","8","9","10","10.a","10.b","10.c","10.d","10.e","10f","11","12","13","14"]
# n=0
# for i in range(len(checkpoint_list)):
#     n=i+1
#     checkpoint_indexlist.append(n)
qcr1,qcr2 = st.tabs(["Final QC Report", "QC Report Summary"])
with qcr1:
    
    qcdf = pd.DataFrame({"QC checkpoint":checkpoint_list,"SNo.":checkpoint_indexlist}).set_index(["SNo."])
    # qcdf["Link"]=qcdf["Link"].apply(lambda x: f"[Go to {x}](#{x.lower().replace(' ', '-')})")

    # Function to determine the cell type based on the row index
    # ============Apply formatting to Status column

    qcdf['Status'] = qcreport_mark

    # ======================Adding the remarks column=========================
    qcdf['Remarks'] = None
    # ===========================the final QCDF====================================
    # st.data_editor(qcdf,num_rows="dynamic",column_config={
    #     "QC checkpoint": st.column_config.TextColumn(width="large",disabled=True),
    #     "Status": st.column_config.SelectboxColumn("Status",help="Select correct status of the check",options=mcheck_selection),
    #     "Remarks": st.column_config.TextColumn(width="medium")
    #     },
    #     use_container_width=True)
    
    # ======================Adding the remarks column=========================
    
    def highlight_status(val):
        if "Passed" in str(val):
            return 'background-color: #00FF40'  # Highlight cells based on status
        elif "Failed" in str(val):
            return 'background-color: #FDBCB4'
        elif "To be discussed" in str(val):
            return 'background-color: #FFA500'
        else:
            return ''
    styled_qcdf = qcdf

    # styled_qcdf = styled_qcdf.insert(0, 'Link', styled_qcdf.index.map(create_link))

    final_qcdf=st.data_editor(styled_qcdf,num_rows="dynamic",width=1500,column_config={"SNo.":{"width":7},"Link":{"width":3}},height=750)#.style.applymap(highlight_status,subset=["Status"])

    qclist_msg = (f"QC Checklist comprises of {final_qcdf['QC checkpoint'].notnull().sum()} checkpoints as of now")
    if upload_csv is not None:
        st.write_stream(sp_stream(qclist_msg))

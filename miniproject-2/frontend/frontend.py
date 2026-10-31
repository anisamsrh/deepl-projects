import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Receipt Validator by anisamsrh", layout="centered", page_icon=":receipt:")
st.markdown("<h1 style='text-align: center;'>Receipt Validator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload your receipt to validate claim eligibility</p>", unsafe_allow_html=True)

with st.status("1. Upload the receipt", type="step", expanded=True, state="running"):
    uploaded_file = st.file_uploader("Choose a file (JPG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        st.image(uploaded_file, caption="Preview", width='stretch')
        analyze_btn = st.button("Analyze", type="primary", width='stretch')

with st.status("2. Validation Result", type="step", expanded=True, state="running"):
    if uploaded_file and 'analyze_btn' in locals() and analyze_btn:
            with st.spinner("VLM is analyzing your receipt..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post("http://localhost:8000/analyze-claim", files=files)

                    if res.status_code == 200:
                        data = res.json()

                        status = data["validation_result"]["status"]
                        if status == "approved":
                            st.success("✅ **CLAIM STATUS: APPROVED**")
                        elif status == "needs_review":
                            st.warning("⚠️ **CLAIM STATUS: NEEDS MANUAL REVIEW**")
                        else:
                            st.error("❌ **CLAIM STATUS: REJECTED**")
                        
                        st.markdown("<h3 style='text-align: center'>Validation Result Summary</h3>", unsafe_allow_html=True)
                        checks = data["validation_result"]["validation_checks"]
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Merchant's Name", "PRESENT" if checks["store_name_present"] else "MISSING")
                        c2.metric("Merchant's NPWP", "VALID" if checks["npwp_present"] else "INVALID")
                        c3.metric("PPN/Tax Status", f"VALID ({data['financial_summary']['detected_ppn_rate']}%)" if checks["ppn_valid"] else "INVALID")

                        if data["validation_result"]["rejection_reasons"]:
                            st.markdown("**Rejection Notes**")
                            for reason in data["validation_result"]["rejection_reasons"]:
                                st.write(f"- 🔴 {reason}")

                        with st.expander("🔍 Read Raw JSON Output"):
                            st.json(data)

                    elif res.status_code == 429:
                        st.error("⏳ **Usage limit execed!**")
                        st.warning("You can only make a request 5x per minute. Please wait a moment before you try again!")
                    else:
                        st.error(f"[{res.status_code}] Error : {res.text}")
                except Exception as e:
                    st.error(f"Failed connecting to the server: {e}")

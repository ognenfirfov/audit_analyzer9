
import streamlit as st
from utils.audit_parser import process_audits
import tempfile
import os

st.set_page_config(page_title="Audit Analyzer", layout="wide")
st.title("📊 Audit Analyzer")
st.markdown("Upload 3–4 PDF audit reports of **similar companies** to extract and compare key conclusions.")

uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    if len(uploaded_files) < 3 or len(uploaded_files) > 4:
        st.warning("Please upload between 3 and 4 PDF files.")
    else:
        with st.spinner("Analyzing audit reports with AI..."):
            # Save uploaded files temporarily
            temp_paths = []
            for file in uploaded_files:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                temp_file.write(file.read())
                temp_paths.append(temp_file.name)

            table_data = process_audits(temp_paths)

            st.success("Analysis complete!")
            st.markdown("### 🧾 Audit Comparison Table")
            st.dataframe(table_data, use_container_width=True)

            # Export to CSV
            csv = table_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="audit_analysis_results.csv",
                mime="text/csv"
            )
            # Export to PDF
            from fpdf import FPDF

            class PDF(FPDF):
                def header(self):
                    self.set_font("Arial", "B", 14)
                    self.cell(0, 10, "Audit Analysis Summary", ln=True, align="C")
                    self.ln(10)

                def add_table(self, df):
                    self.set_font("Arial", "", 10)
                    col_widths = [40, 40, 40, 40, 40]
                    headers = df.columns.tolist()
                    for i, header in enumerate(headers):
                        self.cell(col_widths[i % len(col_widths)], 10, str(header), 1, 0, "C")
                    self.ln()
                    for _, row in df.iterrows():
                        for i, item in enumerate(row):
                            self.cell(col_widths[i % len(col_widths)], 10, str(item), 1, 0, "L")
                        self.ln()

            pdf = PDF()
            pdf.add_page()
            pdf.add_table(table_data)
            pdf_output = "/tmp/audit_summary.pdf"
            pdf.output(pdf_output)

            with open(pdf_output, "rb") as f:
                st.download_button("📄 Download Results as PDF", f, file_name="audit_analysis_results.pdf", mime="application/pdf")


            # Clean up
            for path in temp_paths:
                os.remove(path)

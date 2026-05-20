import streamlit as st
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def extract_text_from_pdf(uploaded_file):
    uploaded_file.seek(0) 
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

st.set_page_config(page_title="Recruit-Agent Pro", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .stExpander { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.title("⚙️ Control Panel")
    st.subheader("Target Settings")
    
    JOB_ROLES = {
    "Select a Role": "",
    # --- AI, ML & DATA SCIENCE ---
    "AI / ML Engineer": "Skills: Python, PyTorch, TensorFlow, LLMs, RAG, Model Deployment.",
    "Data Scientist": "Skills: Statistics, Python, R, Machine Learning, Data Cleaning, Scikit-learn.",
    "Data Analyst": "Skills: SQL, Excel, PowerBI, Tableau, Exploratory Data Analysis (EDA).",
    "Data Engineer": "Skills: ETL Pipelines, Spark, Hadoop, SQL, Airflow, Data Warehousing.",
    "NLP Researcher": "Skills: Transformers, BERT, GPT, Tokenization, Linguistics, Deep Learning.",
    "Computer Vision Engineer": "Skills: OpenCV, CNNs, Image Processing, Object Detection, YOLO.",
    "MLOps Engineer": "Skills: Model Monitoring, CI/CD for ML, Kubernetes, MLflow, Docker.",
    "Deep Learning Engineer": "Skills: Neural Networks, Keras, CUDA, GPU Optimization, PyTorch.",
    "AI Product Manager": "Skills: AI Ethics, Product Lifecycle, Agile, Technical Communication.",
    "Big Data Architect": "Skills: NoSQL, Kafka, Cassandra, Distributed Systems, Spark.",
    
    # --- WEB & MOBILE DEVELOPMENT ---
    "Full Stack Developer": "Skills: React, Node.js, HTML/CSS, MongoDB, JavaScript, API Integration.",
    "Backend Developer": "Skills: Python, Django, FastAPI, Databases (PostgreSQL), Redis, Docker.",
    "Frontend Developer": "Skills: JavaScript, React, Vue, CSS Frameworks, UI/UX Principles.",
    "Python Developer": "Skills: Django, Flask, Scripting, Automation, REST APIs.",
    "Java Developer": "Skills: Spring Boot, Microservices, Hibernate, Multi-threading.",
    "Android Developer": "Skills: Kotlin, Java, Android SDK, Jetpack Compose, API Integration.",
    "iOS Developer": "Skills: Swift, SwiftUI, Objective-C, Xcode, Cocoa Touch.",
    "PHP Developer": "Skills: Laravel, Symfony, MySQL, WordPress, Backend Logic.",
    "React Developer": "Skills: React.js, Redux, Hooks, Tailwind CSS, Frontend State.",
    "Angular Developer": "Skills: TypeScript, Angular Framework, RXJS, Material UI.",
    
    # --- CLOUD, DEVOPS & INFRASTRUCTURE ---
    "Cloud Architect": "Skills: AWS, Azure, GCP, Terraform, Kubernetes, Networking.",
    "DevOps Engineer": "Skills: CI/CD, Docker, Kubernetes, Jenkins, Linux, Monitoring Tools.",
    "Site Reliability Engineer (SRE)": "Skills: Systems Engineering, Automation, Incident Response, Python.",
    "AWS Specialist": "Skills: EC2, S3, Lambda, IAM, VPC, CloudFormation.",
    "Azure Administrator": "Skills: Azure AD, Virtual Machines, Azure DevOps, Networking.",
    "Cloud Security Engineer": "Skills: Cloud Identity, Encryption, Compliance, Network Security.",
    "Network Engineer": "Skills: TCP/IP, Cisco, Routing, Switching, Firewalls, DNS.",
    "System Administrator": "Skills: Linux/Windows Server, Scripting, Active Directory, Backups.",
    "Kubernetes Administrator": "Skills: Helm, K8s Architecture, Container Orchestration, Monitoring.",
    "Infrastructure Engineer": "Skills: IaC, Terraform, Ansible, Shell Scripting, Bare Metal.",

    # --- CYBERSECURITY ---
    "Cybersecurity Analyst": "Skills: Network Security, Pentesting, SIEM, Threat Intelligence, Compliance.",
    "Information Security Manager": "Skills: Risk Management, ISO 27001, GRC, Policy Design.",
    "Ethical Hacker / Pen Tester": "Skills: Kali Linux, Metasploit, Web App Security, OWASP.",
    "Security Architect": "Skills: Zero Trust, Encryption Protocols, Security Frameworks.",
    "SOC Analyst": "Skills: Incident Logging, Log Analysis, Splunk, Threat Hunting.",

    # --- SOFTWARE ENGINEERING & QUALITY ---
    "Software Architect": "Skills: Design Patterns, System Design, Scalability, Architecture Blueprints.",
    "QA Automation Engineer": "Skills: Selenium, PyTest, Cypress, Automated Testing, Jenkins.",
    "Manual Tester": "Skills: Test Case Design, Bug Tracking, Regression Testing, SDLC.",
    "Embedded Systems Engineer": "Skills: C, C++, Microcontrollers, RTOS, Firmware Development.",
    "Blockchain Developer": "Skills: Solidity, Ethereum, Smart Contracts, Rust, Cryptography.",
    "Game Developer": "Skills: Unity, Unreal Engine, C#, C++, 3D Modeling.",
    "RPA Developer": "Skills: UiPath, Automation Anywhere, Blue Prism, Process Mining.",
    
    # --- DATABASE & BI ---
    "SQL Developer": "Skills: Complex Queries, Stored Procedures, Indexing, Database Optimization.",
    "Database Administrator (DBA)": "Skills: Recovery, Patching, Tuning, Security, High Availability.",
    "Business Intelligence (BI) Developer": "Skills: DAX, SQL, Data Modeling, ETL, Reporting Tools.",
    "Tableau Developer": "Skills: Data Viz, Dashboards, LOD Expressions, Tableau Server.",
    
    # --- MANAGEMENT & OTHER ---
    "Project Manager": "Skills: Agile, Scrum, JIRA, Resource Planning, Stakeholder Management.",
    "Business Analyst": "Skills: Requirements Gathering, UML, User Stories, Gap Analysis.",
    "UI/UX Designer": "Skills: Figma, Adobe XD, Prototyping, User Research, Wireframing.",
    "Technical Writer": "Skills: Documentation, API Guides, Markdown, Clear Communication."
}

    selected_role = st.selectbox("🎯 Target Job Role", options=list(JOB_ROLES.keys()))

    if selected_role != "Select a Role":
        job_description = JOB_ROLES[selected_role]
        st.info(f"Targeting: **{selected_role}**")
    else:
        job_description = st.text_area("Or paste a custom Job Description here:")

    uploaded_resume = st.file_uploader("📤 Upload Resume (PDF)", type="pdf")
    
    st.markdown("---")
    analyze_clicked = st.button("🔍 Run Full Analysis")

st.title("💼 Recruit-Agent Pro: Intelligence Dashboard")

if uploaded_resume and job_description:
    resume_text = extract_text_from_pdf(uploaded_resume)
    
    
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)

    if analyze_clicked:
        with st.spinner("🤖 AI is deep-scanning your resume..."):
            
            prompt = f"""
            You are an Expert Technical Recruiter.
            Target Role: {selected_role}
            Role Requirements: {job_description}
            Candidate Resume: {resume_text}
            
            Please provide:
            1. ATS Match Score (0-100%).
            2. Top 5 Missing Skills (Gaps).
            3. 20 Interview Questions categorized as:
               - 5 Behavioral
               - 5 Technical Fundamentals
               - 10 Scenario-based Advanced Questions.
            """
            
            try:
                response = llm.invoke(prompt).content
                
            
                tab1, tab2, tab3 = st.tabs(["📊 Analysis Report", "❓ 20 Interview Questions", "📄 Resume Preview"])
                
                with tab1:
                    st.subheader("ATS Scoring & Skill Gaps")
                    st.markdown(response)
                    st.download_button(
                        label="📥 Download Full Report",
                        data=response,
                        file_name=f"Analysis_{selected_role}.txt",
                        mime="text/plain"
                    )

                with tab2:
                    st.subheader("Tailored Interview Preparation")
                    st.success("These questions are generated based on your specific gaps and experience.")
                    st.markdown(response)

                with tab3:
                    st.subheader("Parsed Text Content")
                    st.text_area("What the AI sees:", resume_text, height=500)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.write("### Ready to Analyze")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Target Role:** {selected_role if selected_role != 'Select a Role' else 'Custom'}")
            st.write(f"**File:** {uploaded_resume.name}")
        with col2:
            st.info("Click the 'Run Full Analysis' button in the sidebar to begin.")
        
        with st.expander("👀 View Extracted Resume Text"):
            st.write(resume_text[:1000] + "...")

elif not uploaded_resume:
    st.warning("👈 Use the sidebar on the left to select a role and upload your resume.")

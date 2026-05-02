import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
#import shap
import xgboost as xgb

# -----------------------------
# Load model and threshold
# -----------------------------
#model = joblib.load("C:/Users/Acer/Documents/healthcare-digital-twin/models/diabetes_xgb_digital_twin_model.pkl")
#threshold = joblib.load("C:/Users/Acer/Documents/healthcare-digital-twin/models/diabetes_risk_threshold.pkl")
#explainer = shap.TreeExplainer(model)

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "diabetes_xgb_digital_twin_model.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "diabetes_risk_threshold.pkl"

model = joblib.load(MODEL_PATH)
threshold = joblib.load(THRESHOLD_PATH)

def risk_category(probability):
    if probability < 0.25:
        return "Low Risk"
    elif probability < 0.60:
        return "Medium Risk"
    else:
        return "High Risk"


def predict_risk(patient_data):
    patient_df = pd.DataFrame([patient_data])
    probability = model.predict_proba(patient_df)[:, 1][0]
    prediction = int(probability >= threshold)
    category = risk_category(probability)
    return probability, prediction, category


# -----------------------------
# Streamlit page setup
# -----------------------------
st.set_page_config(
    page_title="Healthcare Digital Twin",
    page_icon="🩺",
    layout="wide"
)

st.title("Healthcare Digital Twin for Diabetes Risk Monitoring")
st.write(
    "This prototype simulates a virtual patient and predicts diabetes risk using "
    "machine learning. You can change health indicators and observe how the predicted risk changes."
)

# -----------------------------
# Sidebar: baseline patient input
# -----------------------------
st.sidebar.header("Virtual Patient Profile")

pregnancies = st.sidebar.slider("Pregnancies", 0, 17, 2)
glucose = st.sidebar.slider("Glucose", 40, 200, 150)
blood_pressure = st.sidebar.slider("Blood Pressure", 20, 130, 85)
skin_thickness = st.sidebar.slider("Skin Thickness", 5, 100, 30)
insulin = st.sidebar.slider("Insulin", 10, 850, 130)
bmi = st.sidebar.slider("BMI", 15.0, 70.0, 32.5)
dpf = st.sidebar.slider("Diabetes Pedigree Function", 0.05, 2.50, 0.55)
age = st.sidebar.slider("Age", 18, 90, 45)

baseline_patient = {
    "Pregnancies": pregnancies,
    "Glucose": glucose,
    "BloodPressure": blood_pressure,
    "SkinThickness": skin_thickness,
    "Insulin": insulin,
    "BMI": bmi,
    "DiabetesPedigreeFunction": dpf,
    "Age": age
}

# -----------------------------
# Main risk prediction
# -----------------------------
baseline_probability, baseline_prediction, baseline_category = predict_risk(baseline_patient)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Risk Probability", f"{baseline_probability * 100:.2f}%")

with col2:
    st.metric("Risk Category", baseline_category)

with col3:
    st.metric("Risk Prediction", "At Risk" if baseline_prediction == 1 else "Low Risk")

st.subheader("Current Virtual Patient Data")
st.dataframe(pd.DataFrame([baseline_patient]))

# -----------------------------
# Feature importance
# -----------------------------
st.subheader("Key Risk Drivers")

st.write(
    "The chart below shows which health indicators were most important for the model "
    "when learning diabetes-risk patterns from the dataset."
)

feature_importance_df = pd.DataFrame({
    "Feature": model.feature_names_in_,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

st.dataframe(feature_importance_df, use_container_width=True)

fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(
    feature_importance_df["Feature"],
    feature_importance_df["Importance"]
)
ax.invert_yaxis()
ax.set_xlabel("Importance")
ax.set_ylabel("Feature")
ax.set_title("Model Feature Importance")

st.pyplot(fig)

# -----------------------------
# Patient-specific contribution explanation
# -----------------------------
st.subheader("Patient-Specific Risk Explanation")

st.write(
    "This section explains which health indicators contribute most to the current "
    "virtual patient's diabetes-risk prediction. Positive contributions push the "
    "model toward higher risk, while negative contributions push it toward lower risk."
)

baseline_patient_df = pd.DataFrame([baseline_patient])

# XGBoost built-in feature contribution values
booster = model.get_booster()

patient_dmatrix = xgb.DMatrix(
    baseline_patient_df,
    feature_names=list(baseline_patient_df.columns)
)

contributions = booster.predict(
    patient_dmatrix,
    pred_contribs=True
)
# Last value is the bias/base value, so remove it
feature_contributions = contributions[0][:-1]

contribution_df = pd.DataFrame({
    "Feature": baseline_patient_df.columns,
    "Patient Value": baseline_patient_df.iloc[0].values,
    "Contribution": feature_contributions
})

contribution_df["Effect"] = contribution_df["Contribution"].apply(
    lambda x: "Increases Risk" if x > 0 else "Reduces Risk"
)

contribution_df["Absolute Impact"] = contribution_df["Contribution"].abs()

contribution_df = contribution_df.sort_values(
    by="Absolute Impact",
    ascending=False
)

st.dataframe(
    contribution_df[
        ["Feature", "Patient Value", "Contribution", "Effect"]
    ],
    use_container_width=True
)

top_increasing = contribution_df[
    contribution_df["Contribution"] > 0
].head(3)

top_reducing = contribution_df[
    contribution_df["Contribution"] < 0
].head(3)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Main Risk-Increasing Factors")
    if not top_increasing.empty:
        for _, row in top_increasing.iterrows():
            st.write(
                f"- **{row['Feature']}** = {row['Patient Value']} "
                f"(Contribution: {row['Contribution']:.3f})"
            )
    else:
        st.write("No major risk-increasing factors identified.")

with col_b:
    st.markdown("#### Main Risk-Reducing Factors")
    if not top_reducing.empty:
        for _, row in top_reducing.iterrows():
            st.write(
                f"- **{row['Feature']}** = {row['Patient Value']} "
                f"(Contribution: {row['Contribution']:.3f})"
            )
    else:
        st.write("No major risk-reducing factors identified.")

st.info(
    "These contribution values are generated using XGBoost's built-in prediction "
    "contribution method. They provide a patient-level explanation similar to SHAP values."
)

# -----------------------------
# What-if simulation
# -----------------------------
st.subheader("What-if Simulation")

st.write(
    "Adjust the simulation sliders below to test how improvements in health indicators "
    "could affect the predicted diabetes risk."
)

sim_col1, sim_col2, sim_col3 = st.columns(3)

with sim_col1:
    glucose_reduction = st.slider("Reduce Glucose by (%)", 0, 50, 15)

with sim_col2:
    bmi_reduction = st.slider("Reduce BMI by (%)", 0, 30, 10)

with sim_col3:
    bp_reduction = st.slider("Reduce Blood Pressure by (%)", 0, 30, 5)

simulated_patient = baseline_patient.copy()
simulated_patient["Glucose"] = baseline_patient["Glucose"] * (1 - glucose_reduction / 100)
simulated_patient["BMI"] = baseline_patient["BMI"] * (1 - bmi_reduction / 100)
simulated_patient["BloodPressure"] = baseline_patient["BloodPressure"] * (1 - bp_reduction / 100)

simulated_probability, simulated_prediction, simulated_category = predict_risk(simulated_patient)

risk_reduction = baseline_probability - simulated_probability

st.subheader("Before vs After Simulation")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric(
        "Before Risk",
        f"{baseline_probability * 100:.2f}%"
    )

with result_col2:
    st.metric(
        "After Simulation Risk",
        f"{simulated_probability * 100:.2f}%",
        delta=f"{risk_reduction * 100:.2f} percentage points"
    )

with result_col3:
    st.metric(
        "After Category",
        simulated_category
    )

comparison_df = pd.DataFrame({
    "Health Indicator": baseline_patient.keys(),
    "Before": baseline_patient.values(),
    "After Simulation": simulated_patient.values()
})

st.subheader("Health Indicator Changes")
st.dataframe(comparison_df)


# -----------------------------
# Patient risk trajectory
# -----------------------------
st.subheader("Patient Risk Trajectory Over Time")

st.write(
    "This simulated trajectory shows how the virtual patient's predicted risk could change "
    "over time if glucose, BMI, and blood pressure gradually improve."
)

months = ["Month 0", "Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]

trajectory_data = []

for i, month in enumerate(months):
    progress = i / (len(months) - 1)

    patient_month = baseline_patient.copy()

    # Gradually apply the selected improvements over 6 months
    patient_month["Glucose"] = baseline_patient["Glucose"] * (
        1 - progress * glucose_reduction / 100
    )
    patient_month["BMI"] = baseline_patient["BMI"] * (
        1 - progress * bmi_reduction / 100
    )
    patient_month["BloodPressure"] = baseline_patient["BloodPressure"] * (
        1 - progress * bp_reduction / 100
    )

    month_probability, _, month_category = predict_risk(patient_month)

    trajectory_data.append({
        "Month": month,
        "Glucose": round(patient_month["Glucose"], 2),
        "BMI": round(patient_month["BMI"], 2),
        "BloodPressure": round(patient_month["BloodPressure"], 2),
        "Risk Probability (%)": round(month_probability * 100, 2),
        "Risk Category": month_category
    })

trajectory_df = pd.DataFrame(trajectory_data)

st.dataframe(trajectory_df, use_container_width=True)

st.line_chart(
    trajectory_df.set_index("Month")[["Risk Probability (%)"]]
)
st.caption(
    "Note: Risk values are generated by a tree-based ML model, so the trajectory may not decrease perfectly smoothly. "
    "Small increases or flat segments can occur when simulated patient values cross model decision thresholds."
)

# -----------------------------
# Interpretation
# -----------------------------
st.subheader("Interpretation")

if simulated_probability < baseline_probability:
    st.success(
        f"The simulated changes reduced the predicted risk from "
        f"{baseline_probability * 100:.2f}% to {simulated_probability * 100:.2f}%."
    )
elif simulated_probability > baseline_probability:
    st.warning(
        f"The simulated changes increased the predicted risk from "
        f"{baseline_probability * 100:.2f}% to {simulated_probability * 100:.2f}%."
    )
else:
    st.info("The simulated changes did not change the predicted risk.")

# -----------------------------
# Model comparison
# -----------------------------
st.subheader("Model Evaluation Summary")

st.write(
    "Several machine learning models were evaluated. Since this is a healthcare risk-monitoring "
    "prototype, the final model was selected by prioritizing recall and F1-score for the diabetes-risk class."
)

model_comparison_df = pd.DataFrame({
    "Model": [
        "Random Forest",
        "XGBoost",
        "XGBoost Balanced",
        "XGBoost Balanced Tuned",
        "LightGBM Balanced",
        "LightGBM Balanced Tuned"
    ],
    "Threshold": [
        "0.50",
        "0.50",
        "0.50",
        "0.25",
        "0.50",
        "0.40"
    ],
    "Accuracy": [
        0.779,
        0.773,
        0.753,
        0.740,
        0.766,
        0.740
    ],
    "Precision Class 1": [
        0.727,
        0.694,
        0.629,
        0.583,
        0.650,
        0.595
    ],
    "Recall Class 1": [
        0.593,
        0.630,
        0.722,
        0.907,
        0.722,
        0.815
    ],
    "F1 Class 1": [
        0.653,
        0.660,
        0.672,
        0.710,
        0.684,
        0.688
    ]
})

st.dataframe(model_comparison_df, use_container_width=True)

st.success(
    "Final selected model: XGBoost Balanced with threshold = 0.25. "
    "This setup achieved the highest positive-class recall and F1-score, making it suitable "
    "for a screening-style healthcare risk-monitoring prototype."
)

st.caption(
    "Disclaimer: This is a simple portfolio prototype for healthcare digital twin simulation."
    "It is not a clinical diagnostic tool."
)
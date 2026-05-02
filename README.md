# Healthcare Digital Twin for Diabetes Risk Monitoring

An interactive healthcare AI prototype that uses machine learning, digital twin simulation, and model explainability to estimate and visualize patient-specific diabetes risk.

This project demonstrates how clinical indicators such as glucose, BMI, blood pressure, insulin, age, and diabetes pedigree function can be used to create a virtual patient profile, predict diabetes risk, simulate health improvements, and explain the factors influencing the prediction.

---

## Project Overview

Diabetes risk monitoring is an important healthcare challenge because early identification of high-risk patients can support preventive care, lifestyle intervention, and clinical decision-making.

This project builds a simplified **healthcare digital twin prototype** for diabetes risk monitoring. The digital twin represents a virtual patient using clinical health indicators and allows users to simulate how changes in those indicators may affect the model-predicted diabetes risk.

The goal is not to create a clinical diagnostic tool, but to demonstrate how machine learning and digital twin concepts can support transparent, interactive, and data-driven healthcare risk analysis.

---

## What Problem Does This Project Solve?

Traditional machine learning healthcare projects often stop at:

> Input patient data → predict disease risk

This project goes further by adding simulation and explainability:

> Virtual patient profile → risk prediction → what-if simulation → risk trajectory → explanation of risk drivers

The dashboard allows users to answer questions such as:

- What is the current predicted diabetes risk for this virtual patient?
- Which health indicators contribute most to the risk prediction?
- How would predicted risk change if glucose, BMI, or blood pressure improved?
- How could risk evolve over time under a simulated health-improvement scenario?
- Why did the model classify the patient as low, medium, or high risk?

---

## Digital Twin Concept

In this project, the digital twin is a simplified virtual representation of a patient.

It combines:

1. Patient health indicators  
2. A machine learning risk prediction model  
3. What-if simulation  
4. Risk trajectory over time  
5. Model interpretability  

The digital twin allows users to test simulated changes before they happen in real life.

Example:

```text
Current virtual patient:
Glucose = 150
BMI = 32.5
Blood Pressure = 85

Predicted diabetes risk = High

Simulation:
Reduce glucose by 15%
Reduce BMI by 10%
Reduce blood pressure by 5%

Updated predicted diabetes risk = Low / Medium / High depending on the model output.

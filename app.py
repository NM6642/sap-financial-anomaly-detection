import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.ensemble import IsolationForest

st.title("SAP Financial Anomaly Detection System")

df = pd.read_csv("finance_data.csv")

# Detect anomalies
model = IsolationForest(contamination=0.02, random_state=42)
df["anomaly"] = model.fit_predict(df[["amount"]])

# Assign risk levels
def get_risk(row):
    if row["amount"] > 50000:
        return "High Risk"
    elif row["amount"] > 10000:
        return "Medium Risk"
    else:
        return "Low Risk"

df["risk_level"] = df.apply(get_risk, axis=1)

# Filter suspicious transactions
anomalies = df[df["anomaly"] == -1].copy()

# Assign varied reasons
def anomaly_reason(row):
    if row["amount"] > 50000:
        return "Unusually high amount"
    elif row["amount"] > 20000:
        return "High amount outlier"
    elif row["amount"] > 10000:
        return "Medium amount outlier"
    elif row["amount"] < 0:
        return "Unexpected negative transaction"
    else:
        return "Minor anomaly"

anomalies["reason"] = anomalies.apply(anomaly_reason, axis=1)

# KPIs
st.metric("Total Transactions", len(df))
st.metric("Suspicious Transactions", len(anomalies))

# Cost center bar chart
fig1 = px.bar(df, x="cost_center", y="amount", color="risk_level",
              title="Financial Activity by Cost Center")
st.plotly_chart(fig1)

# Monthly trend chart
df["posting_date"] = pd.to_datetime(df["posting_date"])
monthly = df.groupby(df["posting_date"].dt.to_period("M"))["amount"].sum().reset_index()
monthly["posting_date"] = monthly["posting_date"].dt.to_timestamp()

fig2 = px.line(monthly, x="posting_date", y="amount", title="Monthly Financial Trend")
st.plotly_chart(fig2)

# Table of top suspicious transactions
st.subheader("Suspicious Transactions")
st.dataframe(anomalies[["document_id","cost_center","vendor","amount","risk_level","reason"]].head(50))

# Top vendors contributing to anomalies
top_vendors = anomalies.groupby("vendor")["amount"].sum().sort_values(ascending=False).reset_index()

# Top cost centers contributing to anomalies
top_cost_centers = anomalies.groupby("cost_center")["amount"].sum().sort_values(ascending=False).reset_index()

st.subheader("Top Vendors with Anomalies")
fig_vendor = px.bar(top_vendors, x="vendor", y="amount",
                    title="Top Vendors Contributing to Suspicious Transactions")
st.plotly_chart(fig_vendor)

st.subheader("Top Cost Centers with Anomalies")
fig_cc = px.bar(top_cost_centers, x="cost_center", y="amount",
                title="Top Cost Centers Contributing to Suspicious Transactions")
st.plotly_chart(fig_cc)
import { useState } from "react";
import axios from "axios";
import { BASE_URL } from "../api";

const initialForm = {
  tenure: 12,
  monthly_charges: 75,
  contract_type: "Month-to-month",
  service_count: 3,
};

function ChurnPrediction() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const getRiskStyle = (score) => {
    if (score < 0.3) {
      return { backgroundColor: "#1f7a1f", color: "white" };
    }

    if (score <= 0.6) {
      return { backgroundColor: "#d18b00", color: "white" };
    }

    return { backgroundColor: "#b22222", color: "white" };
  };

  const getRiskText = (score) => {
    if (score < 0.3) {
      return "Low Risk";
    }

    if (score <= 0.6) {
      return "Medium Risk";
    }

    return "High Risk";
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = {
        tenure: Number(form.tenure),
        monthly_charges: Number(form.monthly_charges),
        contract_type: form.contract_type,
        service_count: Number(form.service_count),
      };

      const response = await axios.post(`${BASE_URL}/predict-churn`, payload);
      setResult(response.data);
    } catch (err) {
      if (err.response?.status === 422) {
        const details = err.response.data?.detail;
        if (Array.isArray(details) && details.length > 0) {
          setError(details[0].msg || "Validation error");
        } else {
          setError("Validation error");
        }
      } else {
        setError("Failed to predict churn");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Churn Prediction</h2>
      <p>Estimate churn risk from a small set of customer profile inputs.</p>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "10px", maxWidth: "360px" }}>
        <label>
          Tenure
          <input
            type="number"
            min="0"
            value={form.tenure}
            onChange={(e) => updateField("tenure", e.target.value)}
            required
          />
        </label>

        <label>
          Monthly Charges
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.monthly_charges}
            onChange={(e) => updateField("monthly_charges", e.target.value)}
            required
          />
        </label>

        <label>
          Contract Type
          <select
            value={form.contract_type}
            onChange={(e) => updateField("contract_type", e.target.value)}
          >
            <option value="Month-to-month">Month-to-month</option>
            <option value="One year">One year</option>
            <option value="Two year">Two year</option>
          </select>
        </label>

        <label>
          Service Count
          <input
            type="number"
            min="0"
            max="6"
            value={form.service_count}
            onChange={(e) => updateField("service_count", e.target.value)}
            required
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Churn"}
        </button>
      </form>

      {error && <p style={{ color: "#b22222" }}>{error}</p>}

      {result && (
        <div style={{ marginTop: "16px", border: "1px solid #ccc", padding: "12px", borderRadius: "8px" }}>
          <h3>Prediction Result</h3>
          <p>Risk Score: {(result.risk_score * 100).toFixed(1)}%</p>
          <p>Prediction: {result.prediction}</p>
          <p>Confidence: {result.confidence_level}</p>

          <p style={{ ...getRiskStyle(result.risk_score), padding: "8px", borderRadius: "6px", width: "fit-content" }}>
            {getRiskText(result.risk_score)}
          </p>
        </div>
      )}
    </div>
  );
}

export default ChurnPrediction;

import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL } from "./api";
import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("summary");

  useEffect(() => {
    axios
      .get(`${BASE_URL}/churn/summary`)
      .then((response) => {
        console.log("/churn/summary response:", response.data);
        setData(response.data);
      })
      .catch(() => {
        setError("Failed to load churn summary");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div>
      <h1>Customer Churn Dashboard</h1>

      <p>Total Customers: {data.total_customers}</p>
      <p>Total Churned: {data.total_churned}</p>
      <p>Churn Rate: {(data.churn_rate * 100).toFixed(1)}%</p>

      <hr />
      <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
        <button onClick={() => setActiveTab("summary")}>Churn Summary</button>
        <button onClick={() => setActiveTab("search")}>Customer Search</button>
        <button onClick={() => setActiveTab("highRisk")}>High-Risk Customers</button>
        <button onClick={() => setActiveTab("prediction")}>Churn Prediction</button>
      </div>

      {activeTab === "summary" && <ChurnSummary />}
      {activeTab === "search" && <CustomerSearch />}
      {activeTab === "highRisk" && <HighRiskCustomers />}
      {activeTab === "prediction" && <ChurnPrediction />}
    </div>
  );
}

export default App;
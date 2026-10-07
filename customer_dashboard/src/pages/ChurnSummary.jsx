import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL } from "../api";

function ChurnSummary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get(`${BASE_URL}/churn/summary`)
      .then((response) => {
        setData(response.data);
      })
      .catch(() => {
        setError("Failed to load churn summary");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Churn Summary</h2>

      <p>
        Overview of customer churn and churn rates by contract type.
      </p>

      {/* Metric Cards */}
      <div style={{ display: "flex", gap: "20px" }}>
        <div>
          <h3>Total Customers</h3>
          <p>{data.total_customers}</p>
        </div>

        <div>
          <h3>Total Churned</h3>
          <p>{data.total_churned}</p>
        </div>

        <div>
          <h3>Churn Rate</h3>
          <p>{(data.churn_rate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <h3>Churn by Contract Type</h3>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Contract Type</th>
            <th>Churn Rate</th>
            <th>Visual</th>
          </tr>
        </thead>

        <tbody>
          {data.by_contract_type.map((item) => (
            <tr key={item.contract_type}>
              <td>{item.contract_type}</td>

              <td>
                {(item.churn_rate * 100).toFixed(1)}%
              </td>

              <td style={{ width: "250px" }}>
                <div
                  style={{
                    width: `${item.churn_rate * 100}%`,
                    height: "20px",
                    backgroundColor: "steelblue",
                  }}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ChurnSummary;
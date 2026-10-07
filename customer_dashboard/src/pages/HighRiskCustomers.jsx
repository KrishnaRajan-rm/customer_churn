import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_URL } from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [ascending, setAscending] = useState(true);

  const fetchCustomers = async (newLimit) => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.get(
        `${BASE_URL}/customers/high-risk?limit=${newLimit}`
      );

      setCustomers(response.data);
    } catch {
      setError("Failed to load high-risk customers");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers(limit);
  }, [limit]);

  const sortedCustomers = [...customers].sort((a, b) => {
    return ascending
      ? a.tenure - b.tenure
      : b.tenure - a.tenure;
  });

  const loadMore = () => {
    setLimit(limit + 50);
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>High-Risk Customers</h2>

      <p>{customers.length} high-risk customers identified</p>

      {customers.length === 0 ? (
        <p>No high-risk customers found</p>
      ) : (
        <>
          <table border="1">
            <thead>
              <tr>
                <th>Customer ID</th>

                <th onClick={() => setAscending(!ascending)}>
                  Tenure {ascending ? "↑" : "↓"}
                </th>

                <th>Monthly Charges</th>
                <th>Contract Type</th>
                <th>Risk Reason</th>
              </tr>
            </thead>

            <tbody>
              {sortedCustomers.map((customer) => (
                <tr key={customer.customer_id}>
                  <td>{customer.customer_id}</td>
                  <td>{customer.tenure}</td>
                  <td>${customer.monthly_charges.toFixed(2)}</td>
                  <td>{customer.contract_type}</td>
                  <td>{customer.risk_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button onClick={loadMore}>
            Load More
          </button>
        </>
      )}
    </div>
  );
}

export default HighRiskCustomers;
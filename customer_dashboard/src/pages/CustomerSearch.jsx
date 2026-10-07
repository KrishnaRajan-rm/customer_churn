import { useState } from "react";
import axios from "axios";
import { BASE_URL } from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!customerId.trim()) return;

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const response = await axios.get(
        `${BASE_URL}/customer/${customerId}`
      );

      setCustomer(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        setError("Customer not found");
      } else {
        setError("Failed to fetch customer");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Customer Search</h2>

      <input
        type="text"
        placeholder="Enter Customer ID"
        value={customerId}
        onChange={(e) => setCustomerId(e.target.value)}
      />

      <button onClick={handleSearch}>Search</button>

      {loading && <p>Loading...</p>}

      {error && <p>{error}</p>}

      {customer && (
        <div>
          <h3>Customer Details</h3>

          <p>Customer ID: {customer.customer_id}</p>
          <p>Tenure: {customer.tenure}</p>
          <p>Contract: {customer.contract_type}</p>
          <p>Internet Service: {customer.internet_service}</p>
          <p>Monthly Charges: {customer.monthly_charges}</p>

          <p
            style={{
              backgroundColor: customer.churn ? "red" : "green",
              color: "white",
              padding: "8px",
              display: "inline-block",
            }}
          >
            {customer.churn ? "Churned" : "Active"}
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;
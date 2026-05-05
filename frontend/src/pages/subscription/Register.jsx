// ================================================================
// Register.jsx — First time registration
// src/pages/subscription/Register.jsx
// ================================================================
import { useState } from "react";
import { registerCustomer } from "../../services/licenseService";

export default function Register({ onSuccess }) {
  const [form, setForm] = useState({
    business_name: "", owner_name: "",
    email: "", phone: "", city: "", password: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  }

  async function handleSubmit() {
    setError("");
    if (!form.business_name || !form.email || !form.phone || !form.password) {
      setError("Please fill all required fields");
      return;
    }
    setLoading(true);
    try {
      const data = await registerCustomer(form);
      localStorage.setItem("sp_email", form.email);
      onSuccess?.(data);
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: "100vh", background: "#F5F7FA",
      display: "flex", alignItems: "center", justifyContent: "center", padding: "20px"
    }}>
      <div style={{
        background: "white", borderRadius: "16px",
        padding: "40px", width: "100%", maxWidth: "440px",
        boxShadow: "0 4px 24px rgba(0,0,0,0.08)"
      }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <h1 style={{ fontSize: "24px", fontWeight: "bold", color: "#1565C0", margin: 0 }}>
            SalaryPay
          </h1>
          <p style={{ color: "#666", marginTop: "8px" }}>
            Register to get <strong>7 days free trial</strong>
          </p>
        </div>

        {error && (
          <div style={{
            background: "#FFEBEE", color: "#C62828",
            border: "1px solid #FFCDD2", borderRadius: "8px",
            padding: "10px 14px", marginBottom: "20px", fontSize: "14px"
          }}>
            {error}
          </div>
        )}

        {[
          { name: "business_name", label: "Business Name *", placeholder: "e.g. ABC Enterprises" },
          { name: "owner_name", label: "Owner Name *", placeholder: "Your full name" },
          { name: "email", label: "Email *", placeholder: "email@example.com", type: "email" },
          { name: "phone", label: "Phone *", placeholder: "10-digit mobile number" },
          { name: "city", label: "City", placeholder: "Pune, Mumbai..." },
          { name: "password", label: "Password *", placeholder: "Min 8 characters", type: "password" },
        ].map(field => (
          <div key={field.name} style={{ marginBottom: "16px" }}>
            <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#444", marginBottom: "6px" }}>
              {field.label}
            </label>
            <input
              name={field.name}
              type={field.type || "text"}
              value={form[field.name]}
              onChange={handleChange}
              placeholder={field.placeholder}
              style={{
                width: "100%", padding: "10px 14px",
                border: "1px solid #E0E0E0", borderRadius: "8px",
                fontSize: "14px", outline: "none", boxSizing: "border-box",
                fontFamily: "inherit",
              }}
            />
          </div>
        ))}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: "100%", padding: "13px",
            background: loading ? "#90CAF9" : "#1565C0",
            color: "white", border: "none",
            borderRadius: "8px", fontSize: "15px",
            fontWeight: "bold", cursor: loading ? "default" : "pointer",
            marginTop: "8px",
          }}
        >
          {loading ? "Registering..." : "🚀 Start Free Trial"}
        </button>

        <p style={{ textAlign: "center", color: "#999", fontSize: "12px", marginTop: "16px" }}>
          No credit card required • Cancel anytime
        </p>
      </div>
    </div>
  );
}

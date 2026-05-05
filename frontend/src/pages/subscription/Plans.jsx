// ================================================================
// Plans.jsx — Subscription Plans Page
// src/pages/subscription/Plans.jsx
// ================================================================
import { useState } from "react";
import { createPaymentOrder, verifyPayment } from "../../services/licenseService";
import { useLicense } from "../../context/LicenseContext";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: 0,
    priceLabel: "₹0 / forever",
    color: "#757575",
    features: [
      "✅ 5 Employees",
      "✅ Basic Attendance",
      "✅ Leave Management",
      "❌ Face Recognition",
      "❌ Salary Reports",
      "❌ Export PDF/Excel",
      "❌ Tax / TDS",
    ],
  },
  {
    id: "basic",
    name: "Basic",
    price: 499,
    priceLabel: "₹499 / month",
    color: "#1565C0",
    popular: false,
    features: [
      "✅ 25 Employees",
      "✅ Face Attendance",
      "✅ Full Salary System",
      "✅ Tax / TDS",
      "✅ Export PDF & Excel",
      "✅ Leave Management",
      "❌ Loans Module",
    ],
  },
  {
    id: "premium",
    name: "Premium",
    price: 999,
    priceLabel: "₹999 / month",
    color: "#4A148C",
    popular: true,
    features: [
      "✅ Unlimited Employees",
      "✅ Face Attendance",
      "✅ Full Salary System",
      "✅ Tax / TDS + Form 16",
      "✅ Export PDF & Excel",
      "✅ Loans Module",
      "✅ Priority Support",
    ],
  },
];

export default function Plans() {
  const { license, refreshLicense } = useLicense();
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState("");

  const currentPlan = license?.plan || "free";

  async function handleUpgrade(plan) {
    if (plan.price === 0) return;
    setError("");
    setLoading(plan.id);

    try {
      // Step 1: Order create करा
      const order = await createPaymentOrder(plan.id);

      // Step 2: Razorpay checkout open करा
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID,
        amount: order.amount,
        currency: order.currency,
        name: "SalaryPay",
        description: `${plan.name} Plan - Monthly Subscription`,
        order_id: order.order_id,
        handler: async function (response) {
          try {
            // Step 3: Payment verify करा
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            }, plan.id);

            // License refresh करा
            refreshLicense();
            alert(`🎉 ${plan.name} plan activated successfully!`);
          } catch (err) {
            setError("Payment verification failed. Contact support.");
          }
        },
        prefill: {
          email: localStorage.getItem("sp_email") || "",
        },
        theme: { color: plan.color },
        modal: { ondismiss: () => setLoading(null) },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();

    } catch (err) {
      setError(err.message || "Payment failed. Try again.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div style={{ padding: "32px 20px", maxWidth: "960px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "40px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "#1A1A2E", margin: 0 }}>
          Choose Your Plan
        </h1>
        <p style={{ color: "#666", marginTop: "8px", fontSize: "15px" }}>
          {currentPlan === "trial"
            ? `🎉 You have ${license?.days_remaining ?? 0} trial days remaining`
            : `Current plan: ${currentPlan.toUpperCase()}`}
        </p>
      </div>

      {error && (
        <div style={{
          background: "#FFEBEE", color: "#C62828", border: "1px solid #FFCDD2",
          borderRadius: "8px", padding: "12px 16px", marginBottom: "24px", textAlign: "center"
        }}>
          {error}
        </div>
      )}

      {/* Plan Cards */}
      <div style={{ display: "flex", gap: "20px", justifyContent: "center", flexWrap: "wrap" }}>
        {PLANS.map((plan) => {
          const isCurrent = currentPlan === plan.id;
          const isPopular = plan.popular;

          return (
            <div key={plan.id} style={{
              background: "white",
              border: isPopular ? `2px solid ${plan.color}` : "1px solid #E0E0E0",
              borderRadius: "16px",
              padding: "28px 24px",
              width: "280px",
              position: "relative",
              boxShadow: isPopular ? `0 4px 20px rgba(0,0,0,0.1)` : "none",
            }}>
              {isPopular && (
                <div style={{
                  position: "absolute", top: "-14px", left: "50%",
                  transform: "translateX(-50%)",
                  background: plan.color, color: "white",
                  borderRadius: "20px", padding: "4px 16px",
                  fontSize: "12px", fontWeight: "bold", whiteSpace: "nowrap"
                }}>
                  ⭐ Most Popular
                </div>
              )}

              <div style={{ marginBottom: "16px" }}>
                <h2 style={{ margin: 0, color: plan.color, fontSize: "20px", fontWeight: "bold" }}>
                  {plan.name}
                </h2>
                <p style={{ margin: "8px 0 0", fontSize: "22px", fontWeight: "bold", color: "#1A1A2E" }}>
                  {plan.priceLabel}
                </p>
              </div>

              <div style={{ marginBottom: "24px" }}>
                {plan.features.map((f, i) => (
                  <div key={i} style={{ padding: "6px 0", fontSize: "14px", color: "#444", borderBottom: "1px solid #F5F5F5" }}>
                    {f}
                  </div>
                ))}
              </div>

              <button
                onClick={() => handleUpgrade(plan)}
                disabled={isCurrent || plan.price === 0 || loading === plan.id}
                style={{
                  width: "100%",
                  padding: "12px",
                  borderRadius: "8px",
                  border: "none",
                  background: isCurrent ? "#E0E0E0" : plan.price === 0 ? "#F5F5F5" : plan.color,
                  color: isCurrent ? "#999" : plan.price === 0 ? "#757575" : "white",
                  fontWeight: "bold",
                  fontSize: "15px",
                  cursor: isCurrent || plan.price === 0 ? "default" : "pointer",
                  transition: "opacity 0.2s",
                  opacity: loading && loading !== plan.id ? 0.6 : 1,
                }}
              >
                {isCurrent ? "✅ Current Plan"
                  : loading === plan.id ? "Processing..."
                  : plan.price === 0 ? "Free Forever"
                  : `Upgrade to ${plan.name}`}
              </button>
            </div>
          );
        })}
      </div>

      {/* Razorpay script */}
      <script src="https://checkout.razorpay.com/v1/checkout.js" />
    </div>
  );
}

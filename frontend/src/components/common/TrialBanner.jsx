// ================================================================
// TrialBanner.jsx
// Admin layout च्या top मध्ये add करा
// src/components/common/TrialBanner.jsx
// ================================================================
import { useState } from "react";
import { useLicense } from "../../context/LicenseContext";

export default function TrialBanner() {
  const { license } = useLicense();
  const [dismissed, setDismissed] = useState(false);

  if (!license?.valid || dismissed) return null;

  // Trial plan असेल तरच दाखवा
  if (license.plan !== "trial") return null;

  const days = license.days_remaining ?? 0;
  const isUrgent = days <= 2;
  const isWarning = days <= 5;

  const bgColor = isUrgent ? "#B71C1C" : isWarning ? "#E65100" : "#1565C0";
  const emoji = isUrgent ? "⚠️" : isWarning ? "⏰" : "🎉";

  return (
    <div style={{
      background: bgColor,
      color: "white",
      padding: "10px 20px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      fontSize: "14px",
      fontWeight: "500",
    }}>
      <span>
        {emoji} Free Trial: <strong>{days} days remaining</strong>
        {isUrgent && " — Upgrade now to keep your data!"}
        {!isUrgent && " — Upgrade anytime to unlock all features"}
      </span>
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <button
          onClick={() => window.dispatchEvent(new CustomEvent("show-plans"))}
          style={{
            background: "white", color: bgColor,
            border: "none", borderRadius: "6px",
            padding: "6px 16px", fontWeight: "bold",
            cursor: "pointer", fontSize: "13px"
          }}
        >
          Upgrade Now
        </button>
        {!isUrgent && (
          <button
            onClick={() => setDismissed(true)}
            style={{
              background: "transparent", color: "rgba(255,255,255,0.7)",
              border: "none", cursor: "pointer", fontSize: "18px"
            }}
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

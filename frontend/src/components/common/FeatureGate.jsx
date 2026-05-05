// ================================================================
// FeatureGate.jsx
// तुमच्या existing components मध्ये use करा
// src/components/common/FeatureGate.jsx
// ================================================================
import { useLicense } from "../../context/LicenseContext";
import { hasFeature } from "../../services/licenseService";

/**
 * Usage:
 * <FeatureGate feature="attendance_face">
 *   <FaceAttendanceButton />
 * </FeatureGate>
 *
 * <FeatureGate feature="export_pdf" showLock>
 *   <ExportButton />
 * </FeatureGate>
 */
export default function FeatureGate({ feature, children, showLock = true, fallback = null }) {
  const { license } = useLicense();

  if (!license) return null;

  const features = license.features || [];
  const allowed = hasFeature(features, feature);

  if (allowed) return <>{children}</>;

  if (showLock) {
    return (
      <div style={{ position: "relative", display: "inline-block" }}>
        <div style={{ opacity: 0.4, pointerEvents: "none", userSelect: "none" }}>
          {children}
        </div>
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: "rgba(0,0,0,0.05)",
          borderRadius: "8px",
          cursor: "pointer",
        }}
          onClick={() => window.dispatchEvent(new CustomEvent("show-plans"))}
          title="Upgrade to unlock"
        >
          <div style={{
            background: "#1565C0", color: "white",
            borderRadius: "20px", padding: "4px 12px",
            fontSize: "12px", fontWeight: "bold",
            display: "flex", alignItems: "center", gap: "4px"
          }}>
            🔒 Upgrade
          </div>
        </div>
      </div>
    );
  }

  return fallback;
}

// ================================================================
// LicenseContext.jsx
// तुमच्या existing app च्या src/context/LicenseContext.jsx मध्ये add करा
// ================================================================
import { createContext, useContext, useEffect, useState } from "react";
import { checkLicense } from "../services/licenseService";

const LicenseContext = createContext(null);

export function LicenseProvider({ children }) {
  const [license, setLicense] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initLicense();

    // दर 30 मिनिटांनी check करा
    const interval = setInterval(initLicense, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  async function initLicense() {
    try {
      const result = await checkLicense();
      setLicense(result);
    } catch (err) {
      console.error("License check error:", err);
      setLicense({ valid: false, reason: "error" });
    } finally {
      setLoading(false);
    }
  }

  function refreshLicense() {
    setLoading(true);
    initLicense();
  }

  return (
    <LicenseContext.Provider value={{ license, loading, refreshLicense }}>
      {children}
    </LicenseContext.Provider>
  );
}

export function useLicense() {
  return useContext(LicenseContext);
}

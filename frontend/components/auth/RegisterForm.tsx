/**
 * Register Form Component
 *
 * User registration with email/password validation.
 */

import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export default function RegisterForm({ onSuccess, onSwitchToLogin }: RegisterFormProps) {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const getPasswordStrength = (pwd: string): { strength: number; label: string; color: string } => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;

    if (strength <= 1) return { strength, label: "Weak", color: "#ef4444" };
    if (strength === 2) return { strength, label: "Fair", color: "#f59e0b" };
    if (strength === 3) return { strength, label: "Good", color: "#10b981" };
    return { strength, label: "Strong", color: "#10b981" };
  };

  const passwordStrength = password ? getPasswordStrength(password) : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all required fields");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
      setError("Password must contain at least one uppercase letter and one number");
      return;
    }

    setIsLoading(true);

    try {
      await register({
        email,
        password,
        full_name: fullName || undefined,
        invite_code: inviteCode || undefined,
      });
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <div>
        <label
          htmlFor="register-email"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Email *
        </label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "15px",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
      </div>

      <div>
        <label
          htmlFor="register-fullname"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Full Name (optional)
        </label>
        <input
          id="register-fullname"
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="John Doe"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "15px",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
      </div>

      <div>
        <label
          htmlFor="register-password"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Password *
        </label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "15px",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
        {passwordStrength && (
          <div style={{ marginTop: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
            <div
              style={{
                flex: 1,
                height: "4px",
                background: "rgba(255,255,255,0.1)",
                borderRadius: "2px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${(passwordStrength.strength / 4) * 100}%`,
                  height: "100%",
                  background: passwordStrength.color,
                  transition: "width 0.3s",
                }}
              />
            </div>
            <span style={{ fontSize: "12px", color: passwordStrength.color }}>
              {passwordStrength.label}
            </span>
          </div>
        )}
      </div>

      <div>
        <label
          htmlFor="register-confirm-password"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Confirm Password *
        </label>
        <input
          id="register-confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="••••••••"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "15px",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
      </div>

      <div>
        <label
          htmlFor="register-invite-code"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Invite Code (for beta access)
        </label>
        <input
          id="register-invite-code"
          type="text"
          value={inviteCode}
          onChange={(e) => setInviteCode(e.target.value)}
          placeholder="PAIID_BETA_2025"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "rgba(15, 23, 42, 0.6)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            color: "#fff",
            fontSize: "15px",
            outline: "none",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
      </div>

      {error && (
        <div
          style={{
            padding: "12px",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "8px",
            color: "#fca5a5",
            fontSize: "14px",
          }}
        >
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        style={{
          padding: "14px",
          background: isLoading
            ? "rgba(16, 185, 129, 0.5)"
            : "linear-gradient(135deg, #10b981 0%, #059669 100%)",
          border: "none",
          borderRadius: "8px",
          color: "#fff",
          fontSize: "16px",
          fontWeight: 600,
          cursor: isLoading ? "not-allowed" : "pointer",
          transition: "transform 0.2s, box-shadow 0.2s",
          boxShadow: "0 4px 12px rgba(16, 185, 129, 0.3)",
        }}
        onMouseEnter={(e) => !isLoading && (e.currentTarget.style.transform = "translateY(-1px)")}
        onMouseLeave={(e) => (e.currentTarget.style.transform = "translateY(0)")}
      >
        {isLoading ? "Creating account..." : "Register"}
      </button>

      <div style={{ textAlign: "center", fontSize: "14px", color: "#94a3b8" }}>
        Already have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToLogin}
          style={{
            background: "none",
            border: "none",
            color: "#10b981",
            cursor: "pointer",
            textDecoration: "underline",
            fontSize: "14px",
          }}
        >
          Login here
        </button>
      </div>
    </form>
  );
}

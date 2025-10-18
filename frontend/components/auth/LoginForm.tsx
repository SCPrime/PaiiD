/**
 * Login Form Component
 *
 * Email/password login with validation and error handling.
 */

import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export default function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter email and password");
      return;
    }

    setIsLoading(true);

    try {
      await login(email, password);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      <div>
        <label
          htmlFor="login-email"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Email
        </label>
        <input
          id="login-email"
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
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.6)")}
          onBlur={(e) => (e.target.style.borderColor = "rgba(16, 185, 129, 0.3)")}
        />
      </div>

      <div>
        <label
          htmlFor="login-password"
          style={{
            display: "block",
            marginBottom: "8px",
            color: "#cbd5e1",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Password
        </label>
        <input
          id="login-password"
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
            transition: "border-color 0.2s",
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
        {isLoading ? "Logging in..." : "Login"}
      </button>

      <div style={{ textAlign: "center", fontSize: "14px", color: "#94a3b8" }}>
        Don&apos;t have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToRegister}
          style={{
            background: "none",
            border: "none",
            color: "#10b981",
            cursor: "pointer",
            textDecoration: "underline",
            fontSize: "14px",
          }}
        >
          Register here
        </button>
      </div>
    </form>
  );
}

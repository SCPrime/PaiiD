/**
 * User Profile Dropdown
 *
 * Shows user avatar/info with dropdown menu for profile and logout.
 */

import { useState, useRef, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";

export default function UserProfileDropdown() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  if (!user) return null;

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const displayName = user.full_name || user.email;
  const initials = getInitials(displayName);

  return (
    <div ref={dropdownRef} style={{ position: "relative" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "8px 12px",
          background: "rgba(30, 41, 59, 0.6)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          borderRadius: "12px",
          color: "#fff",
          cursor: "pointer",
          transition: "all 0.2s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "rgba(30, 41, 59, 0.8)";
          e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.5)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "rgba(30, 41, 59, 0.6)";
          e.currentTarget.style.borderColor = "rgba(16, 185, 129, 0.3)";
        }}
      >
        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "13px",
            fontWeight: 700,
          }}
        >
          {initials}
        </div>
        <div className="user-info">
          <div style={{ fontSize: "14px", fontWeight: 600, lineHeight: 1.2 }}>{displayName}</div>
          <div style={{ fontSize: "11px", color: "#94a3b8", lineHeight: 1.2, marginTop: "2px" }}>
            {user.role}
          </div>
        </div>
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          style={{
            transform: isOpen ? "rotate(180deg)" : "rotate(0)",
            transition: "transform 0.2s",
          }}
        >
          <path
            d="M4 6l4 4 4-4"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            minWidth: "220px",
            background: "rgba(30, 41, 59, 0.98)",
            backdropFilter: "blur(20px)",
            border: "1px solid rgba(16, 185, 129, 0.2)",
            borderRadius: "12px",
            boxShadow: "0 12px 32px rgba(0, 0, 0, 0.4)",
            overflow: "hidden",
            zIndex: 1000,
            animation: "fadeIn 0.2s ease-out",
          }}
        >
          <div style={{ padding: "16px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <div style={{ fontSize: "14px", fontWeight: 600, color: "#fff", marginBottom: "4px" }}>
              {displayName}
            </div>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>{user.email}</div>
            <div
              style={{
                marginTop: "8px",
                padding: "4px 8px",
                background: "rgba(16, 185, 129, 0.1)",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                borderRadius: "6px",
                fontSize: "11px",
                color: "#10b981",
                display: "inline-block",
                textTransform: "capitalize",
              }}
            >
              {user.role.replace("_", " ")}
            </div>
          </div>

          <div style={{ padding: "8px" }}>
            <button
              onClick={() => {
                setIsOpen(false);
                // Navigate to settings - for now just close
              }}
              style={{
                width: "100%",
                padding: "12px 16px",
                background: "transparent",
                border: "none",
                color: "#cbd5e1",
                fontSize: "14px",
                textAlign: "left",
                cursor: "pointer",
                borderRadius: "8px",
                transition: "background 0.2s",
                display: "flex",
                alignItems: "center",
                gap: "12px",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <span>⚙️</span>
              Account Settings
            </button>

            <button
              onClick={async () => {
                setIsOpen(false);
                await logout();
              }}
              style={{
                width: "100%",
                padding: "12px 16px",
                background: "transparent",
                border: "none",
                color: "#ef4444",
                fontSize: "14px",
                textAlign: "left",
                cursor: "pointer",
                borderRadius: "8px",
                transition: "background 0.2s",
                display: "flex",
                alignItems: "center",
                gap: "12px",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(239, 68, 68, 0.1)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <span>🚪</span>
              Logout
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        .user-info {
          text-align: left;
          display: none;
        }

        @media (min-width: 640px) {
          .user-info {
            display: block;
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}

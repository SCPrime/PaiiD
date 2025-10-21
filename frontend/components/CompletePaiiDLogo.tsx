/**
 * 🔒 LOCKED PaiiD LOGO COMPONENT - v46 FINAL
 *
 * DO NOT MODIFY THIS FILE
 * This is the definitive, working version of the PaiiD logo
 *
 * Features:
 * - Full "PaiiD" branding with animated π symbol
 * - Dual clickable dots on π (left and right)
 * - Multiple size variants (xs, small, medium, large, xlarge, custom)
 * - Optional subtitles
 * - Built-in v46 modal interface
 *
 * Colors (NEVER change these):
 * - Teal: #45f0c0
 * - Dark backgrounds: #0f172a, #1e293b
 * - Light text: #cbd5e1
 * - Muted text: #94a3b8
 *
 * Usage:
 * <PaiiDLogo size="medium" showSubtitle={true} />
 * - onClick prop will override internal modal (use carefully!)
 * - Without onClick, clicking π opens v46 interface automatically
 *
 * Locked by: Dr. SC Prime & Dr. Cursor Claude
 * Date: October 20, 2025
 * Version: v46 Final
 */

"use client";

import React, { useState } from "react";

interface PaiiDLogoProps {
  size?: "xs" | "small" | "medium" | "large" | "xlarge" | "custom";
  customFontSize?: number;
  showSubtitle?: boolean;
  onClick?: () => void; // ⚠️ If provided, overrides v46 modal
  fullPage?: boolean;
  className?: string;
}

const PaiiDLogoLocked: React.FC<PaiiDLogoProps> = ({
  size = "xlarge",
  customFontSize,
  showSubtitle = true,
  onClick,
  fullPage = false,
  className = "",
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [query, setQuery] = useState("");

  // Size mapping (LOCKED - DO NOT MODIFY)
  const sizeMap = {
    xs: 18,
    small: 36,
    medium: 64,
    large: 96,
    xlarge: 120,
    custom: customFontSize || 120,
  };

  const fontSize = customFontSize || sizeMap[size];

  // Proportional calculations (LOCKED)
  const dotSize = fontSize * 0.1;
  const dotTop = fontSize * 0.483;
  const subtitleSize1 = fontSize * 0.22;
  const subtitleSize2 = fontSize * 0.18;

  const handlePiClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onClick) {
      onClick(); // External onClick overrides modal
    } else {
      setShowAIModal(true); // Default: show v46 interface
      setIsClosing(false);
      console.log("AI Launch triggered!");
    }
  };

  const handleCloseModal = () => {
    setIsClosing(true);
    setTimeout(() => {
      setShowAIModal(false);
      setIsClosing(false);
    }, 300);
  };

  const handleQuerySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      console.log("User query:", query);
      // TODO: Send to AI backend
    }
  };

  const wrapperStyle: React.CSSProperties = fullPage
    ? {
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px",
      }
    : {
        display: "inline-block",
      };

  return (
    <div className={className} style={wrapperStyle}>
      {/* 🔒 LOCKED CSS ANIMATIONS */}
      <style>
        {`
          @keyframes glow-ai {
            0%, 100% {
              text-shadow:
                0 0 15px rgba(69, 240, 192, 0.6),
                0 0 30px rgba(69, 240, 192, 0.4);
            }
            50% {
              text-shadow:
                0 0 25px rgba(69, 240, 192, 0.9),
                0 0 50px rgba(69, 240, 192, 0.6),
                0 0 75px rgba(69, 240, 192, 0.3);
            }
          }

          @keyframes slideUpFromBottom {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
          }

          @keyframes slideDownToBottom {
            from { transform: translateY(0); opacity: 1; }
            to { transform: translateY(100%); opacity: 0; }
          }

          .pi-symbol {
            position: relative;
            display: inline-block;
          }

          /* Dot styles for different sizes (LOCKED) */
          .pi-dot-left {
            position: absolute; top: 58px; left: 22%;
            width: 12px; height: 12px;
            background: #45f0c0; border-radius: 50%;
            box-shadow: 0 0 10px rgba(69, 240, 192, 0.8);
            cursor: pointer; transition: transform 0.2s ease;
          }
          .pi-dot-right {
            position: absolute; top: 58px; right: 22%;
            width: 12px; height: 12px;
            background: #45f0c0; border-radius: 50%;
            box-shadow: 0 0 10px rgba(69, 240, 192, 0.8);
            cursor: pointer; transition: transform 0.2s ease;
          }
          .pi-dot-left-md { position: absolute; top: 23px; left: 22%; width: 5px; height: 5px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 8px rgba(69, 240, 192, 0.8); }
          .pi-dot-right-md { position: absolute; top: 23px; right: 22%; width: 5px; height: 5px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 8px rgba(69, 240, 192, 0.8); }
          .pi-dot-left-sm { position: absolute; top: 10px; left: 22%; width: 2.5px; height: 2.5px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 5px rgba(69, 240, 192, 0.8); }
          .pi-dot-right-sm { position: absolute; top: 10px; right: 22%; width: 2.5px; height: 2.5px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 5px rgba(69, 240, 192, 0.8); }
          .pi-dot-left-xs { position: absolute; top: 9px; left: 22%; width: 2px; height: 2px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 4px rgba(69, 240, 192, 0.8); }
          .pi-dot-right-xs { position: absolute; top: 9px; right: 22%; width: 2px; height: 2px; background: #45f0c0; border-radius: 50%; box-shadow: 0 0 4px rgba(69, 240, 192, 0.8); }
        `}
      </style>

      {/* 🔒 LOCKED LOGO STRUCTURE */}
      <div
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: "bold",
          fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
          display: "flex",
          alignItems: "center",
          marginBottom: fullPage ? "20px" : "0",
          userSelect: "none",
        }}
      >
        <span style={{ color: "#45f0c0" }}>P</span>
        <span style={{ color: "#45f0c0" }}>a</span>
        <span
          onClick={handlePiClick}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            color: "#45f0c0",
            animation: "glow-ai 3s ease-in-out infinite",
            cursor: "pointer",
            transition: "transform 0.2s ease",
            transform: isHovered ? "scale(1.1)" : "scale(1)",
          }}
        >
          <span className="pi-symbol">
            <span className="pi-dot-left" onClick={handlePiClick}></span>
            <span className="pi-dot-right" onClick={handlePiClick}></span>
            π
          </span>
        </span>
        <span style={{ color: "#45f0c0" }}>D</span>
      </div>

      {/* 🔒 LOCKED SUBTITLES */}
      {showSubtitle && (
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              fontSize: `${subtitleSize1}px`,
              color: "#cbd5e1",
              marginBottom: "8px",
              fontFamily: '"Inter", sans-serif',
              letterSpacing: "0.5px",
            }}
          >
            Personal <span style={{ fontStyle: "italic" }}>artificial intelligence</span>
            /<span style={{ fontStyle: "italic" }}>investment</span> Dashboard
          </div>
          <div
            style={{
              fontSize: `${subtitleSize2}px`,
              color: "#94a3b8",
              fontFamily: '"Inter", sans-serif',
            }}
          >
            10 Stage Workflow
          </div>
        </div>
      )}

      {/* 🔒 LOCKED FULL-PAGE INSTRUCTION */}
      {fullPage && (
        <div
          style={{
            marginTop: "40px",
            padding: "16px 32px",
            background: "rgba(69, 240, 192, 0.1)",
            border: "1px solid rgba(69, 240, 192, 0.3)",
            borderRadius: "8px",
            color: "#45f0c0",
            fontSize: "14px",
            fontFamily: '"Inter", sans-serif',
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: "6px",
          }}
        >
          <span>Click the π symbol to launch PaiiD Assistant interface</span>
        </div>
      )}

      {/* 🔒 LOCKED v46 MODAL INTERFACE */}
      {showAIModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.6)",
            zIndex: 1000,
            display: "flex",
            alignItems: "flex-end",
          }}
        >
          <div
            style={{
              width: "100%",
              background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
              border: "2px solid #45f0c0",
              borderBottom: "none",
              borderTopLeftRadius: "24px",
              borderTopRightRadius: "24px",
              padding: "40px",
              boxShadow: "0 -10px 50px rgba(69, 240, 192, 0.3)",
              animation: isClosing
                ? "slideDownToBottom 0.3s ease-out forwards"
                : "slideUpFromBottom 0.3s ease-out forwards",
            }}
          >
            {/* Close button */}
            <button
              onClick={handleCloseModal}
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                color: "#45f0c0",
                fontSize: "32px",
                cursor: "pointer",
                padding: "8px",
                lineHeight: 1,
                fontWeight: "bold",
              }}
            >
              ×
            </button>

            {/* Title: "PaiiD Interface" */}
            <div
              style={{
                marginBottom: "20px",
                textAlign: "center",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: "12px",
              }}
            >
              <div
                style={{
                  fontSize: "48px",
                  fontWeight: "bold",
                  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <span style={{ color: "#45f0c0" }}>P</span>
                <span style={{ color: "#45f0c0" }}>a</span>
                <span
                  style={{
                    color: "#45f0c0",
                    animation: "glow-ai 3s ease-in-out infinite",
                    position: "relative",
                  }}
                >
                  <span className="pi-symbol">
                    <span className="pi-dot-left-md"></span>
                    <span className="pi-dot-right-md"></span>
                    π
                  </span>
                </span>
                <span style={{ color: "#45f0c0" }}>D</span>
              </div>
              <span
                style={{
                  color: "#cbd5e1",
                  fontSize: "24px",
                  fontFamily: '"Inter", sans-serif',
                }}
              >
                Interface
              </span>
            </div>

            {/* Subtitle */}
            <div
              style={{
                color: "#cbd5e1",
                fontSize: "16px",
                lineHeight: "1.6",
                textAlign: "center",
                marginBottom: "30px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                flexWrap: "wrap",
                gap: "6px",
              }}
            >
              <span>This is your</span>
              <span
                style={{
                  fontSize: "20px",
                  fontWeight: "bold",
                  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                  display: "inline-flex",
                  alignItems: "center",
                }}
              >
                <span style={{ color: "#45f0c0" }}>P</span>
                <span style={{ color: "#45f0c0" }}>a</span>
                <span
                  style={{
                    color: "#45f0c0",
                    animation: "glow-ai 3s ease-in-out infinite",
                    position: "relative",
                  }}
                >
                  <span className="pi-symbol">
                    <span className="pi-dot-left-sm"></span>
                    <span className="pi-dot-right-sm"></span>
                    π
                  </span>
                </span>
                <span style={{ color: "#45f0c0" }}>D</span>
              </span>
              <span>investment assistance to inform your financial decisions</span>
            </div>

            {/* Capabilities box */}
            <div
              style={{
                background: "rgba(69, 240, 192, 0.1)",
                border: "1px solid rgba(69, 240, 192, 0.3)",
                borderRadius: "12px",
                padding: "24px",
                color: "#94a3b8",
                fontSize: "14px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  color: "#45f0c0",
                  fontSize: "18px",
                  marginBottom: "12px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                <span
                  style={{
                    fontSize: "20px",
                    fontWeight: "bold",
                    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                    display: "inline-flex",
                    alignItems: "center",
                  }}
                >
                  <span style={{ color: "#45f0c0" }}>P</span>
                  <span style={{ color: "#45f0c0" }}>a</span>
                  <span
                    style={{
                      color: "#45f0c0",
                      animation: "glow-ai 3s ease-in-out infinite",
                      position: "relative",
                    }}
                  >
                    <span className="pi-symbol">
                      <span className="pi-dot-left-sm"></span>
                      <span className="pi-dot-right-sm"></span>
                      π
                    </span>
                  </span>
                  <span style={{ color: "#45f0c0" }}>D</span>
                </span>
                <span>Capabilities Active:</span>
              </div>
              <ul style={{ margin: "15px 0", paddingLeft: "20px", lineHeight: "1.8" }}>
                <li>Portfolio Analysis & Optimization</li>
                <li>Market Sentiment Analysis</li>
                <li>Risk Assessment & Management</li>
                <li>Investment Strategy Recommendations</li>
                <li>Real-time Market Insights</li>
              </ul>
            </div>

            {/* Ask PaiiD input */}
            <form onSubmit={handleQuerySubmit} style={{ marginTop: "20px" }}>
              <div
                style={{
                  marginBottom: "12px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  color: "#45f0c0",
                  fontSize: "16px",
                  fontWeight: "bold",
                }}
              >
                <span>Ask</span>
                <span
                  style={{
                    fontSize: "20px",
                    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                    display: "inline-flex",
                    alignItems: "center",
                  }}
                >
                  <span>P</span>
                  <span>a</span>
                  <span style={{ position: "relative" }}>
                    <span className="pi-symbol">
                      <span className="pi-dot-left-sm"></span>
                      <span className="pi-dot-right-sm"></span>
                      π
                    </span>
                  </span>
                  <span>D</span>
                </span>
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your investment question here..."
                style={{
                  width: "100%",
                  padding: "16px",
                  background: "#0f172a",
                  border: "2px solid #45f0c0",
                  borderRadius: "8px",
                  color: "#45f0c0",
                  fontSize: "16px",
                  fontFamily: '"Inter", sans-serif',
                  outline: "none",
                  boxSizing: "border-box",
                }}
              />
              <div
                style={{
                  marginTop: "8px",
                  fontSize: "12px",
                  color: "#94a3b8",
                  textAlign: "center",
                }}
              >
                Press Enter to submit
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PaiiDLogoLocked;

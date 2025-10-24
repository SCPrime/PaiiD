import { logger } from "@/lib/logger";
import React, { useState } from "react";

/**
 * 🔒 LOCKED FINAL PaiiD CHAT BOX 🔒
 *
 * DO NOT MODIFY THIS FILE WITHOUT EXPLICIT APPROVAL
 *
 * This is the final approved version with complete logo integration
 * All logos are size 21 and aligned inline with text
 */

interface CompletePaiiDLogoProps {
  size?: number;
  enableModal?: boolean;
}

const CompletePaiiDLogo: React.FC<CompletePaiiDLogoProps> = ({ size = 80, enableModal = true }) => {
  const [showModal, setShowModal] = useState(false);
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const iPiWidth = size * 0.56;
  const leftSpacingGap = size * 0.08;
  const rightSpacingGap = size * 0.02436;
  const viewBoxWidth = size * 2 + iPiWidth + leftSpacingGap + rightSpacingGap;
  const viewBoxHeight = size * 1.5;
  const baseline = size * 1.063;

  const scaleFactor = size / 120;
  const leftDotOffsetX = -15 * scaleFactor;
  const rightDotOffsetX = 15 * scaleFactor;
  const dotOffsetY = -75 * scaleFactor;
  const dotRadius = 6 * scaleFactor;
  const piCenterX = size * 0.55 + size * 0.5 + leftSpacingGap + iPiWidth / 2;

  const capabilitiesLeft = [
    "Morning Routine",
    "Active Positions",
    "Execute Trade",
    "P&L Dashboard",
    "News Review",
  ];

  const capabilitiesRight = [
    "Recommendations",
    "Strategy Builder",
    "Backtesting",
    "Research",
    "Settings",
  ];

  const handleQuerySubmit = async () => {
    if (query.trim()) {
      logger.info("User query submitted", { query });
      const userMessage = query.trim();
      setQuery("");
      setLoading(true);

      try {
        // Call the chat API
        const apiResponse = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [
              {
                role: "user",
                content: userMessage,
              },
            ],
            max_tokens: 2000,
            system:
              "You are PaiiD AI, a helpful trading assistant. Provide concise, actionable trading insights.",
          }),
        });

        if (!apiResponse.ok) {
          const errorData = await apiResponse.json();
          logger.error("Chat API error", errorData);
          setResponse(`Error: ${errorData.detail || "Failed to get response from AI"}`);
          setLoading(false);
          return;
        }

        const data = await apiResponse.json();
        logger.info("AI Response received", { responseLength: data.response?.length || 0 });
        setResponse(data.response || data.content || JSON.stringify(data));
        setLoading(false);
      } catch (error: unknown) {
        logger.error("Chat submission error", error);
        const errorMessage =
          error instanceof Error ? error.message : "Failed to submit chat message";
        setResponse(`Error: ${errorMessage}`);
        setLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleQuerySubmit();
    }
  };

  const handleLogoClick = () => {
    if (enableModal) {
      setShowModal(true);
    }
  };

  return (
    <>
      <div
        style={{
          position: "relative",
          display: "inline-block",
          verticalAlign: "middle",
          cursor: enableModal ? "pointer" : "default",
        }}
        onClick={handleLogoClick}
      >
        <style>{`
        @keyframes ipi-glow-breathe-${size} {
          0%, 100% {
            filter: drop-shadow(0 0 15px rgba(69, 240, 192, 0.6))
                    drop-shadow(0 0 30px rgba(69, 240, 192, 0.4));
          }
          50% {
            filter: drop-shadow(0 0 25px rgba(69, 240, 192, 0.9))
                    drop-shadow(0 0 50px rgba(69, 240, 192, 0.6))
                    drop-shadow(0 0 75px rgba(69, 240, 192, 0.3));
          }
        }
        .ipi-glow-pi-${size} {
          animation: ipi-glow-breathe-${size} 3s ease-in-out infinite;
        }
      `}</style>

        <svg
          width={viewBoxWidth}
          height={viewBoxHeight}
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          style={{ display: "block", overflow: "visible" }}
        >
          <defs>
            <linearGradient id={`paiid-blue-${size}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: "#1a7560", stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: "#0d5a4a", stopOpacity: 1 }} />
            </linearGradient>
          </defs>

          <text
            x={0}
            y={baseline}
            fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
            fontSize={size}
            fontWeight="bold"
            fill={`url(#paiid-blue-${size})`}
          >
            P
          </text>

          <text
            x={size * 0.55}
            y={baseline}
            fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
            fontSize={size}
            fontWeight="bold"
            fill={`url(#paiid-blue-${size})`}
          >
            a
          </text>

          <circle
            cx={piCenterX + leftDotOffsetX}
            cy={baseline + dotOffsetY}
            r={dotRadius}
            fill="#45f0c0"
          />

          <circle
            cx={piCenterX + rightDotOffsetX}
            cy={baseline + dotOffsetY}
            r={dotRadius}
            fill="#45f0c0"
          />

          <text
            x={piCenterX}
            y={baseline}
            textAnchor="middle"
            fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
            fontSize={size}
            fontWeight="bold"
            fill="#45f0c0"
            className={`ipi-glow-pi-${size}`}
          >
            π
          </text>

          <text
            x={size * 0.55 + size * 0.5 + leftSpacingGap + iPiWidth + rightSpacingGap}
            y={baseline}
            fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
            fontSize={size}
            fontWeight="bold"
            fill={`url(#paiid-blue-${size})`}
          >
            D
          </text>
        </svg>
      </div>

      {/* Modal - Shows when logo is clicked */}
      {showModal && (
        <div
          onClick={() => setShowModal(false)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(8px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "95%",
              minWidth: "800px",
              maxWidth: "1100px",
              backgroundColor: "#0f172a",
              borderRadius: "16px",
              padding: "32px",
              boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
              border: "2px solid #45f0c0",
              animation: "slideUp 0.3s ease-out",
              position: "relative",
            }}
          >
            <style>{`
            @keyframes slideUp {
              from {
                opacity: 0;
                transform: translateY(20px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }
          `}</style>

            <button
              onClick={() => setShowModal(false)}
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                color: "#94a3b8",
                fontSize: "24px",
                cursor: "pointer",
                padding: "8px",
                lineHeight: 1,
              }}
            >
              ×
            </button>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                marginBottom: "24px",
              }}
            >
              <span
                style={{
                  fontSize: "24px",
                  fontWeight: "bold",
                  color: "#45f0c0",
                }}
              >
                10 Active
              </span>
              <CompletePaiiDLogo size={32} enableModal={false} />
              <span
                style={{
                  fontSize: "24px",
                  fontWeight: "bold",
                  color: "#cbd5e1",
                  fontStyle: "italic",
                }}
              >
                Abilities
              </span>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "24px",
                marginBottom: "32px",
              }}
            >
              <div>
                <div
                  style={{
                    marginBottom: "12px",
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: "#cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <CompletePaiiDLogo size={21} enableModal={false} />
                  <span style={{ fontStyle: "italic" }}>Abilities</span>
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  {capabilitiesLeft.map((capability, index) => (
                    <div
                      key={index}
                      style={{
                        padding: "12px 16px",
                        backgroundColor: "rgba(15, 23, 42, 0.6)",
                        borderRadius: "8px",
                        border: "1px solid rgba(69, 240, 192, 0.3)",
                        color: "#cbd5e1",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <span style={{ color: "#45f0c0", fontSize: "18px" }}>•</span>
                      {capability}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div
                  style={{
                    marginBottom: "12px",
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: "#cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <CompletePaiiDLogo size={21} enableModal={false} />
                  <span style={{ fontStyle: "italic" }}>Abilities</span>
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  {capabilitiesRight.map((capability, index) => (
                    <div
                      key={index}
                      style={{
                        padding: "12px 16px",
                        backgroundColor: "rgba(15, 23, 42, 0.6)",
                        borderRadius: "8px",
                        border: "1px solid rgba(69, 240, 192, 0.3)",
                        color: "#cbd5e1",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <span style={{ color: "#45f0c0", fontSize: "18px" }}>•</span>
                      {capability}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <div
                style={{
                  marginBottom: "12px",
                  textAlign: "center",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  fontSize: "16px",
                  fontWeight: "bold",
                }}
              >
                <span style={{ color: "#45f0c0" }}>Ask</span>
                <CompletePaiiDLogo size={21} enableModal={false} />
              </div>

              <div style={{ position: "relative" }}>
                {!query && (
                  <div
                    style={{
                      position: "absolute",
                      top: "16px",
                      left: "16px",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                      pointerEvents: "none",
                      color: "#64748b",
                      fontSize: "16px",
                    }}
                  >
                    <span>Investment questions? Ask here to get</span>
                    <CompletePaiiDLogo size={21} enableModal={false} />
                    <span>! ...</span>
                  </div>
                )}

                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
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
                  placeholder="Ask PaiiD AI..."
                />

                {loading && (
                  <div
                    style={{
                      marginTop: "16px",
                      padding: "16px",
                      background: "rgba(69, 240, 192, 0.1)",
                      borderRadius: "8px",
                      color: "#45f0c0",
                      fontSize: "14px",
                      textAlign: "center",
                    }}
                  >
                    Loading response...
                  </div>
                )}

                {response && !loading && (
                  <div
                    style={{
                      marginTop: "16px",
                      padding: "16px",
                      background: "#0f172a",
                      borderRadius: "8px",
                      border: "1px solid #45f0c0",
                      color: "#45f0c0",
                      fontSize: "14px",
                      lineHeight: "1.6",
                      maxHeight: "300px",
                      overflowY: "auto",
                    }}
                  >
                    {response}
                  </div>
                )}
              </div>

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
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const PaiiDChatBoxWithLogo = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const capabilitiesLeft = [
    "Morning Routine",
    "Active Positions",
    "Execute Trade",
    "P&L Dashboard",
    "News Review",
  ];

  const capabilitiesRight = [
    "Recommendations",
    "Strategy Builder",
    "Backtesting",
    "Research",
    "Settings",
  ];

  const handleQuerySubmit = async () => {
    if (query.trim()) {
      logger.info("User query submitted", { query });
      const userMessage = query.trim();
      setQuery("");
      setLoading(true);

      try {
        // Call the chat API
        const apiResponse = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [
              {
                role: "user",
                content: userMessage,
              },
            ],
            max_tokens: 2000,
            system:
              "You are PaiiD AI, a helpful trading assistant. Provide concise, actionable trading insights.",
          }),
        });

        if (!apiResponse.ok) {
          const errorData = await apiResponse.json();
          logger.error("Chat API error", errorData);
          setResponse(`Error: ${errorData.detail || "Failed to get response from AI"}`);
          setLoading(false);
          return;
        }

        const data = await apiResponse.json();
        logger.info("AI Response received", { responseLength: data.response?.length || 0 });
        setResponse(data.response || data.content || JSON.stringify(data));
        setLoading(false);
      } catch (error: unknown) {
        logger.error("Chat submission error", error);
        const errorMessage =
          error instanceof Error ? error.message : "Failed to submit chat message";
        setResponse(`Error: ${errorMessage}`);
        setLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleQuerySubmit();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#0a0e12",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
      }}
    >
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(8px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "95%",
              minWidth: "800px",
              maxWidth: "1100px",
              backgroundColor: "#0f172a",
              borderRadius: "16px",
              padding: "32px",
              boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
              border: "2px solid #45f0c0",
              animation: "slideUp 0.3s ease-out",
              position: "relative",
            }}
          >
            <style>{`
              @keyframes slideUp {
                from {
                  opacity: 0;
                  transform: translateY(20px);
                }
                to {
                  opacity: 1;
                  transform: translateY(0);
                }
              }
            `}</style>

            <button
              onClick={() => setIsOpen(false)}
              style={{
                position: "absolute",
                top: "16px",
                right: "16px",
                background: "transparent",
                border: "none",
                color: "#94a3b8",
                fontSize: "24px",
                cursor: "pointer",
                padding: "8px",
                lineHeight: 1,
              }}
            >
              ×
            </button>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                marginBottom: "24px",
              }}
            >
              <span
                style={{
                  fontSize: "24px",
                  fontWeight: "bold",
                  color: "#45f0c0",
                }}
              >
                5 Active
              </span>
              <CompletePaiiDLogo size={32} />
              <span
                style={{
                  fontSize: "24px",
                  fontWeight: "bold",
                  color: "#cbd5e1",
                  fontStyle: "italic",
                }}
              >
                Abilities
              </span>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "24px",
                marginBottom: "32px",
              }}
            >
              <div>
                <div
                  style={{
                    marginBottom: "12px",
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: "#cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <CompletePaiiDLogo size={21} />
                  <span style={{ fontStyle: "italic" }}>Abilities</span>
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  {capabilitiesLeft.map((capability, index) => (
                    <div
                      key={index}
                      style={{
                        padding: "12px 16px",
                        backgroundColor: "rgba(15, 23, 42, 0.6)",
                        borderRadius: "8px",
                        border: "1px solid rgba(69, 240, 192, 0.3)",
                        color: "#cbd5e1",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <span style={{ color: "#45f0c0", fontSize: "18px" }}>•</span>
                      {index === 0 ? (
                        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                          <CompletePaiiDLogo size={21} />
                          <span>{capability}</span>
                        </div>
                      ) : (
                        capability
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div
                  style={{
                    marginBottom: "12px",
                    fontSize: "14px",
                    fontWeight: "bold",
                    color: "#cbd5e1",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  <CompletePaiiDLogo size={21} />
                  <span style={{ fontStyle: "italic" }}>Abilities</span>
                </div>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px",
                  }}
                >
                  {capabilitiesRight.map((capability, index) => (
                    <div
                      key={index}
                      style={{
                        padding: "12px 16px",
                        backgroundColor: "rgba(15, 23, 42, 0.6)",
                        borderRadius: "8px",
                        border: "1px solid rgba(69, 240, 192, 0.3)",
                        color: "#cbd5e1",
                        fontSize: "14px",
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >
                      <span style={{ color: "#45f0c0", fontSize: "18px" }}>•</span>
                      {index === 0 ? (
                        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                          <CompletePaiiDLogo size={21} />
                          <span>{capability}</span>
                        </div>
                      ) : (
                        capability
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <div
                style={{
                  marginBottom: "12px",
                  textAlign: "center",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "6px",
                  fontSize: "16px",
                  fontWeight: "bold",
                }}
              >
                <span style={{ color: "#45f0c0" }}>Ask</span>
                <CompletePaiiDLogo size={21} />
              </div>

              <div style={{ position: "relative" }}>
                {!query && (
                  <div
                    style={{
                      position: "absolute",
                      top: "16px",
                      left: "16px",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                      pointerEvents: "none",
                      color: "#64748b",
                      fontSize: "16px",
                    }}
                  >
                    <span>Investment questions? Ask here to get</span>
                    <CompletePaiiDLogo size={21} />
                    <span>! ...</span>
                  </div>
                )}

                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
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
                  placeholder="Ask PaiiD AI..."
                />

                {loading && (
                  <div
                    style={{
                      marginTop: "16px",
                      padding: "16px",
                      background: "rgba(69, 240, 192, 0.1)",
                      borderRadius: "8px",
                      color: "#45f0c0",
                      fontSize: "14px",
                      textAlign: "center",
                    }}
                  >
                    Loading response...
                  </div>
                )}

                {response && !loading && (
                  <div
                    style={{
                      marginTop: "16px",
                      padding: "16px",
                      background: "#0f172a",
                      borderRadius: "8px",
                      border: "1px solid #45f0c0",
                      color: "#45f0c0",
                      fontSize: "14px",
                      lineHeight: "1.6",
                      maxHeight: "300px",
                      overflowY: "auto",
                    }}
                  >
                    {response}
                  </div>
                )}
              </div>

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
            </div>
          </div>
        </div>
      )}

      <div
        style={{
          textAlign: "center",
          color: "rgba(255, 255, 255, 0.8)",
          maxWidth: "600px",
          padding: "2rem",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: "1rem",
          }}
        >
          <CompletePaiiDLogo size={80} />
        </div>
        <h1 style={{ color: "#45f0c0", marginBottom: "1rem", fontSize: "2rem" }}>
          🔒 Chat Box with Full Logo - LOCKED FINAL
        </h1>
        <p style={{ marginBottom: "2rem" }}>Complete integration ready for implementation</p>
        <button
          onClick={() => setIsOpen(true)}
          style={{
            padding: "14px 28px",
            backgroundColor: "#45f0c0",
            color: "#0a0e12",
            border: "none",
            borderRadius: "8px",
            fontSize: "16px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Open Chat Box
        </button>
      </div>
    </div>
  );
};

// Export both components for different use cases
export { CompletePaiiDLogo, PaiiDChatBoxWithLogo };
export default CompletePaiiDLogo;

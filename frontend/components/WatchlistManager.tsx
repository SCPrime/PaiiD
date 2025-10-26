import { Plus, Star, Trash2, TrendingUp, X } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { logger } from "../lib/logger";
import {
  UserProfile,
  Watchlist,
  addWatchlist,
  getOrCreateProfile,
  removeWatchlist,
  saveProfile,
} from "../types/profile";

interface WatchlistManagerProps {
  onSymbolClick?: (symbol: string) => void;
  showPrices?: boolean;
  compact?: boolean;
}

interface SymbolPrice {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

const WatchlistManager: React.FC<WatchlistManagerProps> = ({
  onSymbolClick,
  showPrices = true,
  compact = false,
}) => {
  const [profile, setProfile] = useState<UserProfile>(getOrCreateProfile());
  const [selectedWatchlistId, setSelectedWatchlistId] = useState<string | null>(null);
  const [newWatchlistName, setNewWatchlistName] = useState("");
  const [newSymbol, setNewSymbol] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [symbolPrices, setSymbolPrices] = useState<Record<string, SymbolPrice>>({});
  const [loading, setLoading] = useState(false);
  const isMobile = useIsMobile();

  const theme = {
    bg: "rgba(15, 23, 42, 0.7)",
    bgLight: "rgba(30, 41, 59, 0.8)",
    text: "#e2e8f0",
    textMuted: "#94a3b8",
    primary: "#10b981",
    danger: "#ef4444",
    border: "rgba(148, 163, 184, 0.2)",
    warning: "#f59e0b",
    spacing: {
      xs: "4px",
      sm: "8px",
      md: "12px",
      lg: "16px",
      xl: "24px",
    },
  };

  useEffect(() => {
    // Load profile on mount
    const loadedProfile = getOrCreateProfile();
    setProfile(loadedProfile);

    // Set first watchlist as selected if exists
    if (loadedProfile.watchlists.length > 0 && !selectedWatchlistId) {
      setSelectedWatchlistId(loadedProfile.watchlists[0].id);
    }

    // Listen for profile updates from other components
    const handleProfileUpdate = (event: CustomEvent) => {
      setProfile(event.detail);
    };

    window.addEventListener("profile-updated", handleProfileUpdate as EventListener);
    return () => {
      window.removeEventListener("profile-updated", handleProfileUpdate as EventListener);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedWatchlistId]);

  useEffect(() => {
    // Fetch prices for symbols in selected watchlist
    if (showPrices && selectedWatchlistId) {
      const watchlist = profile.watchlists.find((w) => w.id === selectedWatchlistId);
      if (watchlist && watchlist.symbols.length > 0) {
        fetchPrices(watchlist.symbols);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedWatchlistId, showPrices, profile.watchlists]);

  const fetchPrices = async (symbols: string[]) => {
    setLoading(true);
    try {
      const prices: Record<string, SymbolPrice> = {};

      // Fetch all symbols in parallel
      await Promise.all(
        symbols.map(async (symbol) => {
          try {
            const response = await fetch(`/api/proxy/api/stock/${symbol}/info`, {
              headers: {
                Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
              },
            });

            if (response.ok) {
              const data = await response.json();
              prices[symbol] = {
                symbol,
                price: data.current_price,
                change: data.change,
                changePercent: data.change_percent,
              };
            }
          } catch (err) {
            logger.error(`Failed to fetch price for ${symbol}`, err);
          }
        })
      );

      setSymbolPrices(prices);
    } catch (error) {
      logger.error("Failed to fetch prices", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = () => {
    if (!newWatchlistName.trim()) {
      showToast("⚠️ Please enter a watchlist name");
      return;
    }

    const newWatchlist: Watchlist = {
      id: `watchlist-${Date.now()}`,
      name: newWatchlistName.trim(),
      symbols: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const updatedProfile = addWatchlist({ ...profile }, newWatchlist);
    setProfile(updatedProfile);
    saveProfile(updatedProfile);
    setSelectedWatchlistId(newWatchlist.id);
    setNewWatchlistName("");
    setShowCreateForm(false);
    showToast(`✅ Created watchlist "${newWatchlist.name}"`);
  };

  const handleDeleteWatchlist = (watchlistId: string) => {
    const watchlist = profile.watchlists.find((w) => w.id === watchlistId);
    if (!watchlist) return;

    if (!confirm(`Delete watchlist "${watchlist.name}"?`)) return;

    const updatedProfile = removeWatchlist({ ...profile }, watchlistId);
    setProfile(updatedProfile);
    saveProfile(updatedProfile);

    // Select first watchlist if deleted was selected
    if (selectedWatchlistId === watchlistId) {
      setSelectedWatchlistId(
        updatedProfile.watchlists.length > 0 ? updatedProfile.watchlists[0].id : null
      );
    }

    showToast(`✅ Deleted watchlist "${watchlist.name}"`);
  };

  const handleAddSymbol = () => {
    if (!selectedWatchlistId) {
      showToast("⚠️ Please select a watchlist first");
      return;
    }

    const symbol = newSymbol.trim().toUpperCase();
    if (!symbol) {
      showToast("⚠️ Please enter a symbol");
      return;
    }

    const watchlistIndex = profile.watchlists.findIndex((w) => w.id === selectedWatchlistId);
    if (watchlistIndex === -1) return;

    // Check if symbol already exists
    if (profile.watchlists[watchlistIndex].symbols.includes(symbol)) {
      showToast(`⚠️ ${symbol} is already in this watchlist`);
      return;
    }

    const updatedProfile = { ...profile };
    updatedProfile.watchlists[watchlistIndex].symbols.push(symbol);
    updatedProfile.watchlists[watchlistIndex].updatedAt = new Date().toISOString();

    setProfile(updatedProfile);
    saveProfile(updatedProfile);
    setNewSymbol("");
    showToast(`✅ Added ${symbol} to watchlist`);

    // Fetch price for new symbol
    if (showPrices) {
      fetchPrices([symbol]);
    }
  };

  const handleRemoveSymbol = (watchlistId: string, symbol: string) => {
    const watchlistIndex = profile.watchlists.findIndex((w) => w.id === watchlistId);
    if (watchlistIndex === -1) return;

    const updatedProfile = { ...profile };
    updatedProfile.watchlists[watchlistIndex].symbols = updatedProfile.watchlists[
      watchlistIndex
    ].symbols.filter((s) => s !== symbol);
    updatedProfile.watchlists[watchlistIndex].updatedAt = new Date().toISOString();

    setProfile(updatedProfile);
    saveProfile(updatedProfile);
    showToast(`✅ Removed ${symbol} from watchlist`);

    // Remove price data
    const newPrices = { ...symbolPrices };
    delete newPrices[symbol];
    setSymbolPrices(newPrices);
  };

  const showToast = (message: string) => {
    // Dispatch custom event for toast notifications
    window.dispatchEvent(new CustomEvent("show-toast", { detail: { message } }));
  };

  const selectedWatchlist = profile.watchlists.find((w) => w.id === selectedWatchlistId);

  if (compact) {
    // Compact view - just symbols with prices
    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: theme.spacing.sm,
          width: "100%",
        }}
      >
        {selectedWatchlist?.symbols.map((symbol) => {
          const priceData = symbolPrices[symbol];
          return (
            <div
              key={symbol}
              onClick={() => onSymbolClick?.(symbol)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: theme.spacing.md,
                background: theme.bgLight,
                borderRadius: "8px",
                cursor: onSymbolClick ? "pointer" : "default",
                transition: "all 0.2s",
              }}
            >
              <div style={{ fontWeight: 600, color: theme.text }}>{symbol}</div>
              {priceData && (
                <div style={{ textAlign: "right" }}>
                  <div style={{ color: theme.text }}>${priceData.price.toFixed(2)}</div>
                  <div
                    style={{
                      fontSize: "12px",
                      color: priceData.change >= 0 ? theme.primary : theme.danger,
                    }}
                  >
                    {priceData.change >= 0 ? "+" : ""}
                    {priceData.changePercent.toFixed(2)}%
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: theme.spacing.lg,
        width: "100%",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: theme.spacing.md,
        }}
      >
        <h2
          style={{
            fontSize: isMobile ? "20px" : "24px",
            fontWeight: 700,
            color: theme.text,
            margin: 0,
          }}
        >
          Watchlists
        </h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
            padding: `${theme.spacing.sm} ${theme.spacing.md}`,
            background: theme.primary,
            color: "#0f172a",
            border: "none",
            borderRadius: "8px",
            fontSize: "14px",
            fontWeight: 600,
            cursor: "pointer",
            transition: "all 0.2s",
          }}
        >
          <Plus size={18} />
          Create Watchlist
        </button>
      </div>

      {/* Create Watchlist Form */}
      {showCreateForm && (
        <div
          style={{
            padding: theme.spacing.lg,
            background: theme.bg,
            borderRadius: "12px",
            border: `1px solid ${theme.border}`,
          }}
        >
          <h3
            style={{
              fontSize: "18px",
              fontWeight: 600,
              color: theme.text,
              margin: `0 0 ${theme.spacing.md} 0`,
            }}
          >
            Create New Watchlist
          </h3>
          <div
            style={{
              display: "flex",
              gap: theme.spacing.sm,
              flexDirection: isMobile ? "column" : "row",
            }}
          >
            <input
              type="text"
              value={newWatchlistName}
              onChange={(e) => setNewWatchlistName(e.target.value)}
              placeholder="Watchlist name (e.g., Tech Stocks)"
              style={{
                flex: 1,
                padding: theme.spacing.md,
                background: theme.bgLight,
                border: `1px solid ${theme.border}`,
                borderRadius: "8px",
                color: theme.text,
                fontSize: "14px",
                outline: "none",
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreateWatchlist();
                if (e.key === "Escape") setShowCreateForm(false);
              }}
            />
            <button
              onClick={handleCreateWatchlist}
              style={{
                padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
                background: theme.primary,
                color: "#0f172a",
                border: "none",
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              Create
            </button>
            <button
              onClick={() => setShowCreateForm(false)}
              style={{
                padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
                background: theme.bgLight,
                color: theme.text,
                border: `1px solid ${theme.border}`,
                borderRadius: "8px",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Watchlist Tabs */}
      {profile.watchlists.length > 0 ? (
        <>
          <div
            style={{
              display: "flex",
              gap: theme.spacing.sm,
              overflowX: "auto",
              padding: `${theme.spacing.xs} 0`,
            }}
          >
            {profile.watchlists.map((watchlist) => (
              <button
                key={watchlist.id}
                onClick={() => setSelectedWatchlistId(watchlist.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: theme.spacing.sm,
                  padding: `${theme.spacing.sm} ${theme.spacing.md}`,
                  background: selectedWatchlistId === watchlist.id ? theme.primary : theme.bgLight,
                  color: selectedWatchlistId === watchlist.id ? "#0f172a" : theme.text,
                  border: `1px solid ${selectedWatchlistId === watchlist.id ? theme.primary : theme.border}`,
                  borderRadius: "8px",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  transition: "all 0.2s",
                }}
              >
                {watchlist.name}
                <span
                  style={{
                    padding: "2px 6px",
                    background:
                      selectedWatchlistId === watchlist.id ? "rgba(15, 23, 42, 0.2)" : theme.bg,
                    borderRadius: "4px",
                    fontSize: "12px",
                  }}
                >
                  {watchlist.symbols.length}
                </span>
              </button>
            ))}
          </div>

          {/* Selected Watchlist Content */}
          {selectedWatchlist && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: theme.spacing.md,
              }}
            >
              {/* Watchlist Header */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: theme.spacing.lg,
                  background: theme.bg,
                  borderRadius: "12px",
                  border: `1px solid ${theme.border}`,
                }}
              >
                <div>
                  <h3
                    style={{
                      fontSize: "18px",
                      fontWeight: 600,
                      color: theme.text,
                      margin: 0,
                    }}
                  >
                    {selectedWatchlist.name}
                  </h3>
                  <p
                    style={{
                      fontSize: "12px",
                      color: theme.textMuted,
                      margin: `${theme.spacing.xs} 0 0 0`,
                    }}
                  >
                    {selectedWatchlist.symbols.length} symbols • Updated{" "}
                    {new Date(selectedWatchlist.updatedAt).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteWatchlist(selectedWatchlist.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: theme.spacing.sm,
                    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
                    background: "rgba(239, 68, 68, 0.1)",
                    color: theme.danger,
                    border: `1px solid ${theme.danger}`,
                    borderRadius: "8px",
                    fontSize: "14px",
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                >
                  <Trash2 size={16} />
                  {!isMobile && "Delete"}
                </button>
              </div>

              {/* Add Symbol Form */}
              <div
                style={{
                  padding: theme.spacing.lg,
                  background: theme.bg,
                  borderRadius: "12px",
                  border: `1px solid ${theme.border}`,
                }}
              >
                <h4
                  style={{
                    fontSize: "16px",
                    fontWeight: 600,
                    color: theme.text,
                    margin: `0 0 ${theme.spacing.md} 0`,
                  }}
                >
                  Add Symbol
                </h4>
                <div
                  style={{
                    display: "flex",
                    gap: theme.spacing.sm,
                    flexDirection: isMobile ? "column" : "row",
                  }}
                >
                  <input
                    type="text"
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                    placeholder="Symbol (e.g., AAPL, TSLA)"
                    style={{
                      flex: 1,
                      padding: theme.spacing.md,
                      background: theme.bgLight,
                      border: `1px solid ${theme.border}`,
                      borderRadius: "8px",
                      color: theme.text,
                      fontSize: "14px",
                      outline: "none",
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleAddSymbol();
                    }}
                  />
                  <button
                    onClick={handleAddSymbol}
                    disabled={!newSymbol.trim()}
                    style={{
                      padding: `${theme.spacing.sm} ${theme.spacing.lg}`,
                      background: newSymbol.trim() ? theme.primary : theme.textMuted,
                      color: "#0f172a",
                      border: "none",
                      borderRadius: "8px",
                      fontSize: "14px",
                      fontWeight: 600,
                      cursor: newSymbol.trim() ? "pointer" : "not-allowed",
                      whiteSpace: "nowrap",
                    }}
                  >
                    <Plus
                      size={18}
                      style={{ verticalAlign: "middle", marginRight: theme.spacing.xs }}
                    />
                    Add Symbol
                  </button>
                </div>
              </div>

              {/* Symbols List */}
              {selectedWatchlist.symbols.length > 0 ? (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fill, minmax(300px, 1fr))",
                    gap: theme.spacing.md,
                  }}
                >
                  {selectedWatchlist.symbols.map((symbol) => {
                    const priceData = symbolPrices[symbol];
                    return (
                      <div
                        key={symbol}
                        style={{
                          padding: theme.spacing.lg,
                          background: theme.bg,
                          borderRadius: "12px",
                          border: `1px solid ${theme.border}`,
                          display: "flex",
                          flexDirection: "column",
                          gap: theme.spacing.md,
                          cursor: onSymbolClick ? "pointer" : "default",
                          transition: "all 0.2s",
                        }}
                        onClick={() => onSymbolClick?.(symbol)}
                      >
                        {/* Symbol Header */}
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                          }}
                        >
                          <div>
                            <div
                              style={{
                                fontSize: "20px",
                                fontWeight: 700,
                                color: theme.text,
                              }}
                            >
                              {symbol}
                            </div>
                            {priceData && (
                              <div
                                style={{
                                  fontSize: "24px",
                                  fontWeight: 600,
                                  color: theme.text,
                                  marginTop: theme.spacing.xs,
                                }}
                              >
                                ${priceData.price.toFixed(2)}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemoveSymbol(selectedWatchlist.id, symbol);
                            }}
                            style={{
                              padding: theme.spacing.sm,
                              background: "rgba(239, 68, 68, 0.1)",
                              color: theme.danger,
                              border: "none",
                              borderRadius: "6px",
                              cursor: "pointer",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                            }}
                          >
                            <X size={16} />
                          </button>
                        </div>

                        {/* Price Change */}
                        {priceData && (
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: theme.spacing.sm,
                            }}
                          >
                            <TrendingUp
                              size={16}
                              style={{
                                color: priceData.change >= 0 ? theme.primary : theme.danger,
                                transform: priceData.change < 0 ? "rotate(180deg)" : "none",
                              }}
                            />
                            <span
                              style={{
                                fontSize: "14px",
                                fontWeight: 600,
                                color: priceData.change >= 0 ? theme.primary : theme.danger,
                              }}
                            >
                              {priceData.change >= 0 ? "+" : ""}
                              {priceData.change.toFixed(2)}(
                              {priceData.changePercent >= 0 ? "+" : ""}
                              {priceData.changePercent.toFixed(2)}%)
                            </span>
                          </div>
                        )}

                        {loading && !priceData && (
                          <div
                            style={{
                              fontSize: "12px",
                              color: theme.textMuted,
                            }}
                          >
                            Loading price...
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div
                  style={{
                    padding: `${theme.spacing.xl} ${theme.spacing.lg}`,
                    background: theme.bg,
                    borderRadius: "12px",
                    border: `1px solid ${theme.border}`,
                    textAlign: "center",
                    color: theme.textMuted,
                  }}
                >
                  <Star size={48} style={{ margin: "0 auto 12px", opacity: 0.3 }} />
                  <p style={{ margin: 0, fontSize: "16px" }}>No symbols in this watchlist yet</p>
                  <p style={{ margin: "8px 0 0 0", fontSize: "14px" }}>
                    Add symbols using the form above
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      ) : (
        <div
          style={{
            padding: `${theme.spacing.xl} ${theme.spacing.lg}`,
            background: theme.bg,
            borderRadius: "12px",
            border: `1px solid ${theme.border}`,
            textAlign: "center",
            color: theme.textMuted,
          }}
        >
          <Star size={48} style={{ margin: "0 auto 12px", opacity: 0.3 }} />
          <p style={{ margin: 0, fontSize: "16px" }}>No watchlists created yet</p>
          <p style={{ margin: "8px 0 0 0", fontSize: "14px" }}>
            Create your first watchlist to track stocks
          </p>
        </div>
      )}
    </div>
  );
};

export default WatchlistManager;

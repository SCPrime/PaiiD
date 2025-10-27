/**
 * StoryboardCanvas Component
 * Screenshot capture + annotation tools for UI refinement
 */

import React, { useState, useRef, useEffect } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

type AnnotationTool = 'none' | 'arrow' | 'box' | 'text' | 'highlight';

interface Annotation {
  id: string;
  type: AnnotationTool;
  x: number;
  y: number;
  width?: number;
  height?: number;
  endX?: number;
  endY?: number;
  text?: string;
  color: string;
}

interface StoryboardVersion {
  id: string;
  timestamp: number;
  imageDataUrl: string;
  annotations: Annotation[];
  title: string;
}

interface StoryboardCanvasProps {
  onClose: () => void;
}

const StoryboardCanvas: React.FC<StoryboardCanvasProps> = ({ onClose }) => {
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);
  const [currentTool, setCurrentTool] = useState<AnnotationTool>('none');
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [currentAnnotation, setCurrentAnnotation] = useState<Annotation | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentColor, setCurrentColor] = useState('#ef4444'); // Red default
  const [textInput, setTextInput] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);
  const [textPosition, setTextPosition] = useState({ x: 0, y: 0 });
  const [versions, setVersions] = useState<StoryboardVersion[]>([]);
  const [showVersions, setShowVersions] = useState(false);
  const [versionTitle, setVersionTitle] = useState('');

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Load versions from localStorage on mount
  useEffect(() => {
    const savedVersions = localStorage.getItem('storyboard-versions');
    if (savedVersions) {
      try {
        setVersions(JSON.parse(savedVersions));
      } catch (err) {
        console.error('Failed to load storyboard versions:', err);
      }
    }
  }, []);

  // Capture screenshot
  const captureScreenshot = async () => {
    setIsCapturing(true);

    try {
      // Hide the storyboard modal temporarily
      const storyboardModal = document.getElementById('storyboard-modal');
      if (storyboardModal) {
        storyboardModal.style.display = 'none';
      }

      // Wait for render
      await new Promise(resolve => setTimeout(resolve, 100));

      const canvas = await html2canvas(document.body, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#0f172a',
        scale: 1,
        logging: false,
      } as any);

      const dataUrl = canvas.toDataURL('image/png');
      setScreenshot(dataUrl);

      // Restore modal
      if (storyboardModal) {
        storyboardModal.style.display = 'flex';
      }
    } catch (err) {
      console.error('Screenshot capture failed:', err);
      alert('Failed to capture screenshot. Please try again.');

      // Ensure modal is restored on error
      const storyboardModal = document.getElementById('storyboard-modal');
      if (storyboardModal) {
        storyboardModal.style.display = 'flex';
      }
    } finally {
      setIsCapturing(false);
    }
  };

  // Start drawing annotation
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (currentTool === 'none') return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (currentTool === 'text') {
      setTextPosition({ x, y });
      setShowTextInput(true);
      return;
    }

    const newAnnotation: Annotation = {
      id: `annotation-${Date.now()}`,
      type: currentTool,
      x,
      y,
      color: currentColor,
    };

    setCurrentAnnotation(newAnnotation);
    setIsDrawing(true);
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !currentAnnotation) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    if (currentTool === 'arrow') {
      setCurrentAnnotation({ ...currentAnnotation, endX, endY });
    } else if (currentTool === 'box' || currentTool === 'highlight') {
      setCurrentAnnotation({
        ...currentAnnotation,
        width: endX - currentAnnotation.x,
        height: endY - currentAnnotation.y,
      });
    }
  };

  const handleMouseUp = () => {
    if (currentAnnotation) {
      setAnnotations([...annotations, currentAnnotation]);
      setCurrentAnnotation(null);
    }
    setIsDrawing(false);
  };

  // Add text annotation
  const addTextAnnotation = () => {
    if (!textInput.trim()) return;

    const newAnnotation: Annotation = {
      id: `annotation-${Date.now()}`,
      type: 'text',
      x: textPosition.x,
      y: textPosition.y,
      text: textInput,
      color: currentColor,
    };

    setAnnotations([...annotations, newAnnotation]);
    setTextInput('');
    setShowTextInput(false);
  };

  // Render annotations on canvas
  useEffect(() => {
    if (!screenshot || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Load screenshot
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // Draw all annotations
      [...annotations, currentAnnotation].filter((ann): ann is Annotation => ann !== null).forEach((ann) => {
        ctx.strokeStyle = ann.color;
        ctx.fillStyle = ann.color;
        ctx.lineWidth = 3;

        if (ann.type === 'arrow' && ann.endX !== undefined && ann.endY !== undefined) {
          drawArrow(ctx, ann.x, ann.y, ann.endX, ann.endY, ann.color);
        } else if (ann.type === 'box' && ann.width && ann.height) {
          ctx.strokeRect(ann.x, ann.y, ann.width, ann.height);
        } else if (ann.type === 'highlight' && ann.width && ann.height) {
          ctx.fillStyle = ann.color + '40'; // Add transparency
          ctx.fillRect(ann.x, ann.y, ann.width, ann.height);
        } else if (ann.type === 'text' && ann.text) {
          ctx.font = '16px Inter, sans-serif';
          ctx.fillText(ann.text, ann.x, ann.y);
        }
      });
    };

    img.src = screenshot;
  }, [screenshot, annotations, currentAnnotation]);

  // Draw arrow helper
  const drawArrow = (
    ctx: CanvasRenderingContext2D,
    fromX: number,
    fromY: number,
    toX: number,
    toY: number,
    color: string
  ) => {
    const headLength = 15;
    const angle = Math.atan2(toY - fromY, toX - fromX);

    ctx.beginPath();
    ctx.moveTo(fromX, fromY);
    ctx.lineTo(toX, toY);
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Arrowhead
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(
      toX - headLength * Math.cos(angle - Math.PI / 6),
      toY - headLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      toX - headLength * Math.cos(angle + Math.PI / 6),
      toY - headLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
  };

  // Export as PNG
  const exportAsPNG = () => {
    if (!canvasRef.current) return;

    const link = document.createElement('a');
    link.download = `storyboard-${Date.now()}.png`;
    link.href = canvasRef.current.toDataURL('image/png');
    link.click();
  };

  // Export as PDF
  const exportAsPDF = () => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const imgData = canvas.toDataURL('image/png');

    const pdf = new jsPDF({
      orientation: canvas.width > canvas.height ? 'landscape' : 'portrait',
      unit: 'px',
      format: [canvas.width, canvas.height],
    });

    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
    pdf.save(`storyboard-${Date.now()}.pdf`);
  };

  // Save version
  const saveVersion = () => {
    if (!canvasRef.current) return;

    const title = versionTitle.trim() || `Version ${versions.length + 1}`;
    const newVersion: StoryboardVersion = {
      id: `version-${Date.now()}`,
      timestamp: Date.now(),
      imageDataUrl: canvasRef.current.toDataURL('image/png'),
      annotations: [...annotations],
      title,
    };

    const updatedVersions = [...versions, newVersion];
    setVersions(updatedVersions);
    localStorage.setItem('storyboard-versions', JSON.stringify(updatedVersions));

    setVersionTitle('');
    alert(`Saved as "${title}"`);
  };

  // Load version
  const loadVersion = (version: StoryboardVersion) => {
    setScreenshot(version.imageDataUrl);
    setAnnotations(version.annotations);
    setShowVersions(false);
  };

  // Delete version
  const deleteVersion = (versionId: string) => {
    const updatedVersions = versions.filter(v => v.id !== versionId);
    setVersions(updatedVersions);
    localStorage.setItem('storyboard-versions', JSON.stringify(updatedVersions));
  };

  // Clear annotations
  const clearAnnotations = () => {
    if (confirm('Clear all annotations?')) {
      setAnnotations([]);
    }
  };

  // Undo last annotation
  const undoAnnotation = () => {
    setAnnotations(annotations.slice(0, -1));
  };

  return (
    <div
      id="storyboard-modal"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.95)',
        zIndex: 10000,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 24px',
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '24px', color: '#f1f5f9' }}>
            Storyboard Canvas
          </h2>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Capture, annotate, and refine your UI ideas
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {screenshot && (
            <>
              <button
                onClick={() => setShowVersions(!showVersions)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: '#818cf8',
                  border: '1px solid #818cf8',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Versions ({versions.length})
              </button>

              <button
                onClick={exportAsPNG}
                style={{
                  padding: '8px 16px',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  border: '1px solid #10b981',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Export PNG
              </button>

              <button
                onClick={exportAsPDF}
                style={{
                  padding: '8px 16px',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  border: '1px solid #10b981',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Export PDF
              </button>
            </>
          )}

          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: '#ef4444',
              border: '1px solid #ef4444',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Close (Esc)
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Left Sidebar - Tools */}
        {screenshot && (
          <div
            style={{
              width: '280px',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(10px)',
              padding: '20px',
              overflowY: 'auto',
              borderRight: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#f1f5f9' }}>
              Annotation Tools
            </h3>

            {/* Tool Selection */}
            <div style={{ marginBottom: '20px' }}>
              {[
                { tool: 'none', label: 'Select', icon: '↖' },
                { tool: 'arrow', label: 'Arrow', icon: '→' },
                { tool: 'box', label: 'Box', icon: '□' },
                { tool: 'text', label: 'Text', icon: 'T' },
                { tool: 'highlight', label: 'Highlight', icon: '▮' },
              ].map(({ tool, label, icon }) => (
                <button
                  key={tool}
                  onClick={() => setCurrentTool(tool as AnnotationTool)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    marginBottom: '8px',
                    backgroundColor:
                      currentTool === tool
                        ? 'rgba(99, 102, 241, 0.2)'
                        : 'rgba(255, 255, 255, 0.05)',
                    color: currentTool === tool ? '#818cf8' : '#cbd5e1',
                    border:
                      currentTool === tool
                        ? '1px solid #818cf8'
                        : '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    textAlign: 'left',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                  }}
                >
                  <span style={{ fontSize: '18px' }}>{icon}</span>
                  {label}
                </button>
              ))}
            </div>

            {/* Color Picker */}
            <div style={{ marginBottom: '20px' }}>
              <label
                style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontSize: '14px',
                  color: '#cbd5e1',
                }}
              >
                Color
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'].map(
                  color => (
                    <button
                      key={color}
                      onClick={() => setCurrentColor(color)}
                      style={{
                        width: '36px',
                        height: '36px',
                        backgroundColor: color,
                        border:
                          currentColor === color
                            ? '3px solid white'
                            : '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '6px',
                        cursor: 'pointer',
                      }}
                    />
                  )
                )}
              </div>
            </div>

            {/* Actions */}
            <div style={{ marginBottom: '20px' }}>
              <button
                onClick={undoAnnotation}
                disabled={annotations.length === 0}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginBottom: '8px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  color: annotations.length > 0 ? '#cbd5e1' : '#64748b',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '6px',
                  cursor: annotations.length > 0 ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                }}
              >
                Undo (Ctrl+Z)
              </button>

              <button
                onClick={clearAnnotations}
                disabled={annotations.length === 0}
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: 'rgba(239, 68, 68, 0.1)',
                  color: annotations.length > 0 ? '#ef4444' : '#64748b',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '6px',
                  cursor: annotations.length > 0 ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                }}
              >
                Clear All
              </button>
            </div>

            {/* Save Version */}
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#f1f5f9' }}>
                Save Version
              </h3>
              <input
                type="text"
                placeholder="Version title (optional)"
                value={versionTitle}
                onChange={e => setVersionTitle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginBottom: '8px',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  color: '#f1f5f9',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '6px',
                  fontSize: '14px',
                }}
              />
              <button
                onClick={saveVersion}
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: 'rgba(16, 185, 129, 0.1)',
                  color: '#10b981',
                  border: '1px solid #10b981',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Save Current State
              </button>
            </div>

            {/* Stats */}
            <div
              style={{
                padding: '12px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '6px',
                fontSize: '13px',
                color: '#94a3b8',
              }}
            >
              <div>Annotations: {annotations.length}</div>
              <div>Versions: {versions.length}</div>
            </div>
          </div>
        )}

        {/* Center - Canvas */}
        <div
          ref={containerRef}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'auto',
            padding: '20px',
            position: 'relative',
          }}
        >
          {!screenshot ? (
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: '20px', color: '#f1f5f9', marginBottom: '16px' }}>
                Ready to capture
              </h3>
              <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '24px' }}>
                Click the button below to take a screenshot of your current screen
              </p>
              <button
                onClick={captureScreenshot}
                disabled={isCapturing}
                style={{
                  padding: '16px 32px',
                  backgroundColor: 'rgba(99, 102, 241, 0.2)',
                  color: '#818cf8',
                  border: '2px solid #818cf8',
                  borderRadius: '8px',
                  cursor: isCapturing ? 'wait' : 'pointer',
                  fontSize: '16px',
                  fontWeight: 600,
                }}
              >
                {isCapturing ? 'Capturing...' : 'Capture Screenshot'}
              </button>
            </div>
          ) : (
            <div style={{ position: 'relative' }}>
              <canvas
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                style={{
                  maxWidth: '100%',
                  maxHeight: 'calc(100vh - 200px)',
                  cursor:
                    currentTool === 'none'
                      ? 'default'
                      : currentTool === 'text'
                      ? 'text'
                      : 'crosshair',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
                  borderRadius: '8px',
                }}
              />

              {/* Text Input Modal */}
              {showTextInput && (
                <div
                  style={{
                    position: 'absolute',
                    top: textPosition.y,
                    left: textPosition.x,
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    backdropFilter: 'blur(10px)',
                    padding: '16px',
                    borderRadius: '8px',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
                    zIndex: 1000,
                  }}
                >
                  <input
                    type="text"
                    value={textInput}
                    onChange={e => setTextInput(e.target.value)}
                    onKeyDown={e => {
                      if (e.key === 'Enter') addTextAnnotation();
                      if (e.key === 'Escape') {
                        setShowTextInput(false);
                        setTextInput('');
                      }
                    }}
                    autoFocus
                    placeholder="Enter text..."
                    style={{
                      width: '250px',
                      padding: '8px 12px',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      color: '#f1f5f9',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: '6px',
                      fontSize: '14px',
                      marginBottom: '8px',
                    }}
                  />
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={addTextAnnotation}
                      style={{
                        flex: 1,
                        padding: '6px',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        color: '#10b981',
                        border: '1px solid #10b981',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '13px',
                      }}
                    >
                      Add
                    </button>
                    <button
                      onClick={() => {
                        setShowTextInput(false);
                        setTextInput('');
                      }}
                      style={{
                        flex: 1,
                        padding: '6px',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        color: '#ef4444',
                        border: '1px solid #ef4444',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '13px',
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Sidebar - Versions */}
        {showVersions && (
          <div
            style={{
              width: '320px',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(10px)',
              padding: '20px',
              overflowY: 'auto',
              borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#f1f5f9' }}>
              Version History
            </h3>

            {versions.length === 0 ? (
              <p style={{ fontSize: '14px', color: '#64748b', textAlign: 'center' }}>
                No saved versions yet
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {versions
                  .slice()
                  .reverse()
                  .map(version => (
                    <div
                      key={version.id}
                      style={{
                        padding: '12px',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: '8px',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                      }}
                    >
                      <img
                        src={version.imageDataUrl}
                        alt={version.title}
                        style={{
                          width: '100%',
                          height: '120px',
                          objectFit: 'cover',
                          borderRadius: '6px',
                          marginBottom: '8px',
                          cursor: 'pointer',
                        }}
                        onClick={() => loadVersion(version)}
                      />
                      <div
                        style={{
                          fontSize: '14px',
                          color: '#f1f5f9',
                          fontWeight: 600,
                          marginBottom: '4px',
                        }}
                      >
                        {version.title}
                      </div>
                      <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>
                        {new Date(version.timestamp).toLocaleString()}
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={() => loadVersion(version)}
                          style={{
                            flex: 1,
                            padding: '6px',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            color: '#818cf8',
                            border: '1px solid #818cf8',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                          }}
                        >
                          Load
                        </button>
                        <button
                          onClick={() => deleteVersion(version.id)}
                          style={{
                            padding: '6px 12px',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            color: '#ef4444',
                            border: '1px solid #ef4444',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px',
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryboardCanvas;

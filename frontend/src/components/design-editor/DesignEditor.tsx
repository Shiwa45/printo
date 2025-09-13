import React, { useRef, useCallback, useState } from "react";
import { Canvas } from "react-design-editor";
import { Button, message, Upload, Select, Spin } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import axios from "axios";

const { Option } = Select;

export interface DesignEditorProps {
  productType?: string;
  templateId?: string;
  designId?: string;
  width?: number;
  height?: number;
  onSave?: (designData: any) => Promise<void> | void;
  onExport?: (format: string, data: any) => Promise<void> | void;
}

const DesignEditor: React.FC<DesignEditorProps> = ({
  productType = "business-card",
  templateId,
  designId,
  width = 800,
  height = 600,
  onSave,
  onExport,
}) => {
  const canvasRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  /** ========================
   *   INIT CANVAS
   *  ======================== */
  const handleCanvasReady = useCallback((canvasInstance: any) => {
    canvasRef.current = canvasInstance;
    console.log("Canvas ready:", canvasInstance);
  }, []);

  /** ========================
   *   IMAGE UPLOAD
   *  ======================== */
  const handleImageUpload = async (file: File) => {
    if (!canvasRef.current) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const { data } = await axios.post("/api/images/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // Django should return { url: "https://yourdomain.com/media/filename.png" }
      if (data.url) {
        canvasRef.current.addImage(data.url);
      }
    } catch (err) {
      console.error(err);
      message.error("Image upload failed");
    }
  };

  /** ========================
   *   TEXT TOOLS
   *  ======================== */
  const addText = () => {
    if (!canvasRef.current) return;
    canvasRef.current.addText("Your Text Here", {
      fontSize: 24,
      fill: "#000",
      fontFamily: "Arial",
    });
  };

  const changeFont = (font: string) => {
    if (!canvasRef.current) return;
    const active = canvasRef.current.getActiveObject();
    if (active && active.type === "text") {
      active.set("fontFamily", font);
      canvasRef.current.renderAll();
    }
  };

  /** ========================
   *   SAVE DESIGN (JSON)
   *  ======================== */
  const handleSave = async () => {
    if (!canvasRef.current) {
      message.warning("Canvas not ready");
      return;
    }

    const designData = canvasRef.current.toJSON();
    setIsLoading(true);

    try {
      if (onSave) {
        await onSave(designData);
      } else {
        await axios.post("/api/designs/save/", {
          data: designData,
          productType,
          templateId,
          designId,
        });
      }
      message.success("Design saved!");
    } catch (err) {
      console.error(err);
      message.error("Failed to save design");
    } finally {
      setIsLoading(false);
    }
  };

  /** ========================
   *   EXPORT DESIGN
   *  ======================== */
  const handleExport = async (format = "png") => {
    if (!canvasRef.current) {
      message.warning("Canvas not ready");
      return;
    }

    setIsLoading(true);
    try {
      let data;
      if (format === "png") {
        data = canvasRef.current.toDataURL({ format: "png" });
      } else if (format === "jpeg") {
        data = canvasRef.current.toDataURL({ format: "jpeg" });
      } else if (format === "svg") {
        data = canvasRef.current.toSVG();
      }

      if (onExport) {
        await onExport(format, data);
      } else {
        await axios.post("/api/designs/export/", { format, data });
      }

      message.success(`Exported as ${format}!`);
    } catch (err) {
      console.error(err);
      message.error("Export failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-gray-50">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900">
          ✨ Design Editor
        </h2>
        <div className="flex items-center space-x-2">
          <Upload
            beforeUpload={(file) => {
              handleImageUpload(file);
              return false; // prevent auto upload
            }}
          >
            <Button size="small" icon={<UploadOutlined />}>
              Upload Image
            </Button>
          </Upload>
          <Button size="small" onClick={addText}>
            Add Text
          </Button>
          <Select size="small" defaultValue="Arial" onChange={changeFont}>
            <Option value="Arial">Arial</Option>
            <Option value="Roboto">Roboto</Option>
            <Option value="Times New Roman">Times New Roman</Option>
          </Select>
          <Button
            onClick={handleSave}
            loading={isLoading}
            type="primary"
            size="small"
          >
            Save
          </Button>
          <Button
            onClick={() => handleExport("png")}
            loading={isLoading}
            size="small"
          >
            PNG
          </Button>
          <Button
            onClick={() => handleExport("jpeg")}
            loading={isLoading}
            size="small"
          >
            JPG
          </Button>
          <Button
            onClick={() => handleExport("svg")}
            loading={isLoading}
            size="small"
          >
            SVG
          </Button>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/60 z-10">
            <Spin />
          </div>
        )}
        <Canvas width={width} height={height} onLoad={handleCanvasReady} />
      </div>
    </div>
  );
};

export default DesignEditor;

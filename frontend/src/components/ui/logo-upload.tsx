"use client";

import { useEffect, useRef, useState } from "react";
import { ImagePlus, Upload, Trash2 } from "lucide-react";
import { Button } from "./button";
import clsx from "clsx";

interface LogoUploadProps {
  value?: File | string | null;
  onChange: (file: File | null) => void;
  className?: string;
}

export function LogoUpload({ value, onChange, className }: LogoUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!value) {
      setPreview(null);
      return;
    }

    if (typeof value === "string") {
      // base64 or URL
      setPreview(value);
    } else if (value instanceof File) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(value);
    }
  }, [value]);

  // console.log(value || preview);
  // const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  //   const file = e.target.files?.[0];
  //   if (file) {
  //     onChange(file);
  //     const reader = new FileReader();
  //     reader.onloadend = () => {
  //       setPreview(reader.result as string);
  //     };
  //     reader.readAsDataURL(file);
  //   }
  // };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    onChange(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  // const handleDelete = () => {
  //   onChange(null);
  //   setPreview(null);
  //   if (fileInputRef.current) {
  //     fileInputRef.current.value = "";
  //   }
  // };
  const handleDelete = () => {
    onChange(null);
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className={clsx("relative w-full", className)}>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      <div
        className={clsx(
          "flex items-center gap-3 rounded-lg bg-gray-50 h-[80px] px-4",
          "cursor-pointer hover:bg-gray-100 transition-colors"
        )}
        onClick={handleClick}
      >
        {/* Icon/Image with circular background */}
        <div className="flex  items-center justify-center w-12 h-12 rounded-full bg-gray-200 overflow-hidden">
          {preview ? (
            <img
              src={preview}
              alt="Logo preview"
              className="w-full h-full object-cover"
            />
          ) : (
            <ImagePlus className="w-5 h-5 text-gray-400" strokeWidth={1} />
          )}
        </div>

        {/* Preview text */}
        <div className="flex-1 text-sm text-gray-600"></div>

        {/* Upload/Change button */}
        <Button
          type="button"
          color="white"
          className="flex items-center gap-2 text-sm border !border-gray-300"
          onClick={(e) => {
            e.stopPropagation();
            handleClick();
          }}
        >
          {!preview && <Upload className="w-4 h-4 text-primary" />}
          {preview ? "Change picture" : "Upload Logo"}
        </Button>

        {/* Delete icon */}
        {preview && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              handleDelete();
            }}
            className="flex items-center justify-center w-8 h-8 hover:bg-gray-200 transition-colors"
          >
            <Trash2 className="w-4 h-4 text-red-600" />
          </button>
        )}
      </div>
    </div>
  );
}

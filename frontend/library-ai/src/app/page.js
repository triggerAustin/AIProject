"use client";

import { useState, useRef } from "react";

export default function UploadComponent() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null); // Reference for file input

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a document first.");
      setMessages([]);
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("prompt", prompt);

    try {
      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload document");
      }

      const data = await response.json();
      setMessages((prev) => [...prev, { type: "bot", text: data.answer }]);
    } catch (error) {
      console.error("Error uploading document:", error);
      alert("Upload failed. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!prompt.trim()) return;

    setMessages((prev) => [...prev, { type: "user", text: prompt }]);
    setPrompt("");
    await handleUpload();
  };

  const handleClearChat = () => {
    setFile(null);
    setPrompt("");
    setMessages([]);
    setLoading(false);

    // Clear file input field
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 p-6">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
        <h2 className="text-xl font-semibold mb-4 text-black">Chat with Your Document</h2>

        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="mb-4 text-black" 
        />

        <div className="h-64 overflow-y-auto bg-gray-200 p-4 rounded-lg mb-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-2 rounded-lg mb-2 ${
                msg.type === "user" ? "bg-blue-500 text-white self-end" : "bg-gray-300 text-black self-start"
              }`}
            >
              {msg.text}
            </div>
          ))}
        </div>

        <div className="flex gap-2 text-black">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 p-2 border rounded-lg"
          />
          <button
            onClick={handleSendMessage}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>

        <button
          onClick={handleClearChat}
          className="bg-red-500 text-white px-4 py-2 mt-4 rounded-lg hover:bg-red-600 w-full"
          disabled={loading}
        >
          Clear Chat
        </button>
      </div>
    </div>
  );
}

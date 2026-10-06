import { useState } from "react";

const MAX_LENGTH = 20000;

export default function EntryForm({ onSubmit }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!text.trim()) {
      setError("Please enter some text first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await onSubmit(text);
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2>New entry</h2>
      <p className="muted">Paste a note, article draft or meeting transcript.</p>
      <textarea
        id="text"
        rows={12}
        placeholder="Start typing or paste your text here…"
        value={text}
        maxLength={MAX_LENGTH}
        onChange={(e) => {
          setText(e.target.value);
          if (error) setError("");
        }}
        disabled={loading}
      />
      <div className="row">
        <span className="muted">
          {text.length.toLocaleString()} / {MAX_LENGTH.toLocaleString()}
        </span>
        <button type="submit" disabled={loading}>
          {loading && <span className="spinner" />}
          {loading ? "Generating…" : "Summarize & tag"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

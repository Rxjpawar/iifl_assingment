export default function EntryDetail({ entry, loading, error, onNew }) {
  if (loading) return <div className="card muted">Loading entry…</div>;
  if (error) {
    return (
      <div className="card">
        <p className="error">{error}</p>
        <button className="secondary" onClick={onNew}>Back to new entry</button>
      </div>
    );
  }
  if (!entry) return null;

  return (
    <article className="card">
      <div className="detail-head">
        <h2>Entry #{entry.id}</h2>
        <span className="muted">{new Date(entry.created_at).toLocaleString()}</span>
      </div>

      <h3>Summary</h3>
      <p className="summary">{entry.summary}</p>

      <h3>Tags</h3>
      <div className="tags">
        {entry.tags.map((tag) => (
          <span key={tag} className="tag">
            {tag}
          </span>
        ))}
      </div>

      <h3>Original text</h3>
      <pre className="original">{entry.original_text}</pre>
    </article>
  );
}

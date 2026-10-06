export default function EntryList({ entries, selectedId }) {
  return (
    <ul className="list">
      {entries.map((entry) => (
        <li key={entry.id}>
          <a
            href={`#/entries/${entry.id}`}
            className={`item ${entry.id === selectedId ? "active" : ""}`}
          >
            <span className="item-summary">{entry.summary}</span>
            <span className="item-meta">
              <span className="tag small">{entry.tags[0]}</span>
              <span className="muted">{new Date(entry.created_at).toLocaleDateString()}</span>
            </span>
          </a>
        </li>
      ))}
    </ul>
  );
}

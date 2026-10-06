import { useCallback, useEffect, useState } from "react";
import { createEntry, getEntry, listEntries } from "./api.js";
import EntryForm from "./components/EntryForm.jsx";
import EntryList from "./components/EntryList.jsx";
import EntryDetail from "./components/EntryDetail.jsx";

// The open entry lives in the URL hash (#/entries/3) so it survives a reload.
function idFromHash() {
  const match = window.location.hash.match(/^#\/entries\/(\d+)$/);
  return match ? Number(match[1]) : null;
}

export default function App() {
  const [entries, setEntries] = useState([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState("");

  const [selectedId, setSelectedId] = useState(idFromHash);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  // GET /entries
  const refreshList = useCallback(async () => {
    setListLoading(true);
    try {
      setEntries(await listEntries());
      setListError("");
    } catch (err) {
      setListError(err.message);
    } finally {
      setListLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshList();
  }, [refreshList]);

  useEffect(() => {
    const onHashChange = () => setSelectedId(idFromHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  // GET /entries/{id}
  useEffect(() => {
    if (selectedId === null) {
      setDetail(null);
      setDetailError("");
      return;
    }
    let cancelled = false;
    setDetailLoading(true);
    setDetailError("");
    getEntry(selectedId)
      .then((entry) => !cancelled && setDetail(entry))
      .catch((err) => {
        if (cancelled) return;
        setDetail(null);
        setDetailError(err.message);
      })
      .finally(() => !cancelled && setDetailLoading(false));
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  // POST /entries
  async function handleSubmit(text) {
    const entry = await createEntry(text); // errors are shown by the form
    setEntries((prev) => [entry, ...prev]);
    window.location.hash = `#/entries/${entry.id}`;
  }

  function openNew() {
    window.location.hash = "";
    setSelectedId(null);
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="logo">✦</span>
        <h1>AI Content Assistant</h1>
        <span className="topbar-sub">Summaries and tags for any text</span>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <button className="new-btn" onClick={openNew}>
            + New entry
          </button>
          <div className="sidebar-title">Saved entries ({entries.length})</div>
          {listLoading && <p className="muted pad">Loading…</p>}
          {listError && (
            <div className="error pad">
              {listError} <button className="link" onClick={refreshList}>Retry</button>
            </div>
          )}
          {!listLoading && !listError && entries.length === 0 && (
            <p className="muted pad">No entries yet.</p>
          )}
          <EntryList entries={entries} selectedId={selectedId} />
        </aside>

        <main className="main">
          {selectedId === null ? (
            <EntryForm onSubmit={handleSubmit} />
          ) : (
            <EntryDetail
              entry={detail}
              loading={detailLoading}
              error={detailError}
              onNew={openNew}
            />
          )}
        </main>
      </div>
    </div>
  );
}

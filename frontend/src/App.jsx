import { useState } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/search", { url, query });
      setResults(res.data.results || []);
    } catch (err) {
      alert("Search failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Website Content Search</h2>
      <p>Enter a website URL and a search query to find relevant content.</p>
      <form onSubmit={onSubmit}>
        <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com" style={{width:400, height:30, padding:5}}/>
        <br/><br/>
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search query" style={{width:400, height:30, padding:5}} />
        <br/><br/>
        <button type="submit" disabled={loading}>{loading ? "Searching..." : "Search"}</button>
      </form>

      <div style={{marginTop:20}}>
        {results.map((r, i) => (
          <div key={i} style={{border:"1px solid #ddd", padding:10, marginBottom:10}}>
            <div><b>Score:</b> {r.score.toFixed(4)}</div>
            <div><b>Text snippet:</b> {r.text.slice(0,400)}...</div>
            <details>
              <summary>View HTML</summary>
              <div dangerouslySetInnerHTML={{__html: r.html}} />
            </details>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

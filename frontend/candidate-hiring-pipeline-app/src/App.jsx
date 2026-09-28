import { useEffect, useRef, useState } from "react";
import "./App.css";

const stages = ["Applied", "Screening", "Interview", "Offer", "Hired"];

function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searchMessage, setSearchMessage] = useState("");
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [candidateHistory, setCandidateHistory] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showForm, setShowForm] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");

  const historyRef = useRef(null);

  const loadCandidates = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/candidates/");

      const data = await response.json();

      setCandidates(data);
    } catch (error) {
      console.error("Failed to load candidates:", error);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const addCandidate = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/candidates/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          role,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add candidate");
      }

      setName("");
      setEmail("");
      setRole("");
      setShowForm(false);

      loadCandidates();
    } catch (error) {
      console.error("Failed to add candidate:", error);
    }
  };
  const moveCandidate = async (candidateId) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/candidates/${candidateId}/advance`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        const error = await response.json();
        alert(error.detail);
        return;
      }

      loadCandidates();
    } catch (error) {
      console.error("Failed to move candidate:", error);
    }
  };

  const rejectCandidate = async (candidateId) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/candidates/${candidateId}/reject`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        const error = await response.json();
        alert(error.detail);
        return;
      }

      loadCandidates();
    } catch (error) {
      console.error("Failed to reject candidate:", error);
    }
  };

  const viewHistory = async (candidate) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/candidates/${candidate.id}/history`,
      );

      if (!response.ok) {
        throw new Error("Failed to load history");
      }

      const data = await response.json();

      setSelectedCandidate(candidate);
      setCandidateHistory(data);
      setTimeout(() => {
        historyRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 100);
    } catch (error) {
      console.error("Failed to load candidate history:", error);
    }
  };
  const searchCandidates = async () => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      setSearchMessage("");
      loadCandidates();
      return;
    }

    setIsSearching(true);
    setSearchMessage("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/search/?query=${encodeURIComponent(searchQuery)}`,
      );

      const data = await response.json();

      if (Array.isArray(data)) {
        setSearchResults(data);
        setSearchMessage("");
      } else {
        setSearchResults(data.results || []);
        setSearchMessage(data.message || "");
      }
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults([]);
      setSearchMessage("Something went wrong while searching.");
    } finally {
      setIsSearching(false);
    }
  };

  const displayedCandidates =
    searchResults !== null ? searchResults : candidates;

  return (
    <div className="app">
      <header className="header">
        <h1>Mini Hiring Pipeline</h1>

        <button className="add-button" onClick={() => setShowForm(true)}>
          + Add Candidate
        </button>
      </header>

      {showForm && (
        <div className="candidate-form">
          <h2>Add Candidate</h2>

          <form onSubmit={addCandidate}>
            <input
              type="text"
              placeholder="Candidate name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
            />

            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <input
              type="text"
              placeholder="Role, Like Software Developer, QA, CA"
              value={role}
              onChange={(event) => setRole(event.target.value)}
              required
            />

            <div className="form-buttons">
              <button type="submit">Add Candidate</button>

              <button type="button" onClick={() => setShowForm(false)}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="search-box">
        <input
          type="text"
          placeholder="Search candidates..."
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !isSearching) {
              searchCandidates();
            }
          }}
        />
        {searchResults !== null && (
          <button
            className="clear-search"
            onClick={() => {
              setSearchResults(null);
              setSearchMessage("");
              setSearchQuery("");
            }}
          >
            Clear Search
          </button>
        )}
        {searchMessage && <div className="search-message">{searchMessage}</div>}

        <button onClick={searchCandidates} disabled={isSearching}>
          {isSearching ? "Finding..." : "Search"}
        </button>
      </div>

      <main className="pipeline">
        {stages.map((stage) => (
          <section className="stage-column" key={stage}>
            <h2>{stage}</h2>

            {displayedCandidates
              .filter((candidate) => candidate.current_stage === stage)
              .map((candidate) => (
                <div className="candidate-card" key={candidate.id}>
                  <h3>{candidate.name}</h3>

                  <p>{candidate.email}</p>

                  <p>{candidate.role}</p>

                  <small>
                    {candidate.days_in_current_stage} days in this stage
                  </small>

                  {candidate.current_stage !== "Hired" && (
                    <div className="candidate-actions">
                      <button onClick={() => moveCandidate(candidate.id)}>
                        Move Forward
                      </button>

                      <button onClick={() => rejectCandidate(candidate.id)}>
                        Reject
                      </button>
                    </div>
                  )}
                  <button
                    className="history-button"
                    onClick={() => viewHistory(candidate)}
                  >
                    View History
                  </button>
                </div>
              ))}
          </section>
        ))}
      </main>

      <section className="rejected-section">
        <h2>Rejected</h2>

        {displayedCandidates
          .filter((candidate) => candidate.current_stage === "Rejected")
          .map((candidate) => (
            <div className="candidate-card" key={candidate.id}>
              <h3>{candidate.name}</h3>
              <p>{candidate.email}</p>
              <p>{candidate.role}</p>

              <small>
                {candidate.days_in_current_stage} days in this stage
              </small>
              <button
                className="history-button"
                onClick={() => viewHistory(candidate)}
              >
                View History
              </button>
            </div>
          ))}
      </section>
      {selectedCandidate && (
        <section className="history-section" ref={historyRef}>
          <div className="history-header">
            <div>
              <h2>{selectedCandidate.name}</h2>
              <p>{selectedCandidate.email}</p>
              <p>{selectedCandidate.role}</p>
              <strong>Current stage: {selectedCandidate.current_stage}</strong>
              <p>
                {selectedCandidate.days_in_current_stage} days in current stage
              </p>
            </div>

            <button onClick={() => setSelectedCandidate(null)}>Close</button>
          </div>

          <h3>Stage History</h3>

          <div className="history-list">
            {candidateHistory.map((item) => (
              <div className="history-item" key={item.id}>
                <strong>
                  {item.from_stage || "New candidate"}
                  {" → "}
                  {item.to_stage}
                </strong>

                <span>{new Date(item.changed_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default App;

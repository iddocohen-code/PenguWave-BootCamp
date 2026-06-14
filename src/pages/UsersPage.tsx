import { useState, useEffect } from "react";
import { getUsers, createUser, deleteUser } from "../api";

interface User {
  id: string;
  email: string;
  role: string;
  status: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("analyst");

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getUsers();
      if (data.error) {
        setError(data.error);
      } else {
        setUsers(data || []);
      }
    } catch (err) {
      setError("Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newPassword) return;

    try {
      const data = await createUser({ email: newEmail, password: newPassword, role: newRole });
      if (data.error) {
        setError(data.error);
      } else {
        setUsers([...users, data]);
        setNewEmail("");
        setNewPassword("");
        setNewRole("analyst");
        setShowForm(false);
      }
    } catch (err) {
      setError("Failed to create user");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const data = await deleteUser(id);
      if (data.error) {
        setError(data.error);
      } else {
        setUsers(users.filter((u) => u.id !== id));
      }
    } catch (err) {
      setError("Failed to delete user");
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1>User Management</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {error && <p style={{ color: "red", marginBottom: 12 }}>{error}</p>}

      {showForm && (
        <div style={{ border: "1px solid #ddd", padding: 16, marginBottom: 20, background: "#fafafa" }}>
          <h3 style={{ marginBottom: 12 }}>New User</h3>
          <form onSubmit={handleAddUser}>
            <div style={{ marginBottom: 8 }}>
              <label>Email</label>
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="user@penguwave.io"
                required
              />
            </div>
            <div style={{ marginBottom: 8 }}>
              <label>Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Role</label>
              <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
                <option value="admin">Admin</option>
                <option value="analyst">Analyst</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <button type="submit" className="btn-primary">
              Create User
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <p style={{ color: "#999" }}>Loading...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>
                  <span style={{ color: user.status === "active" ? "green" : "#999" }}>
                    {user.status}
                  </span>
                </td>
                <td>
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      handleDelete(user.id);
                    }}
                    style={{ color: "red" }}
                  >
                    Delete
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!loading && users.length === 0 && <p style={{ color: "#999" }}>No users.</p>}
    </div>
  );
}

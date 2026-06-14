const API_URL = "http://localhost:3001";

export async function login(email: string, password: string) {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) {
    localStorage.setItem("token", data.token);
    if (data.user?.role) {
      localStorage.setItem("role", data.user.role);
    }
  }
  return data;
}

export async function logout() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/auth/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  return res.json();
}

export async function getMe() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getEvents() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/events`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getEvent(id: string) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/events/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getUsers() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function createUser(user: { email: string; password: string; role: string }) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(user),
  });
  return res.json();
}

export async function patchUser(id: string, updates: { role?: string; status?: string }) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(updates),
  });
  return res.json();
}

export async function deleteUser(id: string) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/api/users/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

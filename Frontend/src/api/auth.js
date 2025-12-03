import axios from "axios";

const API = "http://localhost:8000";

export async function login(email, password) {
  const formData = new FormData();
  formData.append("username", email); // FastAPI requires "username"
  formData.append("password", password);

  return axios.post(`${API}/auth/login`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export async function register(email, password) {
  return axios.post(`${API}/auth/register`, {
    email,
    password,
  });
}

export async function getCurrentUser(token) {
  return axios.get(`${API}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
